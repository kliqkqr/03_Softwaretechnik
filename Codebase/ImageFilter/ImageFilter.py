import abc
import multiprocessing
import math


from Rust import Rust


# def pixelate_square(image, diameter, threads = None):
#     threads = multiprocessing.cpu_count() if threads is None else threads
#
#     return Rust.pixelate_square(image, diameter, threads)
#
#
# def blur_box(image, radius, iterations, threads = None):
#     threads = multiprocessing.cpu_count() if threads is None else threads
#
#     return Rust.blur_box(image, radius, iterations, threads)
#
#
# def blur_gaussian_radius(radius, iterations):
#     sigma    = radius ** 2 / iterations
#     # Box length
#     length   = math.sqrt(12 * sigma + 1)
#     # Integer part of box radius
#     i_radius = math.floor((length - 1) / 2)
#     # Fractional part of box radius
#     f_radius = (2 * i_radius + 1) * (i_radius * (i_radius + 1) - 3 * sigma)
#     f_radius /= 6 * (sigma - (i_radius + 1) ** 2)
#
#     radius = int(i_radius + f_radius)
#     return radius
#
#
# def blur_gaussian(image, radius = None, iterations = None, threads = None):
#     # https://www.mia.uni-saarland.de/Publications/gwosdek-ssvm11.pdf
#
#     radius     = 2 if radius     is None else radius
#     iterations = 3 if iterations is None else iterations
#     radius     = blur_gaussian_radius(radius, iterations)
#
#     return blur_box(image, radius, iterations, threads)


class ImageFilter(abc.ABC):
    @abc.abstractmethod
    def apply(self, image):
        pass

    @abc.abstractmethod
    def name(self):
        pass

    @abc.abstractmethod
    def copy(self):
        pass


class BoxBlur(ImageFilter):
    def __init__(self, radius, iterations, threads = None):
        self.radius     = radius
        self.iterations = iterations
        self.threads    = threads if threads is not None else multiprocessing.cpu_count()

    def apply(self, image):
        threads = multiprocessing.cpu_count() if self.threads is None else self.threads
        return Rust.blur_box(image, self.radius, self.iterations, threads)

    def name(self):
        return 'BoxBlur'

    def copy(self):
        return BoxBlur(self.radius, self.iterations, self.threads)


class GaussianBlur(ImageFilter):
    def __init__(self, radius, iterations = None, threads = None):
        self.radius     = radius
        self.iterations = iterations if iterations is not None else 3
        self.threads    = threads    if threads    is not None else multiprocessing.cpu_count()

    def box_radius(self):
        # https://www.mia.uni-saarland.de/Publications/gwosdek-ssvm11.pdf
        sigma    = self.radius ** 2 / self.iterations
        # Box length
        length   = math.sqrt(12 * sigma + 1)
        # Integer part of box radius
        i_radius = math.floor((length - 1) / 2)
        # Fractional part of box radius
        f_radius = (2 * i_radius + 1) * (i_radius * (i_radius + 1) - 3 * sigma)
        f_radius /= 6 * (sigma - (i_radius + 1) ** 2)

        radius = int(i_radius + f_radius)
        return radius

    def apply(self, image):
        box_radius = self.box_radius()
        box_blur_filter = BoxBlur(box_radius, self.iterations, self.threads)
        return box_blur_filter.apply(image)

    def name(self):
        return 'GaussianBlur'

    def copy(self):
        return GaussianBlur(self.radius, self.iterations, self.threads)


class PixelateSquare(ImageFilter):
    def __init__(self, diameter, threads = None):
        self.diameter = diameter
        self.threads  = threads if threads is not None else multiprocessing.cpu_count()

    def apply(self, image):
        return Rust.pixelate_square(image, self.diameter, self.threads)

    def name(self):
        return 'PixelateSquare'

    def copy(self):
        return PixelateSquare(self.diameter, self.threads)