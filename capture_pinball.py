import Tkinter as tkinter
import sys
import cv2
import os

import pinball

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
        self.setup_pinball()
        self.frame_index = 0
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

    def setup_pinball(self):
        self.pinball = pinball.DummyPinball()
        #self.pinball = pinball.Pinball()

    def on_frame(self):
        self.frame_index += 1
        if self.is_recording:
            fname = 'sessions/%d/test_%09d_%d_%d.jpg' % (self.episode_index,
                                                         self.frame_index,
                                                         self.pinball.is_left_down,
                                                         self.pinball.is_right_down)
            # hmmm, whats grabbed?
            grabbed, frame = self.camera_stream.read()
            cv2.imwrite(fname, frame)

        tk.after(10, self.on_frame)

    def on_key_release(self, event):
        global has_prev_key_release
        has_prev_key_release = None
        # print("on_key_release", repr(event.char))
        if event.keycode == left_code:
            self.pinball.release_left()
        elif event.keycode == right_code:
            self.pinball.release_right()

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
            self.pinball.flip_left()
        elif event.keycode == right_code:
            self.pinball.flip_right()
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
