import tkinter
import serial

ser = serial.Serial('/dev/cu.usbmodem1411', 115200)

def flipLeft():
    print('flip left')
    ser.write(b'2')

def releaseLeft():
    print('Release Left')
    ser.write(b'3')

def flipRight():
    print("Flip Right")
    ser.write(b'0')

def releaseRight():
    print("Flip Right")
    ser.write(b'1')

tk = tkinter.Tk()

has_prev_key_release = None

left_code = 8124162
right_code = 8189699

def on_key_release(event):
    global has_prev_key_release
    has_prev_key_release = None
    # print("on_key_release", repr(event.char))
    if event.keycode == left_code:
        releaseLeft()
    elif event.keycode == right_code:
        releaseRight()

def on_key_press(event):
    # print("on_key_press", repr(event.char))
    print("press", event.keycode)
    if event.keycode == left_code:
        flipLeft()
    elif event.keycode == right_code:
        flipRight()

def on_key_release_repeat(event):
    global has_prev_key_release
    has_prev_key_release = tk.after_idle(on_key_release, event)
    # print("on_key_release_repeat", repr(event.char))

def on_key_press_repeat(event):
    global has_prev_key_release
    if has_prev_key_release:
        tk.after_cancel(has_prev_key_release)
        has_prev_key_release = None
        # print("on_key_press_repeat", repr(event.char))
    else:
        on_key_press(event)

frame = tkinter.Frame(tk, width=100, height=100)
frame.bind("<KeyRelease-Left>", on_key_release_repeat)
frame.bind("<KeyPress-Left>", on_key_press_repeat)
frame.bind("<KeyRelease-Right>", on_key_release_repeat)
frame.bind("<KeyPress-Right>", on_key_press_repeat)
frame.pack()
frame.focus_set()

tk.mainloop()
