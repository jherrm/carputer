import serial


class Pinball(object):
    def __init__(self):
        self.ser = self.setup_serial()
        self.is_left_down = False
        self.is_right_down = False

    def setup_serial(self):
        return serial.Serial('/dev/cu.usbmodem1411', 115200)

    def flip_left(self):
        print("Flip left")
        self.ser.write(b'2')
        self.is_left_down = True

    def flip_right(self):
        print("Flip Right")
        self.ser.write(b'0')
        self.is_right_down = True

    def release_left(self):
        print('Release Left')
        self.ser.write(b'3')
        self.is_left_down = False

    def release_right(self):
        print("Release Right")
        self.ser.write(b'1')
        self.is_right_down = False


class DummySerial(object):
    def write(self, val):
        print('dummy write %s' % val)


class DummyPinball(Pinball):
    def setup_serial(self):
        return DummySerial()
