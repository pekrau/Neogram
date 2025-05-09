"Pie chart with slices."

__all__ = ["Piechart", "Slice"]

import itertools

from degrees import *
from diagram import *
from path import *


class Piechart(Diagram):
    "Pie chart containing slices."

    DEFAULT_START = Degrees(-90)
    DEFAULT_PALETTE = ["#4c78a8", "#9ecae9", "#f58518"]

    SCHEMA = {
        "title": "Pie chart with slices.",
        "type": "object",
        "properties": {
            "title": {
                "title": "Title of pie chart.",
                "type": "string",
            },
            "width": {
                "title": "Width of chart, in pixels.",
                "type": "number",
                "default": constants.DEFAULT_WIDTH,
                "exclusiveMinimum": 0,
            },
            "total": {
                "title": "Total value to relate slice values to.",
                "type": "number",
                "exclusiveMinimum": 0,
            },
            "start": {
                "title": "Starting point for first slice; in degrees from top.",
                "type": "number",
            },
            "entries": {
                "title": "Entries (slices) in the pie chart.",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "slice": {
                            "title": "Slice representing a value.",
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "value": {"type": "number"},
                            },
                            "required": ["label", "value"],
                            "additionalProperties": False,
                        },
                        "additionalProperties": False,
                    },
                },
            },
        },
        "additionalProperties": False,
    }

    def __init__(
        self,
        title=None,
        width=None,
        entries=None,
        total=None,
        start=None,
    ):
        super().__init__(title=title, width=width, entries=entries)
        assert total is None or isinstance(total, (int, float))
        assert start is None or isinstance(start, (int, float))

        self.total = total
        self.start = start

    def check_entry(self, entry):
        return isinstance(entry, Slice)

    def build(self):
        "Create and set the 'svg' and 'height' attributes."
        super().build()

        if self.total is None:
            total = sum([e.value for e in self.entries])
        else:
            total = self.total
        colors = itertools.cycle(self.DEFAULT_PALETTE)
        radius = (constants.DEFAULT_WIDTH - constants.DEFAULT_PADDING) / 2
        x = radius + constants.DEFAULT_PADDING
        y = self.height + radius + constants.DEFAULT_PADDING
        self.height += 2 * (radius + constants.DEFAULT_PADDING)

        self.svg += (pie := Element("g", transform=f"translate({N(x)}, {N(y)})"))
        pie += Element("circle", r=N(radius))

        # Add slices.
        pie += (slices := Element("g"))
        slices["stroke"] = "black"
        slices["stroke-width"] = 1
        if self.start is None:
            stop = self.DEFAULT_START
        else:
            stop = Degrees(self.start) + self.DEFAULT_START
        for entry in self.entries:
            entry.fraction = entry.value / total
            entry.start = stop
            stop = entry.start + entry.fraction * Degrees(360)
            p0 = Vector2.from_polar(radius, float(entry.start))
            p1 = Vector2.from_polar(radius, float(stop))
            lof = 1 if stop - entry.start > Degrees(180) else 0
            slices += (
                path := Element(
                    "path",
                    d=Path(Vector2(0, 0))
                    .L(p0)
                    .A(radius, radius, 0, lof, 1, p1)
                    .Z(),
                )
            )
            path["fill"] = next(colors)

        # Add labels on top of slices.
        pie += (labels := Element("g"))
        labels["stroke"] = "none"
        labels["fill"] = "black"
        labels["text-anchor"] = "middle"
        for entry in self.entries:
            middle = entry.start + 0.5 * entry.fraction * Degrees(360)
            pos = Vector2.from_polar(0.7 * radius, float(middle))
            labels += Element("text", entry.label, x=N(pos.x), y=N(pos.y))

    def data_as_dict(self):
        result = super().data_as_dict()
        result["entries"] = [e.as_dict() for e in self.entries]
        if self.total is not None:
            result["total"] = self.total 
        if self.start is not None:
            result["start"] = self.start
        return result


class Slice(Entity):
    "A slice in a pie chart."

    def __init__(self, label, value):
        assert isinstance(value, (int, float))
        assert isinstance(label, str)

        self.value = value
        self.label = label

    def data_as_dict(self):
        return {"label": self.label, "value": self.value}


register(Piechart)
register(Slice)


if __name__ == "__main__":
    pass
