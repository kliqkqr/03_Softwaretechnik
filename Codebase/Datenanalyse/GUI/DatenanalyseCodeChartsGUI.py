import tkinter
from tkinter import Button
from PIL import Image, ImageTk

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import os

from CodeChart.ImageExplorer import ImageExplorer

# Inspired from: https://stackoverflow.com/questions/42481203/heatmap-on-top-of-image


class DatenanalyseCodeChartsGUI:

    # Constants
    DELTA_X = 50
    DELTA_Y = 50
    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 500

    SELECT_HEATMAP = "Heatmap darstellen"

    def __init__(self, datenanalyse, canvas, image, image_path):
        # Class variables
        self.datenanalyse = datenanalyse
        file_name = os.path.basename(image_path)
        self.image_name = os.path.splitext(file_name)[0]  # filename only without extension

        # Display the image
        # image = ImageExplorer.resizeImage(image, self.IMAGE_WIDTH, self.IMAGE_HEIGHT)
        # self.image_cache = ImageTk.PhotoImage(image)
        # canvas.create_image(self.DELTA_X, self.DELTA_Y, anchor=tkinter.NW, image=self.image_cache)

        # Display the analysis option(s)
        heatmap_button = Button(canvas, text=self.SELECT_HEATMAP, command=self.showHeatmap)
        heatmap_button.place(relx=0.5, rely=0.9, relheight=0.05, relwidth=0.3)

        # Display the image
        #fig = Figure(figsize=(8, 6), dpi=100)
        #ax = fig.add_subplot()
        fig, ax = plt.subplots(1, 1)
        ax.imshow(image)

        # TODO: unfinished processing
        heatmap = self.datenanalyse.calculateImageHeatmap(self.image_name, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
        x = np.arange(0, self.IMAGE_WIDTH)
        y = np.arange(0, self.IMAGE_HEIGHT).reshape(-1, 1)
        cs = plt.contourf(heatmap, levels=[1000, 10000, 100000],
                          colors=['#808080', '#A0A0A0', '#C0C0C0'], extend='both')
        cs.cmap.set_over('red')
        cs.cmap.set_under('blue')
        cs.changed()
        plt.colorbar(cs)

        plt_canvas = FigureCanvasTkAgg(fig, master=canvas)
        plt_canvas.draw()

        # pack_toolbar=False will make it easier to use a layout manager later on.
        toolbar = NavigationToolbar2Tk(plt_canvas, canvas, pack_toolbar=False)
        toolbar.update()

        # Show toolbar and the image-canvas
        toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        plt_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    def destroy(self):
        pass

    def showHeatmap(self):
        heatmap = self.datenanalyse.calculateImageHeatmap(self.image_name, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
