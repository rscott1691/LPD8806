#coding:utf8


#Calculate gamma correction table. This includes
#LPD8806-specific conversion (7-bit color w/high bit set).
GAMMA = bytearray(256)
for i in range(256):
    GAMMA[i] = 0x80 | int(pow(float(i) / 255.0, 2.5) * 127.0 + 0.5)


class Led8806(object):

    def __init__(self, num_of_leds, device):
        self.array = bytearray(num_of_leds * 3 + 1)
        self.num = num_of_leds
        self.spidev = file(device, "wb")
        self.init()

    def init(self):
        for col in ((255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)):
            for led in range(self.num):
                self.set_led(led, *col)
            self.update()
            self.update()

    def update(self):
        self.spidev.write(self.array)
        self.spidev.flush()

    def set_led(self, target, r, g, b):
        target = target * 3
        self.array[target] = GAMMA[g]
        self.array[target + 1] = GAMMA[r]
        self.array[target + 2] = GAMMA[b]

    def set_leds_from_dict(self, data):
        for led, color in data.items():
            target = led * 3
            for offset in range(3):
                self.array[target + offset] = GAMMA[color[offset]]
        self.update()
