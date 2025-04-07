import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import time, threading
from config_check import get_config
import utils as u
import math 
import tkinter as tk
from PIL import Image, ImageTk

if __name__ == '__main__':
    raise RuntimeError("This file should not be run directly. Use index.py.")

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=get_config().getfloat("tracking", "min_detection"), min_tracking_confidence=get_config().getfloat("tracking", "min_tracking"))

# the countdown to show on screen when saving
save_countdown = -2

# a temporary image to display instead of the live feed (used when saving)
display = None

# Webcam
cap = None
side_by_side = True
brush_size = get_config().getint("brushes", "default_brush_size")
color = None
width = 0
height = 0

# keep track of where the finger was last seen
x_prev = 0
y_prev = 0

# if the finger movements should be recorded on the drawing canvas
draw_mode = False

window_width, window_height = (0, 0)

def eraser_color():
    if (side_by_side):
        return (255, 255, 255)
    else:
        return (0, 0, 0)

def new_drawing(self=None):
    global drawing
    bg_color = 255 if side_by_side else 0
    drawing = np.full((height,width,3), bg_color, np.uint8)

def create_flash():
    # Create a white image to act as a "camera flash"
    if side_by_side:
        flash = np.full((height, width, 3), 255, dtype=np.uint8)
    else:
        flash = np.full((window_height, window_width, 3), 255, dtype=np.uint8)
    return cv2.cvtColor(flash, cv2.COLOR_BGR2RGB)

def save_image():
    global save_countdown
    global display

    # 3 2 1 0 save
    for i in reversed(range(get_config().getint("saving", "count_from") + 1)):
        save_countdown = i
        print(save_countdown)
        time.sleep(1)

    save_countdown = -1

    # Capture the frame to save and show it instead of the camera feed
    _, display = cap.read()
    display = cv2.flip(display, 1)
    if not side_by_side:
        display = overlay_drawing(display, drawing)

    # Show a "flash" over the camera
    time.sleep(get_config().getfloat("saving", "flash_duration"))
    save_countdown = -2

    # Save the image
    path = get_config().get("saving", "path") + "/" + datetime.today().strftime("%B %d, %Y, %H %M %S") + ".jpg"
    print(f"Saving {path}")
    if side_by_side:
        cv2.imwrite(path, drawing)
    else:
        cv2.imwrite(path, display)

    # Resume displaying the camera feed
    time.sleep(get_config().getint("saving", "show_duration"))
    display = None

# Used to put the drawing on top of the camera feed. Math magic, don't ask me how it works lol
def overlay_drawing(frame: cv2.Mat, drawing: cv2.Mat):
    gray = cv2.cvtColor(drawing, cv2.COLOR_BGR2GRAY)
    _, invert = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY_INV)
    invert = cv2.cvtColor(invert, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, invert)
    frame = cv2.bitwise_or(frame, drawing)
    return cv2.resize(frame, (window_width, window_height))

def init():
    global cap, width, height, drawing, x_prev, y_prev, color
    global draw_mode, side_by_side, window_width, window_height
    stop()
    cap = cv2.VideoCapture(get_config().getint("config", "camera_id"))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    window_width, window_height = u.calc_window_size(get_config(), width, height, True)
    color = u.colors[get_config().get("brushes", "default_color")]
    new_drawing()
    x_prev = 0
    y_prev = 0
    draw_mode = False
    side_by_side = True

def next_frame(tk: tk.Tk, delay=1):
    tk.after(delay, tk.process_frame)

def display_image(tk: tk.Tk, img: cv2.Mat):
    display_result = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    display_result = ImageTk.PhotoImage(display_result)
    tk.image.imgtk = display_result
    tk.image.config(image=display_result)
    next_frame(tk)
    # cv2.imshow("Hand Tracking", img)


