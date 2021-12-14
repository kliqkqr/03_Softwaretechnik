import rust

from timeit import default_timer as timer

from PIL import Image, ImageFilter

SOURCE = r'C:\OneDrive\Code\03_Softwaretechnik\Codebase\ImageFilter\source\geo.jpg'
TARGET = r'C:\OneDrive\Code\03_Softwaretechnik\Codebase\ImageFilter\target\geo.tiff'
APP    = r'C:\OneDrive\Code\03_Softwaretechnik\Codebase\Rust\swtp\target\release\swtp.exe'


def benchmark(f):
    start  = timer()
    result = f()
    time   = timer() - start
    return result, time


def blur_box_pil(source, radius, iterations):
    target = source
    for _ in range(iterations):
        target = target.filter(ImageFilter.BoxBlur(radius))

    return target


def blur_box(source, radius, iterations, threads):
    width, height = source.size
    buffer        = source.tobytes()

    buffer = rust.blur_box(width, height, buffer, radius, iterations, threads)
    target = Image.frombuffer('RGB', (width, height), buffer)

    return target


def pixelate_square_pil(source, diameter):
    width, height = source.size

    target = source.resize((width // diameter, height // diameter), resample = Image.BILINEAR)
    target = target.resize((width, height), resample = Image.NEAREST)

    return target


def pixelate_square(source, diameter, threads):
    width, height = source.size
    buffer        = source.tobytes()

    buffer = rust.pixelate_square(width, height, buffer, diameter, threads)
    target = Image.frombuffer('RGB', (width, height), buffer)

    return target
