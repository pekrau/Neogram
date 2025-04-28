"Various utility functions."

import constants


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
    total = 0
    for c in text:
        total += widths.get(c, widths["default"])[key]
    return total * size / 100
