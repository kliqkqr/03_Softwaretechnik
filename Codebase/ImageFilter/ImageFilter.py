import multiprocessing
import math

from PIL import Image


from Rust import Rust


def pixelate_square(image, diameter, threads = None):
    threads = multiprocessing.cpu_count() if threads is None else threads

    return Rust.pixelate_square(image, diameter, threads)


def blur_box(image, radius, iterations, threads = None):
    threads = multiprocessing.cpu_count() if threads is None else threads

    return Rust.blur_box(image, radius, iterations, threads)


def blur_gaussian(image, radius = None, iterations = None, threads = None):
    # https://www.mia.uni-saarland.de/Publications/gwosdek-ssvm11.pdf

    radius     = 2 if radius     is None else radius
    iterations = 3 if iterations is None else iterations

    sigma    = radius ** 2 / iterations
    # Box length
    length   = math.sqrt(12 * sigma + 1)
    # Integer part of box radius
    i_radius = math.floor((length - 1) / 2)
    # Fractional part of box radius
    f_radius = (2 * i_radius + 1) * (i_radius * (i_radius + 1) - 3 * sigma)
    f_radius /= 6 * (sigma - (i_radius + 1) ** 2)

    radius = int(i_radius + f_radius)

    return blur_box(image, radius, iterations, threads)