def process_frame(tk: tk.Tk):
    global draw_mode, x_prev, y_prev, drawing
    ret, frame = cap.read()
    
    # If saving, display the flash image
    if save_countdown == -1:
        fl = create_flash()
        if side_by_side:
            fl = np.hstack((fl, fl))
        display_image(tk, fl)
        # cv2.waitKey(1)
        return
    
    # If an image was recently saved, display the saved picture
    elif display is not None:
        display_image(tk, np.hstack((display, drawing)) if side_by_side else display)
        return

    # If the camera feed couldn't be read
    elif not ret:
        draw_mode = False
        return next_frame(tk, 100)

    # Detect hands
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    display_drawing = drawing.copy()
    # If it detects someone's hand
    if save_countdown == -2 and result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            if get_config().getboolean("config", "debug"):
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the position of the tip of the index finger
            x_index = int(hand_landmarks.landmark[8].x * frame.shape[1])
            y_index = int(hand_landmarks.landmark[8].y * frame.shape[0])
            z_index = int(hand_landmarks.landmark[8].z * get_config().getint("tracking", "z_scale"))

            thickness = -1 if draw_mode else 2
            cv2.circle(display_drawing, (x_index, y_index), brush_size // 2, color, thickness)
            if side_by_side:
                cv2.circle(frame, (x_index, y_index), brush_size // 2, color, thickness)

            # Get the position of the tip of the middle finger
            middle_x = int(hand_landmarks.landmark[12].x * frame.shape[1])
            middle_y = int(hand_landmarks.landmark[12].y * frame.shape[0])
            if get_config().getboolean("config", "debug"):
                line_color = (0, 0, 0) if not draw_mode else (255, 0, 255)
                cv2.line(frame, (x_index, y_index), (middle_x, middle_y), line_color)

            # Calculate the distance between the two
            finger_distance = int(math.sqrt((middle_x - x_index)**2 + (middle_y - y_index)**2))
            
            # Z Position based drawing. It works, but not well. Gotta find another way
            # if z_index < get_config().getint("tracking", "z_cutoff"):
            #     drawMode = False
            #     continue

            # Display hand position, for debugging.
            if (get_config().getboolean("config", "debug") == True):
                cv2.putText(frame, f"X: {x_index}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"Y: {y_index}", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"Z: {z_index}", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"D: {finger_distance}", (50, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
            
            # Fingers together = draw, otherwise don't. Also filter out false positives
            if finger_distance > get_config().getint("tracking", "finger_distance") or finger_distance < 3:
                draw_mode = False
                continue

            # Prevent pauses in drawing from creating unwanted brush strokes
            if draw_mode == False:
                x_prev = x_index
                y_prev = y_index

            # Draw on the canvas
            cv2.line(drawing, (x_prev, y_prev), (x_index, y_index), color, brush_size) #sets drawing color to white
            cv2.circle(frame, center=(x_index, y_index), radius=5, color=color, thickness=-10)
            # cv2.line(display_drawing, (x_prev, y_prev), (x_index, y_index), color, brush_size) #sets drawing color to white
            draw_mode = True

            # Update the hand position
            x_prev = x_index
            y_prev = y_index

    # No hand detected, drawing has stopped
    else:
        draw_mode = False

    # Display save countdown on screen
    if save_countdown > -1:
        cv2.putText(frame, f"Saving in: {save_countdown}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

    # Show the drawing next to the camera
    if (side_by_side == True):
        frame = np.hstack((frame, display_drawing))
    # Or overlay the drawing on the camera
    else:
        frame = overlay_drawing(frame, display_drawing)
    
    # Show the result
    display_image(tk, frame)

def stop():
    if cap is not None:
        cap.release()

def set_color(tk: tk.Tk, new_color):
    global color
    tk.color = new_color
    if isinstance(new_color, str):
        new_color = u.colors.get(new_color)
    color = new_color
    tk.set_color()

def set_brush_size(new_size):
    global brush_size
    brush_size = new_size

def swap_camera_mode():
    global side_by_side, drawing
    side_by_side = not side_by_side
    drawing = u.switch_overlay_mode(drawing, side_by_side)

