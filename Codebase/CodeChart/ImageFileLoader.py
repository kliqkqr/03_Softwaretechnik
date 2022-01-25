from PIL import Image
from tkinter import filedialog


class ImageFileLoader:

    def __init__(self, code_charts):
        self.code_charts = code_charts

    def display(self):
        # open explorer dialog
        file_path = filedialog.askopenfilename()
        if file_path:
            # save Image in cache
            try:
                image = Image.open(file_path)
                self.code_charts.image_cache = image
            except IOError:
                # file is not an image
                pass
