"Various utility functions."

import copy

import constants


def join(base, *others):
    "Join the dictionaries into a new one."
    result = copy.deepcopy(base)
    for other in others:
        result.update(copy.deepcopy(other))
    return result


def N(x):
    "Return a compact string representation of the numerical value."
    assert isinstance(x, (int, float))
    if (x < 0.0 and -x % 1.0 < constants.PRECISION) or x % 1.0 < constants.PRECISION:
        return f"{round(x):d}"
    else:
        return f"{x:.3f}"


def get_text_length(text, font, size, italic=False, bold=False):
    """Compute length of string given the size in points (pt).
    Uses empirically based measurements.
    """
    assert font in ("sans-serif", "serif", "monospace"), font
    widths = constants.CHARACTER_WIDTHS[font]
    if italic:
        if bold:
            key = "ib"
        else:
            key = "i"
    elif bold:
        key = "b"
    else:
        key = "n"
    total = sum([widths.get(c, widths["default"])[key] for c in text])
    return total * size / 100
