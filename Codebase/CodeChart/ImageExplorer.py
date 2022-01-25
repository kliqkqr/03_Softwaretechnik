import os

from PIL import ImageTk
import PIL.Image
import tkinter as tk
from tkinter import Button, Toplevel, Canvas

import glob

from functools import partial



class ImageExplorer:

    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 600

    IMAGE_DISP_WIDTH = 190
    IMAGE_DISP_HEIGHT = 140
    BORDER_LENGTH = 5

    IMAGE_LIB_PATH = 'CodeChart/images/'

    def __init__(self, code_charts):
        # The outcome
        self.selected_image = None
        self.selected_image_path = None

        # Window display
        self.canvas = None
        self.win = None
        self.code_charts = code_charts

        # Lookup all provided images in the python package
        self.image_path_list = glob.glob(self.IMAGE_LIB_PATH + '*.jpg')
        self.image_list = []

    def display(self):
        # 1. build new window
        self.win = Toplevel()
        self.win.title('Image Explorer - Select')

        # 2. Create a canvas to draw the image preview
        self.canvas = Canvas(self.win, highlightthickness=0, bd=0, bg='gray',
                             width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT)

        # 3.
        self.image_list = []
        i_x = 0
        i_y = 0
        idx = 0
        x_max = self.WINDOW_WIDTH / (self.IMAGE_DISP_WIDTH + 2*self.BORDER_LENGTH)
        y_max = self.WINDOW_HEIGHT / (self.IMAGE_DISP_HEIGHT + 2*self.BORDER_LENGTH)
        x_diff = self.BORDER_LENGTH / self.WINDOW_WIDTH
        y_diff = self.BORDER_LENGTH / self.WINDOW_WIDTH
        for image in self.image_path_list:
            idx = idx + 1

            # Draw underlying rectangle
            corner_x = i_x * (self.IMAGE_DISP_WIDTH + 2*self.BORDER_LENGTH)
            corner_y = i_y * (self.IMAGE_DISP_HEIGHT + 2*self.BORDER_LENGTH)
            width_rect = self.IMAGE_DISP_WIDTH + 10
            height_rect = self.IMAGE_DISP_HEIGHT + 10
            self.canvas.create_rectangle(corner_x, corner_y,
                                         corner_x + width_rect,
                                         corner_y + height_rect,
                                         fill="green")

            # Load the image
            img = PIL.Image.open(image)
            resized_img = img.resize((self.IMAGE_DISP_WIDTH, self.IMAGE_DISP_HEIGHT))
            ph_img = ImageTk.PhotoImage(resized_img)
            self.image_list.append(ph_img)  # save images, otherwise they won't be displayed

            # Display the image button
            callback = partial(self.select_image, img, image)
            img_button = tk.Button(self.win, text=image, image=ph_img, command=callback)
            img_button.place(relx=x_diff + i_x/x_max, rely=y_diff+i_y/y_max,
                             relwidth=self.IMAGE_DISP_WIDTH/self.WINDOW_WIDTH,
                             relheight=self.IMAGE_DISP_HEIGHT/self.WINDOW_HEIGHT)

            # Increase indexes by one
            i_x = i_x + 1
            if i_x % x_max == 0:
                i_x = 0
                i_y = i_y + 1

        # Add button for closing
        button_back = Button(self.win, text="Zurückkehren", command=self.close_and_quit)
        button_back.place(relx=0.4, rely=0.89, relwidth=0.2, relheight=0.06)

        # Pack canvas and call redraw function while staying in the main loop()
        self.canvas.pack()
        self.canvas.after(ms=1000, func=self.redraw)

        self.win.mainloop()
        return [self.selected_image, self.selected_image_path]

    def redraw(self):
        self.canvas.after(ms=1000, func=self.redraw)

    def close_and_quit(self):
        self.win.quit()
        self.win.destroy()

    def select_image(self, image, img_path):
        # Set the selected image
        self.selected_image = image
        self.selected_image_path = img_path

        # Close the window and proceed in CodeCharts
        self.close_and_quit()

    @staticmethod
    def resizeImage(image, width, height):
        height_percent = (height / float(image.size[1]))
        width_size = int((float(image.size[0]) * float(height_percent)))
        image = image.resize((width, height), PIL.Image.NEAREST)
        return image
