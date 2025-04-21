"Neogram: Various utility functions."

import math

import constants

def get_ticks(first, last, target=10):
    "Return the tick mark positions for the interval [first, last]."
    step = round((last - first) / target)
    base = 10 ** round(math.log10(step))
    for step in [base, 2 * base, 5 * base, 10 * base]:
        if target * step > (last - first):
            break
    for pos in range(first - step, last + step, step):
        if pos < first:
            continue
        elif pos > last:
            continue
        yield pos


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


if __name__ == "__main__":
    for t in ["test", "Per Kraulis", "Per", " ", "Kraulis"]:
        print(t, get_text_length(t, 14, "sans"))
