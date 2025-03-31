import cv2
import os
import numpy as np
from math import ceil
import utils as u

WINDOW_NAME = "Slideshow"

#Kristen Here: Gallery uses saved images to make a small slideshow. Start slideshow with 'g' and end slideshow with 'g'.
#Currently slideshow does not display in main display but creates a new window.
def display_gallery():
    dst = "./output/"
    images = os.listdir(dst) #puts everything in output folder into an images variable
    length = len(images)
    result = np.zeros((360,360,3), np.uint8) #window size, change to fit
    i=0 #loops images
    a = 1.0  #uses a and b as alpha values used later to create slide show effect
    b = 0.0
    img = cv2.imread(dst + images[i])
    img = cv2.resize(img, (360, 360))

    #Slide show created using while loop. Breaks loop with 'g' key.
    while(True):
        if(ceil(a)==0):
            a = 1.0
            b = 0.0

            img = cv2.imread(dst + images[i])
            img = cv2.resize(img, (360, 360))
            i += 1
            if i == len(images) - 1:
                i = 0
        a -= 0.01
        b += 0.01

        result = cv2.addWeighted(result, a, img, b, 0)
        cv2.imshow(WINDOW_NAME, result)
        key = cv2.waitKey(1) & 0xff
        if key == ord('g'):
            cv2.destroyWindow(WINDOW_NAME)
            u.loading_screen(True)
            break