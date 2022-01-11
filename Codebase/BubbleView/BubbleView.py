import tkinter as tk
import os
import math

from timeit  import default_timer as timer
from PIL     import Image, ImageTk, ImageDraw
from tkinter import filedialog as fd, messagebox


from Rust import Rust

from ImageFilter import ImageFilter
from Tool        import Tool


class BubbleView(Tool):
    def __init__(self, win, frame, config):
        win.state('zoomed')

        # Config
        self.bubble_width  = 200
        self.bubble_height = 200
        self.bubble_shape  = 'ellipse'
        self.motion_min_distance = 10

        self.source_image = None
        self.target_image = None
        self.photo_image  = None
        self.canvas       = None

        self.radius_var     = tk.StringVar()
        self.iterations_var = tk.StringVar()
        self.diameter_var   = tk.StringVar()

        self.start_timer = None
        self.clicks      = None
        self.motions     = None

        super().__init__(win, frame)

    def drawView(self):
        load_button = tk.Button(self.frame, text = 'Bild Laden', command = self.load_button_click)
        load_button.place(x = 100, y = 10, width = 80, height = 30)

        reset_button = tk.Button(self.frame, text = 'Reset', command = self.reset_button_click)
        reset_button.place(x = 190, y = 10, width = 80, height = 30)

        gaussian_button = tk.Button(self.frame, text = 'Gaussian Blur', command = self.gaussian_button_click)
        gaussian_button.place(x = 280, y = 10, width = 80, height = 30)

        radius_entry = tk.Entry(self.frame, textvariable = self.radius_var)
        radius_entry.place(x = 370, y = 10, width = 80, height = 30)

        iterations_entry = tk.Entry(self.frame, textvariable = self.iterations_var)
        iterations_entry.place(x = 460, y = 10, width = 80, height = 30)

        blur_button = tk.Button(self.frame, text = 'Box Blur', command = self.blur_button_click)
        blur_button.place(x = 550, y = 10, width = 80, height = 30)

        diameter_entry = tk.Entry(self.frame, textvariable = self.diameter_var)
        diameter_entry.place(x = 640, y = 10, width = 80, height = 30)

        pixelate_button = tk.Button(self.frame, text = 'Pixelate', command = self.pixelate_button_click)
        pixelate_button.place(x = 730, y = 10, width = 80, height = 30)

        start_button = tk.Button(self.frame, text = 'Start', command = self.start_button_click)
        start_button.place(x = 820, y = 10, width = 80, height = 30)

        end_button = tk.Button(self.frame, text = 'Fertig', command = self.end_button_click)
        end_button.place(x = 910, y = 10, width = 80, height = 30)

    def load_button_click(self):
        file = fd.askopenfilename()
        if file:
            try:
                # TODO: PIL.Image.tobytes() funktioniert nicht richtig bei PNG's (wird aber von ImageFilter benötigt)
                image = Image.open(file)
                image.save('bubble_view_temp.bmp')
                self.source_image = Image.open('bubble_view_temp.bmp')
                self.source_image.load()

                if os.path.exists('bubble_view_temp.bmp'):
                    os.remove('bubble_view_temp.bmp')

                self.target_image = self.source_image.copy()
                self.display_image(self.target_image)

            except IOError:
                messagebox.showerror('Dateifehler', f'Keine Bilddatei: {file}')

    def reset_button_click(self):
        if self.source_image is not None:
            self.target_image = self.source_image.copy()
            self.display_image(self.target_image)

    def gaussian_button_click(self):
        try:
            if self.target_image is not None:
                radius = int(self.radius_var.get())

                if radius < 0:
                    raise ValueError

                image = ImageFilter.blur_gaussian(self.target_image, radius)

                if image is None:
                    raise RuntimeError

                self.target_image = image
                self.display_image(self.target_image)

        except ValueError:
            messagebox.showerror('Inputfehler',
                                 f'Keine natürlichen Zahlen: {self.radius_var.get()}, {self.iterations_var.get()}')

        except RuntimeError:
            messagebox.showerror('Filterfehler',
                                 f'Konnte Box-Blur-Filter nicht anwenden')

    def blur_button_click(self):
        try:
            radius     = int(self.radius_var.get())
            iterations = int(self.iterations_var.get())

            if radius < 0 or iterations < 0:
                raise ValueError

            image = ImageFilter.blur_box(self.target_image, radius, iterations)

            if self.target_image is None:
                raise RuntimeError

            self.target_image = image
            self.display_image(self.target_image)

        except ValueError:
            messagebox.showerror('Inputfehler',
                                 f'Keine natürlichen Zahlen: {self.radius_var.get()}, {self.iterations_var.get()}')
            
        except RuntimeError:
            messagebox.showerror('Filterfehler',
                                 f'Konnte Box-Blur-Filter nicht anwenden')

    def pixelate_button_click(self):
        try:
            diameter = int(self.diameter_var.get())

            if diameter < 0:
                raise ValueError

            image = ImageFilter.pixelate_square(self.target_image, diameter)

            if self.target_image is None:
                raise RuntimeError

            self.target_image = image
            self.display_image(self.target_image)

        except ValueError:
            messagebox.showerror('Inputfehler',
                                 f'Keine natürliche Zahl: {self.diameter_var.get()}')

        except RuntimeError:
            messagebox.showerror('Filterfehler',
                                 f'Konnte Pixelatefilter nicht anwenden')

    def start_button_click(self):
        self.start_timer = timer()
        self.clicks      = []
        self.motions     = []

    def end_button_click(self):
        analyse = self.render_analyse(self.source_image.copy())

        self.start_timer = None
        self.clicks      = None
        self.motions     = None

        if analyse is not None:
            self.display_image(analyse)

    def display_image(self, image):
        self.photo_image = ImageTk.PhotoImage(image)

        if self.canvas:
            self.canvas.destroy()

        self.canvas = tk.Canvas(self.frame, bd = 0, highlightthickness = 0)
        self.canvas.place(x = 10, y = 50, width = self.photo_image.width(), height = self.photo_image.height())
        self.canvas.create_image(0, 0, anchor = tk.NW, image = self.photo_image)
        self.canvas.bind('<Button-1>',  self.canvas_click)
        self.canvas.bind('<Motion>',    self.canvas_motion)

    def canvas_click(self, event):
        if self.start_timer and self.clicks is not None:
            x = event.x
            y = event.y
            t = timer() - self.start_timer

            self.clicks.append(((x, y), t))
            self.display_bubble(x, y)

    def canvas_motion(self, event):
        if self.start_timer and self.motions is not None:
            x = event.x
            y = event.y
            t = timer() - self.start_timer

            if len(self.motions) == 0:
                self.motions.append(((x, y), t))
                return

            (last_x, last_y), _ = self.motions[-1]
            dif_x = x - last_x
            dif_y = y - last_y

            if math.sqrt(dif_x ** 2 + dif_y ** 2) < self.motion_min_distance:
                return

            self.motions.append(((x, y), t))

    def bubble_rectangle(self, left, top, width, height):
        image = Rust.bubble_rectangle(self.target_image, self.source_image, left, top, width, height)
        self.display_image(image)

    def bubble_ellipse(self, left, top, width, height):
        image = Rust.bubble_ellipse(self.target_image, self.source_image, left, top, width, height)
        self.display_image(image)

    def display_bubble(self, x, y):
        left = x - (self.bubble_width  // 2)
        top  = y - (self.bubble_height // 2)

        if   self.bubble_shape == 'ellipse':
            self.bubble_ellipse(left, top, self.bubble_width, self.bubble_height)
        elif self.bubble_shape == 'rectangle':
            self.bubble_rectangle(left, top, self.bubble_width, self.bubble_height)

    def render_analyse(self, image):
        if self.clicks is not None and self.motions is not None:
            draw = ImageDraw.Draw(image, 'RGBA')
            motions = [xy for xy, t in self.motions]
            draw.line(motions, fill = 'green', width = 3)

            for (x, y), t in self.clicks:
                left = x - (self.bubble_width  // 2)
                top  = y - (self.bubble_height // 2)
                draw.ellipse([(left, top), (left + self.bubble_width, top + self.bubble_height)],
                             fill = (75, 75, 75, 75), outline = 'red', width = 2)

            return image
