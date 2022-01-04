import tkinter
from threading import Timer
from tkinter import *
from tkinter import filedialog

from PIL import Image, ImageTk, ImageDraw

import random
import string
import numpy as np

from Tool import Tool
from Config.Wechselzeitdauer import Wechselzeitdauer
from Config.Stringordnung import Stringordnung
from Config.Rastergroesse import Rastergroesse


class CodeChart(Tool):

    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 500
    STRING_LENGTH = 4

    def __init__(self, win, frame, config):
        self.image = None
        self.image_cache = None
        self.canvas = None
        self.timer = None

        # Load setting
        self.wechseldauer = config.getSetting(Wechselzeitdauer.NAME)
        self.ordnung = config.getSetting(Stringordnung.NAME)
        self.rastergroesse = config.getSetting(Rastergroesse.NAME)

        # Execute super class constructor
        super().__init__(win, frame)

    def drawView(self):
        # Standard view
        self.draw_standard_view()

        # Redraw loop
        self.canvas.after(1000, self.redraw())

        # Update loop, blocks the program
        self.win.mainloop()

    def draw_standard_view(self):
        # 1. Create a canvas
        self.canvas = tkinter.Canvas(self.frame, highlightthickness=0, bd=0, bg='gray',
                                     width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
        self.canvas.pack()

        # Standard white background if no codechart cycle has started
        self.image = Image.new(mode="RGB", size=(self.IMAGE_WIDTH, self.IMAGE_HEIGHT),
                               color=(255, 255, 255))

        # draw = ImageDraw.Draw(self.image)
        # draw.rectangle([(100, 100), (200, 200)], fill="green")
        # del draw
        self.image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(50, 50, anchor=NW, image=self.image)

        # 2. Create buttons: load & start
        self.left_button = Button(self.frame, text='Bild Laden', command=self.load_image)
        self.left_button.place(relx=0.25, rely=0.8, relheight=0.05, relwidth=0.2)

        self.right_button = Button(self.frame, text='Starten', command=self.show_image)
        self.right_button.place(relx=0.55, rely=0.8, relheight=0.05, relwidth=0.2)

    def redraw(self):
        self.canvas.after(ms=1000, func=self.redraw)

    def abort(self):
        if self.timer is not None:
            self.timer.cancel()

        #for widget in self.frame.winfo_children():
        #    widget.destroy()
        self.canvas.destroy()
        self.left_button.destroy()
        self.right_button.destroy()

        self.draw_standard_view()

    def load_image(self):
        # hide the root window
        self.win.withdraw()

        # open explorer dialog
        file_path = filedialog.askopenfilename()
        if file_path:
            # save Image in cache
            try:
                self.image_cache = Image.open(file_path)
            except IOError:
                # file is not an image
                pass

        # reshow the window
        self.win.deiconify()

    def show_image(self):
        if self.image_cache is None:
            return

        # ...
        self.left_button.config(text="Abbrechen", command=self.abort)
        self.right_button.place_forget()

        # Clear the canvas
        self.canvas.delete("all")

        # Set the cached image as the displayed image
        self.image = ImageTk.PhotoImage(self.image_cache)
        self.canvas.create_image(50, 50, anchor=NW, image=self.image)

        # Switch the screen after waiting period (specified in the settings)
        self.timer = Timer(self.wechseldauer.getValue(), self.show_matrix)
        self.timer.start()

    def show_matrix(self):
        # Clear the canvas
        self.canvas.delete("all")

        # Get matrix size
        dimension = self.rastergroesse.getValue()
        columns = dimension[0]
        rows = dimension[1]
        column_width = round(self.IMAGE_WIDTH / columns)
        row_height = round(self.IMAGE_HEIGHT / rows)

        # String cache
        strings = []

        # Decide between sorted and random strings
        # Draw the string matrix
        if self.ordnung.getValue():
            for y in range(rows):
                strings.append([])
                for x in range(columns):
                    # Create the rectangle
                    self.canvas.create_rectangle(x*column_width, y*row_height,
                                                 (x+1)*column_width-1, (y+1)*row_height-1,
                                                 fill="yellow")
                    # Create a string and save it to check the user input later
                    rand_str = self.get_random_string(self.STRING_LENGTH)
                    strings[y].append(rand_str)
                    self.canvas.create_text((x+0.5)*column_width, (y+0.5) * row_height, text=rand_str)

        # Switch the screen after waiting period (specified in the settings)
        self.timer = Timer(self.wechseldauer.getValue(), self.show_input)
        self.timer.start()

    def get_random_string(self, length):
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    def show_input(self):
        # Clear the canvas
        self.canvas.delete("all")

        # Show submit button
        self.right_button.config(text="Abgeben", command=self.submit)
        self.right_button.place(relx=0.55, rely=0.8, relheight=0.05, relwidth=0.2)

        # Add input field
        self.input = Text(self.frame)
        self.input.place(relx=0.4, rely=0.45, relheight=0.05, relwidth=0.2)

        # Add Label
        label = Label(self.frame, text="Bitte tragen Sie den betrachteten Text hier ein: ", bg="grey")
        label.place(relx=0.35, rely=0.38, relheight=0.05, relwidth=0.3)

    def submit(self):
        print(self.input.get("1.0", 'end-1c'))

        self.abort()
