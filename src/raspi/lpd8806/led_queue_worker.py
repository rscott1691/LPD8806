#coding:utf8
from haigha.connection import Connection
from haigha.message import Message
from led_lib import Strip
from ledstrip import *
import argparse
import inspect
import json
import os
import requests
import requests.exceptions
import time
import urllib


def get_used_leds(seq):
    used = []
    for led in seq.leds:
        if isinstance(led, str):
            used += Strip(led).contained_leds
        else:
            used.append(led)
    return set(used)


class LedQueueWorker(object):

    def __init__(self, num_of_leds, backend, www_url, packages, delay):
        self.available = {}
        self.www_url = www_url
        self.delay = delay
        for package in packages:
            seqs = __import__(package, fromlist=[''])
            if not hasattr(seqs, 'sequences'):
                raise ValueError(
                    "{} is not a valid sequence package. "
                    "(Missing 'sequences' attribute.)".format(package))
            for sequence_name, sequence_class in seqs.sequences.items():
                self.available.update(
                    {sequence_name: sequence_class(num_of_leds)})
        self.avail_data = urllib.quote(json.dumps(self.available.keys()))
        self.update_avail()
        self.num_of_leds = num_of_leds
        self.backend = backend
        self.current_sequences = []
        self.queue = [seq for name, seq
                       in self.available.items() if seq.autostart]
        connection = Connection(
            user='guest', password='guest',
            vhost='/', host='localhost',
            heartbeat=None, debug=True)
        self.ch = connection.channel()
        self.ch.exchange.declare('www_to_leds', 'direct')
        self.ch.queue.declare('queue', auto_delete=True)
        self.ch.queue.bind('queue', 'www_to_leds', 'key')

    def update_avail(self):
        try:
            requests.get('{}/update_availables?{}'.format(
                self.www_url, self.avail_data))
        except requests.exceptions.ConnectionError:
            pass

    def notify_current(self):
        data = urllib.quote(json.dumps(
            [seq.name for seq, gen in self.current_sequences]))
        requests.get('{}/update_current?{}'.format(self.www_url, data))

    def notify_queue(self):
        data = urllib.quote(json.dumps([seq.name for seq in self.queue]))
        requests.get('{}/update_queue?{}'.format(self.www_url, data))

    def stop_sequence(self, sequence):
        new_current = []
        for seq, gen in self.current_sequences:
            if seq == sequence:
                data = {}
                for led in get_used_leds(seq):
                    data[led] = (0, 0, 0)
                self.backend(data)
                continue
            new_current.append((seq, gen))
        if new_current != self.current_sequences:
            self.current_sequences = new_current
            self.notify_current()

    def remove_from_queue(self, sequence):
        new_queue = []
        for seq in self.queue:
            if seq == sequence:
                continue
            new_queue.append(seq)
        if new_queue != self.queue:
            self.queue = new_queue
            self.notify_queue()

    def remove_finished(self, do_looping=True):
        cur_new = []
        for seq, gen in self.current_sequences:
            if seq.finished:
                if not do_looping:
                    continue
                if not seq.loop:
                    continue
                seq.finished = False
                gen = seq()
            cur_new.append((seq, gen))
        if cur_new != self.current_sequences:
            self.current_sequences = cur_new
            self.notify_current()

    def check_queue(self):
        if self.queue:
            seq_to_add = self.queue.pop()
            seq_to_add.finished = False
            current_used = set()
            map_used_leds_to_seq = dict()
            for seq, gen in self.current_sequences:
                used_leds_of_seq = get_used_leds(seq)
                current_used.update(used_leds_of_seq)
                for led in used_leds_of_seq:
                    map_used_leds_to_seq[led] = seq
            used_leds_of_seq_to_add = get_used_leds(seq_to_add)
            if used_leds_of_seq_to_add.intersection(current_used):
                if seq_to_add.loop:
                    #no need to do further checking because it makes no sense
                    #to overwrite a looping seq with another looping seq
                    self.queue.insert(0, seq_to_add)
                    return
                overlapping_seqs = []
                for led in used_leds_of_seq_to_add:
                    overlapping_seq = map_used_leds_to_seq.get(led)
                    if overlapping_seq:
                        if not overlapping_seq.loop:
                            #we found a overlepping sequence which is no loop,
                            #so we can't add queued seq here
                            break
                        overlapping_seqs.append(overlapping_seq)
                #stop overlapping seqs and queue them
                for seq in overlapping_seqs:
                    seq.finished = True
                    self.queue.insert(0, seq)
                    self.notify_queue()
                    self.current_sequences.append((seq_to_add, seq_to_add()))
                    self.notify_current()
                    return
                self.queue.insert(0, seq_to_add)
                return
            self.current_sequences.append((seq_to_add, seq_to_add()))
            self.notify_queue()
            self.notify_current()
            return

    def main(self):
        index = 0
        current = {}
        last = {}
        while True:
            if not index % 100:
                self.update_avail()
            msg = self.ch.basic.get('queue')
            if msg:
                if str(msg.body).startswith('stop:'):
                    seq_name = str(msg.body).replace('stop:', '')
                    seq = self.available.get(seq_name)
                    if seq:
                        self.stop_sequence(seq)
                elif str(msg.body).startswith('remove:'):
                    seq_name = str(msg.body).replace('remove:', '')
                    seq = self.available.get(seq_name)
                    if seq:
                        self.remove_from_queue(seq)
                else:
                    seq_name = str(msg.body)
                    seq = self.available.get(seq_name)
                    if seq and seq not in self.queue:
                        self.queue.append(seq)
                        self.notify_queue()
            self.remove_finished()
            self.check_queue()
            self.remove_finished(do_looping=False)
            for seq, seq_generator in self.current_sequences:
                if seq.finished:
                    continue
                try:
                    last = current.copy()
                    current.update(seq_generator.next())
                except StopIteration:
                    seq.finished = True
            if current != last:
                self.backend(current)
            time.sleep(self.delay)
            index += 1


def printbackend(data):
    print data


def main(backend, num, packages, url, device, delay):
    if backend == 'stdout':
        output = printbackend
    elif backend == 'lpd8806':
        output = Led8806(num, device).set_leds_from_dict
    queueworker = LedQueueWorker(num, output, url, packages, delay)
    queueworker.main()


def entry():
    parser = argparse.ArgumentParser(description='Run the led sequence queue.')
    parser.add_argument(
        '-p', '--packages', metavar='PACKAGE', type=str,
        nargs='+', help='Python modules containing sequences.',
        default=['raspi.lpd8806.default_sequences'])
    parser.add_argument(
        '-b', '--backend', type=str, choices=['stdout', 'lpd8806'],
        help='Backend which should be used.',
        default='lpd8806')
    parser.add_argument(
        '-d', '--device', type=str,
        help='Device where lpd8806 strip is connected.',
        default='/dev/spidev0.0')
    parser.add_argument(
        '-n', '--num', type=int, help='Number of LEDs on your strip.',
        default=136)
    parser.add_argument(
        '-u', '--url', type=str, help='URL of the Webserver.',
        default='http://localhost:8080')
    parser.add_argument(
        '-t', '--time', type=float, help='Delay between cycles. With the '
        'default value of 0.035 you get approximately 24fps with 136 LEDs.',
        default='0.035')
    args = parser.parse_args()
    main(args.backend,
         args.num,
         args.packages,
         args.url,
         args.device,
         args.time)

if __name__ == '__main__':
    entry()
