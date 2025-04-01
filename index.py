import tkinter as tk
from tkinter import ttk, PhotoImage  # themed tkinter
from config_check import (load_config, get_config)
import utils as u

# Config loading should be the first thing
if __name__ == "__main__":
    load_config()

# Only import other parts once the config is loaded
import app as finger_painting_part
import gallery

class MyApp(tk.Tk):
    def __init__(self):
        # constructor
        super().__init__()

        # create window
        self.title("WTCC: Finger Painting")
        width = get_config().getint("screen", "width")
        height = get_config().getint("screen", "height")
        (x, y) = u.calc_window_size(config=get_config(), cam_width=width, cam_height=height)

        self.geometry(f"{x}x{y}")
        # self.configure(bg='navyblue')
        # self.image = None
        self.slideshow = tk.Label(self)
        self.slideshow.grid(row=1, column=0, columnspan=3, pady=10)
        self.create_widgets()
        
        gallery.init()
        gallery.display_gallery(self)

    def create_widgets(self):
        # label
        self.label = ttk.Label(self, 
		text="WTCC: Finger Painting",
        	font=("Times New Roman", 25))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        # button 1
        self.button1 = ttk.Button(self, text="Finger Painting", command=self.on_button_click)
        self.button1.grid(row=2, column=0, pady=5, sticky="ew")

        # button 2
        #self.button2 = ttk.Button(self, text="Slideshow", command=self.play_gallery_image)
        #self.button2.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # expanding columns if window resized
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    # displays image when finger painting pressed
    def on_button_click(self):
        self.destroy()
        finger_painting_part.detect_hand()
        # self.image = PhotoImage(file="school.png")  # Make sure the file is in the same directory or provide the correct path
        # self.label.config(image=self.image, text="")  # Update the label to display the image
        # self.label.grid(row=1, column=0, pady=10)

    def play_gallery_image(self):
        gallery.display_gallery(self)
        # self.label.config(text="Button Clicked", image="")  # Update text for button 2 click
    

def start():
    app = MyApp()
    def stop(event):
        app.destroy()

    # Exit the app easily
    app.bind_all("<Control-c>", stop)
    app.bind_all("<q>", stop)

    # Start 'er up!
    app.mainloop()

if __name__ == "__main__":
    start()