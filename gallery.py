import cv2
import os
import numpy as np
from config_check import (load_config, get_config)
from math import ceil
import utils as u
# import index as main_menu
import tkinter as tk
from PIL import Image, ImageTk

if __name__ == '__main__':
    load_config()

i = 0
a = 1.0
b = 0.0
dst = "./output/"
img = None
images = None
result = None

#Kristen Here: Gallery uses saved images to make a small slideshow. Starts automatically in the main menu
def init():
    global i, a, b, img, result, images
    
    #window size, change to fit
    width = get_config().getint("gallery", "image_width")
    height = get_config().getint("gallery", "image_height")
    result = np.full((height, width,3), 255, np.uint8)
    
    #puts everything in output folder into an images variable
    #here is where we fix omitting the .md
    images = os.listdir(dst)
    for i in images:
        if images == 'readme.md':
            continue    
    
    print(images)

    #loops images
    i = 0
    
    #uses a and b as alpha values used later to create slide show effect
    a = 1.0
    b = 0.0

    # read the first image
    img = cv2.imread(dst + images[i])
    img = cv2.resize(img, (width, height))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    i += 1

def display_gallery(tk: tk.Tk):
    global i, a, b, img, result

    width = get_config().getint("gallery", "image_width")
    height = get_config().getint("gallery", "image_height")

    # Next image is ready. reset alpha and read next image
    if(ceil(a)==0):
        a = 1.0
        b = 0.0

        img = cv2.imread(dst + images[i])
        img = cv2.resize(img, (width, height))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        i += 1

        # We've gone through all the images!
        if i == len(images) - 1:
            i = 0
    
    # Fade a bit
    a -= 0.01
    b += 0.01

    # Convert to tk and display result
    result = cv2.addWeighted(result, a, img, b, 0)
    display_image = Image.fromarray(result)
    display_image = ImageTk.PhotoImage(display_image)

    tk.image.imgtk = display_image
    tk.image.config(image=display_image)
    tk.after(10, tk.play_gallery_image)
