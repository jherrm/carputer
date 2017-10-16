
import tkinter
from PIL import Image, ImageTk
import serial
import config
import cv2
import os
import imutils
import time

ser = serial.Serial('/dev/cu.usbmodem1411', 115200)

# class DummySerial(object):
#     def write(self, val):
#         print('dummy write %s' % val)
# ser = DummySerial()

tk = tkinter.Tk()

has_prev_key_release = None

left_code = 8124162
right_code = 8189699
space_code = 3211296


class MainLoop(object):
    def __init__(self):
        frame = tkinter.Frame(tk, width=100, height=100)
        self.lmain = tkinter.Label(tk)
        self.lmain.grid(row=0, column=0)
        self.lmain.pack()
        self.lmain.focus_set()
        self.commands = []

        keys = ['Left', 'Right', 'space']
        for k in keys:
            frame.bind('<KeyRelease-%s>' % k, self.on_key_release_repeat)
            frame.bind('<KeyPress-%s>' % k, self.on_key_press_repeat)

        frame.pack()
        frame.focus_set()
        self.setup_cam()
        self.frame_index = 0
        self.first_frame = None
        self.first_left = None
        self.first_right = None
        self.is_left_down = False
        self.is_right_down = False
        self.is_recording = False
        self.episode_index = 0
        if not os.path.exists('sessions'):
            os.mkdir('sessions')
        print('init\'d!')

        tk.after(16, self.on_frame)
        tk.mainloop()

    def setup_cam(self, src=1):
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

    def calculate_thresh(self, first_frame, current_frame):
        frame_delta = cv2.absdiff(first_frame, current_frame)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=2)
        result = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # print(result)
        cnts = result[1]
        # print(cnts)
        return cnts

    def on_frame(self):
        self.frame_index += 1

        now = time.time()

        new_list = []
        for func, scheduled_time in self.commands:
            if scheduled_time < now:
                func()
            else:
                new_list.append((func, scheduled_time))

        self.commands = new_list

        # hmmm, whats grabbed?
        grabbed, frame = self.camera_stream.read()

        width = 500
        # frame = cv2.flip(frame, 1)
	frame = imutils.resize(frame, width=width)
        # frame = frame[100:220, 100:400]
        frame = frame[120:220, :]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.Canny(gray, 200,300)

        frame = gray
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # 100 300
        left = gray[:, :width/2]
        right = gray[:, width/2:]

        cv2.imwrite('/tmp/frame.jpg', frame)
        cv2.imwrite('/tmp/left.jpg', left)
        cv2.imwrite('/tmp/right.jpg', right)

        # store the first_frame for image diff
        if self.first_frame is None:
            self.first_frame = gray
            self.first_left = left
            self.first_right = right
        else:
            THRESH = 500

            cnts = self.calculate_thresh(self.first_frame, frame)
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < THRESH:
                    continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"

            left_cnts = self.calculate_thresh(self.first_left, left)
            for c in left_cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) > THRESH:
                    self.flip_left()
                    self.commands.append((self.release_left, time.time() + 0.05))
                else:
                    # self.release_left()
                    pass

            right_cnts = self.calculate_thresh(self.first_right, right)
            for c in right_cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) > THRESH:
                    self.flip_right()
                    self.commands.append((self.release_right, time.time() + 0.05))
                else:
                    # self.release_right()
                    pass


        # display image in GUI
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)

        if self.is_recording:
            fname = 'sessions/%d/test_%09d_%d_%d.jpg' % (self.episode_index,
                                                        self.frame_index,
                                                        self.is_left_down,
                                                        self.is_right_down)
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
