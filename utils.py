from configparser import ConfigParser
import numpy as np
import cv2

def calc_window_size(config: ConfigParser, cam_width: int, cam_height: int):
    screen_width = config.getint("screen", "width")
    screen_height = config.getint("screen", "height")

    cam_aspect_ratio = cam_width / cam_height
    screen_aspect_ratio = screen_width / screen_height

    if cam_aspect_ratio > screen_aspect_ratio:
        window_width = screen_width
        window_height = int(window_width / cam_aspect_ratio)
    else:
        window_height = screen_height
        window_width = int(window_height * cam_aspect_ratio)

    return int(window_width * 0.9), int(window_height * 0.9)

def color_swap(num_codes): #(b, g, r)
    if num_codes == ord("1"):
        return (22, 22, 112)    # red
    elif num_codes == ord("2"):
        return (0, 129, 235)    # orange
    elif num_codes == ord("3"):
        return (76, 207, 255)   # yellow
    elif num_codes == ord("4"):
        return (37, 116, 97)    # green
    elif num_codes == ord("5"):
        return (255, 153, 0)    # blue
    elif num_codes == ord("6"):
        return (153, 0, 136)    # purple
    elif num_codes == ord("7"):
        return (182, 171, 243)  # pink
    else:
        return 0 