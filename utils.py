from configparser import ConfigParser

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
