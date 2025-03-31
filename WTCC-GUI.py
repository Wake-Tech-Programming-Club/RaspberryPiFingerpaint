import tkinter as tk
from tkinter import ttk, PhotoImage  # themed tkinter

class MyApp(tk.Tk):
    def __init__(self):
        # constructor
        super().__init__()

        # create window
        self.title("WTCC: Finger Painting")
        self.geometry("400x300")
        # self.configure(bg='navyblue')
        self.create_widgets()
        self.image = None

    def create_widgets(self):
        # label
        self.label = ttk.Label(self, text="Choose an option below:")
        # font=("Times New Roman, 25))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        # button 1
        self.button1 = ttk.Button(self, text="Finger Painting", command=self.on_button_click)
        self.button1.grid(row=2, column=0, pady=5, sticky="ew")

        # button 2
        self.button2 = ttk.Button(self, text="Slideshow", command=self.on_button2_click)
        self.button2.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # expanding columns if window resized
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    # displays image when finger painting pressed
    def on_button_click(self):
        self.image = PhotoImage(file="school.png")  # Make sure the file is in the same directory or provide the correct path
        self.label.config(image=self.image, text="")  # Update the label to display the image
        self.label.grid(row=1, column=0, pady=10)

    def on_button2_click(self):
        self.label.config(text="Button Clicked", image="")  # Update text for button 2 click


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
