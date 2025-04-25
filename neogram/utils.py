"Neogram: Various utility functions."

from icecream import ic

import collections
import math

import constants


PRECISION = 0.0005


def N(x):
    "Return a compact representation of the numerical value."
    assert isinstance(x, (int, float))
    if (x < 0.0 and -x % 1.0 < PRECISION) or x % 1.0 < PRECISION:
        return f"{round(x):d}"
    else:
        return f"{x:.3f}"


Tick = collections.namedtuple("Tick", ["user", "x"])


class Dimension:
    "Store min/max and calculate base/first/last and ticks for the span."

    def __init__(self, offset=0, width=100):
        self.min = None
        self.max = None
        self.offset = offset
        self.width = width

    @property
    def span(self):
        return (self.min, self.max)

    @span.setter
    def span(self, value):
        if self.min is None:
            if isinstance(value, (tuple, list)):
                self.min = min(*value)
            else:
                self.min = value
        elif isinstance(value, (tuple, list)):
            self.min = min(self.min, *value)
        else:
            self.min = min(self.min, value)
        if self.max is None:
            if isinstance(value, (tuple, list)):
                self.max = max(*value)
            else:
                self.max = value
        elif isinstance(value, (tuple, list)):
            self.max = max(self.max, *value)
        else:
            self.max = max(self.max, value)

    def get_ticks(self, approx=5):
        "Return tick positions for the current span."
        span = self.max - self.min
        self.base = 10 ** round(math.log10(round(span / approx)) - 0.5)
        for step in [2 * self.base, 5 * self.base]:
            if approx * step > span:
                break
            self.base = step
        self.first = round(self.min / self.base - 0.5) * self.base
        self.last = round(self.max / self.base + 0.5) * self.base
        self.scale = (self.width - self.offset) / (self.last - self.first)
        num = 0
        result = []
        while True:
            value = self.first + num * self.base
            if value > self.last:
                break
            result.append(Tick(user=value, x=self.get_x(value)))
            num += 1
        return result

    def get_x(self, user):
        "Convert user coordinate to pixel coordinate."
        return self.offset + self.scale * (user - self.first)

    def get_width(self, begin, end):
        "Convert user width to pixel width."
        return self.scale * abs(end - begin)


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
    d = Dimension()
    d.span = -18.9
    d.span = 88.2
    d.offset = 20
    ic(d.span, d.get_ticks(5), d.base)
    d = Dimension()
    d.span = [-13800000000, 0]
    d.offset = 10
    ic(d.span, d.get_ticks(5), d.base)
