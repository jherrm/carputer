import tkinter
import serial
import config
import camera
import cv2
# ser = serial.Serial('/dev/cu.usbmodem1411', 115200)


class DummySerial(object):
    def write(self, val):
        pass


ser = DummySerial()

tk = tkinter.Tk()

has_prev_key_release = None

left_code = 8124162
right_code = 8189699


class MainLoop(object):
    def __init__(self):
        frame = tkinter.Frame(tk, width=100, height=100)
        frame.bind("<KeyRelease-Left>", self.on_key_release_repeat)
        frame.bind("<KeyPress-Left>", self.on_key_press_repeat)
        frame.bind("<KeyRelease-Right>", self.on_key_release_repeat)
        frame.bind("<KeyPress-Right>", self.on_key_press_repeat)
        frame.pack()
        frame.focus_set()
        self.camera_stream = camera.CameraStream(src=config.camera_id).start()
        self.frame_index = 0
        self.is_left_down = False
        self.is_right_down = False
        print('init\'d!')

        tk.after(10, self.on_frame)
        tk.mainloop()

    def on_frame(self):
        self.frame_index += 1
        frame = self.camera_stream.read()
        cv2.imwrite('/tmp/test_%d_%d_%d.jpg' % (self.frame_index, self.is_left_down, self.is_right_down), frame)

        tk.after(10, self.on_frame)

    def flip_left(self):
        print("Flip left")
        ser.write(b'2')
        self.is_left_down = True


    def flip_right(self):
        print("Flip Right")
        ser.write(b'0')
        self.is_right_down = True

    def release_left(self):
        print('Release Left')
        ser.write(b'3')
        self.is_left_down = False


    def release_right(self):
        print("Release Right")
        ser.write(b'1')
        self.is_right_down = False

    def on_key_release(self, event):
        global has_prev_key_release
        has_prev_key_release = None
        # print("on_key_release", repr(event.char))
        if event.keycode == left_code:
            self.release_left()
        elif event.keycode == right_code:
            self.release_right()

    def on_key_press(self, event):
        # print("on_key_press", repr(event.char))
        print("press", event.keycode)
        if event.keycode == left_code:
            self.flip_left()
        elif event.keycode == right_code:
            self.flip_right()

    def on_key_release_repeat(self, event):
        global has_prev_key_release
        has_prev_key_release = tk.after_idle(self.on_key_release, event)
        # print("on_key_release_repeat", repr(event.char))

    def on_key_press_repeat(self, event):
        global has_prev_key_release
        if has_prev_key_release:
            tk.after_cancel(has_prev_key_release)
            has_prev_key_release = None
            # print("on_key_press_repeat", repr(event.char))
        else:
            self.on_key_press(event)


if __name__ == '__main__':
    m = MainLoop()
