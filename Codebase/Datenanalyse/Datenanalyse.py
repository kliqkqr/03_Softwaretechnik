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
        self.view = DatenanalyseCodeChartsGUI(self, self.frame, self.canvas, image, image_path)

    def startBVAnalysis(self):
        # TODO
        pass

    ##############################
    #  METHODS FOR THE ANALYTICS #
    ##############################

    # inspired by: https://stackoverflow.com/questions/42481203/heatmap-on-top-of-image
    def calculateImageHeatmap(self, image_name, image_size):
        # TODO implement: viewpoints = database.getImageViewPoints(image_name)
        # For now random points:
        viewpoints = [np.random.random((1, 2)) for i in range(10)]

        # Create a mesh grid, matching the image size
        # p = np.asarray(I).astype('float')
        w, h = image_size # I.size
        y, x = np.mgrid[0:h, 0:w]

        # Calculate Gauss activation for viewpoints on the image
        heatmap = None
        for point in viewpoints:
            point = point[0]
            x_abs = math.floor(point[0] * image_size[0])
            y_abs = math.floor(point[1] * image_size[1])

            if heatmap is None:
                heatmap = self.twoD_Gaussian(x, y, x_abs, y_abs, .025 * x.max(), .025 * y.max())
            else:
                heatmap = heatmap + self.twoD_Gaussian(x, y, x_abs, y_abs, .025 * x.max(), .025 * y.max())

        return [x, y, heatmap.reshape(x.shape[0], y.shape[1])]

    @staticmethod
    def twoD_Gaussian(x, y, xo, yo, sigma_x, sigma_y):
        # 2D Gaussian function
        a = (1./(2*sigma_x**2) + 1./(2*sigma_y**2))
        c = (1./(2*sigma_x**2) + 1./(2*sigma_y**2))
        g = np.exp( - (a*((x-xo)**2) + c*((y-yo)**2)))
        return g.ravel()
