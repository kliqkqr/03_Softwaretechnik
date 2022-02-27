import tkinter
from tkinter import *
from tkinter import messagebox

from PIL import Image, ImageTk

import random
import string
import time

from CodeChart.ImageExplorer import ImageExplorer
from Config.Einstellungen.Wechselzeitdauer import Wechselzeitdauer
from Config.Einstellungen.Stringordnung import Stringordnung
from Config.Einstellungen.Rastergroesse import Rastergroesse
from Tool import Tool


class CodeChart(Tool):

    # States
    IDLE = 0
    SHOW_IMAGE = 1
    SHOW_MATRIX = 2
    SHOW_INPUT = 3

    THREAD_CYCLE_TIME = 300

    # Constants
    DELTA_X = 50
    DELTA_Y = 50
    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 500
    STRING_LENGTH = 4

    # Labels
    LOAD_IMG_STR = "Bild Auswählen"
    RUN_PROGRAM_STR = "Starten"
    ABORT_STR = "Abbrechen"
    ENTER_STR = "Abgeben"
    INFO_ENTER_STR = "Bitte tragen Sie den betrachteten Text hier ein: "

    def __init__(self, win, frame, config):
        self.image = None
        self.image_cache = None

        # Graphic elements
        self.canvas = None
        self.input = None
        self.left_button = None
        self.right_button = None
        self.label_enter = None

        # State machine and timing
        self.state = 0
        self.time_disp_change = 0

        # String matrix
        self.string_matrix = None  # will be created on demand

        # Load setting
        self.wechseldauer = config.getSetting(Wechselzeitdauer.NAME)
        self.ordnung = config.getSetting(Stringordnung.NAME)
        self.rastergroesse = config.getSetting(Rastergroesse.NAME)

        # Execute super class constructor
        super().__init__(win, frame)

    def drawView(self):
        # Standard view
        self.draw_standard_view()

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
        self.image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(self.DELTA_X, self.DELTA_Y, anchor=NW, image=self.image)

        # 2. Create buttons: load & start
        self.left_button = Button(self.frame, text=self.LOAD_IMG_STR, command=self.load_image)
        self.left_button.place(relx=0.25, rely=0.8, relheight=0.05, relwidth=0.2)

        self.right_button = Button(self.frame, text=self.RUN_PROGRAM_STR, command=self.show_image)
        self.right_button.place(relx=0.55, rely=0.8, relheight=0.05, relwidth=0.2)

        # redraw loop
        self.canvas.after(ms=self.THREAD_CYCLE_TIME, func=self.redraw)

    def redraw(self):
        # This method can be used to do updates at the frame before every
        # redraw is happening.
        if self.state and time.time() >= self.time_disp_change:
            if self.state == self.SHOW_IMAGE:
                self.state = self.SHOW_MATRIX
                self.show_matrix()

                # Switch the screen after waiting period (specified in the settings)
                self.time_disp_change = time.time() + self.wechseldauer.getValue()
            elif self.state == self.SHOW_MATRIX:
                self.state = self.SHOW_INPUT
                self.show_input()

        self.canvas.after(ms=self.THREAD_CYCLE_TIME, func=self.redraw)

    def abort(self):
        # Reset the state
        self.state = self.IDLE

        # Destroy all the graphic components
        #for widget in self.frame.winfo_children():
        #    widget.destroy()
        self.canvas.destroy()
        self.left_button.destroy()
        self.right_button.destroy()
        if self.input is not None:
            self.input.destroy()
        if self.label_enter is not None:
            self.label_enter.destroy()

        # Reload the landing view
        self.draw_standard_view()

    def load_image(self):
        # hide the root window
        self.win.withdraw()

        # Open up the image selection display
        image_loader = ImageExplorer(self)
        self.image_cache = image_loader.display()[0]

        # reshow the window
        self.win.deiconify()

    def show_image(self):
        if self.image_cache is None:
            return

        # ...
        self.left_button.config(text=self.ABORT_STR, command=self.abort)
        self.right_button.place_forget()

        # Clear the canvas
        self.canvas.delete("all")

        # Set the cached image as the displayed image
        self.image_cache = ImageExplorer.resizeImage(self.image_cache, self.IMAGE_WIDTH, self.IMAGE_HEIGHT)
        self.image = ImageTk.PhotoImage(self.image_cache)
        self.canvas.create_image(self.DELTA_X, self.DELTA_Y, anchor=NW, image=self.image)

        # Switch the screen after waiting period (specified in the settings)
        self.state = self.SHOW_IMAGE
        self.time_disp_change = time.time() + self.wechseldauer.getValue()

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
        self.string_matrix = []

        # Decide between sorted and random strings
        # Draw the string matrix
        if self.ordnung.getValue():
            for y in range(rows):
                self.string_matrix.append([])
                for x in range(columns):
                    # Create the rectangle
                    self.canvas.create_rectangle(self.DELTA_X + x*column_width, self.DELTA_Y + y*row_height,
                                                 self.DELTA_X + (x+1)*column_width-1, self.DELTA_Y + (y+1)*row_height-1,
                                                 fill="yellow")
                    # Create a string and save it to check the user input later
                    rand_str = self.get_random_string(self.STRING_LENGTH)
                    self.string_matrix[y].append(rand_str)
                    self.canvas.create_text(self.DELTA_X + (x+0.5)*column_width, self.DELTA_Y + (y+0.5) * row_height,
                                            text=rand_str)

    def get_random_string(self, length):
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    def show_input(self):
        # Clear the canvas
        self.canvas.delete("all")

        # Show submit button
        self.right_button.config(text=self.ENTER_STR, command=self.submit)
        self.right_button.place(relx=0.55, rely=0.8, relheight=0.05, relwidth=0.2)

        # Add input field
        self.input = Text(self.frame)
        self.input.place(relx=0.4, rely=0.45, relheight=0.05, relwidth=0.2)

        # Add Label
        self.label_enter = Label(self.frame, text=self.INFO_ENTER_STR, bg="grey")
        self.label_enter.place(relx=0.35, rely=0.38, relheight=0.05, relwidth=0.3)

    def submit(self):
        input_str = self.input.get("1.0", 'end-1c');
        index = self.findIndex(input_str)

        if index == -1:
            # Wrong input --> no element found
            messagebox.showerror(title="Wrong Input",
                                 message="Die eingegebenen Zeichen konnten nicht zugeordnet werden!\n"
                                         "Bitte überprüfen Sie ihre Eingabe!")
        else:
            print(index)
            # TODO SAVE!
            self.abort()

    # HELPER FUNCTIONS
    def findIndex(self, element):
        for row, array in enumerate(self.string_matrix):
            try:
                col = array.index(element)
            except ValueError:
                continue
            return row, col
        return -1
