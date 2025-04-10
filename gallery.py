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

    # Filter the list to only include image files (e.g., jpg, png, etc.)
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    #images = [img for img in images if any(img.lower().endswith(ext) for ext in image_extensions)]
    
    # Create an empty list to hold the valid image filenames
    valid_images = []

    

    # Loops through all files in the images list
    for img in images:
        # Converts the file name to lowercase and check if it ends with any valid image extension
        is_valid_image = False
        for ext in image_extensions:
            if img.lower().endswith(ext):
                is_valid_image = True
                break  # If a match is found, no need to check further extensions
        
        # If it's a valid image, add it to the valid_images list
        if is_valid_image:
            valid_images.append(img)

    # Replace the original images list with the filtered valid images
    images = valid_images

    #adds the splash image to images list if no images are present
    if not valid_images:
        valid_images.append("splash.jpg")

   
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
        # maybe change this so it checks if files end in .jpg instead. Change to -2 if issue.
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
