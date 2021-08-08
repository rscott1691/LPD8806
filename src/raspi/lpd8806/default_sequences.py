from raspi.lpd8806.led_lib import Leds, tick, Sequence


class FlashAll(Sequence):

    name = 'flashall'

    def __init__(self, num):
        super(FlashAll, self).__init__(num)
        self.leds = range(1, num + 1)
        self.all_on = dict((x, (255, 255, 255)) for x in self.leds)

    def __call__(self):
        yield Leds(*self.leds).on(self.all_on)
        yield Leds(*self.leds).off()
        yield tick()
        yield tick()
        yield tick()
        yield tick()
        yield tick()
        yield tick()


class Smooth(Sequence):

    name = 'smooth'
    loop = True

    def __init__(self, num):
        super(Smooth, self).__init__(num)
        self.leds = range(1, num + 1)

    def __call__(self):
        for x in range(0, 256):
            r = 0
            g = 90
            b = 200
            red = r + x + 1
            green = g + x
            blue = b + x + 2
            all_leds = dict(
                (led, (red % 256, blue % 256, green % 256))
                for led in self.leds)
            yield Leds(*self.leds).on(all_leds)

sequences = {FlashAll.name: FlashAll, Smooth.name: Smooth}
