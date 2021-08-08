from haigha.connection import Connection
from haigha.message import Message
import mushroom
import logging
import led_server
import gevent
import os.path


SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080


TEMPLATE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'led.html')


class LedServer(led_server.LedBaseServer):

    def __init__(self, listener):
        connection = Connection(
            user='guest', password='guest',
            vhost='/', host='localhost',
            heartbeat=None, debug=True)
        self.ch = connection.channel()
        self.ch.exchange.declare('www_to_leds', 'direct')
        self.ch.queue.declare('queue', auto_delete=True)
        self.ch.queue.bind('queue', 'www_to_leds', 'key')
        super(LedServer, self).__init__(
            listener, TEMPLATE, mushroom.MethodDispatcher(self, 'rpc_'))

    def rpc_get_availables(self, request):
        self.sessions.notify(
            'available', self.application.available)

    def rpc_message(self, request):
        msg = request.data['message']
        self.ch.basic.publish(
            Message(msg,
                    application_headers={'hello': 'world'}),
                    'www_to_leds', 'key')
        if msg.startswith('stop:'):
            pass
        elif msg.startswith('remove:'):
            pass
        else:
            self.sessions.notify('button_pressed', request.data['message'])


def runserver(listener):
    server = LedServer(listener)
    server.serve_forever()


def main():
    logging.basicConfig()
    listener = (SERVER_HOST, SERVER_PORT)
    print 'Server running at %s:%d' % listener
    runserver(listener)

if __name__ == '__main__':
    main()
