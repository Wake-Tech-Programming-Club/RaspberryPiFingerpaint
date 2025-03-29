from configparser import ConfigParser
import numpy as np

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

 #(b, g, r)
colors = {
    "red": (22, 22, 112),
    "orange": (0, 129, 235),
    "yellow": (76, 207, 255),
    "green": (37, 116, 97),
    "blue": (255, 153, 0),
    "purple": (153, 0, 136),
    "pink": (182, 171, 243)
}

def color_swap(num_codes):
    if num_codes == ord("1"):
        return colors["red"]
    elif num_codes == ord("2"):
        return colors["orange"]
    elif num_codes == ord("3"):
        return  colors["yellow"]
    elif num_codes == ord("4"):
        return colors["green"]
    elif num_codes == ord("5"):
        return colors["blue"]
    elif num_codes == ord("6"):
        return colors["purple"]
    elif num_codes == ord("7"):
        return colors["pink"]
    else:
        return colors["red"]

def switch_overlay_mode(drawing, new_mode):
    if new_mode == True:
        search_color = 0
        set_color = 255
    else:
        search_color = 255
        set_color = 0
    background = np.where(
        (drawing[:, :, 0] == search_color) & 
        (drawing[:, :, 1] == search_color) & 
        (drawing[:, :, 2] == search_color)
    )

    # set those pixels to the new color
    drawing[background] = [
        set_color,
        set_color,
        set_color
    ]
    return drawing