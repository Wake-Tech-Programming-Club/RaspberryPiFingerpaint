import math
import tkinter as tk
from tkinter import ttk, StringVar  # themed tkinter
from config_check import (load_config, get_config)
import utils as u

# Config loading should be the first thing
if __name__ == "__main__":
    load_config()

# Only import other parts once the config is loaded
import painting
import gallery

class MyApp(tk.Tk):
    in_main_menu = True
    color = None
    brush_size = get_config().getint("brushes", "default_brush_size")
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
        self.image = tk.Label(self)
        self.image.grid(row=1, column=0, columnspan=3, pady=10)

        self.drawing = tk.Label(self)
        self.drawing.grid(row=2, column=1, columnspan=3, pady=10)
        
        self.start_gallery_mode()

    def create_widgets(self):
        # label
        self.label = ttk.Label(self, 
		text="WTCC: Finger Painting",
        	font=("Times New Roman", 25))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        # button 1
        self.button1 = ttk.Button(self, text="Finger Painting", command=self.start_painting_mode)
        self.button1.grid(row=2, column=0, pady=5, sticky="ew")

        # Drawing UI
        # button 2
        #self.button2 = ttk.Button(self, text="Slideshow", command=self.play_gallery_image)
        #self.button2.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # expanding columns if window resized
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def toolbar_init(self):
        self.button1.destroy()
        
        self.toolbar = ttk.Frame(self, padding=10, relief="solid", borderwidth=2, style='info.TFrame')
        self.toolbar.grid(row=2, column=0)
        self.toolbar.grid_columnconfigure(0, weight=1)
        
        # Back to main menu button
        self.back = ttk.Button(self.toolbar, text="Back", command=self.start_gallery_mode)
        self.back.grid(row=3, column=0)
        
        # Eraser Mode
        self.eraser = ttk.Button(self.toolbar, text="Eraser", command=lambda: painting.set_color(self, painting.eraser_color()))
        self.eraser.grid(row=3, column=1)

        # Color Selector
        self.set_color()

        # Brush Size
        self.brush_size = ttk.Scale(self.toolbar, from_=1, to=get_config().getint("brushes", "max_brush_size"), value=self.brush_size, command=self.set_brush_size)
        self.brush_size.grid(row=3, column=3)
        self.brush_size_label = ttk.Label(self.toolbar, text="Brush Size")
        self.brush_size_label.grid(row=2, column=3)
        self.set_brush_size(get_config().getint("brushes", "default_brush_size"))

    def set_color(self):
        if hasattr(self, "color_panel"):
            self.color_panel.destroy()

        self.color_panel = tk.Canvas(self.toolbar, height=40, width=175, bg="white")
        for i, color_name in enumerate(u.colors.keys()):
            outline = "black" if color_name == self.color else "white"
            btn = self.color_panel.create_oval(i * 20 + 20, 10, (i + 1) * 20 + 20, 30,
                fill=color_name,
                outline=outline
            )
            self.color_panel.tag_bind(btn, "<Button-1>", lambda e, c=color_name: painting.set_color(self, c))
        
        self.color_panel.grid(row=3, column=2)
    
    def set_brush_size(self, size):
        size = int(float(size))
        self.brush_size = size
        if hasattr(self, "brush_size_indicator"):
            self.brush_size_indicator.destroy()

        self.brush_size_indicator = tk.Canvas(self.toolbar, height=40, width=40)
        offset = 20 - size // 2
        self.brush_size_indicator.create_oval(offset, offset, self.brush_size + offset, self.brush_size + offset, fill="black")
        self.brush_size_indicator.grid(row=3, column=4)
        painting.set_brush_size(size)

    def start_gallery_mode(self):
        self.in_main_menu = True
        if hasattr(self, "toolbar"):
            self.toolbar.destroy()
        self.create_widgets()
        painting.stop()
        gallery.init()
        gallery.display_gallery(self)

    # displays image when finger painting pressed
    def start_painting_mode(self):
        self.in_main_menu = False
        self.toolbar_init()
        painting.init()
        painting.process_frame(self)
        # self.image = PhotoImage(file="school.png")  # Make sure the file is in the same directory or provide the correct path
        # self.label.config(image=self.image, text="")  # Update the label to display the image
        # self.label.grid(row=1, column=0, pady=10)

    def play_gallery_image(self):
        if self.in_main_menu:
            gallery.display_gallery(self)
        # self.label.config(text="Button Clicked", image="")  # Update text for button 2 click
    def process_frame(self):
        if not self.in_main_menu:
            painting.process_frame(self)


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