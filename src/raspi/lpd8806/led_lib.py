#Maps strip names to lists of led numbers, so that
#multiple leds can be addressed at once.
#i.e. {'left': range(0, 48)}

STRIPS = {}


def register_strip(name, leds):
    if name in STRIPS:
        raise ValueError("Strip with name {} is already registered.".format(
            name))
    STRIPS[name] = leds


class Sequence(object):

    loop = False
    finished = False
    autostart = False
    leds = []
    num = 0

    def __init__(self, num):
        self.num = num


class Led(object):

    def __init__(self, id):
        self.id = id

    def on(self, r, g, b):
        return {self.id: (r, g, b)}

    def off(self):
        return {self.id: (0, 0, 0)}


class Leds(object):
    def __init__(self, *leds):
        self.contained_leds = leds
        self.leds = {led_id: Led(led_id) for led_id in self.contained_leds}

    def on(self, color_map):
        rets = {}
        for led in color_map.keys():
            rets.update(self.leds[led].on(*color_map[led]))
        return rets

    def off(self):
        rets = {}
        for led in self.leds.values():
            rets.update(led.off())
        return rets


class Strip(object):

    def __init__(self, name):
        self.contained_leds = STRIPS[name]
        self.leds = [Led(led_id) for led_id in self.contained_leds]

    def on(self, r, g, b):
        rets = {}
        for led in self.leds:
            rets.update(led.on(r, g, b))
        return rets

    def off(self):
        rets = {}
        for led in self.leds:
            rets.update(led.off())
        return rets


def tick():
    #NOOP
    return {}
