import tkinter
from tkinter import Button

import numpy as np
import matplotlib.pyplot as plt
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
    HIDE_HEATMAP = "Heatmap verstecken"

    def __init__(self, datenanalyse, frame, canvas, image, image_path):
        # Class variables
        self.datenanalyse = datenanalyse
        file_name = os.path.basename(image_path)
        self.image_name = os.path.splitext(file_name)[0]  # filename only without extension

        # Display the image
        # self.image_cache = ImageTk.PhotoImage(image)
        # canvas.create_image(self.DELTA_X, self.DELTA_Y, anchor=tkinter.NW, image=self.image_cache)

        # Display the analysis option(s)
        self.heatmap_button = Button(frame, text=self.HIDE_HEATMAP, command=self.hideHeatmap)
        self.heatmap_button.place(relx=0.5, rely=0.925, relheight=0.05, relwidth=0.3)

        # Display the image
        self.image = ImageExplorer.resizeImage(image, self.IMAGE_WIDTH, self.IMAGE_HEIGHT)
        fig, self.ax = plt.subplots(1, 1)
        self.ax.imshow(self.image)

        # Overlay the heatmap
        self.showHeatmap()

        # Plot canvas
        self.plt_canvas = FigureCanvasTkAgg(fig, master=canvas)
        self.plt_canvas.draw()

        # pack_toolbar=False will make it easier to use a layout manager later on.
        toolbar = NavigationToolbar2Tk(self.plt_canvas, canvas, pack_toolbar=False)
        toolbar.update()

        # Show toolbar and the image-canvas
        toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.plt_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    def destroy(self):
        pass

    def showHeatmap(self):
        [x, y, heatmap] = self.datenanalyse.calculateImageHeatmap(self.image_name, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
        mycmap = self.transparent_cmap(plt.cm.Reds)
        cb = self.ax.contourf(x, y, heatmap, 15, cmap=mycmap)
        plt.colorbar(cb)

        self.heatmap_button.config(text=self.HIDE_HEATMAP, command=self.hideHeatmap)

    def hideHeatmap(self):
        self.ax.clear()
        self.ax.imshow(self.image)
        self.plt_canvas.draw()

        self.heatmap_button.config(text=self.SELECT_HEATMAP, command=self.showHeatmap)

    @staticmethod
    def transparent_cmap(cmap, N=255):
        # Copy colormap and set alpha values
        mycmap = cmap
        mycmap._init()
        mycmap._lut[:, -1] = np.linspace(0, 0.8, N + 4)
        return mycmap
