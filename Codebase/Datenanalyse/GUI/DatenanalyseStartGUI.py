import tkinter
from tkinter import Label, Button


class DatenanalyseStartGUI:

    HEADER_TEXT = 'Analyse für das jeweilige Tool auswählen!'
    SELECT_CODE_CHARTS = "Code Charts - Hotspots"
    SELECT_BUBBLE_VIEW = "Bubble View - Hotspots"

    def __init__(self, datenanalyse, canvas):
        # Header label
        header_label = Label(canvas, text=self.HEADER_TEXT, bg='grey', font=("Courier", 20))
        header_label.place(relx=0.075, rely=0.1, relheight=0.1, relwidth=0.85)

        # Analysis options buttons
        code_charts_button = Button(canvas, text=self.SELECT_CODE_CHARTS, command=datenanalyse.startCCAnalysis)
        code_charts_button.place(relx=0.1, rely=0.25, relheight=0.1, relwidth=0.3)

        bubble_view_button = Button(canvas, text=self.SELECT_BUBBLE_VIEW, command=datenanalyse.startBVAnalysis)
        bubble_view_button.place(relx=0.6, rely=0.25, relheight=0.1, relwidth=0.3)

        # ...
        # eyetracking_view_button = Button(canvas, text=self.SELECT_EYE_TRACKING)  # , command=self.show_image)
        # eyetracking_view_button.place(relx=0.35, rely=0.4, relheight=0.1, relwidth=0.3)

        self.elements = [header_label, code_charts_button, bubble_view_button]  # eyetracking_view_button

    def destroy(self):
        for element in self.elements:
            element.destroy()