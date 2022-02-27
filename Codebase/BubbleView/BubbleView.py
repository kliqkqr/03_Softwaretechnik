import tkinter     as tk
import tkinter.ttk as tkk
import os
import math


from timeit  import default_timer as timer
from PIL     import Image, ImageTk, ImageDraw
from tkinter import filedialog as fd, messagebox


from Rust import Rust

from ImageFilter import ImageFilter
from Tool import Tool


class BubbleViewStudy(Tool):
    def __init__(self, win, frame, config, trial):
        self.trial = trial

        self._index = 0

        # Config
        self.bubble_width  = 300
        self.bubble_height = 200
        self.bubble_shape  = 'ellipse'
        self.motion_min_distance = 10
        self.blur_radius = 50
        self.blur_iterations = 3
        self.pixelate_diameter = 100
        self.slider_resolution = 0.05
        self.analyse_render_motion_width = 3
        self.analyse_render_motion_color = 'green'
        self.analyse_render_click_outline_with  = 2
        self.analyse_render_click_outline_color = 'red'
        self.analyse_render_click_fill_color = (75, 75, 75, 75)

        self.photo_image          = None
        self.filter_image         = None
        self.display_image        = None
        self.display_image_resize = True

        self.menu_bar_width       = 0
        self.menu_bar_height      = 0
        self.default_margin_left  = 10
        self.default_margin_top   = 10
        self.default_margin_right = 0

        # Analyse
        self.start_timer                = None
        self.clicks                     = None
        self.motions                    = None
        self.display_image_resize_ratio = None
        self.show_analyse_widgets       = False
        self.end_time                   = None
        self.analyse_slider_resolution  = 0.05

        # Vars
        self.index_var = tk.StringVar()

        # Widgets
        self.canvas   = None
        self.menu_bar = None

        super().__init__(win, frame)

        # Events
        self.frame.bind('<Configure>', self.frame_configure)

    def case(self):
        return self.trial[self._index]

    def source_image(self):
        return self.case().get('source_image', None)

    def image_filters(self):
        return self.case().get('image_filters', None)

    def filter_source_image(self):
        source_image = self.source_image()
        if source_image is None:
            return None

        filter_image = source_image.copy()
        filter_image = self.apply_image_filters(filter_image)
        return filter_image

    def display_filter_image(self):
        self.filter_image = self.filter_source_image()
        if self.filter_image is None:
            message = 'Versuchsfall hat kein Bild'
            tk.messagebox.showinfo('Fehler', message)
            return

        self.display_image_set(self.filter_image)

    def init_case(self):
        self.index_var.set(f'{self._index + 1} / {len(self.trial)}')
        self.display_filter_image()

        self.start_timer = timer()
        self.clicks      = []
        self.motions     = []

        self.show_analyse_widgets = False
        self.draw_menu_bar()

    def drawView(self):
        self.draw_menu_bar()
        self.init_case()

    def draw_menu_bar(self):
        if self.menu_bar is not None:
            for widget in self.menu_bar:
                widget.destroy()

        default_width  = 80
        default_height = 30

        index_label = tk.Label(self.frame, textvariable = self.index_var)
        next_button = tk.Button(self.frame, text = 'Weiter', command = self.next_button_click)
        done_button = tk.Button(self.frame, text = 'Fertig', command = self.done_button_click)

        widgets = [
            (index_label, {'width': 40}),
            (next_button, {}),
            (done_button, {})
        ]

        if self.show_analyse_widgets:
            analyse_scale = tk.Scale(self.frame, from_ = 0, to = self.end_time, orient = tk.HORIZONTAL, command = self.analyse_scale_change,
                                     showvalue = True, resolution = self.analyse_slider_resolution, width = 10)

            widgets.extend([
                (analyse_scale, {'width': 170})
            ])

        self.menu_bar = []
        self.menu_bar_width  = 0
        self.menu_bar_height = 0

        for widget, kwargs in widgets:
            margin_left  = kwargs.get('margin_left',  self.default_margin_left)
            margin_top   = kwargs.get('margin_top',   self.default_margin_top)
            margin_right = kwargs.get('margin_right', self.default_margin_right)

            x = margin_left + self.menu_bar_width
            y = margin_top

            width  = kwargs.get('width',  default_width)
            height = kwargs.get('height', default_height)

            self.menu_bar_width  = x + width + margin_right
            self.menu_bar_height = max(self.menu_bar_height, height + y)

            widget.place(x = x, y = y, width = width, height = height)
            self.menu_bar.append(widget)

    def next_button_click(self):
        self._index = min(self._index + 1, len(self.trial) - 1)
        self.init_case()

    def done_button_click(self):
        if self.start_timer is not None:
            self.end_time = timer() - self.start_timer
            self.end_time = math.ceil(self.end_time / self.analyse_slider_resolution) * self.analyse_slider_resolution

        self.start_timer = None
        self.show_analyse_widgets = True
        self.display_image_set(self.source_image().copy())
        self.draw_menu_bar()

    def frame_configure(self, event):
        if self.display_image is not None and self.display_image_resize:
            self.display_image_set(self.display_image)

    def analyse_scale_change(self, event):
        time = float(event)

        analyse = self.render_analyse_until(self.source_image().copy(), time)
        self.display_image_set(analyse)

    def display_image_set(self, image):
        self.display_image = image

        if image is None:
            if self.canvas is None:
                return

            self.canvas.destroy()
            self.canvas = None
            return

        x = self.default_margin_left
        y = self.default_margin_top + self.menu_bar_height

        width  = image.width
        height = image.height

        if self.display_image_resize:
            window_width  = self.win.winfo_width()
            window_height = self.win.winfo_height()

            max_width  = window_width - 2 * self.default_margin_left
            max_height = window_height - y - self.default_margin_top

            width_ratio  = max_width  / width
            height_ratio = max_height / height

            min_ratio = min(width_ratio, height_ratio)

            if min_ratio < 1:
                width  = round(width  * min_ratio)
                height = round(height * min_ratio)

                self.display_image_resize_ratio = min_ratio
                image = image.resize((width, height))

            else:
                self.display_image_resize_ratio = None

        self.photo_image = ImageTk.PhotoImage(image)

        if self.canvas is None:
            self.canvas = tk.Canvas(self.frame, bd = 0, highlightthickness = 0)

        self.canvas.place(x = x, y = y, width = width, height = height)
        self.canvas.create_image(0, 0, anchor = tk.NW, image = self.photo_image)
        self.canvas.bind('<Button-1>', self.canvas_click)
        self.canvas.bind('<Motion>',   self.canvas_motion)

    def apply_image_filters(self, image):
        image_filters = self.image_filters()

        if image_filters is None:
            message = 'Versuchsfall hat kein Filter'
            tk.messagebox.showinfo('Fehler', message)
            return

        for image_filter in image_filters:
            image = image_filter.apply(image)

        return image

    def canvas_click(self, event):
        if self.start_timer is not None and self.clicks is not None:
            x = event.x
            y = event.y
            t = timer() - self.start_timer

            self.clicks.append(((x, y), t))
            self.display_bubble(x, y)

    def canvas_motion(self, event):
        if self.start_timer is not None and self.motions is not None:
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
        image = Rust.bubble_rectangle(self.filter_image, self.source_image(), left, top, width, height)
        self.display_image_set(image)

    def bubble_ellipse(self, left, top, width, height):
        image = Rust.bubble_ellipse(self.filter_image, self.source_image(), left, top, width, height)
        self.display_image_set(image)

    def display_bubble(self, x, y):
        if self.display_image_resize and self.display_image_resize_ratio is not None:
            x *= 1 / self.display_image_resize_ratio
            y *= 1 / self.display_image_resize_ratio

        left = x - (self.bubble_width  // 2)
        top  = y - (self.bubble_height // 2)

        if   self.bubble_shape == 'ellipse':
            self.bubble_ellipse(left, top, self.bubble_width, self.bubble_height)
        elif self.bubble_shape == 'rectangle':
            self.bubble_rectangle(left, top, self.bubble_width, self.bubble_height)

    def render_analyse_until(self, image, time):
        if self.clicks is not None and self.motions is not None:
            draw = ImageDraw.Draw(image, 'RGBA')
            motions = []
            clicks  = []

            for (x, y), t in self.motions:
                if t > time:
                    break

                if self.display_image_resize and self.display_image_resize_ratio is not None:
                    x *= 1 / self.display_image_resize_ratio
                    y *= 1 / self.display_image_resize_ratio

                motions.append((x, y))

            for (x, y), t in self.clicks:
                if t > time:
                    break

                if self.display_image_resize and self.display_image_resize_ratio is not None:
                    x *= 1 / self.display_image_resize_ratio
                    y *= 1 / self.display_image_resize_ratio

                clicks.append((x, y))

            draw.line(motions, fill = self.analyse_render_motion_color, width = self.analyse_render_motion_width)

            for x, y in clicks:
                left = x - (self.bubble_width  // 2)
                top  = y - (self.bubble_height // 2)
                draw.ellipse([(left, top), (left + self.bubble_width, top + self.bubble_height)],
                             fill = self.analyse_render_click_fill_color,
                             outline = self.analyse_render_click_outline_color,
                             width = self.analyse_render_click_outline_with)

            return image


class BubbleViewTrial(Tool):
    def __init__(self, win, frame, config):
        win.state('zoomed')

        self.config = config

        # Config
        self.display_image_resize = True

        self._index           = 0
        self._cases           = [{}]
        self._applied_filters = []

        self.menu_bar_width       = 0
        self.menu_bar_height      = 0
        self.default_margin_left  = 10
        self.default_margin_top   = 10
        self.default_margin_right = 0

        # Vars
        self.index_var            = tk.StringVar(value = '1')
        self.filter_selection     = tk.StringVar(value = '')
        self.box_blur_radius      = tk.StringVar(value = '1')
        self.box_blur_iterations  = tk.StringVar(value = '1')
        self.gaussian_blur_radius = tk.StringVar(value = '1')
        self.pixelate_diameter    = tk.StringVar(value = '1')

        # Widgets
        self.canvas   = None
        self.menu_bar = []

        super().__init__(win, frame)

        # Events
        self.frame.bind('<Configure>', self.frame_configure)

    def case(self):
        return self._cases[self._index]

    def source_image(self):
        return self.case().get('source_image', None)

    def source_image_set(self, image):
        self.case()['source_image'] = image

    def filter_image(self):
        return self.case().get('filter_image', None)

    def filter_image_set(self, image):
        self.case()['filter_image'] = image

    def photo_image(self):
        return self.case().get('photo_image', None)

    def photo_image_set(self, tk_image):
        self.case()['photo_image'] = tk_image

    def display_image(self):
        return self.case().get('display_image', None)

    def applied_filters(self):
        return self.case().get('applied_filters', None)

    def applied_filters_set(self, image_filters):
        self.case()['applied_filters'] = image_filters

    def applied_filters_append(self, image_fitler):
        if self.applied_filters() is None:
            self.applied_filters_set([])

        self.applied_filters().append(image_fitler)

    def applied_filters_pop(self):
        if self.applied_filters() is None or len(self.applied_filters()) == 0:
            return None

        return self.applied_filters().pop()

    def drawView(self):
        self.draw_menu_bar()

    def draw_menu_bar(self):
        for widget in self.menu_bar:
            widget.destroy()

        self.menu_bar = []

        default_width  = 80
        default_height = 30

        back_button = tk.Button(self.frame, text = 'Zurück',     command = self.back_button_click)
        index_label = tk.Label(self.frame, textvariable = self.index_var)
        next_button = tk.Button(self.frame, text = 'Weiter',     command = self.next_button_click)
        load_button = tk.Button(self.frame, text = 'Bild Laden', command = self.load_button_click)

        filter_label    = tk.Label(self.frame, text = 'Filter')
        filter_combobox = tkk.Combobox(self.frame, textvariable = self.filter_selection,
                                       values = ['Box Blur', 'Gaussian Blur', 'Pixelate'],
                                       state = 'readonly')
        filter_combobox.bind('<<ComboboxSelected>>', self.filter_combobox_change)

        widgets = [
            (back_button,     {}),
            (index_label,     {'width': default_width // 2}),
            (next_button,     {'margin_right': 20}),
            (load_button,     {'margin_right': 20}),
            (filter_label,    {}),
            (filter_combobox, {'width': 100, 'margin_left': 0})
        ]

        filter_selected = False
        if   self.filter_selection.get() == 'Box Blur':
            filter_selected = True

            radius_label = tk.Label(self.frame, text = 'Radius')
            radius_entry = tk.Entry(self.frame, textvariable = self.box_blur_radius)

            iterations_label = tk.Label(self.frame, text = 'Iterationen')
            iterations_entry = tk.Entry(self.frame, textvariable = self.box_blur_iterations)

            widgets.extend([
                (radius_label, {}),
                (radius_entry, {'margin_left': 0}),
                (iterations_label, {}),
                (iterations_entry, {'margin_left': 0})
            ])

        elif self.filter_selection.get() == 'Gaussian Blur':
            filter_selected = True

            radius_label = tk.Label(self.frame, text = 'Radius')
            radius_entry = tk.Entry(self.frame, textvariable = self.gaussian_blur_radius)

            widgets.extend([
                (radius_label, {}),
                (radius_entry, {'margin_left': 0, 'margin_right': 170})
            ])

        elif self.filter_selection.get() == 'Pixelate':
            filter_selected = True

            diameter_label = tk.Label(self.frame, text = 'Durchmesser')
            diameter_entry = tk.Entry(self.frame, textvariable = self.pixelate_diameter)

            widgets.extend([
                (diameter_label, {}),
                (diameter_entry, {'margin_left': 0, 'margin_right': 170})
            ])

        if filter_selected:
            apply_button = tk.Button(self.frame, text = 'Anwenden',   command = self.apply_button_click)
            undo_button  = tk.Button(self.frame, text = 'Rückgängig', command = self.undo_button_click)
            save_button  = tk.Button(self.frame, text = 'Speichern',  command = self.save_button_click)

            widgets.extend([
                (apply_button, {}),
                (undo_button,  {'margin_right': 20}),
                (save_button,  {'margin_right': 20})
            ])

        done_button = tk.Button(self.frame, text = 'Fertig', command = self.done_button_click)

        widgets.extend([
            (done_button, {})
        ])

        # export_button = tk.Button(self.frame, text = 'Export', command = self.export_button_click)
        #
        # widgets.extend([
        #     (export_button, {})
        # ])

        self.menu_bar_width  = 0
        self.menu_bar_height = 0

        for widget, kwargs in widgets:
            margin_left  = kwargs.get('margin_left',  self.default_margin_left)
            margin_top   = kwargs.get('margin_top',   self.default_margin_top)
            margin_right = kwargs.get('margin_right', self.default_margin_right)

            x = margin_left + self.menu_bar_width
            y = margin_top

            width  = kwargs.get('width',  default_width)
            height = kwargs.get('height', default_height)

            self.menu_bar_width  = x + width + margin_right
            self.menu_bar_height = max(self.menu_bar_height, height + y)

            widget.place(x = x, y = y, width = width, height = height)
            self.menu_bar.append(widget)

    # def export_button_click(self):
    #     image = self.filter_image()
    #
    #     if image is not None:
    #         image.save('export.jpg')

    def frame_configure(self, event):
        if self.display_image() is not None and self.display_image_resize:
            self.display_image_set(self.display_image())

    def back_button_click(self):
        self._index = max(self._index - 1, 0)
        self.index_var.set(str(self._index + 1))

        filter_image = self.filter_image()
        self.display_image_set(filter_image)

    def load_button_click(self):
        file = fd.askopenfilename()
        if file:
            try:
                # TODO: PIL.Image.tobytes() funktioniert nicht richtig bei PNG's (wird aber von ImageFilter benötigt)
                image = Image.open(file)
                image.save('bubble_view_temp.bmp')

                source_image = Image.open('bubble_view_temp.bmp')
                source_image.load()

                if os.path.exists('bubble_view_temp.bmp'):
                    os.remove('bubble_view_temp.bmp')

                self._cases[self._index] = {}
                filter_image = source_image.copy()

                self.source_image_set(source_image)
                self.filter_image_set(filter_image)
                self.display_image_set(filter_image)

            except IOError:
                messagebox.showinfo('Fehler', f'Keine Bilddatei: {file}')

    def next_button_click(self):
        self._index += 1
        self.index_var.set(str(self._index + 1))

        if len(self._cases) == self._index:
            self._cases.append({})

        filter_image = self.filter_image()
        self.display_image_set(filter_image)

    def done_button_click(self):
        trial = []

        for case in self._cases:
            source_image  = case.get('source_image', None)
            image_filters = case.get('saved_filters', None)

            if source_image is not None and image_filters is not None:
                trial.append({
                    'source_image':  source_image,
                    'image_filters': image_filters
                })

        for widget in self.frame.winfo_children():
            widget.destroy()

        study = BubbleViewStudy(self.win, self.frame, self.config, trial)

    def filter_combobox_change(self, event):
        self.draw_menu_bar()

    def apply_button_click(self):
        image_filter = None

        if   self.filter_selection.get() == 'Box Blur':
            radius_error     = not self.box_blur_radius.get().isdigit()
            iterations_error = not self.box_blur_iterations.get().isdigit()

            if radius_error or iterations_error:
                message = ''

                if radius_error:
                    message += f'Radius: {self.box_blur_radius.get()} - Keine natürliche Zahl\n'

                if iterations_error:
                    message += f'Iterationen: {self.box_blur_iterations.get()} - Kein natürliche Zahl\n'

                tk.messagebox.showinfo('Fehler', message)
                return

            radius       = int(self.box_blur_radius.get())
            iterations   = int(self.box_blur_iterations.get())
            image_filter = ImageFilter.BoxBlur(radius, iterations)

        elif self.filter_selection.get() == 'Gaussian Blur':
            radius_error = not self.gaussian_blur_radius.get().isdigit()

            if radius_error:
                message = f'Radius: {self.gaussian_blur_radius.get()} - Keine natürliche Zahl'
                tk.messagebox.showinfo('Fehler', message)
                return

            radius = int(self.gaussian_blur_radius.get())
            image_filter = ImageFilter.GaussianBlur(radius)

        elif self.filter_selection.get() == 'Pixelate':
            diameter_error = not self.pixelate_diameter.get().isdigit()

            if diameter_error:
                message = f'Durchmesser: {self.pixelate_diameter.get()} - Keine natürliche Zahl'
                tk.messagebox.showinfo('Fehler', message)
                return

            diameter = int(self.pixelate_diameter.get())
            image_filter = ImageFilter.PixelateSquare(diameter)

        self.apply_filter(image_filter)

    def undo_button_click(self):
        _ = self.applied_filters_pop()

        filter_image = self.source_image()
        if filter_image is None:
            return

        for image_filter in self.applied_filters():
            filter_image = image_filter.apply(filter_image)

        self.filter_image_set(filter_image)
        self.display_image_set(filter_image)

    def save_button_click(self):
        saved_filters = []

        for image_filter in self.applied_filters():
            image_filter_copy = image_filter.copy()
            saved_filters.append(image_filter_copy)

        self.case()['saved_filters'] = saved_filters

    def display_image_set(self, image):
        self.case()['display_image'] = image

        if image is None:
            if self.canvas is None:
                return

            self.canvas.destroy()
            self.canvas = None
            return

        x = self.default_margin_left
        y = self.default_margin_top + self.menu_bar_height

        width  = image.width
        height = image.height

        if self.display_image_resize:
            window_width  = self.win.winfo_width()
            window_height = self.win.winfo_height()

            max_width  = window_width - 2 * self.default_margin_left
            max_height = window_height - y - self.default_margin_top

            width_ratio  = max_width  / width
            height_ratio = max_height / height

            min_ratio = min(width_ratio, height_ratio)

            if min_ratio < 1:
                width  = round(width  * min_ratio)
                height = round(height * min_ratio)

                image = image.resize((width, height))

        self.photo_image_set(ImageTk.PhotoImage(image))

        if self.canvas is None:
            self.canvas = tk.Canvas(self.frame, bd = 0, highlightthickness = 0)

        self.canvas.place(x = x, y = y, width = width, height = height)
        self.canvas.create_image(0, 0, anchor = tk.NW, image = self.photo_image())

    def apply_filter(self, image_filter, show_error = True):
        filter_image = self.case().get('filter_image')

        if filter_image is None and show_error:
            message = 'Kein Bild geladen'
            tk.messagebox.showinfo('Fehler', message)
            return

        filter_image = image_filter.apply(filter_image)
        self.filter_image_set(filter_image)

        self.display_image_set(filter_image)
        self.applied_filters_append(image_filter)


# class BubbleView(Tool):
#     def __init__(self, win, frame, config):
#         win.state('zoomed')
#
#         # Config
#         self.bubble_width  = 200
#         self.bubble_height = 200
#         self.bubble_shape  = 'ellipse'
#         self.motion_min_distance = 10
#         self.blur_radius = 50
#         self.blur_iterations = 3
#         self.pixelate_diameter = 100
#         self.slider_resolution = 0.05
#         self.analyse_render_motion_width = 3
#         self.analyse_render_motion_color = 'green'
#         self.analyse_render_click_outline_with  = 2
#         self.analyse_render_click_outline_color = 'red'
#         self.analyse_render_click_fill_color = (75, 75, 75, 75)
#
#         self.source_image = None
#         self.target_image = None
#         self.photo_image  = None
#         self.canvas       = None
#
#         self.radius_var     = tk.StringVar(value = str(self.blur_radius))
#         self.iterations_var = tk.StringVar(value = str(self.blur_iterations))
#         self.diameter_var   = tk.StringVar(value = str(self.pixelate_diameter))
#
#         self.start_timer = None
#         self.clicks      = None
#         self.motions     = None
#
#         super().__init__(win, frame)
#
#     def drawView(self):
#         load_button = tk.Button(self.frame, text = 'Bild Laden', command = self.load_button_click)
#         load_button.place(x = 100, y = 10, width = 80, height = 30)
#
#         reset_button = tk.Button(self.frame, text = 'Reset', command = self.reset_button_click)
#         reset_button.place(x = 190, y = 10, width = 80, height = 30)
#
#         gaussian_button = tk.Button(self.frame, text = 'Gaussian Blur', command = self.gaussian_button_click)
#         gaussian_button.place(x = 280, y = 10, width = 80, height = 30)
#
#         radius_entry = tk.Entry(self.frame, textvariable = self.radius_var)
#         radius_entry.place(x = 370, y = 10, width = 80, height = 30)
#
#         iterations_entry = tk.Entry(self.frame, textvariable = self.iterations_var)
#         iterations_entry.place(x = 460, y = 10, width = 80, height = 30)
#
#         blur_button = tk.Button(self.frame, text = 'Box Blur', command = self.blur_button_click)
#         blur_button.place(x = 550, y = 10, width = 80, height = 30)
#
#         diameter_entry = tk.Entry(self.frame, textvariable = self.diameter_var)
#         diameter_entry.place(x = 640, y = 10, width = 80, height = 30)
#
#         pixelate_button = tk.Button(self.frame, text = 'Pixelate', command = self.pixelate_button_click)
#         pixelate_button.place(x = 730, y = 10, width = 80, height = 30)
#
#         start_button = tk.Button(self.frame, text = 'Start', command = self.start_button_click)
#         start_button.place(x = 820, y = 10, width = 80, height = 30)
#
#         end_button = tk.Button(self.frame, text = 'Fertig', command = self.end_button_click)
#         end_button.place(x = 910, y = 10, width = 80, height = 30)
#
#     def load_button_click(self):
#         file = fd.askopenfilename()
#         if file:
#             try:
#                 # TODO: PIL.Image.tobytes() funktioniert nicht richtig bei PNG's (wird aber von ImageFilter benötigt)
#                 image = Image.open(file)
#                 image.save('bubble_view_temp.bmp')
#                 self.source_image = Image.open('bubble_view_temp.bmp')
#                 self.source_image.load()
#
#                 if os.path.exists('bubble_view_temp.bmp'):
#                     os.remove('bubble_view_temp.bmp')
#
#                 self.target_image = self.source_image.copy()
#                 self.display_image(self.target_image)
#
#             except IOError:
#                 messagebox.showerror('Dateifehler', f'Keine Bilddatei: {file}')
#
#     def reset_button_click(self):
#         if self.source_image is not None:
#             self.target_image = self.source_image.copy()
#             self.display_image(self.target_image)
#
#     def gaussian_button_click(self):
#         try:
#             if self.target_image is not None:
#                 radius = int(self.radius_var.get())
#
#                 if radius < 0:
#                     raise ValueError
#
#                 image = ImageFilter.blur_gaussian(self.target_image, radius)
#
#                 if image is None:
#                     raise RuntimeError
#
#                 self.target_image = image
#                 self.update_display_image(self.target_image)
#
#         except ValueError:
#             messagebox.showerror('Inputfehler',
#                                  f'Keine natürlichen Zahlen: {self.radius_var.get()}, {self.iterations_var.get()}')
#
#         except RuntimeError:
#             messagebox.showerror('Filterfehler',
#                                  f'Konnte Box-Blur-Filter nicht anwenden')
#
#     def blur_button_click(self):
#         try:
#             radius     = int(self.radius_var.get())
#             iterations = int(self.iterations_var.get())
#
#             if radius < 0 or iterations < 0:
#                 raise ValueError
#
#             image = ImageFilter.blur_box(self.target_image, radius, iterations)
#
#             if self.target_image is None:
#                 raise RuntimeError
#
#             self.target_image = image
#             self.update_display_image(self.target_image)
#
#         except ValueError:
#             messagebox.showerror('Inputfehler',
#                                  f'Keine natürlichen Zahlen: {self.radius_var.get()}, {self.iterations_var.get()}')
#
#         except RuntimeError:
#             messagebox.showerror('Filterfehler',
#                                  f'Konnte Box-Blur-Filter nicht anwenden')
#
#     def pixelate_button_click(self):
#         try:
#             diameter = int(self.diameter_var.get())
#
#             if diameter < 0:
#                 raise ValueError
#
#             image = ImageFilter.pixelate_square(self.target_image, diameter)
#
#             if self.target_image is None:
#                 raise RuntimeError
#
#             self.target_image = image
#             self.update_display_image(self.target_image)
#
#         except ValueError:
#             messagebox.showerror('Inputfehler',
#                                  f'Keine natürliche Zahl: {self.diameter_var.get()}')
#
#         except RuntimeError:
#             messagebox.showerror('Filterfehler',
#                                  f'Konnte Pixelatefilter nicht anwenden')
#
#     def start_button_click(self):
#         self.start_timer = timer()
#         self.clicks      = []
#         self.motions     = []
#
#         self.update_display_image(self.target_image.copy())
#
#     def end_button_click(self):
#         resolution = 0.05
#
#         end_time = timer() - self.start_timer
#         end_time = math.ceil(end_time / resolution) * resolution
#
#         slider = tk.Scale(self.frame, from_ = 0, to = end_time, orient = tk.HORIZONTAL, command = self.slider_change,
#                           showvalue = True, resolution = self.slider_resolution, width = 10)
#         slider.place(x = 1000, y = 10, width = 170, height = 30)
#
#         self.update_display_image(self.source_image.copy())
#
#     def slider_change(self, event):
#         time = float(event)
#
#         analyse = self.render_analyse_until(self.source_image.copy(), time)
#         self.update_display_image(analyse)
#
#     def display_image(self, image):
#         self.photo_image = ImageTk.PhotoImage(image)
#
#         if self.canvas:
#             self.canvas.destroy()
#
#         self.canvas = tk.Canvas(self.frame, bd = 0, highlightthickness = 0)
#         self.canvas.place(x = 10, y = 50, width = self.photo_image.width(), height = self.photo_image.height())
#         self.canvas.create_image(0, 0, anchor = tk.NW, image = self.photo_image)
#         self.canvas.bind('<Button-1>', self.canvas_click)
#         self.canvas.bind('<Motion>',   self.canvas_motion)
#
#     def update_display_image(self, image):
#         if self.canvas is not None:
#             self.photo_image = ImageTk.PhotoImage(image)
#             self.canvas.create_image(0, 0, anchor = tk.NW, image = self.photo_image)
#
#     def canvas_click(self, event):
#         if self.start_timer and self.clicks is not None:
#             x = event.x
#             y = event.y
#             t = timer() - self.start_timer
#
#             self.clicks.append(((x, y), t))
#             self.display_bubble(x, y)
#
#     def canvas_motion(self, event):
#         if self.start_timer and self.motions is not None:
#             x = event.x
#             y = event.y
#             t = timer() - self.start_timer
#
#             if len(self.motions) == 0:
#                 self.motions.append(((x, y), t))
#                 return
#
#             (last_x, last_y), _ = self.motions[-1]
#             dif_x = x - last_x
#             dif_y = y - last_y
#
#             if math.sqrt(dif_x ** 2 + dif_y ** 2) < self.motion_min_distance:
#                 return
#
#             self.motions.append(((x, y), t))
#
#     def bubble_rectangle(self, left, top, width, height):
#         image = Rust.bubble_rectangle(self.target_image, self.source_image, left, top, width, height)
#         self.update_display_image(image)
#
#     def bubble_ellipse(self, left, top, width, height):
#         image = Rust.bubble_ellipse(self.target_image, self.source_image, left, top, width, height)
#         self.update_display_image(image)
#
#     def display_bubble(self, x, y):
#         left = x - (self.bubble_width  // 2)
#         top  = y - (self.bubble_height // 2)
#
#         if   self.bubble_shape == 'ellipse':
#             self.bubble_ellipse(left, top, self.bubble_width, self.bubble_height)
#         elif self.bubble_shape == 'rectangle':
#             self.bubble_rectangle(left, top, self.bubble_width, self.bubble_height)
#
#     def render_analyse(self, image):
#         if self.clicks is not None and self.motions is not None:
#             draw = ImageDraw.Draw(image, 'RGBA')
#             motions = [xy for xy, t in self.motions]
#             draw.line(motions, fill = self.analyse_render_motion_color, width = self.analyse_render_motion_width)
#
#             for (x, y), t in self.clicks:
#                 left = x - (self.bubble_width  // 2)
#                 top  = y - (self.bubble_height // 2)
#                 draw.ellipse([(left, top), (left + self.bubble_width, top + self.bubble_height)],
#                              fill = self.analyse_render_click_fill_color,
#                              outline = self.analyse_render_click_outline_color,
#                              width = self.analyse_render_click_outline_with)
#
#             return image
#
#     def render_analyse_until(self, image, time):
#         if self.clicks is not None and self.motions is not None:
#             draw = ImageDraw.Draw(image, 'RGBA')
#             motions = []
#             clicks  = []
#
#             for xy, t in self.motions:
#                 if t > time:
#                     break
#
#                 motions.append(xy)
#
#             for xy, t in self.clicks:
#                 if t > time:
#                     break
#
#                 clicks.append(xy)
#
#             draw.line(motions, fill = self.analyse_render_motion_color, width = self.analyse_render_motion_width)
#
#             for x, y in clicks:
#                 left = x - (self.bubble_width  // 2)
#                 top  = y - (self.bubble_height // 2)
#                 draw.ellipse([(left, top), (left + self.bubble_width, top + self.bubble_height)],
#                              fill = self.analyse_render_click_fill_color,
#                              outline = self.analyse_render_click_outline_color,
#                              width = self.analyse_render_click_outline_with)
#
#             return image
