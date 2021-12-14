from tkinter import *

# initiate window
win = Tk()
win.title('Project Toolbox')
win_width=400
win_height=400
win.geometry(f"{win_width}x{win_height}")

# creating frames
start_screen_frame = Frame(win, bg='grey')
bubbleView_screen_frame = Frame(win, bg='grey')
codeCharts_screen_frame = Frame(win, bg='grey')
datenanalyse_screen_frame = Frame(win, bg='grey')
settings_screen_frame = Frame(win, bg='grey')


# pack frames
def start_screen():
    hide_all_frames()
    start_screen_frame.pack(fill="both", expand=1)

    bubbleView_button = Button(start_screen_frame, text='Bubble View', command=bubbleView_screen)
    bubbleView_button.place(relx=0.15, rely=0.15, relheight=0.1, relwidth=0.7)

    codeCharts_button = Button(start_screen_frame, text='Code Charts', width=40, command=codeCharts_screen)
    codeCharts_button.place(relx=0.15, rely=0.35, relheight=0.1, relwidth=0.7)

    datenanalyse_button = Button(start_screen_frame, text='Datenanalyse', width=40, command=datenanalyse_screen)
    datenanalyse_button.place(relx=0.15, rely=0.55, relheight=0.1, relwidth=0.7)

    settings_button = Button(start_screen_frame, text='Einstellungen', width=40, command=settings_screen)
    settings_button.place(relx=0.15, rely=0.75, relheight=0.1, relwidth=0.7)


def bubbleView_screen():
    hide_all_frames()

    # pack the frame and place Button and Canvas
    bubbleView_screen_frame.pack(fill="both", expand=1)
    bubbleView_back_button = Button(bubbleView_screen_frame, text='Zurück', command=start_screen)
    bubbleView_back_button.place(relx=0.05, rely=0.925, relheight=0.05, relwidth=0.2)

    bubbleView_canvas = Canvas(bubbleView_screen_frame)
    bubbleView_canvas.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.85)

    # resize the window for the picture ?
    win_height=700
    win_width=900
    win.geometry(f"{win_width}x{win_height}")

    # just a gapfiller
    bubbleView_label = Label(bubbleView_screen_frame, text='*le Bubble View...')
    bubbleView_label.place(relx=0.15, rely=0.45, relheight=0.1, relwidth=0.7)


def codeCharts_screen():
    hide_all_frames()

    # pack the frame and place Button
    codeCharts_screen_frame.pack(fill="both", expand=1)
    codeCharts_back_button = Button(codeCharts_screen_frame, text='Zurück', command=start_screen)
    codeCharts_back_button.place(relx=0.05, rely=0.85, relheight=0.1, relwidth=0.2)

    # just a gapfiller
    codeCharts_label = Label(codeCharts_screen_frame, text='*le Code Charts...', bg='grey')
    codeCharts_label.place(relx=0.15, rely=0.45, relheight=0.1, relwidth=0.7)


def datenanalyse_screen():
    hide_all_frames()

    # pack the frame and place Button
    datenanalyse_screen_frame.pack(fill="both", expand=1)
    datenanalyse_back_button = Button(datenanalyse_screen_frame, text='Zurück', command=start_screen)
    datenanalyse_back_button.place(relx=0.05, rely=0.85, relheight=0.1, relwidth=0.2)

    # just a gapfiller
    datenanalyse_label = Label(datenanalyse_screen_frame, text='*le Datenanalyse...', bg='grey')
    datenanalyse_label.place(relx=0.15, rely=0.45, relheight=0.1, relwidth=0.7)

def settings_screen():
    hide_all_frames()

    # pack the frame and place Button
    settings_screen_frame.pack(fill="both", expand=1)
    settings_back_button = Button(settings_screen_frame, text='Zurück', command=start_screen)
    settings_back_button.place(relx=0.05, rely=0.85, relheight=0.1, relwidth=0.2)

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

    for widget in datenanalyse_screen_frame.winfo_children():
        widget.destroy()

    for widget in settings_screen_frame.winfo_children():
        widget.destroy()


    start_screen_frame.pack_forget()
    bubbleView_screen_frame.pack_forget()
    codeCharts_screen_frame.pack_forget()
    datenanalyse_screen_frame.pack_forget()
    settings_screen_frame.pack_forget()


# open start_screen_frame on startup
start_screen()

# start event loop
win.mainloop()