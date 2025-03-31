import cv2
import os
import numpy as np
from config_check import (load_config, get_config)
from math import ceil
import utils as u
import index as main_menu

WINDOW_NAME = "Slideshow"

if __name__ == '__main__':
    load_config()

#Kristen Here: Gallery uses saved images to make a small slideshow. Start slideshow with 'g' and end slideshow with 'g'.
#Currently slideshow does not display in main display but creates a new window.
def display_gallery():
    dst = "./output/"
    images = os.listdir(dst) #puts everything in output folder into an images variable
    width = get_config().getint("gallery", "image_width")
    height = get_config().getint("gallery", "image_height")
    result = np.zeros((height, width,3), np.uint8) #window size, change to fit
    
    i = 0 #loops images
    
    a = 1.0  #uses a and b as alpha values used later to create slide show effect
    b = 0.0

    img = cv2.imread(dst + images[i])
    img = cv2.resize(img, (width, height))

    #Slide show created using while loop. Breaks loop with 'g' key.
    while(True):
        if(ceil(a)==0):
            a = 1.0
            b = 0.0

            i += 1
            img = cv2.imread(dst + images[i])
            img = cv2.resize(img, (width, height))
            if i == len(images) - 1:
                i = 0
        a -= 0.01
        b += 0.01

        result = cv2.addWeighted(result, a, img, b, 0)
        cv2.imshow(WINDOW_NAME, result)

        # Exit the gallery
        key = cv2.waitKey(1) & 0xff
        if key == ord('g'):
            cv2.destroyWindow(WINDOW_NAME)
            main_menu.start()
            break