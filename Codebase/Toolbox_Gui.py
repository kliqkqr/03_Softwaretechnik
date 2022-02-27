from tkinter import *

# initiate window
from CodeChart.CodeChart import CodeChart
from Config.ConfigFile import ConfigFile

from BubbleView.BubbleView import BubbleViewTrialTool
from EyeTracking.EyeTracking import EyeTracking
from Datenanalyse.Datenanalyse import Datenanalyse

win = Tk()
win.title('Project Toolbox')
win_width=0
win_height=0

# creating frames
start_screen_frame = Frame(win, bg='grey')
bubbleView_screen_frame = Frame(win, bg='grey')
codeCharts_screen_frame = Frame(win, bg='grey')
eyeTracking_screen_frame = Frame(win, bg='grey')
datenanalyse_screen_frame = Frame(win, bg='grey')
settings_screen_frame = Frame(win, bg='grey')

# load the settings
cf = ConfigFile()
cf.loadSettings()
# save in case no config file has been created yet
cf.saveSettings()

# Selected tool
selected_tool = None


# pack frames
def start_screen():
    hide_all_frames()

    # resize the window for the current tool
    win_height=400 # 400x400 is base size
    win_width=400
    win.geometry(f"{win_width}x{win_height}")

    #pack the frame and place buttons
    start_screen_frame.pack(fill="both", expand=1)

    bubbleView_button = Button(start_screen_frame, text='Bubble View', command=bubbleView_screen)
    bubbleView_button.place(relx=0.15, rely=0.05, relheight=0.1, relwidth=0.7)

    codeCharts_button = Button(start_screen_frame, text='Code Charts', command=codeCharts_screen)
    codeCharts_button.place(relx=0.15, rely=0.25, relheight=0.1, relwidth=0.7)

    eyetracking_button = Button(start_screen_frame, text='Eyetracking', command=eyeTracking_screen)
    eyetracking_button.place(relx=0.15, rely=0.45, relheight=0.1, relwidth=0.7)

    datenanalyse_button = Button(start_screen_frame, text='Datenanalyse', command=datenanalyse_screen)
    datenanalyse_button.place(relx=0.15, rely=0.65, relheight=0.1, relwidth=0.7)

    settings_button = Button(start_screen_frame, text='Einstellungen', command=settings_screen)
    settings_button.place(relx=0.15, rely=0.85, relheight=0.1, relwidth=0.7)


def bubbleView_screen():
    hide_all_frames()

    # resize the window for the current tool
    win_height=700 # numbers just for testing purpose
    win_width=900
    win.geometry(f"{win_width}x{win_height}")

    # pack the frame and place Button and Canvas
    bubbleView_screen_frame.pack(fill="both", expand=1)
    # bubbleView_back_button = Button(bubbleView_screen_frame, text='Zurück', command=start_screen)
    # bubbleView_back_button.place(x = 10, y = 10, width = 80, height = 30)

    bubbleView = BubbleViewTrialTool(win, bubbleView_screen_frame, cf, on_back_callback = start_screen)

    # bubbleView_canvas = Canvas(bubbleView_screen_frame)
    # bubbleView_canvas.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.85)


def codeCharts_screen():
    hide_all_frames()

    # resize the window for the current tool
    win_height=700 # numbers just for testing purpose
    win_width=900
    win.geometry(f"{win_width}x{win_height}")

    # place Button and pack the frame
    codeCharts_screen_frame.pack(fill="both", expand=1)
    codeCharts_back_button = Button(codeCharts_screen_frame, text='Zurück', command=start_screen)
    codeCharts_back_button.place(relx=0.05, rely=0.925, relheight=0.05, relwidth=0.2)

    # CodeChart functionality
    codecharts = CodeChart(win, codeCharts_screen_frame, cf)

def eyeTracking_screen():
    hide_all_frames()

    # resize the window for the current tool
    win_height=700 # numbers just for testing purpose
    win_width=900
    win.geometry(f"{win_width}x{win_height}")

    # place Button and pack the frame
    eyeTracking_screen_frame.pack(fill="both", expand=1)
    #eyeTracking_back_button = Button(codeCharts_screen_frame, text='Zurück', command=start_screen)
    #eyeTracking_back_button.place(relx=0.05, rely=0.925, relheight=0.05, relwidth=0.2)

    # EyeTracking functionality
    eyetracking = EyeTracking(win, eyeTracking_screen_frame, start_screen)


def datenanalyse_screen():
    hide_all_frames()

    # resize the window for the current tool
    win_height=700 # numbers just for testing purpose
    win_width=900
    win.geometry(f"{win_width}x{win_height}")

    # pack the frame and place Button
    datenanalyse_screen_frame.pack(fill="both", expand=1)
    datenanalyse_back_button = Button(datenanalyse_screen_frame, text='Zurück', command=start_screen)
    datenanalyse_back_button.place(relx=0.05, rely=0.925, relheight=0.05, relwidth=0.2)

    # Start analysis tool
    analyse = Datenanalyse(win, datenanalyse_screen_frame)

def settings_screen():
    hide_all_frames()

    # resize the window for the current tool
    win_height=700 # numbers just for testing purpose
    win_width=900
    win.geometry(f"{win_width}x{win_height}")

    # pack the frame and place Button
    settings_screen_frame.pack(fill="both", expand=1)
    settings_back_button = Button(settings_screen_frame, text='Zurück', command=start_screen)
    settings_back_button.place(relx=0.05, rely=0.925, relheight=0.05, relwidth=0.2)

    # just a gapfiller
    settings_label = Label(settings_screen_frame, text='*le Einstellungen...', bg='grey')
    settings_label.place(relx=0.15, rely=0.45, relheight=0.1, relwidth=0.7)


# hide all frames
def hide_all_frames():
    # loop through each children in each frame and delete them
    for widget in start_screen_frame.winfo_children():
        widget.destroy()

    for widget in bubbleView_screen_frame.winfo_children():
        widget.destroy()

    for widget in codeCharts_screen_frame.winfo_children():
        widget.destroy()

    for widget in eyeTracking_screen_frame.winfo_children():
        widget.destroy()

    for widget in datenanalyse_screen_frame.winfo_children():
        widget.destroy()

    for widget in settings_screen_frame.winfo_children():
        widget.destroy()


    start_screen_frame.pack_forget()
    bubbleView_screen_frame.pack_forget()
    codeCharts_screen_frame.pack_forget()
    eyeTracking_screen_frame.pack_forget()
    datenanalyse_screen_frame.pack_forget()
    settings_screen_frame.pack_forget()


# open start_screen_frame on startup
start_screen()

# start event loop
win.mainloop()
