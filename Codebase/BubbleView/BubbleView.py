import tkinter     as tk
import tkinter.ttk as tkk
import os
import math

from abc     import ABC, abstractmethod
from timeit  import default_timer as timer
from PIL     import Image, ImageTk, ImageDraw
from tkinter import filedialog as fd, messagebox

from Rust import Rust

from ImageFilter import ImageFilter
from Tool        import Tool


class ImageMetaLocal:
    def __init__(self):
        pass

    def meta_type(self):
        return 'local'


class ImageMetaDatabase:
    def __init__(self, id):
        self._id = id

    def meta_type(self):
        return 'database'


class TrialCase:
    def __init__(self, image = None, image_meta = None, filters = None, bubble = None):
        self._image      = image
        self._image_meta = image_meta
        self._filters    = filters
        self._bubble     = bubble

    def image_get(self):
        return self._image

    def image_set(self, image, meta):
        self._image      = image
        self._image_meta = meta


class Trial:
    def __init__(self):
        self._cases = []

    def append(self, case):
        self._cases.append(case)

        return len(self._cases) - 1

    def index_valid(self, index):
        if index is not None and index < len(self._cases):
            return True

        return False

    def image_get(self, index):
        return self._cases[index].get_image()

    def image_set(self, index, image, meta):
        self._cases[index].image_set(image, meta)

    def empty(self):
        return len(self._cases) == 0

    def __len__(self):
        return len(self._cases)


class BubbleViewTool(Tool):
    pass 


