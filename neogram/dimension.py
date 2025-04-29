"Dimension and Tick classes."

__all__ = ["Dimension", "Tick", "Epoch"]

import collections
import enum
import itertools
import math

Tick = collections.namedtuple("Tick", ["user", "pixel", "label"], defaults=[None])


from utils import N


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

    def get_ticks(self, style):
        "Return ticks for the current span (min and max)."
        number = style["grid.number"]
        span = self.max - self.min
        self.magnitude = math.log10(span / number)
        series = []
        for magnitude in [math.floor(self.magnitude), math.ceil(self.magnitude)]:
            for base in [1, 2, 5]:
                step = base * 10**magnitude
                if self.min == 0:
                    first = 0
                else:
                    first = math.floor(self.min / step) * step
                values = []
                i = itertools.count(0)
                value = first
                while value <= self.max:
                    value = first + next(i) * step
                    values.append(value)
                while len(values) >= 2:
                    if values[-1] > self.max and (
                        values[-2] > self.max or math.isclose(values[-2], self.max)
                    ):
                        values.pop()
                    else:
                        break
                series.append((magnitude, values))
        self.magnitude, best = series[0]
        score = abs(len(best) - number)
        for magnitude, values in series[1:]:
            s = abs(len(values) - number)
            if s < score:
                self.magnitude = magnitude
                best = values
                score = s
        assert best[0] <= self.min
        assert best[1] > self.min
        assert best[-1] >= self.max
        assert best[-2] < self.max
        self.first = best[0]
        self.last = best[-1]
        self.scale = (self.width - self.offset) / (self.last - self.first)
        if style["grid.labels"]:
            step = 10**self.magnitude
            func = (lambda u: abs(u)) if style["grid.absolute"] else (lambda u: u)
            result = [
                Tick(u, self.get_pixel(u), label=N(round(func(u) / step))) for u in best
            ]
        else:
            result = [Tick(u, self.get_pixel(u)) for u in best]
        return result

    def get_pixel(self, user):
        "Convert user coordinate to pixel coordinate."
        return self.offset + self.scale * (user - self.first)

    def get_width(self, begin, end):
        "Convert user width to pixel width."
        return self.scale * abs(end - begin)


if __name__ == "__main__":
    from icecream import ic

    for x in range(1, 8):
        d = Dimension()
        d.update_span([0, x])
        numbers = [t.user for t in d.get_ticks(5)]
        ic(x, d.base, d.step, numbers)
