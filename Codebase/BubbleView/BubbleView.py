import tkinter     as tk
import tkinter.ttk as tkk
import os
import math
import json

from timeit  import default_timer as timer
from PIL     import Image, ImageTk, ImageDraw, ImageColor
from tkinter import filedialog as fd, messagebox

import database

from Rust import Rust
from ImageFilter import ImageFilter
from Tool import Tool


# BUGS
# can't add new images after deleting when no images
# load last filter when editing
# load bubble when editing


_TRIAL_CACHE = {}
_STUDY_CACHE = {}


class Bubble:
    _SHAPE_ELLIPSE   = 'ellipse'
    _SHAPE_RECTANGLE = 'rectangle'

    def __init__(self, width, height, exponent, shape):
        self._width    = width
        self._height   = height
        self._exponent = exponent
        self._shape    = shape

    @staticmethod
    def DiscreteEllipse(width, height):
        return Bubble(width, height, None, Bubble._SHAPE_ELLIPSE)

    @staticmethod
    def DiscreteRectangle(width, height):
        return Bubble(width, height, None, Bubble._SHAPE_RECTANGLE)

    @staticmethod
    def ContinuousEllipse(width, height, exponent):
        return Bubble(width, height, exponent, Bubble._SHAPE_ELLIPSE)

    @staticmethod
    def ContinuousRectangle(width, height, exponent):
        return Bubble(width, height, exponent, Bubble._SHAPE_RECTANGLE)

    # background = filterd_image    foreground = unfiltered_image
    def apply(self, background, foreground, x, y):
        left = x - self._width  // 2
        top  = y - self._height // 2

        if self._shape == self._SHAPE_ELLIPSE:
            if self._exponent is None:
                return Rust.bubble_ellipse(background, foreground, left, top, self._width, self._height)

            return Rust.bubble_power_ellipse_interpolation(background, foreground, left, top, self._width, self._height, self._exponent)

        elif self._shape == self._SHAPE_RECTANGLE:
            if self._exponent is None:
                return Rust.bubble_rectangle(background, foreground, left, top, self._width, self._height)

            return Rust.bubble_power_rectangle_interpolation(background, foreground, left, top, self._width, self._height, self._exponent)

        return None

    def to_json(self):
        return f'{{ "shape": "{self._shape}", "width": {self._width}, "height": {self._height}, "exponent": {self._exponent} }}'


class TrialCase:
    def __init__(self, image = None, image_filters = None, bubble = None):
        self._image         = image
        self._image_filters = [] if image_filters is None else image_filters
        self._bubble        = bubble

    def image_get(self):
        return self._image

    def image_set(self, image):
        self._image = image

    def image_filters_append(self, image_filter):
        self._image_filters.append(image_filter)

    def image_filters_pop(self):
        if len(self._image_filters) != 0:
            return self._image_filters.pop()

        return False

    def image_filters_clear(self):
        self._image_filters = []

    def image_filters_apply_all(self):
        image = self._image
        for image_filter in self._image_filters:
            image = image_filter.apply(image)

        return image

    def bubble_get(self):
        return self._bubble

    def bubble_set(self, bubble):
        self._bubble = bubble

    def filters_to_json(self):
        filters_json = [f.to_json() for f in self._image_filters]

        return f'[{", ".join(filters_json)}]'

    def bubble_to_json(self):
        if self._bubble is None:
            return "null"

        return self._bubble.to_json()


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

    def index_max(self):
        return len(self._cases) - 1

    def image_get(self, index):
        return self._cases[index].image_get()

    def image_set(self, index, image):
        self._cases[index].image_set(image)

    def empty(self):
        return len(self._cases) == 0

    def insert(self, index, case):
        if self.index_valid(index):
            self._cases.insert(index, case)
            return True

        if index == len(self):
            self.append(case)
            return True

        print(f'{index=} {len(self)=}')

        return False

    def remove(self, index):
        if self.index_valid(index):
            self._cases.pop(index)
            return True

        return False

    def image_filter_append(self, index, image_filter):
        if self.index_valid(index):
            self._cases[index].image_filters_append(image_filter)
            return True

        return False

    def image_filter_pop(self, index):
        if self.index_valid(index) and len(self) != 0:
            return self._cases[index].image_filters_pop()

        return None

    def image_filter_clear(self, index):
        if self.index_valid(index):
            self._cases[index].image_filters_clear()
            return True

        return False

    def image_filter_apply_all(self, index):
        if self.index_valid(index):
            case = self._cases[index]
            return case.image_filters_apply_all()

        return None

    def bubble_get(self, index):
        if self.index_valid(index):
            return self._cases[index].bubble_get()

        return None

    def bubble_set(self, index, bubble):
        if self.index_valid(index):
            self._cases[index].bubble_set(bubble)
            return True

        return False

    def _database_meta_data(self, trial_name, case_index):
        trial_id = self._get_next_trial_id()
        image_id = case_index
        study_id = 0

        return f'{{ "trial_id": {trial_id}, "trial_name": "{trial_name}", "image_id": {image_id}, "study_id": {study_id} }}'

    def _get_next_trial_id(self):
        max_trial_id = 0

        for case in database.getBubbleView():
            geometry = case[6]
            geometry_json = json.loads(geometry)

            meta = geometry_json['meta']
            trial_id = int(meta['trial_id'])

            max_trial_id = max(trial_id, max_trial_id)

        return max_trial_id

    def save_to_database(self, name):
        for index, case in enumerate(self._cases):
            image_path = 'temp_trial_case_image.bmp'
            image_file = open(image_path, 'wb')
            image = case.image_get()
            image.save(image_file, 'BMP')

            # wait until file is written
            image_file.flush()
            os.fsync(image_file)
            image_file.close()

            image_filters_json = case.filters_to_json()
            bubble_json        = case.bubble_to_json()
            meta_json          = self._database_meta_data(name, index)

            geometry_json = f'{{ "meta": {meta_json}, "bubble": {bubble_json} }}'

            print(f'filter:\n{image_filters_json}')
            print(f'geometry:\n{geometry_json}')

            # database.saveBubbleView(image_path, [], [], [], image_filters_json, geometry_json)

            os.remove(image_path)

    def save_to_cache(self, name):
        _TRIAL_CACHE[name] = self

    def __len__(self):
        return len(self._cases)


