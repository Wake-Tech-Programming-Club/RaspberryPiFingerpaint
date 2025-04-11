import threading
from PIL import Image
import tkinter as tk
import customtkinter as ctk
from config_check import (load_config, get_config)
import utils as u

# Config loading should be the first thing
if __name__ == "__main__":
    load_config()

# Only import other parts once the config is loaded
import painting
import gallery

def get_icon(path: str):
    return ctk.CTkImage(Image.open(f"./icons/{path}"), size=(40,40))

class MyApp(ctk.CTk):
    in_main_menu = True
    color = None
    brush_size = get_config().getint("brushes", "default_brush_size")
    font = "Arial Bold"
    ctk.set_default_color_theme("dark-blue")
    def __init__(self):
        # constructor
        super().__init__()

        # create window
        self.title("WTCC: Finger Painting")
        self.iconbitmap("icon.ico")
        width = get_config().getint("screen", "width")
        height = get_config().getint("screen", "height")
        
        (x, y) = u.calc_window_size(config=get_config(), cam_width=width, cam_height=height)
        self.geometry(f"{x}x{y}")
        self.grid_anchor("center")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Header
        self.label = ctk.CTkLabel(self, text="WTCC: Finger Painting", font=(self.font, 50))
        self.label.grid(row=0, column=1, pady=20)

        # The gallery display or finger painting
        self.image = ctk.CTkLabel(self, text="")
        self.image.grid(row=1, column=1, pady=10)
        
        # Creates the widgets and starts the slideshow
        self.start_gallery_mode()
        # self.toolbar_init() # Only used for testing styling changes

    def create_widgets(self):
        # Finger Painting Button
        self.button1 = ctk.CTkButton(self, text="Start Finger Painting", font=(self.font, 25), command=self.start_painting_mode)
        self.button1.grid(row=2, column=1, ipady=5, ipadx=20, pady=20)

    def toolbar_init(self):
        self.button1.destroy()
        
        self.column = 0

        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.grid(row=3, column=1, pady=20)
        self.toolbar.grid_anchor("center")
        
        self.column += 1

        def make_button(cmd, icon):
            btn = ctk.CTkButton(self.toolbar, text="", image=get_icon(icon), command=cmd, height=40, width=40)
            btn.grid(row=3, column=self.column, padx=10, pady=10)
            return btn
        
        def make_label(text, columnspan = 1):
            label = ctk.CTkLabel(self.toolbar, text=text, font=(self.font, 20))
            label.grid(row=2, column=self.column, columnspan=columnspan)
        

        # Back to main menu button
        self.back_label = make_label("Back")
        self.back = make_button(self.start_gallery_mode, "back.png")
        
        self.column += 1

        # Clear Drawing
        self.clear_label = make_label("Clear")
        self.clear = make_button(painting.new_drawing, "clear.png")

        self.column += 1

        # Eraser Mode
        self.eraser_label = make_label("Eraser")
        self.eraser = make_button(lambda: painting.set_color(self, painting.eraser_color()), "eraser.png")
        # Color Selector
        self.column += 1
        self.color_label = make_label("Brush Color")
        self.color = get_config().get("brushes", "default_color")
        self.set_color()

        # Brush Size
        self.column += 2
        self.brush_size_label = make_label("Brush Size", 2)
        self.brush_size = ctk.CTkSlider(self.toolbar, from_=1, to=get_config().getint("brushes", "max_brush_size"), command=self.set_brush_size, width=100)
        self.brush_size.grid(row=3, column=self.column)
        
        self.column += 1
        self.set_brush_size(get_config().getint("brushes", "default_brush_size"))

        # Camera Mode
        self.column += 1
        self.camera_mode_label = make_label("Overlay")
        self.camera_mode = make_button(self.set_camera_mode, "camera_mode.png")
        
        # Save Button
        self.column += 1

        self.save_label = make_label("Save")
        self.save_button = make_button(self.save_image, "save.png")

    def set_camera_mode(self):
        painting.swap_camera_mode()

    def save_image(self):
        threading.Thread(target=painting.save_image, args=()).start()

    def set_color(self):
        if hasattr(self, "color_panel"):
            self.color_panel.destroy()

        btn_width = 30
        padding = 2
        canvas_width = (btn_width + padding * 2) * len(u.colors)
        self.color_panel = tk.Canvas(self.toolbar, height=40, width=canvas_width, bg="gray13", highlightthickness=0)
        
        for i, color_name in enumerate(u.colors.keys()):
            outline = "white" if color_name == self.color else "gray13"
            start = i * (btn_width + padding)
            btn = self.color_panel.create_oval(start, padding, start + btn_width, btn_width + padding,
                fill=color_name,
                outline=outline,
                width=2
            )

            self.color_panel.tag_bind(btn, "<Button-1>", lambda e, c=color_name: painting.set_color(self, c))
        
        self.color_panel.grid(row=3, column=4)
    
    def set_brush_size(self, size):
        size = int(float(size))
        self.brush_size = size
        if hasattr(self, "brush_size_indicator"):
            self.brush_size_indicator.destroy()

        self.brush_size_indicator = tk.Canvas(self.toolbar, height=40, width=40, bg="gray13", highlightthickness=0)
        offset = 20 - size // 2
        self.brush_size_indicator.create_oval(offset, offset, self.brush_size + offset, self.brush_size + offset, fill="white")
        self.brush_size_indicator.grid(row=3, column=7)
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
        loading_image = ctk.CTkImage(Image.open("splash.jpg"), size=(480, 270))
        self.image.configure(image=loading_image)
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