from CodeChart.ImageExplorer import ImageExplorer
from Datenanalyse.GUI.DatenanalyseCodeChartsGUI import DatenanalyseCodeChartsGUI
from Datenanalyse.GUI.DatenanalyseStartGUI import DatenanalyseStartGUI
from Tool import Tool

import tkinter

import numpy as np
import math


class Datenanalyse(Tool):

    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600

    def __init__(self, win, frame):
        self.canvas = None

        # Execute super class constructor
        super().__init__(win, frame)

        # Set current view
        self.view = DatenanalyseStartGUI(self, self.canvas)

        # Update loop, blocks the program
        self.win.mainloop()

    def drawView(self):
        self.canvas = tkinter.Canvas(self.frame, highlightthickness=0, bd=0, bg='gray',
                                     width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.canvas.pack()

        # redraw loop
        self.canvas.after(ms=500, func=self.redraw)

    def redraw(self):
        self.canvas.after(ms=500, func=self.redraw)

    # Callback method for the GUI's to change the current view
    def startCCAnalysis(self):
        # Clear the view
        self.view.destroy()
        self.canvas.delete("all")  # Clear the canvas

        # Let's select the image, which should be reviewed, first
        # Hide the main window and reshow at the end
        self.win.withdraw()
        image_loader = ImageExplorer(self)
        [image, image_path] = image_loader.display()
        self.win.deiconify()

        # Set the code charts analysis view
        self.view = DatenanalyseCodeChartsGUI(self, self.canvas, image, image_path)

    def startBVAnalysis(self):
        # TODO
        pass

    ##############################
    #  METHODS FOR THE ANALYTICS #
    ##############################

    def calculateImageHeatmap(self, image_name, image_size):
        # TODO implement: viewpoints = database.getImageViewPoints(image_name)
        # For now random points:
        viewpoints = [np.random.random((1, 2)) for i in range(5)]

        # Create an empty map, matching the image size
        heat_map = np.zeros((image_size[1], image_size[0]))
        for point in viewpoints:
            point = point[0]
            x = math.floor(point[0] * image_size[0])
            y = math.floor(point[1] * image_size[1])
            heat_map[y][x] = 0.5

        return heat_map
