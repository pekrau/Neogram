"Dimension and Tick classes."

__all__ = ["Dimension", "Tick", "Epoch"]

import math

import collections
import enum

Tick = collections.namedtuple("Tick", ["user", "pixel"])


class Epoch(enum.StrEnum):
    ORDINAL = "ordinal"
    DATE = "Julian date"  # XXX not implemented
    DATETIME = "Julian date and time"  # XXX not implemented


class Dimension:
    "Store min/max and calculate base/first/last and ticks for the span."

    def __init__(self, offset=0, width=100):
        self.min = None
        self.max = None
        self.offset = offset
        self.width = width

    @property
    def span(self):
        "Return current min and max values."
        return (self.min, self.max)

    def update_span(self, value):
        "Update current min and max values."
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

    def update_offset(self, value):
        if isinstance(value, (tuple, list)):
            self.offset = max(self.offset, *value)
        else:
            self.offset = max(self.offset, value)

    def get_ticks(self, approx=5):
        "Return tick positions for the current span (min and max)."
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
            result.append(Tick(user=value, pixel=self.get_pixel(value)))
            num += 1
        return result

    def get_pixel(self, user):
        "Convert user coordinate to pixel coordinate."
        return self.offset + self.scale * (user - self.first)

    def get_width(self, begin, end):
        "Convert user width to pixel width."
        return self.scale * abs(end - begin)


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
