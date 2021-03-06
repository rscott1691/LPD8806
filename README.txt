raspi.lpd8806
*************

This package provides helpers to easily build fancy LED stuff with a "lpd8806
based digital addressable RGB led strip":https://www.adafruit.com/products/306. 

It consists of three parts.


API for sequences
=================

To define a sequence you can use `raspi.lpd8806.led_lib.Sequence` as a base
class.

On the class you can set, if the sequence should loop by setting `loop =
True`.

You also have to define the used leds by the sequence on the class in a list
`leds = [12, 33, 44]`.

The actual sequence is defined in the __call__ method which has to
return a generator yielding leds with their values for each frame.

You can set a single Led via `raspi.lpd8806.led_lib.Led(index).on(red, green,
blue)`, or set multiple Leds at once via `Leds([12, 33, 44]).on({12: (r, g, b),
33: (r, g, b), 44: (r, g, b)})`.

There is also a convenience method to set a predefined part of your strip by
using `raspi.lpd8806.led_lib.Strip('strip_name').on(r, g, b)`.

Led, Leds and Strip instances of course also have `off()` methods to set all
colors to 0.


Webserver
=========

The Webserver serves a page with buttons to start or stop the sequences.
It is started with the led_webserver script. See --help for details.

Queue Worker
============

The Queue worker processes the commands of the webserver and communicates with
the LED strip. It can be started with the led_queue_worker script. See --help
for details.