class Study:
    def __init__(self, trial, clicks, motions):
        self._trial   = trial
        self._clicks  = clicks
        self._motions = motions


class BubbleViewTool(Tool):
    _DEFAULT_PADDING_HORIZONTAL             = 5
    _DEFAULT_PADDING_VERTICAL               = 5
    _DEFAULT_MARGIN_HORIZONTAL              = 3
    _DEFAULT_MARGIN_VERTICAL                = 3
    _DEFAULT_HORIZONTAL_FRAME_MARGIN_SCALAR = 4
    _DEFAULT_VERTICAL_FRAME_MARGIN_SCALAR   = 2
    _DEFAULT_TEXT_WIDGET_WIDTH              = 8

    def __init__(self, win, frame, config):
        self.config = config

        # gui style
        self._padding_horizontal             = self._DEFAULT_PADDING_HORIZONTAL
        self._padding_vertical               = self._DEFAULT_PADDING_VERTICAL
        self._margin_horizontal              = self._DEFAULT_MARGIN_HORIZONTAL
        self._margin_vertical                = self._DEFAULT_MARGIN_VERTICAL
        self._horizontal_frame_margin_scalar = self._DEFAULT_HORIZONTAL_FRAME_MARGIN_SCALAR
        self._vertical_frame_margin_scalar   = self._DEFAULT_VERTICAL_FRAME_MARGIN_SCALAR
        self._text_widget_width              = self._DEFAULT_TEXT_WIDGET_WIDTH

        super().__init__(win, frame)

    def drawView(self):
        pass

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


