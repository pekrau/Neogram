"Various utility functions."

import constants
import itertools


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


def get_unique(id="id"):
    count = itertools.count(1)
    while True:
        yield f"{id}{next(count)}"


unique_id = get_unique()


if __name__ == "__main__":
    print(next(unique_id))
    print(next(unique_id))
    print(next(unique_id))
