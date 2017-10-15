
import tkinter
import serial
import config
import cv2
import os
# ser = serial.Serial('/dev/cu.usbmodem1411', 115200)


class DummySerial(object):
    def write(self, val):
        print('dummy write %s' % val)


ser = DummySerial()

tk = tkinter.Tk()

has_prev_key_release = None

left_code = 8124162
right_code = 8189699
space_code = 3211296


class MainLoop(object):
    def __init__(self):
        frame = tkinter.Frame(tk, width=100, height=100)
        keys = ['Left', 'Right', 'space']
        for k in keys:
            frame.bind('<KeyRelease-%s>' % k, self.on_key_release_repeat)
            frame.bind('<KeyPress-%s>' % k, self.on_key_press_repeat)

        frame.pack()
        frame.focus_set()
        self.setup_cam()
        self.frame_index = 0
        self.is_left_down = False
        self.is_right_down = False
        self.is_recording = False
        self.episode_index = 0
        if not os.path.exists('sessions'):
            os.mkdir('sessions')
        print('init\'d!')

        tk.after(33, self.on_frame)
        tk.mainloop()

    def setup_cam(self, src=0):
        self.camera_stream = cv2.VideoCapture(src)
        if not self.camera_stream.isOpened():
            src = 1 - src
            self.camera_stream = cv2.VideoCapture(src)
            if not self.camera_stream.isOpened():
                sys.exit("Error: Camera didn't open for capture.")

        # Setup frame dims.
        self.camera_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.camera_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        self.camera_stream.read()

    def on_frame(self):
        self.frame_index += 1
        if self.is_recording:
            fname = 'sessions/%d/test_%09d_%d_%d.jpg' % (self.episode_index,
                                                         self.frame_index,
                                                         self.is_left_down,
                                                         self.is_right_down)
            # hmmm, whats grabbed?
            grabbed, frame = self.camera_stream.read()
            cv2.imwrite(fname, frame)

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

    def spacebar_toggle(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.episode_index += 1
            print('recording episode %d' % self.episode_index)
            self.frame_index = 0
            target_path = 'sessions/%d' % self.episode_index
            if not os.path.exists(target_path):
                os.mkdir(target_path)
        else:
            print("chillin'")

    def on_key_press(self, event):
        # print("on_key_press", repr(event.char))
        print("press", event.keycode)
        if event.keycode == left_code:
            self.flip_left()
        elif event.keycode == right_code:
            self.flip_right()
        elif event.keycode == space_code:
            self.spacebar_toggle()

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
