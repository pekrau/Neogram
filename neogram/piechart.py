"Pie chart."

__all__ = ["Piechart", "Slice"]


from color import Color, Palette
from diagram import *
from degrees import *
from path import *
import style as style_module
from utils import N


class Piechart(Diagram):
    "Pie chart displaying slices."

    DEFAULT_SIZE = 200.0

    def __init__(
        self,
        entries=None,
        style=None,
        id=None,
        title=None,
        total=None,
    ):
        super().__init__(entries=entries, style=style, id=id, title=title)
        assert total is None or isinstance(total, (int, float))

        self.total = total
        self.start = Degrees(self.style["start"])
        self.style.set_default("size", self.DEFAULT_SIZE)
        width = self.style["size"] + 2 * self.style["padding"]
        if self.style["stroke"] and self.style["stroke_width"]:
            width += self.style["stroke_width"]
        self.style.set_default("width", width)

    def check_entry(self, entry):
        if not isinstance(entry, Slice):
            raise ValueError("entry is not a Slice instance")

    def svg(self):
        "Return the SVG minixml element for the diagram content."
        diagram = super().svg()

        if self.entries:
            total = sum([s.value for s in self.entries])
            if self.total:
                total = max(total, self.total)
        else:
            total = self.total
        stop = self.start - Degrees(90) if self.start else Degrees(-90)

        palette = self.style["palette"]
        if palette:
            colors = palette.cycle()
        else:
            colors = None

        # Create pie with slices.
        radius = self.style["size"] / 2
        x = radius + self.style["padding"]
        y = self.height + x

        diagram += (pie := Element("g", transform=f"translate({N(x)}, {N(y)})"))
        pie += Element("circle", r=N(radius))

        with self.style:
            pie += (slices := Element("g"))
            self.style.set_svg_attribute(slices, "stroke")
            self.style.set_svg_attribute(slices, "stroke_width")

            for slice in self.entries:
                slice.fraction = slice.value / total
                slice.start = stop
                stop = slice.start + slice.fraction * Degrees(360)
                p0 = Vector2.from_polar(radius, float(slice.start))
                p1 = Vector2.from_polar(radius, float(stop))
                lof = 1 if stop - slice.start > Degrees(180) else 0
                slices += (
                    path := Element(
                        "path",
                        d=Path(Vector2(0, 0))
                        .L(p0)
                        .A(radius, radius, 0, lof, 1, p1)
                        .Z(),
                    )
                )
                with self.style:
                    self.style.update(slice.style)
                    self.style.set_svg_attribute(path, "stroke")
                    self.style.set_svg_attribute(path, "stroke_width")
                    if "fill" in self.style:  # If specifically defined for this slice.
                        self.style.set_svg_attribute(path, "fill")
                        slice.color = self.style["fill"]
                    elif colors:  # Otherwise use palette, if defined (default).
                        slice.color = next(colors)
                        path["fill"] = str(slice.color)
                    else:
                        slice.color = self.style["fill"]

        # Add labels.
        with self.style:
            labels = Element("g")
            pie += labels
            self.style.set_svg_attribute(labels, "stroke")
            self.style.set_svg_attribute(labels, "stroke_width")
            self.style.set_svg_attribute(labels, "label.fill")
            self.style.set_svg_text_attributes(labels, "label")

            for slice in self.entries:
                if slice.label:
                    middle = slice.start + 0.5 * slice.fraction * Degrees(360)
                    pos = Vector2.from_polar(0.7 * radius, float(middle))
                    labels += (
                        label := Element("text", slice.label, x=N(pos.x), y=N(pos.y))
                    )
                    with self.style:
                        self.style.update(slice.style)
                        self.style.set_svg_text_attributes(label, "label")
                        # Check if label fill specifically defined for this slice.
                        if (
                            self.style["label.contrast"]
                            and "label.fill" not in self.style
                        ):
                            self.style.set_svg_attribute(
                                label, "fill", value=slice.color.best_contrast()
                            )

        self.origin = Vector2(0, 0)
        self.extent = Vector2(self.style["width"], self.style["width"] + self.height)

        return diagram


class Slice(Entity):
    "A slice in a pie chart."

    def __init__(self, value, label=None, style=None):
        assert isinstance(value, (int, float))
        self.value = value
        self.label = label
        self.style = style_module.stylify(style)

    def as_dict_content(self):
        result = dict(value=self.value)
        if self.label:
            result["label"] = self.label
        if self.style:
            result.update({"style": style_module.destylify(self.style)})
        return result


SCHEMA = {
    "title": "Piechart",
    "description": "Piechart with slices.",
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "style": {"$ref": "#/$defs/style"},
        "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "slice": {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "number",
                            },
                            "label": {
                                "type": "string",
                            },
                            "style": {"$ref": "#/$defs/style"},
                        },
                        "required": ["value"],
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    "required": ["entries"],
    "additionalProperties": False,
}
