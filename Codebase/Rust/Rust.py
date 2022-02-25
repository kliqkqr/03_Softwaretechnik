import rust_extern

from PIL import Image


def bubble_power_ellipse_interpolation(background, foreground, left, top, width, height, exponent):
    b_width, b_height = background.size
    f_width, f_height = foreground.size
    b_bytes = background.tobytes()
    f_bytes = foreground.tobytes()

    left   = int(left)
    top    = int(top)
    width  = int(width)
    height = int(height)

    if not (width >= 0 and height >= 0):
        return None

    r_bytes = rust_extern.bubble_power_ellipse_interpolation(b_width, b_height, b_bytes,
                                                             f_width, f_height, f_bytes,
                                                             left, top, width, height,
                                                             exponent)

    if r_bytes == bytes() and b_width != 0 and b_height != 0:
        return None

    return Image.frombuffer('RGB', (b_width, b_height), r_bytes)


def bubble_power_rectangle_interpolation(background, foreground, left, top, width, height, exponent):
    b_width, b_height = background.size
    f_width, f_height = foreground.size
    b_bytes = background.tobytes()
    f_bytes = foreground.tobytes()

    left   = int(left)
    top    = int(top)
    width  = int(width)
    height = int(height)

    if not (width >= 0 and height >= 0):
        return None

    r_bytes = rust_extern.bubble_power_rectangle_interpolation(b_width, b_height, b_bytes,
                                                               f_width, f_height, f_bytes,
                                                               left, top, width, height,
                                                               exponent)

    if r_bytes == bytes() and b_width != 0 and b_height != 0:
        return None

    return Image.frombuffer('RGB', (b_width, b_height), r_bytes)


def bubble_rectangle(background, foreground, left, top, width, height):
    b_width, b_height = background.size
    f_width, f_height = foreground.size
    b_bytes = background.tobytes()
    f_bytes = foreground.tobytes()

    left   = int(left)
    top    = int(top)
    width  = int(width)
    height = int(height)

    if not (width >= 0 and height >= 0):
        return None

    r_bytes = rust_extern.bubble_rectangle(b_width, b_height, b_bytes,
                                           f_width, f_height, f_bytes,
                                           left, top, width, height)

    if r_bytes == bytes() and b_width != 0 and b_height != 0:
        return None

    return Image.frombuffer('RGB', (b_width, b_height), r_bytes)


def bubble_ellipse(background, foreground, left, top, width, height):
    b_width, b_height = background.size
    f_width, f_height = foreground.size
    b_bytes = background.tobytes()
    f_bytes = foreground.tobytes()

    left   = int(left)
    top    = int(top)
    width  = int(width)
    height = int(height)

    if not (width >= 0 and height >= 0):
        return None

    r_bytes = rust_extern.bubble_ellipse(b_width, b_height, b_bytes,
                                         f_width, f_height, f_bytes,
                                         left, top, width, height)

    if r_bytes == bytes() and b_width != 0 and b_height != 0:
        return None

    return Image.frombuffer('RGB', (b_width, b_height), r_bytes)


def pixelate_square(image, diameter, threads):
    i_width, i_height = image.size
    i_bytes = image.tobytes()

    diameter = int(diameter)
    threads  = int(threads)

    if not (diameter >= 0 and threads >= 0):
        return None

    r_bytes = rust_extern.pixelate_square(i_width, i_height, i_bytes, diameter, threads)

    if r_bytes == bytes() and i_width != 0 and i_height != 0:
        return None

    return Image.frombuffer('RGB', (i_width, i_height), r_bytes)


def blur_box(image, radius, iterations, threads):
    i_width, i_height = image.size
    i_bytes = image.tobytes()

    radius     = int(radius)
    iterations = int(iterations)
    threads    = int(threads)

    if not (radius >= 0 and iterations >= 0 and threads >= 0):
        return None

    r_bytes = rust_extern.blur_box(i_width, i_height, i_bytes, radius, iterations, threads)

    if r_bytes == bytes() and i_width != 0 and i_height != 0:
        return None

    return Image.frombuffer('RGB', (i_width, i_height), r_bytes)
