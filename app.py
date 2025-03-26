import cv2
import mediapipe as mp
import numpy as np
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from configparser import ConfigParser
from datetime import datetime
import time, threading
from config_check import config_check
import utils as u
import os


# Configuration
config = ConfigParser()

if not os.path.exists("./config.ini"):
    raise Exception("Config.ini does not exist. Try copying config-example.ini as config.ini")

def load_config():
        global config
        config = ConfigParser()
        config.read('config.ini')
        if not config_check(config):
            print("There were errors while reading the config file. Please make sure all properties are in both config.ini and config-example.ini.")
            os._exit(0)
        print("Loaded config")

load_config()

# Fancy text for the lols
print(open("./splash.txt").read())


# Hot reload configuration
class ConfigLoader(FileSystemEventHandler):
    def on_modified(self, event: FileSystemEvent) -> None:
        if (event.src_path == ".\config.ini"):
            load_config()

observer = Observer()
observer.schedule(ConfigLoader(), ".", recursive=False)
observer.start()

# Keyboard codes used for swapping colors
num_codes = []

for i in range(10):
    num_codes.append(ord(str(i)))

# Display splash image
splash = cv2.imread("splash.jpg")
cv2.imshow("Hand Tracking", splash)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=config.getfloat("tracking", "min_detection"), min_tracking_confidence=config.getfloat("tracking", "min_tracking"))

# Start webcam
cap = cv2.VideoCapture(config.getint("config", "camera_id"))

# the countdown to show on screen when saving
save_countdown = -2
# a temporary image to display instead of the live feed (used when saving)
display = None

def detect_hand():
    """
    Changes how the drawing is displayed
    True for displaying it next to the camera
    False for displaying it on top of the camera
    """
    side_by_side = False
    brush_size = config.getint("brushes", "default_brush_size")
    color = u.colors[config.get("brushes", "default_color")]

    # Create the drawing canvas the same size as our camera
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def eraser_color():
        if (side_by_side):
            return (255, 255, 255)
        else:
            return (0, 0, 0)

    def new_drawing():
        if side_by_side == True:
            bg_color = 255
        else:
            bg_color = 0
        return np.full((height,width,3), bg_color, np.uint8)
    
    drawing = new_drawing()

    # keep track of where the finger was last seen
    x_prev = 0
    y_prev = 0

    # if the finger movements should be recorded on the drawing canvas
    draw_mode = False

    window_width, window_height = u.calc_window_size(config, width, height)

    # Used to put the drawing on top of the camera feed. Math magic, don't ask me how it works lol
    def overlay_drawing(frame: cv2.Mat):
        gray = cv2.cvtColor(drawing, cv2.COLOR_BGR2GRAY)
        _, invert = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY_INV)
        invert = cv2.cvtColor(invert, cv2.COLOR_GRAY2BGR)
        frame = cv2.bitwise_and(frame, invert)
        frame = cv2.bitwise_or(frame, drawing)
        return cv2.resize(frame, (window_width, window_height))

    # Display an image on the current window
    def display_image(img: cv2.Mat):
        cv2.imshow("Hand Tracking", img)

    # Saves the image to a file after a countdown
    # To be run on a thread so we don't block anything
    def save_image():
        global save_countdown
        global display

        # 3 2 1 0 save
        for i in reversed(range(config.getint("saving", "count_from") + 1)):
            save_countdown = i
            print(save_countdown)
            time.sleep(1)

        save_countdown = -1

        # Capture the frame to save and show it instead of the camera feed
        _, display = cap.read()
        display = cv2.flip(display, 1)
        if not side_by_side:
            display = overlay_drawing(display)

        # Show a "flash" over the camera
        time.sleep(config.getfloat("saving", "flash_duration"))
        save_countdown = -2

        # Save the image
        path = config.get("saving", "path") + "/" + datetime.today().strftime("%B %d, %Y, %H %M %S") + ".jpg"
        print(f"Saving {path}")
        if side_by_side:
            cv2.imwrite(path, drawing)
        else:
            cv2.imwrite(path, display)

        # Resume displaying the camera feed
        time.sleep(config.getint("saving", "show_duration"))
        display = None
    
    def create_flash():
        # Create a white image to act as a "camera flash"
        if side_by_side:
            flash = np.full((height, width, 3), 255, dtype=np.uint8)
        else:
            flash = np.full((window_height, window_width, 3), 255, dtype=np.uint8)
        return cv2.cvtColor(flash, cv2.COLOR_BGR2RGB)

    # Update as often as possible
    while True:
        ret, frame = cap.read()
        # If saving, display the flash image
        if save_countdown == -1:
            fl = create_flash()
            if side_by_side:
                fl = np.hstack((fl, fl))
            display_image(fl)
            cv2.waitKey(1)
            continue
        # If an image was recently saved, display the saved picture
        elif display is not None:
            if side_by_side:
                d = np.hstack((display, drawing))
            else:
                d = display
            display_image(d)
            cv2.waitKey(1)
            continue

        # If the camera feed couldn't be read
        elif not ret:
            draw_mode = False
            continue
            
        # Detect hands
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        # If it detects someone's hand
        if save_countdown == -2 and result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                x_index = int(hand_landmarks.landmark[8].x * frame.shape[1])
                y_index = int(hand_landmarks.landmark[8].y * frame.shape[0])
                z_index = int(hand_landmarks.landmark[8].z * config.getint("tracking", "z_scale"))

                # Z Position based drawing. It works, but not well. Gotta find another way
                # if z_index < config.getint("tracking", "z_cutoff"):
                #     drawMode = False
                #     continue

                # Display hand position, for debugging.
                if (config.getboolean("config", "debug") == True):
                    cv2.putText(frame, f"X: {x_index}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, f"Y: {y_index}", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, f"Z: {z_index}", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                
                # Prevent pauses in drawing from creating unwanted brush strokes
                if draw_mode == False:
                    x_prev = x_index
                    y_prev = y_index

                # Draw on the canvas
                cv2.line(drawing, (x_prev, y_prev), (x_index, y_index), color, brush_size) #sets drawing color to white
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
            frame = np.hstack((frame, drawing))
        # Or overlay the drawing on the camera
        else:
            frame = overlay_drawing(frame)
        
        # Show the result
        display_image(frame)

        ###################
        # BACKUP KEYBINDS #
        ###################

        # Q: Quit
        # C: Clear
        # B: Toggle Background (toggles overlaying on the camera vs the canvas)
        # S: Save
        # [: Brush Smaller
        # ]: Brush Larger
        # 1-9: Color Select
        # E: Eraser mode

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        elif key == ord("c"):
            print("Clearing...")
            drawing = new_drawing()
        
        elif key == ord("s"):
            threading.Thread(target=save_image, args=()).start()

        elif key == ord("b"):
            print("Background Toggled")
            side_by_side = not side_by_side
            drawing = u.switch_overlay_mode(drawing, side_by_side)

        elif key == ord("[") and brush_size > 1:
            print("Brush Smaller")
            brush_size = brush_size - 1
        elif key == ord("]") and brush_size <= config.getint("brushes", "max_brush_size"):
            print("Brush Larger")
            brush_size = brush_size + 1

        elif key in num_codes:
            print("Color Swap")
            # color = new_color
            color = u.color_swap(key)

        elif key == ord("e"):
            color = eraser_color()

    # If you hit quit, stop the program and destroy the windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':

    # Start hand tracking thread
    detect_hand()