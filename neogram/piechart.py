"Pie chart."

__all__ = ["Piechart", "Slice", "Degrees"]


from color import Color, Palette
from diagram import *
from degrees import *
from path import *
from style import stylify, destylify
from utils import N


class Piechart(Diagram):
    "Pie chart displaying slices."

    DEFAULT_RADIUS = 100.0

    def __init__(
        self,
        entries=None,
        style=None,
        id=None,
        start=None,
        total=None,
    ):
        super().__init__(entries=entries, style=style, id=id)
        assert start is None or isinstance(start, (int, float, Degrees))
        assert total is None or isinstance(total, (int, float))

        self.style.set_default("radius", self.DEFAULT_RADIUS)
        if isinstance(start, (int, float)):
            self.start = Degrees(start)
        else:
            self.start = start
        self.total = total

    def check_entry(self, entry):
        if not isinstance(entry, Slice):
            raise ValueError("entry is not a Slice instance")

    def svg(self):
        "Return the SVG minixml element for the diagram content."
        diagram = super().svg()

        radius = self.style["radius"]
        diagram += Element("circle", r=N(radius))

        diameter = 2 * radius
        if self.style["stroke"] and self.style["stroke_width"]:
            diameter += self.style["stroke_width"]
        self.extent = Vector2(diameter, diameter)
        self.origin = -0.5 * self.extent

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

        # Create slice wedges.
        with self.style:
            wedges = Element("g")
            diagram += wedges
            self.style.set_svg_attribute(wedges, "stroke")
            self.style.set_svg_attribute(wedges, "stroke_width")

            for slice in self.entries:
                slice.fraction = slice.value / total
                slice.start = stop
                stop = slice.start + slice.fraction * Degrees(360)
                p0 = Vector2.from_polar(radius, float(slice.start))
                p1 = Vector2.from_polar(radius, float(stop))
                lof = 1 if stop - slice.start > Degrees(180) else 0
                wedges += (
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

        # Create labels.
        with self.style:
            labels = Element("g")
            diagram += labels
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

        return diagram

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        result = super().as_dict_content()
        result["start"] = None if self.start is None else self.start.degrees
        return result


class Slice(Entity):
    "A slice in a pie chart."

    def __init__(self, value, label=None, style=None):
        self.value = value
        self.label = label
        self.style = stylify(style)

    def as_dict_content(self):
        result = dict(value=self.value)
        if self.label:
            result["label"] = self.label
        if self.style:
            result.update({"style": destylify(self.style)})
        return result