class BubbleViewSelectTool(BubbleViewTool):
    def __init__(self, win, frame, config, **kwargs):
        self._on_back_callback = kwargs.get('on_back_callback', None)

        # frames
        self._back_frame  = None
        self._trial_frame = None

        # vars
        self._trial_select_var = tk.StringVar(value = '')

        super().__init__(win, frame, config)

    @staticmethod
    def _all_trial_choices():
        return [name for name in _TRIAL_CACHE]

    def _init_back_frame(self):
        self._back_frame = tk.Frame(self.frame, bg = self.frame['bg'])
        self._back_frame.grid(column = 0, row = 0, sticky = 'w',
                              **self._margin_kwargs(1, self._vertical_frame_margin_scalar))

        self._back_button = tk.Button(self._back_frame, text = 'Zurück', command = self._on_back_callback)
        self._back_button.configure(width = self._text_widget_width)
        self._back_button.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_trial_frame(self):
        self._trial_frame = tk.Frame(self.frame, bg = self.frame['bg'])
        self._trial_frame.grid(column = 0, row = 1, sticky = 'w',
                               **self._margin_kwargs(1, self._vertical_frame_margin_scalar))

        choices = self._all_trial_choices()

        select_trial_combobox = tkk.Combobox(self._trial_frame, textvariable = self._trial_select_var,
                                             values = choices,
                                             state = 'readonly')
        select_trial_combobox.configure(width = self._text_widget_width * 3)
        select_trial_combobox.grid(column = 0, row = 0, columnspan = 2, **self._padding_kwargs(), **self._margin_kwargs())

        new_trial_button = tk.Button(self._trial_frame, text = 'Neu', command = self._trial_new_button_click)
        new_trial_button.configure(width = self._text_widget_width)
        new_trial_button.grid(column = 0, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

        edit_trial_button = tk.Button(self._trial_frame, text = 'Edit', command = self._trial_edit_button_click)
        edit_trial_button.configure(width = self._text_widget_width)
        edit_trial_button.grid(column = 1, row = 1, **self._padding_kwargs(), **self._margin_kwargs())

        study_trial_button = tk.Button(self._trial_frame, text = 'Studie', command = self._trial_study_button_click)
        study_trial_button.configure(width = self._text_widget_width)
        study_trial_button.grid(column = 0, row = 2, **self._padding_kwargs(), **self._margin_kwargs())

        analyse_trial_button = tk.Button(self._trial_frame, text = 'Analyse', command = self._trial_analyse_button_click)
        analyse_trial_button.configure(width = self._text_widget_width)
        analyse_trial_button.grid(column = 1, row = 2, **self._padding_kwargs(), **self._margin_kwargs())

    def drawView(self):
        self._init_back_frame()
        self._init_trial_frame()

    # Events
    def _trial_new_button_click(self):
        for child in self.frame.winfo_children():
            child.destroy()

        def on_back_callback():
            for child in self.frame.winfo_children():
                child.destroy()

            BubbleViewSelectTool(self.win, self.frame, self.config, on_back_callback = self._on_back_callback)

        BubbleViewTrialTool(self.win, self.frame, self.config, on_back_callback = on_back_callback)

    def _trial_edit_button_click(self):
        trial_choice = self._trial_select_var.get()

        trial = _TRIAL_CACHE.get(trial_choice, None)

        if trial is not None:
            for child in self.frame.winfo_children():
                child.destroy()

            def on_back_callback():
                for child in self.frame.winfo_children():
                    child.destroy()

                BubbleViewSelectTool(self.win, self.frame, self.config, on_back_callback = self._on_back_callback)

            BubbleViewTrialTool(self.win, self.frame, self.config, trial = trial, on_back_callback = on_back_callback)

    def _trial_study_button_click(self):
        trial_choice = self._trial_select_var.get()

        trial = _TRIAL_CACHE.get(trial_choice, None)

        if trial is not None:
            for child in self.frame.winfo_children():
                child.destroy()

            def on_back_callback():
                for child in self.frame.winfo_children():
                    child.destroy()

                BubbleViewSelectTool(self.win, self.frame, self.config, on_back_callback = self._on_back_callback)

            BubbleViewStudyTool(self.win, self.frame, self.config, trial = trial, trial_key = trial_choice,
                                on_back_callback = on_back_callback)

    def _trial_analyse_button_click(self):
        trial_choice = self._trial_select_var.get()

        trial = _TRIAL_CACHE.get(trial_choice, None)

        if trial is not None:
            for child in self.frame.winfo_children():
                child.destroy()

            def on_back_callback():
                for child in self.frame.winfo_children():
                    child.destroy()

                BubbleViewSelectTool(self.win, self.frame, self.config, on_back_callback = self._on_back_callback)

            BubbleViewAnalyseTool(self.win, self.frame, self.config, trial = trial, trial_key = trial_choice,
                                  on_back_callback = on_back_callback)


class BubbleViewTrialTool(BubbleViewTool):
    def __init__(self, win, frame, config, **kwargs):
        self._on_back_callback = kwargs.get('on_back_callback', None)
        self._trial            = kwargs.get('trial', Trial())
        self._trial_case_index = None if self._trial.empty() else 0

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

        # display image widgets
        self._display_image_canvas = None

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
        self._menu_bar_write_save_var               = tk.StringVar(value = '')

        # flags
        self._display_image_resize = True

        # images
        self._display_image       = None
        self._display_image_photo = None

        # display image misc
        self._display_image_resize_ratio  = 1
        self._display_image_stacks        = {}

        # bubble
        self._bubbles = {}

        self._display_image_stacks_init()

        super().__init__(win, frame, config)

        self.frame.bind('<Configure>', self._frame_configure)

    # GUI
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

        self._menu_bar_nav_index_spinbox = tk.Spinbox(self._menu_bar_nav_frame, from_ = 1, to = max(1, len(self._trial)),
                                                      textvariable = self._menu_bar_nav_index_var,
                                                      command = self._menu_bar_nav_index_spinbox_change,
                                                      state = 'readonly')
        self._menu_bar_nav_index_spinbox.configure(width = self._text_widget_width)
        self._menu_bar_nav_index_spinbox.grid(column = 1, row = 0,
                                              **self._padding_kwargs(), **self._margin_kwargs())

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
        save_button.grid(column = 0, row = 0, sticky = 'w', **self._padding_kwargs(), **self._margin_kwargs())

        save_entry = tk.Entry(self._menu_bar_write_frame, textvariable = self._menu_bar_write_save_var)
        save_entry.configure(width = self._text_widget_width * 3)
        save_entry.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_frame(self):
        if self._menu_bar_frame is not None:
            self._menu_bar_frame.destroy()

        self._menu_bar_frame = tk.Frame(self.frame, bg = self.frame['bg'])
        self._menu_bar_frame.place(x = 0, y = 0)

        self._init_menu_bar_back_button()
        self._init_menu_bar_nav_frame()
        self._init_menu_bar_filter_choice_frame()
        self._init_menu_bar_filter_input_frame()
        self._init_menu_bar_bubble_choice_frame()
        self._init_menu_bar_bubble_input_frame()
        self._init_menu_bar_write_frame()

    def _display_image_set(self, image):
        self._display_image = image

        if self._display_image is None:
            if self._display_image_canvas is None:
                return

            self._display_image_canvas.destroy()
            self._display_image_canvas = None
            return

        x = self._margin_horizontal * self._horizontal_frame_margin_scalar
        y = self._margin_vertical + self._menu_bar_frame.winfo_height()

        width  = image.width
        height = image.height

        if self._display_image_resize:
            window_width  = self.win.winfo_width()
            window_height = self.win.winfo_height()

            max_width  = window_width - 2 * self._margin_horizontal * self._horizontal_frame_margin_scalar
            max_height = window_height - y - self._margin_vertical * 2

            width_ratio  = max_width  / width
            height_ratio = max_height / height

            min_ratio = min(width_ratio, height_ratio)

            if min_ratio < 1:
                width  = round(width  * min_ratio)
                height = round(height * min_ratio)

                self._display_image_resize_ratio = min_ratio
                image = image.resize((width, height))

            else:
                self._display_image_resize_ratio = 1

        self._display_image_photo = ImageTk.PhotoImage(image)

        if self._display_image_canvas is None:
            self._display_image_canvas = tk.Canvas(self.frame, bd = 0, highlightthickness = 0)
            self._display_image_canvas.bind('<Button-1>', self._display_image_canvas_click)

        self._display_image_canvas.place(x = x, y = y, width = width, height = height)
        self._display_image_canvas.create_image(0, 0, anchor = tk.NW, image = self._display_image_photo)

    def _load_active_trial_case(self):
        if not self._trial.index_valid(self._trial_case_index):
            self._menu_bar_nav_index_var.set('-')
            self._menu_bar_nav_index_spinbox.configure(to = 1)
            self._display_image_set(None)
            return

        self._menu_bar_nav_index_var.set(f'{self._trial_case_index + 1}')
        self._menu_bar_nav_index_spinbox.configure(to = len(self._trial))

        image = self._display_image_stacks_get_last()
        if image is None:
            image = self._trial.image_get(self._trial_case_index)

        self._display_image_set(image)

    def drawView(self):
        self._init_menu_bar_frame()
        self._load_active_trial_case()

    # Events
    def _frame_configure(self, event):
        if self._display_image_resize:
            self._display_image_set(self._display_image)

    def _menu_bar_nav_new_button_click(self):
        file = fd.askopenfilename()
        if file:
            try:
                # TODO: PIL.Image.tobytes() funktioniert nicht richtig bei PNG's (wird aber von ImageFilter benötigt)
                image = Image.open(file)
                image.save('bubble_view_temp.bmp')

                image = Image.open('bubble_view_temp.bmp')
                image.load()

                if os.path.exists('bubble_view_temp.bmp'):
                    os.remove('bubble_view_temp.bmp')

                index = len(self._trial) if self._trial_case_index is None else self._trial_case_index + 1

                if self._trial.insert(index, TrialCase(image = image)):
                    self._trial_case_index_set(index)

            except IOError:
                messagebox.showinfo('Fehler', f'Keine Bilddatei: {file}')

    def _menu_bar_nav_delete_button_click(self):
        if self._trial.remove(self._trial_case_index):
            self._load_active_trial_case()

    def _menu_bar_nav_index_spinbox_change(self):
        try:
            index = int(self._menu_bar_nav_index_var.get()) - 1
            self._trial_case_index_set(index)

        except Exception as e:
            print(f'{e=}')

    def _menu_bar_filter_choice_combobox_changed(self, event):
        self._init_menu_bar_filter_choice_frame()
        self._init_menu_bar_filter_input_frame()

    def _menu_bar_filter_choice_apply_button_click(self):
        image_filter = None
        try:
            filter_choice = self._menu_bar_filter_choice_var.get()

            if filter_choice == 'Box Blur':
                radius     = int(self._menu_bar_filter_box_radius_var.get())
                iterations = int(self._menu_bar_filter_box_iterations_var.get())

                if radius < 0 or iterations < 0:
                    raise Exception(f'Box Blur: radius={radius}; iterations={iterations};')

                image_filter = ImageFilter.BoxBlur(radius, iterations)

            elif filter_choice == 'Gaussian Blur':
                radius = int(self._menu_bar_filter_gauss_radius_var.get())

                if radius < 0:
                    raise Exception(f'Gaussian Blur: radius={radius};')

                image_filter = ImageFilter.GaussianBlur(radius)

            elif filter_choice == 'Pixelate':
                diameter = int(self._menu_bar_filter_pixelate_diameter_var.get())

                if diameter < 0:
                    raise Exception(f'Pixelate: diameter={diameter}')

                image_filter = ImageFilter.PixelateSquare(diameter)

        except Exception as e:
            tk.messagebox.showinfo(f'{e}')

        if image_filter is not None:
            self._display_image_apply_image_filter(image_filter)

    def _menu_bar_filter_choice_reverse_button_click(self):
        self._display_image_remove_last_filter()

    def _menu_bar_bubble_choice_combobox_changed(self, event):
        self._init_menu_bar_bubble_choice_frame()
        self._init_menu_bar_bubble_input_frame()

    def _menu_bar_bubble_choice_apply_button_click(self):
        # choices = ['Ellipse - Diskret', 'Ellipse - Stetig', 'Rechteck - Diskret', 'Rechteck - Stetig']
        bubble = None
        try:
            bubble_choice = self._menu_bar_bubble_choice_var.get()

            width  = int(self._menu_bar_bubble_width_var.get())
            height = int(self._menu_bar_bubble_height_var.get())

            if bubble_choice == 'Ellipse - Diskret':
                if width < 0 or height < 0:
                    raise Exception(f'Ellipse - Diskret: width={width}; height={height};')

                bubble = Bubble.DiscreteEllipse(width, height)

            elif bubble_choice == 'Rechteck - Diskret':
                if width < 0 or height < 0:
                    raise Exception(f'Rechteck - Diskret: width={width}; height={height};')

                bubble = Bubble.DiscreteRectangle(width, height)

            elif bubble_choice == 'Ellipse - Stetig':
                exponent = float(self._menu_bar_bubble_exponent_var.get())

                if width < 0 or height < 0 or exponent < 0:
                    raise Exception(f'Ellipse - Stetig: width={width}; height={height}; exponent={exponent};')

                bubble = Bubble.ContinuousEllipse(width, height, exponent)

            elif bubble_choice == 'Rechteck - Stetig':
                exponent = float(self._menu_bar_bubble_exponent_var.get())

                if width < 0 or height < 0 or exponent < 0:
                    raise Exception(f'Rechteck - Stetig: width={width}; height={height}; exponent={exponent};')

                bubble = Bubble.ContinuousRectangle(width, height, exponent)

        except Exception as e:
            tk.messagebox.showinfo(f'{e}')

        if bubble is not None and self._trial.index_valid(self._trial_case_index) is not None:
            self._bubbles[self._trial_case_index] = bubble
            self._trial.bubble_set(self._trial_case_index, bubble)

    def _menu_bar_write_save_button_click(self):
        save_name = self._menu_bar_write_save_var.get()
        # self._trial.save_to_database('name')
        self._trial.save_to_cache(save_name)

    def _display_image_canvas_click(self, event):
        if self._trial.index_valid(self._trial_case_index):
            bubble = self._bubbles.get(self._trial_case_index, None)

            if bubble is not None:
                foreground = self._trial.image_get(self._trial_case_index)
                background = self._display_image_stacks_get_last()

                if foreground is None or background is None:
                    return

                x = int(event.x / self._display_image_resize_ratio)
                y = int(event.y / self._display_image_resize_ratio)

                image = bubble.apply(background, foreground, x, y)
                self._display_image_set(image)

    # Utility
    def _trial_case_index_set(self, index):
        if index is None:
            self._trial_case_index = None
        else:
            self._trial_case_index = max(0, min(index, len(self._trial) - 1))

        self._load_active_trial_case()

    def _display_image_stacks_append(self, image):
        if not self._trial.index_valid(self._trial_case_index):
            return False

        if image is None:
            return False

        if self._trial_case_index not in self._display_image_stacks:
            self._display_image_stacks[self._trial_case_index] = []

        self._display_image_stacks[self._trial_case_index].append(image)
        return True

    def _display_image_stacks_pop(self):
        if not self._trial.index_valid(self._trial_case_index):
            return None

        if self._trial_case_index not in self._display_image_stacks:
            return None

        stack = self._display_image_stacks[self._trial_case_index]
        if len(stack) == 0:
            return None

        return stack.pop()

    def _display_image_stacks_get_last(self):
        if not self._trial.index_valid(self._trial_case_index):
            return None

        if self._trial_case_index not in self._display_image_stacks:
            return None

        stack = self._display_image_stacks[self._trial_case_index]
        if len(stack) == 0:
            return None

        return stack[-1]

    def _display_image_stacks_clear(self):
        self._display_image_stacks.pop(self._trial_case_index)

    def _display_image_stacks_init(self):
        if len(self._trial) == 0:
            return

        for index, case in enumerate(self._trial._cases):
            stack = []
            image = case._image
            print(f'{index=}')

            for image_filter in case._image_filters:
                image = image_filter.apply(image)
                stack.append(image)
                print(f'{image_filter=}')

            self._display_image_stacks[index] = stack

    def _display_image_apply_image_filter(self, image_filter):
        if not self._trial.index_valid(self._trial_case_index):
            return False

        image = self._display_image_stacks_get_last()
        if image is None:
            image = self._trial.image_get(self._trial_case_index)

        filtered_image = image_filter.apply(image)
        if self._display_image_stacks_append(filtered_image):
            self._trial.image_filter_append(self._trial_case_index, image_filter)
            self._display_image_set(filtered_image)
            return True

        return False

    def _display_image_remove_last_filter(self):
        if not self._trial.index_valid(self._trial_case_index):
            return False

        image_filter = self._display_image_stacks_pop()
        if image_filter is None:
            return False

        trial_image_filter = self._trial.image_filter_pop(self._trial_case_index)
        if trial_image_filter is None:
            message = 'Error: Image filter out of sync. Resetting image.'
            tk.messagebox.showinfo(message)

            self._trial.image_filter_clear(self._trial_case_index)
            self._display_image_stacks_clear()
            self._load_active_trial_case()

        image = self._display_image_stacks_get_last()
        if image is None:
            image = self._trial.image_get(self._trial_case_index)

        self._display_image_set(image)


class BubbleViewStudyTool(BubbleViewTool):
    def __init__(self, win, frame, config, trial, trial_key, **kwargs):
        self._trial            = trial
        self._trial_key        = trial_key
        self._on_back_callback = kwargs.get('on_back_callback', None)
        self._trial_case_index = 0 if not self._trial.empty() else None

        # widgets
        self._menu_bar_frame       = None
        self._menu_bar_back_frame  = None
        self._menu_bar_next_frame  = None
        self._menu_bar_next_button = None

        # display image widgets
        self._display_image_canvas = None

        # images
        self._source_image        = None
        self._display_image       = None
        self._display_image_photo = None

        # flags
        self._display_image_resize = True

        # display image misc
        self._display_image_resize_ratio = 1

        # misc
        self._clicks  = []
        self._motions = []
        self._motion_min_distance = 10
        self._timer   = None

        super().__init__(win, frame, config)

        self.frame.bind('<Configure>', self._frame_configure)

    # GUI
    def _init_menu_bar_back_frame(self):
        if self._menu_bar_frame is None:
            return

        self._menu_bar_back_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_back_frame.grid(column = 0, row = 0, **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        back_button = tk.Button(self._menu_bar_back_frame, text = 'Zurück', command = self._on_back_callback)
        back_button.configure(width = self._text_widget_width)
        back_button.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_next_frame(self):
        if self._menu_bar_frame is None:
            return

        self._menu_bar_next_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_next_frame.grid(column = 1, row = 0, **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        next_name = 'Weiter'
        if self._trial.index_valid(self._trial_case_index) and self._trial.index_max() <= self._trial_case_index:
            next_name = 'Fertig'

        self._menu_bar_next_button = tk.Button(self._menu_bar_next_frame, text = next_name,
                                               command = self._menu_bar_next_button_click)
        self._menu_bar_next_button.configure(width = self._text_widget_width)
        self._menu_bar_next_button.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_frame(self):
        self._menu_bar_frame = tk.Frame(self.frame, bg = self.frame['bg'])
        self._menu_bar_frame.grid(column = 0, row = 0)

        self._init_menu_bar_back_frame()
        self._init_menu_bar_next_frame()

    def _display_image_set(self, image):
        self._display_image = image

        if self._display_image is None:
            if self._display_image_canvas is None:
                return

            self._display_image_canvas.destroy()
            self._display_image_canvas = None
            return

        x = self._margin_horizontal * self._horizontal_frame_margin_scalar
        y = self._margin_vertical + self._menu_bar_frame.winfo_height()

        width  = image.width
        height = image.height

        if self._display_image_resize:
            window_width  = self.win.winfo_width()
            window_height = self.win.winfo_height()

            max_width  = window_width - 2 * self._margin_horizontal * self._horizontal_frame_margin_scalar
            max_height = window_height - y - self._margin_vertical * 2

            width_ratio  = max_width  / width
            height_ratio = max_height / height

            min_ratio = min(width_ratio, height_ratio)

            if min_ratio < 1:
                width  = round(width  * min_ratio)
                height = round(height * min_ratio)

                self._display_image_resize_ratio = min_ratio
                image = image.resize((width, height))

            else:
                self._display_image_resize_ratio = 1

        self._display_image_photo = ImageTk.PhotoImage(image)

        if self._display_image_canvas is None:
            self._display_image_canvas = tk.Canvas(self.frame, bd = 0, highlightthickness = 0)
            self._display_image_canvas.bind('<Button-1>', self._display_image_canvas_click)
            self._display_image_canvas.bind('<Motion>', self._display_image_canvas_motion)

        self._display_image_canvas.place(x = x, y = y, width = width, height = height)
        self._display_image_canvas.create_image(0, 0, anchor = tk.NW, image = self._display_image_photo)

    def drawView(self):
        self._init_menu_bar_frame()

        image = self._trial.image_filter_apply_all(self._trial_case_index)
        if image is not None:
            self._source_image = image
            self._display_image_set(image)

        self._timer = timer()
        self._motions.append([])
        self._clicks.append([])

    # Events
    def _frame_configure(self, event):
        if self._display_image_resize:
            self._display_image_set(self._display_image)

    def _menu_bar_next_button_click(self):
        self._next_image()

    def _display_image_canvas_click(self, event):
        if self._timer is None or self._trial_case_index is None:
            return

        bubble = self._trial.bubble_get(self._trial_case_index)

        if bubble is not None:
            foreground = self._trial.image_get(self._trial_case_index)
            background = self._source_image

            if foreground is None or background is None:
                return

            t = timer() - self._timer
            x = int(event.x / self._display_image_resize_ratio)
            y = int(event.y / self._display_image_resize_ratio)

            self._clicks[self._trial_case_index].append(((x, y), t))

            image = bubble.apply(background, foreground, x, y)
            self._display_image_set(image)

    def _display_image_canvas_motion(self, event):
        if self._timer is None or self._trial_case_index is None:
            return

        t = timer() - self._timer
        x = int(event.x / self._display_image_resize_ratio)
        y = int(event.y / self._display_image_resize_ratio)

        if len(self._motions[self._trial_case_index]) == 0:
            self._motions[self._trial_case_index].append(((x, y), t))
            return

        (last_x, last_y), _ = self._motions[self._trial_case_index][-1]
        dif_x = x - last_x
        dif_y = y - last_y

        if math.sqrt(dif_x ** 2 + dif_y ** 2) < self._motion_min_distance:
            return

        self._motions[self._trial_case_index].append(((x, y), t))

    # Misc
    def _next_image(self):
        if self._trial_case_index is None:
            return

        if self._trial_case_index >= self._trial.index_max():
            if len(self._trial) != len(self._clicks) or len(self._trial) != len(self._clicks):
                return

            if self._trial_key not in _STUDY_CACHE:
                _STUDY_CACHE[self._trial_key] = []

            study = Study(self._trial, self._clicks, self._motions)
            _STUDY_CACHE[self._trial_key].append(study)
            self._on_back_callback()

        self._trial_case_index += 1

        if self._trial_case_index == self._trial.index_max():
            self._menu_bar_next_button.configure(text = 'Fertig')

        image = self._trial.image_filter_apply_all(self._trial_case_index)
        self._source_image = image
        self._display_image_set(image)

        self._timer = timer()
        self._motions.append([])
        self._clicks.append([])


class BubbleViewAnalyseTool(BubbleViewTool):
    def __init__(self, win, frame, config, trial, trial_key, **kwargs):
        self._trial            = trial
        self._trial_case_index = 0 if len(trial) != 0 else None
        self._studies          = _STUDY_CACHE.get(trial_key, [])
        self._study_index      = 0
        self._trial_name       = trial_key
        self._on_back_callback = kwargs.get('on_back_callback')

        # widgets
        self._menu_bar_frame           = None
        self._menu_bar_trial_nav_frame = None
        self._menu_bar_study_nav_frame = None
        self._menu_bar_timeline_frame  = None
        self._menu_bar_timeline_scale  = None

        # vars
        self._menu_bar_trial_index_var = tk.StringVar(value = '1')
        self._menu_bar_study_index_var = tk.StringVar(value = '1')
        self._menu_bar_timeline_var    = tk.DoubleVar(value = 0)

        # display image widgets
        self._display_image_canvas = None

        # images
        self._source_image        = None
        self._display_image       = None
        self._display_image_photo = None

        # flags
        self._display_image_resize = True

        # display image misc
        self._display_image_resize_ratio = 1

        # misc
        self._menu_bar_timeline_resolution = 0.1

        # render
        self._render_motions_color = 'green'
        self._render_motions_width = 2
        self._render_clicks_fill_color = (75, 75, 75, 75)
        self._render_clicks_outline_color = 'red'
        self._render_clicks_width = 2
        self._render_heatmap_color = 'red'
        self._render_heatmap_transparency = 0.5

        # heatmap
        self._heatmap_rel_horizontal_resolution = 20
        self._heatmap_rel_vertical_resolution   = 20

        super().__init__(win, frame, config)

        self.frame.bind('<Configure>', self._frame_configure)

    def _init_menu_bar_trial_nav_frame(self):
        if self._menu_bar_frame is None:
            return

        self._menu_bar_trial_nav_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_trial_nav_frame.grid(column = 0, row = 0, sticky = 'n',
                                            **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        trial_label = tk.Label(self._menu_bar_trial_nav_frame, text = 'Versuch')
        trial_label.configure(width = self._text_widget_width)
        trial_label.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        trial_spinbox = tk.Spinbox(self._menu_bar_trial_nav_frame, from_ = 1, to = max(1, len(self._trial)),
                                   textvariable = self._menu_bar_trial_index_var,
                                   command = self._menu_bar_trial_index_spinbox_change,
                                   state = 'readonly')
        trial_spinbox.configure(width = self._text_widget_width)
        trial_spinbox.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        trial_heatmap_button = tk.Button(self._menu_bar_trial_nav_frame, text = 'Heatmap',
                                         command = self._trial_heatmap_button_click)
        trial_heatmap_button.configure(width = self._text_widget_width)
        trial_heatmap_button.grid(column = 2, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_study_nav_frame(self):
        if self._menu_bar_frame is None:
            return

        self._menu_bar_study_nav_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_study_nav_frame.grid(column = 1, row = 0, sticky = 'n',
                                            **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        study_label = tk.Label(self._menu_bar_study_nav_frame, text = 'Studie')
        study_label.configure(width = self._text_widget_width)
        study_label.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        study_spinbox = tk.Spinbox(self._menu_bar_study_nav_frame, from_ = 1, to = max(1, len(self._studies)),
                                   textvariable = self._menu_bar_study_index_var,
                                   command = self._menu_bar_study_index_spinbox_change,
                                   state = 'readonly')
        study_spinbox.configure(width = self._text_widget_width)
        study_spinbox.grid(column = 1, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

        stduy_heatmap_button = tk.Button(self._menu_bar_study_nav_frame, text = 'Heatmap',
                                         command = self._study_heatmap_button_click)
        stduy_heatmap_button.configure(width = self._text_widget_width)
        stduy_heatmap_button.grid(column = 2, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_timeline_frame(self):
        if self._menu_bar_frame is None:
            return

        self._menu_bar_timeline_frame = tk.Frame(self._menu_bar_frame, bg = self._menu_bar_frame['bg'])
        self._menu_bar_timeline_frame.grid(column = 2, row = 0,
                                           **self._margin_kwargs(self._horizontal_frame_margin_scalar))

        self._menu_bar_timeline_scale = tk.Scale(self._menu_bar_timeline_frame, from_ = 0, to = self._study_max_time(),
                                                 orient = tk.HORIZONTAL, variable = self._menu_bar_timeline_var,
                                                 command = self._menu_bar_timeline_scale_change,
                                                 showvalue = True, resolution = self._menu_bar_timeline_resolution)
        self._menu_bar_timeline_scale.configure(width = self._text_widget_width // 2,
                                                length = self._text_widget_width * 30)
        self._menu_bar_timeline_scale.grid(column = 0, row = 0, **self._padding_kwargs(), **self._margin_kwargs())

    def _init_menu_bar_frame(self):
        self._menu_bar_frame = tk.Frame(self.frame, bg = self.frame['bg'])
        self._menu_bar_frame.grid(column = 0, row = 0)

        self._init_menu_bar_trial_nav_frame()
        self._init_menu_bar_study_nav_frame()
        self._init_menu_bar_timeline_frame()

    def _display_image_set(self, image):
        self._display_image = image

        if self._display_image is None:
            if self._display_image_canvas is None:
                return

            self._display_image_canvas.destroy()
            self._display_image_canvas = None
            return

        x = self._margin_horizontal * self._horizontal_frame_margin_scalar
        y = self._margin_vertical + self._menu_bar_frame.winfo_height()

        width  = image.width
        height = image.height

        if self._display_image_resize:
            window_width  = self.win.winfo_width()
            window_height = self.win.winfo_height()

            max_width  = window_width - 2 * self._margin_horizontal * self._horizontal_frame_margin_scalar
            max_height = window_height - y - self._margin_vertical * 2

            width_ratio  = max_width  / width
            height_ratio = max_height / height

            min_ratio = min(width_ratio, height_ratio)

            if min_ratio < 1:
                width  = round(width  * min_ratio)
                height = round(height * min_ratio)

                self._display_image_resize_ratio = min_ratio
                image = image.resize((width, height))

            else:
                self._display_image_resize_ratio = 1

        self._display_image_photo = ImageTk.PhotoImage(image)

        if self._display_image_canvas is None:
            self._display_image_canvas = tk.Canvas(self.frame, bd = 0, highlightthickness = 0)

        self._display_image_canvas.place(x = x, y = y, width = width, height = height)
        self._display_image_canvas.create_image(0, 0, anchor = tk.NW, image = self._display_image_photo)

    def drawView(self):
        self._init_menu_bar_frame()

        if self._trial_case_index is not None:
            self._trial_case_index_set(0)

    # Events
    def _frame_configure(self, event):
            if self._display_image_resize:
                self._display_image_set(self._display_image)

    def _menu_bar_trial_index_spinbox_change(self):
        index = int(self._menu_bar_trial_index_var.get()) - 1
        self._trial_case_index_set(index)

    def _menu_bar_study_index_spinbox_change(self):
        index = int(self._menu_bar_study_index_var.get()) - 1
        self._study_index_set(index)

    def _menu_bar_timeline_scale_change(self, event):
        time = float(event)
        self._render_analyse_until(time)

    def _trial_heatmap_button_click(self):
        points = []
        for study in self._studies:
            points.extend([(x, y) for (x, y), _ in study._clicks[self._trial_case_index]])

        self._render_heatmap(points)

    def _study_heatmap_button_click(self):
        study  = self._studies[self._study_index]
        points = [(x, y) for (x, y), _ in study._clicks[self._trial_case_index]]

        self._render_heatmap(points)

    # Misc
    def _trial_case_index_set(self, index):
        self._trial_case_index = index

        self._source_image = self._trial.image_get(self._trial_case_index)
        self._study_index_set(0)

    def _study_index_set(self, index):
        self._study_index = index
        self._menu_bar_timeline_var.set(0)
        self._menu_bar_timeline_scale.configure(to = self._study_max_time())

        self._display_image_set(self._source_image)

    def _study_max_time(self):
        if self._trial_case_index is None:
            return 0

        if len(self._studies) <= self._study_index:
            return 0

        study = self._studies[self._study_index]

        max_time = 0
        for _, t in study._clicks[self._trial_case_index]:
            max_time = max(max_time, t)

        for _, t in study._motions[self._trial_case_index]:
            max_time = max(max_time, t)

        return max_time

    # Render
    def _render_analyse_until(self, time):
        motions = self._studies[self._study_index]._motions[self._trial_case_index]
        clicks  = self._studies[self._study_index]._clicks[self._trial_case_index]
        bubble  = self._trial.bubble_get(self._trial_case_index)

        image = self._source_image.copy()
        draw  = ImageDraw.Draw(image, 'RGBA')

        motions_until = []
        for (x, y), t in motions:
            if t > time:
                break

            x *= 1 / self._display_image_resize_ratio
            y *= 1 / self._display_image_resize_ratio

            motions_until.append((x, y))

        clicks_until = []
        for (x, y), t in clicks:
            if t > time:
                break

            x *= 1 / self._display_image_resize_ratio
            y *= 1 / self._display_image_resize_ratio

            clicks_until.append((x, y))

        draw.line(motions_until, fill = self._render_motions_color, width = self._render_motions_width)

        for x, y in clicks_until:
            left = x - (bubble._width // 2)
            top  = y - (bubble._height // 2)

            if bubble._shape == Bubble._SHAPE_ELLIPSE:
                draw.ellipse([(left, top), (left + bubble._width, top + bubble._height)],
                             fill = self._render_clicks_fill_color,
                             outline = self._render_clicks_outline_color,
                             width = self._render_clicks_width)

            if bubble._shape == Bubble._SHAPE_RECTANGLE:
                draw.rectangle([(left, top), (left + bubble._width, top + bubble._height)],
                               fill = self._render_clicks_fill_color,
                               outline = self._render_clicks_outline_color,
                               width = self._render_clicks_width)

        self._display_image_set(image)

    def _render_heatmap(self, points):
        if len(points) == 0:
            return

        rectangle_width, rectangle_height = self._display_image.size
        rectangle_hits = {}

        for i in range(self._heatmap_rel_horizontal_resolution):
            left  = i * rectangle_width
            right = (i + 1) * rectangle_width

            for j in range(self._heatmap_rel_vertical_resolution):
                top = j * rectangle_height
                bot = (j + 1) * rectangle_height

                for x, y in points:
                    if left <= x < right and top <= y < bot:
                        if (x, y) not in rectangle_hits:
                            rectangle_hits[(x, y)] = 1
                            continue

                        rectangle_hits[(x, y)] += 1

        max_hits = max(hits for _, hits in rectangle_hits.items())

        mini_heatmap = Image.new('RGBA', (self._heatmap_rel_horizontal_resolution, self._heatmap_rel_vertical_resolution), self._render_heatmap_color)

        for i in range(self._heatmap_rel_horizontal_resolution):
            for j in range(self._heatmap_rel_vertical_resolution):
                scalar = rectangle_hits.get((i, j), 0) / max_hits
                r, g, b, *_ = mini_heatmap.getpixel((i, j))
                alpha = scalar * 255 * self._render_heatmap_transparency
                print(f'{alpha=}')
                mini_heatmap.putpixel((i, j), (r, g, b, int(alpha)))

        heatmap = mini_heatmap.resize(self._display_image.size, Image.NEAREST)

        heatmap.show()

        image   = self._source_image.copy()

        for i in range(self._heatmap_rel_horizontal_resolution):
            left  = i * rectangle_width
            right = (i + 1) * rectangle_width

            for j in range(self._heatmap_rel_vertical_resolution):
                top = j * rectangle_height
                bot = (j + 1) * rectangle_height

                croped = heatmap.crop((left, top, right, bot))
                image.paste(croped, (left, top, right, bot), croped)

        image.show()