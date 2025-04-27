"Various utility functions."

import constants


def N(x):
    "Return a compact string representation of the numerical value."
    assert isinstance(x, (int, float))
    if (x < 0.0 and -x % 1.0 < constants.PRECISION) or x % 1.0 < constants.PRECISION:
        return f"{round(x):d}"
    else:
        return f"{x:.3f}"


def get_text_length(text, size, family, italic=False, bold=False):
    """Compute length of string given the size in points (pt).
    Uses empirically based measurements.
    """
    assert family in ("sans", "serif", "monospace")
    font = constants.CHARACTER_WIDTHS[family]
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
        total += font.get(c, font["default"])[key]
    return total * size / 100