class BubbleViewTrialTool(BubbleViewTool):
    _DEFAULT_PADDING_HORIZONTAL             = 5
    _DEFAULT_PADDING_VERTICAL               = 5
    _DEFAULT_MARGIN_HORIZONTAL              = 3
    _DEFAULT_MARGIN_VERTICAL                = 3
    _DEFAULT_HORIZONTAL_FRAME_MARGIN_SCALAR = 4
    _DEFAULT_TEXT_WIDGET_WIDTH              = 8

    def __init__(self, win, frame, config, **kwargs):
        self._on_back_callback = kwargs.get('on_back_callback', None)
        self._trial            = kwargs.get('trial', Trial())

        # gui style
        self._padding_horizontal             = self._DEFAULT_PADDING_HORIZONTAL
        self._padding_vertical               = self._DEFAULT_PADDING_VERTICAL
        self._margin_horizontal              = self._DEFAULT_MARGIN_HORIZONTAL
        self._margin_vertical                = self._DEFAULT_MARGIN_VERTICAL
        self._horizontal_frame_margin_scalar = self._DEFAULT_HORIZONTAL_FRAME_MARGIN_SCALAR
        self._text_widget_width              = self._DEFAULT_TEXT_WIDGET_WIDTH

        # menu bar widgets
        self._menu_bar_frame               = None
        self._menu_bar_back_frame          = None
        self._menu_bar_load_frame          = None
        self._menu_bar_nav_frame           = None
        self._menu_bar_filter_choice_frame = None
        self._menu_bar_filter_input_frame  = None
        self._menu_bar_bubble_choice_frame = None
        self._menu_bar_bubble_input_frame  = None
        self._menu_bar_write_frame         = None
        self._menu_bar_nav_index_spinbox   = None

        # vars
        self._menu_bar_nav_index_var                = tk.StringVar(value = '')
        self._menu_bar_filter_choice_var            = tk.StringVar(value = '')
        self._menu_bar_filter_box_radius_var        = tk.StringVar(value = '')
        self._menu_bar_filter_box_iterations_var    = tk.StringVar(value = '')
        self._menu_bar_filter_gauss_radius_var      = tk.StringVar(value = '')
        self._menu_bar_filter_pixelate_diameter_var = tk.StringVar(value = '')
        self._menu_bar_bubble_choice_var            = tk.StringVar(value = '')
        self._menu_bar_bubble_width_var             = tk.StringVar(value = '')
        self._menu_bar_bubble_height_var            = tk.StringVar(value = '')
        self._menu_bar_bubble_exponent_var          = tk.StringVar(value = '')

        super().__init__(win, frame)

    # GUI
    def _padding_kwargs(self, hscale = 1, vscale = 1):
        return {
            'ipadx': self._padding_horizontal * hscale,
            'ipady': self._padding_vertical * vscale
        }

    def _margin_kwargs(self, hscale = 1, vscale = 1):
        return {
            'padx': self._margin_horizontal * hscale,
            'pady': self._margin_vertical * vscale
        }

    def _init_menu_bar_back_button(self):
        if self._menu_bar_frame is None:
            return

        if self._menu_bar_back_frame is not None:
            self._menu_bar_back_frame.destroy()

        self._menu_bar_back_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_back_frame.grid(column = 0, row = 0, sticky = 'n',
                                       **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        self._menu_bar_back_button = tk.Button(self._menu_bar_back_frame, text = 'Zurück',
                                               command = self._on_back_callback)
        self._menu_bar_back_button.configure(width = self._text_widget_width)
        self._menu_bar_back_button.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_nav_frame(self):
        if self._menu_bar_frame is None:
            return

        if self._menu_bar_nav_frame is not None:
            self._menu_bar_nav_frame.destroy()

        self._menu_bar_nav_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_nav_frame.grid(column = 1, row = 0, sticky = 'n',
                                      **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        new_button = tk.Button(self._menu_bar_nav_frame, text = 'Neu', command = self._menu_bar_nav_new_button_click)
        new_button.configure(width = self._text_widget_width)
        new_button.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        delete_button = tk.Button(self._menu_bar_nav_frame, text = 'Löschen',
                                  command = self._menu_bar_nav_delete_button_click)
        delete_button.configure(width = self._text_widget_width)
        delete_button.grid(column = 0, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

        self._menu_bar_nav_index_spinbox = tk.Spinbox(self._menu_bar_nav_frame, from_ = 0, to = len(self._trial),
                                                      textvariable = self._menu_bar_nav_index_var,
                                                      command = self._menu_bar_nav_index_spinbox_change)
        self._menu_bar_nav_index_spinbox.configure(width = self._text_widget_width)
        self._menu_bar_nav_index_spinbox.grid(column = 1, row = 0,
                                              **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_load_frame(self):
        if self._menu_bar_frame is None:
            return

        if self._menu_bar_load_frame is not None:
            self._menu_bar_load_frame.destroy()

        self._menu_bar_load_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_load_frame.grid(column = 2, row = 0, sticky = 'n',
                                       **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        local_button = tk.Button(self._menu_bar_load_frame, text = 'Lokal',
                                 command = self._menu_bar_load_local_button_click)
        local_button.configure(width = self._text_widget_width)
        local_button.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        database_button = tk.Button(self._menu_bar_load_frame, text = 'Datenbank',
                                    command = self._menu_bar_load_database_button_click)
        database_button.configure(width = self._text_widget_width)
        database_button.grid(column = 0, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_filter_choice_frame(self):
        if self._menu_bar_frame is None:
            return

        if self._menu_bar_filter_choice_frame is not None:
            self._menu_bar_filter_choice_frame.destroy()

        self._menu_bar_filter_choice_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_filter_choice_frame.grid(column = 3, row = 0, sticky = 'n',
                                                **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        choices = ['Box Blur', 'Gaussian Blur', 'Pixelate']
        max_choice_len = max(len(c) for c in choices)

        choice_label = tk.Label(self._menu_bar_filter_choice_frame, text = 'Filter')
        choice_label.configure(width = 8)
        choice_label.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        choice_combobox = tkk.Combobox(self._menu_bar_filter_choice_frame,
                                       textvariable = self._menu_bar_filter_choice_var,
                                       values = choices,
                                       state = 'readonly')
        choice_combobox.bind('<<ComboboxSelected>>', self._menu_bar_filter_choice_combobox_changed)
        choice_combobox.configure(width = max_choice_len)
        choice_combobox.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        choice = self._menu_bar_filter_choice_var.get()
        if choice in choices:
            reverse_button = tk.Button(self._menu_bar_filter_choice_frame, text = 'Rückgängig',
                                       command = self._menu_bar_filter_choice_reverse_button_click)
            reverse_button.configure(width = self._text_widget_width)
            reverse_button.grid(column = 0, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

            apply_button = tk.Button(self._menu_bar_filter_choice_frame, text = 'Anwenden',
                                     command = self._menu_bar_filter_choice_apply_button_click)
            apply_button.configure(width = max_choice_len)
            apply_button.grid(column = 1, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_filter_input_frame(self):
        if self._menu_bar_frame is None:
            return

        if self._menu_bar_filter_input_frame is not None:
            self._menu_bar_filter_input_frame.destroy()

        choice = self._menu_bar_filter_choice_var.get()

        self._menu_bar_filter_input_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_filter_input_frame.grid(column = 4, row = 0, sticky ='n',
                                               **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        if 'Box Blur' == choice:
            radius_label = tk.Label(self._menu_bar_filter_input_frame, text ='Radius')
            radius_label.configure(width = self._text_widget_width)
            radius_label.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

            radius_entry = tk.Entry(self._menu_bar_filter_input_frame, textvariable = self._menu_bar_filter_box_radius_var)
            radius_entry.configure(width = self._text_widget_width)
            radius_entry.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

            iterations_label = tk.Label(self._menu_bar_filter_input_frame, text ='Iterationen')
            iterations_label.configure(width = self._text_widget_width)
            iterations_label.grid(column = 0, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

            iterations_entry = tk.Entry(self._menu_bar_filter_input_frame, textvariable = self._menu_bar_filter_box_iterations_var)
            iterations_entry.configure(width = self._text_widget_width)
            iterations_entry.grid(column = 1, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

        elif 'Gaussian Blur' == choice:
            radius_label = tk.Label(self._menu_bar_filter_input_frame, text ='Radius')
            radius_label.configure(width = self._text_widget_width)
            radius_label.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

            radius_entry = tk.Entry(self._menu_bar_filter_input_frame, textvariable = self._menu_bar_filter_gauss_radius_var)
            radius_entry.configure(width = self._text_widget_width)
            radius_entry.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        elif 'Pixelate' == choice:
            diameter_label = tk.Label(self._menu_bar_filter_input_frame, text = 'Größe')
            diameter_label.configure(width = self._text_widget_width)
            diameter_label.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

            diameter_entry = tk.Entry(self._menu_bar_filter_input_frame,
                                      textvariable = self._menu_bar_filter_pixelate_diameter_var)
            diameter_entry.configure(width = self._text_widget_width)
            diameter_entry.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_bubble_choice_frame(self):
        if self._menu_bar_frame is None:
            return

        if self._menu_bar_bubble_choice_frame is not None:
            self._menu_bar_bubble_choice_frame.destroy()

        self._menu_bar_bubble_choice_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_bubble_choice_frame.grid(column = 5, row = 0, sticky = 'n',
                                                **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        choice = self._menu_bar_bubble_choice_var.get()
        choices = ['Ellipse - Diskret', 'Ellipse - Stetig', 'Rechteck - Diskret', 'Rechteck - Stetig']
        max_choice_len = max(len(c) for c in choices)

        choice_label = tk.Label(self._menu_bar_bubble_choice_frame, text = 'Bubble')
        choice_label.configure(width = self._text_widget_width)
        choice_label.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        choice_combobox = tkk.Combobox(self._menu_bar_bubble_choice_frame,
                                       textvariable = self._menu_bar_bubble_choice_var,
                                       values = choices,
                                       state = 'readonly')
        choice_combobox.bind('<<ComboboxSelected>>', self._menu_bar_bubble_choice_combobox_changed)
        choice_combobox.configure(width = max_choice_len)
        choice_combobox.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        if choice in choices:
            apply_button = tk.Button(self._menu_bar_bubble_choice_frame, text = 'Anwenden',
                                     command = self._menu_bar_bubble_choice_apply_button_click)
            apply_button.configure(width = max_choice_len)
            apply_button.grid(column = 1, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_bubble_input_frame(self):
        if self._menu_bar_frame is None:
            return

        if self._menu_bar_bubble_input_frame is not None:
            self._menu_bar_bubble_input_frame.destroy()

        choices = ['Ellipse - Diskret', 'Ellipse - Stetig', 'Rechteck - Diskret', 'Rechteck - Stetig']
        choice = self._menu_bar_bubble_choice_var.get()
        if choice not in choices:
            return

        self._menu_bar_bubble_input_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_bubble_input_frame.grid(column = 6, row = 0, sticky = 'n',
                                               **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        width_label = tk.Label(self._menu_bar_bubble_input_frame, text = 'Breite')
        width_label.configure(width = self._text_widget_width)
        width_label.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        width_entry = tk.Entry(self._menu_bar_bubble_input_frame, textvariable = self._menu_bar_bubble_width_var)
        width_entry.configure(width = self._text_widget_width)
        width_entry.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        height_label = tk.Label(self._menu_bar_bubble_input_frame, text = 'Höhe')
        height_label.configure(width = self._text_widget_width)
        height_label.grid(column = 0, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

        height_entry = tk.Entry(self._menu_bar_bubble_input_frame, textvariable = self._menu_bar_bubble_height_var)
        height_entry.configure(width = self._text_widget_width)
        height_entry.grid(column = 1, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

        continuous_choices = ['Ellipse - Stetig', 'Rechteck - Stetig']
        if choice in continuous_choices:
            exponent_label = tk.Label(self._menu_bar_bubble_input_frame, text = 'Exponent')
            exponent_label.configure(width = self._text_widget_width)
            exponent_label.grid(column = 2, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

            exponent_entry = tk.Entry(self._menu_bar_bubble_input_frame,
                                      textvariable = self._menu_bar_bubble_exponent_var)
            exponent_entry.configure(width = self._text_widget_width)
            exponent_entry.grid(column = 3, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_write_frame(self):
        if self._menu_bar_frame is None:
            return

        if self._menu_bar_write_frame is not None:
            self._menu_bar_write_frame.destroy()

        self._menu_bar_write_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_write_frame.grid(column = 7, row = 0, sticky = 'n',
                                        **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        save_button = tk.Button(self._menu_bar_write_frame, text = 'Speichern',
                                command = self._menu_bar_write_save_button_click)
        save_button.configure(width = self._text_widget_width)
        save_button.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        delete_button = tk.Button(self._menu_bar_write_frame, text = 'Löschen',
                                  command = self._menu_bar_write_delete_button_click)
        delete_button.configure(width = self._text_widget_width)
        delete_button.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        copy_button = tk.Button(self._menu_bar_write_frame, text = 'Kopieren',
                                command = self._menu_bar_write_copy_button_click)
        copy_button.configure(width = self._text_widget_width)
        copy_button.grid(column = 0, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_frame(self):
        if self._menu_bar_frame is not None:
            self._menu_bar_frame.destroy()

        self._menu_bar_frame = tk.Frame(self.frame, bg = self.frame['bg'])
        self._menu_bar_frame.place(x = 0, y = 0)

        self._init_menu_bar_back_button()
        self._init_menu_bar_nav_frame()
        self._init_menu_bar_load_frame()
        self._init_menu_bar_filter_choice_frame()
        self._init_menu_bar_filter_input_frame()
        self._init_menu_bar_bubble_choice_frame()
        self._init_menu_bar_bubble_input_frame()
        self._init_menu_bar_write_frame()

    def drawView(self):
        self._init_menu_bar_frame()

    # Events
    def _menu_bar_nav_new_button_click(self):
        pass

    def _menu_bar_nav_delete_button_click(self):
        pass

    def _menu_bar_nav_prev_button_click(self):
        pass

    def _menu_bar_nav_next_button_click(self):
        pass

    def _menu_bar_nav_index_spinbox_change(self):
        pass

    def _menu_bar_load_local_button_click(self):
        pass

    def _menu_bar_load_database_button_click(self):
        pass

    def _menu_bar_filter_choice_combobox_changed(self, event):
        self._init_menu_bar_filter_choice_frame()
        self._init_menu_bar_filter_input_frame()

    def _menu_bar_filter_choice_apply_button_click(self):
        pass

    def _menu_bar_filter_choice_reverse_button_click(self):
        pass

    def _menu_bar_bubble_choice_combobox_changed(self, event):
        self._init_menu_bar_bubble_choice_frame()
        self._init_menu_bar_bubble_input_frame()

    def _menu_bar_bubble_choice_apply_button_click(self):
        pass

    def _menu_bar_write_save_button_click(self):
        pass

    def _menu_bar_write_delete_button_click(self):
        pass

    def _menu_bar_write_copy_button_click(self):
        pass

        # class BubbleViewTool(Tool):


#
#     # Defaults
#     _DEFAULT_MENU_BAR_WIDGET_WIDTH  = 80
#     _DEFAULT_MENU_BAR_WIDGET_HEIGHT = 30
#     _DEFAULT_MENU_BAR_FRAME_SPACING = 30
#     _DEFAULT_MARGIN_HORIZONTAL = 10
#     _DEFAULT_MARGIN_VERTICAL   = 10
#
#     def __init__(self, win, frame, config, **kwargs):
#         self._on_back_callback = kwargs.get('on_back_callback', None)
#
#         # Angezeigtes image
#         self._display_image              = None
#         self._display_image_canvas       = None
#         # Scale display image mit window
#         self._display_image_resize       = True
#         self._display_image_resize_ratio = None
#         # Photo image von display image für tkinter
#         self._display_image_photo_image  = None
#
#         # Menu bar
#         self._menu_bar_frames = []
#         self._menu_bar_width  = 0
#         self._menu_bar_height = 0
#
#         # Menu bar widgets
#         self._menu_bar_widget_width  = self._DEFAULT_MENU_BAR_WIDGET_WIDTH
#         self._menu_bar_widget_height = self._DEFAULT_MENU_BAR_WIDGET_HEIGHT
#         self._menu_bar_frame_spacing = self._DEFAULT_MENU_BAR_FRAME_SPACING
#
#         # Margins
#         self._margin_horizontal = self._DEFAULT_MARGIN_HORIZONTAL
#         self._margin_vertical   = self._DEFAULT_MARGIN_VERTICAL
#
#         self._override_attributes_with_config(config)
#
#         super().__init__(win, frame)
#
#         # Event für resizing
#         self.frame.bind('<Configure>', self._frame_configure)
#
#     def _override_attributes_with_config(self, config):
#         pass
#
#     @abstractmethod
#     def _create_menu_bar_frames_with_style(self):
#         pass
#
#     def _create_menu_bar(self):
#         for frame in self._menu_bar_frames:
#             frame.destroy()
#
#         self._menu_bar_frames = []
#         self._menu_bar_width   = 0
#         self._menu_bar_height  = 0
#
#         for frame, style in self._create_menu_bar_frames_with_style():
#             margin_horizontal = style.get('margin_horizontal', self._margin_horizontal)
#             margin_vertical   = style.get('margin_vertical',   self._margin_vertical)
#
#             x = self._menu_bar_width + margin_horizontal
#             y = margin_vertical
#
#             width  = style.get('width')
#             height = style.get('height')
#
#             self._menu_bar_width  = x + width + self._menu_bar_frame_spacing
#             self._menu_bar_height = max(self._menu_bar_height, height + y)
#
#             frame.place(x = x, y = y, width = width, height = height)
#             self._menu_bar_frames.append(frame)
#
#     @abstractmethod
#     def drawView(self):
#         pass
#
#     def _display_image_set(self, image):
#         self._display_image = image
#
#         if self._display_image is None:
#             if self._display_image_canvas is None:
#                 return
#
#             self._display_image_canvas.destroy()
#             self._display_image_canvas = None
#             return
#
#         x = self._margin_horizontal
#         y = self._margin_vertical + self._menu_bar_height
#
#         width  = image.width
#         height = image.height
#
#         if self._display_image_resize:
#             window_width  = self.win.winfo_width()
#             window_height = self.win.winfo_height()
#
#             max_width  = window_width - 2 * self._margin_horizontal
#             max_height = window_height - y - self._margin_vertical
#
#             width_ratio  = max_width  / width
#             height_ratio = max_height / height
#
#             min_ratio = min(width_ratio, height_ratio)
#
#             if min_ratio < 1:
#                 width  = round(width  * min_ratio)
#                 height = round(height * min_ratio)
#
#                 self._display_image_resize_ratio = min_ratio
#                 image = image.resize((width, height))
#
#             else:
#                 self._display_image_resize_ratio = None
#
#         self._display_image_photo_image = ImageTk.PhotoImage(image)
#
#         if self._display_image_canvas is None:
#             self._display_image_canvas = tk.Canvas(self.frame, bd = 0, highlightthickness = 0)
#
#         self._display_image_canvas.place(x = x, y = y, width = width, height = height)
#         self._display_image_canvas.create_image(0, 0, anchor = tk.NW, image = self._display_image_photo_image)
#
#     def _frame_configure(self, event):
#         if self._display_image_resize:
#             self._display_image_set(self._display_image)


# class BubbleViewTrialTool(BubbleViewTool):
#     def __init__(self, win, frame, config, trial = None, **kwargs):
#         # Erzeugter trial
#         self._trial = trial or Trial()
#         self._trial_case_index = None if self._trial.empty() else 0
#
#         # Menu bar frames
#         self._menu_bar_nav           = None
#         self._menu_bar_load          = None
#         self._menu_bar_filter_choice = None
#         self._menu_bar_filter        = None
#
#         # Variables
#         self._menu_bar_nav_index_var             = tk.StringVar(value = 'Test')
#         self._menu_bar_filter_choice             = tk.StringVar(value = '')
#         self._menu_bar_filter_box_radius_var     = tk.StringVar(value = '')
#         self._menu_bar_filter_box_iterations_var = tk.StringVar(value = '')
#
#         super().__init__(win, frame, config, **kwargs)
#
#     def _trial_case_index_set(self, index):
#         self._trial_case_index = min(max(0, index), len(self._trial) - 1)
#         self.update_view()
#
#     def _menu_bar_nav_new_button_click(self):
#         trial_case = TrialCase()
#         self._trial_case_index_set(self._trial.append(trial_case))
#
#     def _menu_bar_nav_prev_button_click(self):
#         if self._trial_case_index is not None:
#             self._trial_case_index_set(self._trial_case_index - 1)
#
#     def _menu_bar_nav_next_button_click(self):
#         if self._trial_case_index is not None:
#             self._trial_case_index_set(self._trial_case_index + 1)
#
#     def _create_menu_bar_nav_frame_with_style(self):
#         frame_width  = 2 * self._menu_bar_widget_width  + self._margin_horizontal
#         frame_height = 2 * self._menu_bar_widget_height + self._margin_vertical
#
#         frame = tk.Frame(self.frame, bg = self.frame['bg'])
#         frame_style = {
#             'width':  frame_width,
#             'height': frame_height,
#         }
#
#         back_button = tk.Button(frame, text = 'Zurück', command = self._on_back_callback)
#         new_button  = tk.Button(frame, text = 'Neu', command = self._menu_bar_nav_new_button_click)
#         prev_button = tk.Button(frame, text = '<', command = self._menu_bar_nav_prev_button_click)
#         index_label = tk.Label(frame, textvariable = self._menu_bar_nav_index_var)
#         next_button = tk.Button(frame, text = '>', command = self._menu_bar_nav_next_button_click)
#
#         prev_next_width = (frame_width - 2 * self._margin_horizontal) / 4
#         index_width     = 2 * prev_next_width
#
#         x = 0
#         y = 0
#         back_button.place(x = 0, y = 0, width = self._menu_bar_widget_width, height = self._menu_bar_widget_height)
#
#         x += self._menu_bar_widget_width + self._margin_horizontal
#         new_button.place(x = x, y = y, width = self._menu_bar_widget_width, height = self._menu_bar_widget_height)
#
#         x = 0
#         y = self._menu_bar_widget_height + self._margin_vertical
#         prev_button.place(x = x, y = y, width = prev_next_width, height = self._menu_bar_widget_height)
#
#         x += prev_next_width + self._margin_horizontal
#         index_label.place(x = x, y = y, width = index_width, height = self._menu_bar_widget_height)
#
#         x += index_width + self._margin_horizontal
#         next_button.place(x = x, y = y, width = prev_next_width, height = self._menu_bar_widget_height)
#
#         return frame, frame_style
#
#     def _menu_bar_load_local_button_click(self):
#         file = fd.askopenfilename()
#         if file:
#             try:
#                 # TODO: PIL.Image.tobytes() funktioniert nicht richtig bei PNG's (wird aber von ImageFilter benötigt)
#                 image = Image.open(file)
#                 image.save('bubble_view_temp.bmp')
#
#                 image = Image.open('bubble_view_temp.bmp')
#                 image.load()
#
#                 if os.path.exists('bubble_view_temp.bmp'):
#                     os.remove('bubble_view_temp.bmp')
#
#                 if self._trial.index_valid(self._trial_case_index):
#                     self._trial.image_set(self._trial_case_index, image, ImageMetaLocal())
#                     self._display_image_set(image)
#
#             except IOError:
#                 messagebox.showinfo('Fehler', f'Keine Bilddatei: {file}')
#
#     def _menu_bar_load_database_button_click(self):
#         pass
#
#     def _create_menu_bar_load_frame_with_style(self):
#         frame = tk.Frame(self.frame, bg = self.frame['bg'])
#         frame_style = {
#             'width': self._menu_bar_widget_width,
#             'height': 2 * self._menu_bar_widget_height + self._margin_vertical
#         }
#
#         local_button    = tk.Button(frame, text = 'Lokal', command = self._menu_bar_load_local_button_click)
#         database_button = tk.Button(frame, text = 'Datenbank', command = self._menu_bar_load_database_button_click)
#
#         local_button.place(x = 0, y = 0, width = self._menu_bar_widget_width, height = self._menu_bar_widget_height)
#         database_button.place(x = 0, y = self._menu_bar_widget_height + self._margin_vertical,
#                               width = self._menu_bar_widget_width, height = self._menu_bar_widget_height)
#
#         return frame, frame_style
#
#     def _menu_bar_filter_combobox_changed(self, event):
#         pass
#
#     def _create_menu_bar_filter_choice_frame_with_style(self):
#         frame = tk.Frame(self.frame, bg = self.frame['bg'])
#         frame_style = {
#             'width':  self._menu_bar_widget_width * 2.5,
#             'height': self._menu_bar_widget_height
#         }
#
#         filter_label    = tk.Label(frame, text = 'Filter')
#         filter_combobox = tkk.Combobox(frame, textvariable = self._menu_bar_filter_choice,
#                                        values = ['Box Blur', 'Gaussian Blur', 'Pixelate'],
#                                        state = 'readonly')
#
#         filter_combobox.bind('<<ComboboxSelected>>', self._menu_bar_filter_combobox_changed)
#
#         x = 0
#         y = 0
#         filter_label.place(x = x, y = y, width = self._menu_bar_widget_width, height = self._menu_bar_widget_height)
#
#         x += self._menu_bar_widget_width
#         filter_combobox.place(x = x, y = y,
#                               width = self._menu_bar_widget_width * 1.5, height = self._menu_bar_widget_height)
#
#         return frame, frame_style
#
#     def _create_menu_bar_filter_box_frame_with_style(self):
#         frame = tk.Frame(self.frame, bg = self.frame['bg'])
#         frame_style = {
#             'width':  self._menu_bar_widget_width * 2,
#             'height': self._menu_bar_widget_height * 2 + self._margin_vertical,
#         }
#
#         radius_label = tk.Label(frame, text = 'Radius')
#         radius_entry = tk.Entry(frame, textvariable = self._menu_bar_filter_box_radius_var)
#
#         iterations_label = tk.Label(frame, text = 'Iterationen')
#         iterations_entry = tk.Entry(frame, textvariable = self._menu_bar_filter_box_iterations_var)
#
#         x = 0
#         y = 0
#         radius_label.place(x = x, y = y, width = self._menu_bar_widget_width, height = self._menu_bar_widget_height)
#
#         x += self._menu_bar_widget_width
#         radius_entry.place(x = x, y = y, width = self._menu_bar_widget_width, height = self._menu_bar_widget_height)
#
#         x = 0
#         y += self._menu_bar_widget_height + self._margin_vertical
#         iterations_label.place(x = x, y = y, width = self._menu_bar_widget_width, height = self._menu_bar_widget_height)
#
#         x += self._menu_bar_widget_width
#         iterations_entry.place(x = x, y = y, width = self._menu_bar_widget_width, height = self._menu_bar_widget_height)
#
#         return frame, frame_style
#
#     def _create_menu_bar_frames_with_style(self):
#         frames_with_style = []
#
#         menu_bar_nav = self._create_menu_bar_nav_frame_with_style()
#         menu_bar_load = self._create_menu_bar_load_frame_with_style()
#         menu_bar_filter_choice = self._create_menu_bar_filter_choice_frame_with_style()
#
#         menu_bar_filter = None
#         if self._menu_bar_filter_choice == 'Box Blur':
#             menu_bar_filter = self._create_menu_bar_filter_box_frame_with_style()
#         elif self._menu_bar_filter_choice == 'Gaussian Blur':
#             menu_bar_filter = self._create_menu_bar_filter_gauss_frame_with_style()
#         elif self._menu_bar_filter_choice == 'Pixelate':
#             menu_bar_filter = self._create_menu_bar_filter_pixelate_frame_with_style()
#
#         frames_with_style.extend([menu_bar_nav, menu_bar_load, menu_bar_filter_choice])
#
#         if menu_bar_filter is not None:
#             frames_with_style.append(menu_bar_filter)
#
#         self._menu_bar_nav  = menu_bar_nav[0]
#         self._menu_bar_load = menu_bar_load[0]
#         self._menu_bar_filter_choice = menu_bar_filter_choice[0]
#         self._menu_bar_filter = menu_bar_filter[0] if menu_bar_filter is not None else None
#
#         return frames_with_style
#
#     def update_view(self):
#         if self._trial.index_valid(self._trial_case_index):
#             self._menu_bar_nav_index_var.set(f'{self._trial_case_index + 1} / {len(self._trial)}')
#         else:
#             self._menu_bar_nav_index_var.set('- / -')
#
#
#     def drawView(self):
#         self._menu_bar_nav_index_var.set('- / -')
#         self._create_menu_bar()
#         self.update_view()


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
        self.analyse_render_click_outline_with = 2
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
