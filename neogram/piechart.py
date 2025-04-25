"Neogram: Pie chart."

from diagram import *


__all__ = ["Piechart", "Slice"]


class Piechart(Diagram):
    "Pie chart."

    DEFAULT_RADIUS = 100.0

    def __init__(
        self,
        id=None,
        klass=None,
        style=None,
        radius=None,
        start=None,
        total=None,
        slices=None,
    ):
        assert radius is None or isinstance(radius, (int, float))
        assert start is None or isinstance(start, (int, float, Degrees))
        assert total is None or isinstance(total, (int, float))
        assert slices is None or isinstance(slices, (tuple, list))

        super().__init__(id=id, klass=klass, style=style)

        self.radius = radius if radius is not None else self.DEFAULT_RADIUS
        if isinstance(start, (int, float)):
            self.start = Degrees(start)
        else:
            self.start = start
        self.total = total
        self.slices = []
        if slices:
            for slice in slices:
                self.append(slice)

    def __iadd__(self, other):
        self.append(other)
        return self

    def append(self, slice):
        if isinstance(slice, Slice):
            item = slice
        elif isinstance(slice, (float, int)):
            item = Slice(slice)
        elif isinstance(slice, (tuple, list)) and len(slice) == 2:
            item = Slice(*slice)
        elif isinstance(slice, dict) and "value" in slice:
            item = Slice(slice["value"], slice.get("label"), slice.get("style"))
        else:
            raise ValueError("invalid slice specification")
        self.slices.append(item)

    def viewbox(self):
        diameter = 2 * self.radius
        if self.style["stroke"] and self.style["stroke_width"]:
            diameter += self.style["stroke_width"]
        extent = Vector2(diameter, diameter)
        return (-0.5 * extent, extent)

    def svg(self):
        "Return the SVG minixml element for the diagram content."
        diagram = super().svg()

        diagram += (circle := Element("circle", r=N(self.radius)))
        self.style.set_svg_attribute(circle, "stroke")
        self.style.set_svg_attribute(circle, "stroke_width")

        if self.slices:
            total = sum([s.value for s in self.slices])
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

        with self.style:
            wedges = Element("g")
            diagram += wedges
            self.style.set_svg_attribute(wedges, "stroke")
            self.style.set_svg_attribute(wedges, "stroke_width")

            for slice in self.slices:
                slice.fraction = slice.value / total
                slice.start = stop
                stop = slice.start + slice.fraction * Degrees(360)
                p0 = Vector2.from_polar(self.radius, float(slice.start))
                p1 = Vector2.from_polar(self.radius, float(stop))
                lof = 1 if stop - slice.start > Degrees(180) else 0
                wedges += (
                    path := Element(
                        "path",
                        d=Path(Vector2(0, 0))
                        .L(p0)
                        .A(self.radius, self.radius, 0, lof, 1, p1)
                        .Z(),
                    )
                )
                with self.style:
                    if slice.style:
                        self.style.update(slice.style)
                    self.style.set_svg_attribute(path, "stroke")
                    self.style.set_svg_attribute(path, "stroke_width")
                    if "fill" in self.style: # If defined at this level.
                        self.style.set_svg_attribute(path, "fill")
                    elif colors:
                        path["fill"] = str(next(colors))
                    slice.background = path["fill"]

        with self.style:
            labels = Element("g")
            diagram += labels
            self.style.set_svg_attribute(labels, "stroke")
            self.style.set_svg_attribute(labels, "stroke_width")
            self.style.set_svg_attribute(labels, "label.fill")
            self.style.set_svg_text_attributes(labels, "label")

            for slice in self.slices:
                if slice.label:
                    middle = slice.start + 0.5 * slice.fraction * Degrees(360)
                    pos = Vector2.from_polar(0.7 * self.radius, float(middle))
                    labels += (label := Element("text", x=N(pos.x), y=N(pos.y)))
                    with self.style:
                        if slice.style:
                            self.style.update(slice.style)
                        self.style.set_svg_text_attributes(label, "label")
                        if self.style["label.contrast"]:
                            background = Color(slice.background)
                            self.style.set_svg_attribute(label, "label.fill", value=background.best_contrast())
                    label += slice.label

        return diagram

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        data = super().as_dict_content()
        data["radius"] = self.radius
        data["start"] = None if self.start is None else self.start.degrees
        data["slices"] = []
        for slice in self.slices:
            d = dict(value=slice.value)
            if slice.label:
                d["label"] = slice.label
            if slice.style:
                d.update({"style": slice.style})
            data["slices"].append(d)
        return data


class Slice:

    def __init__(self, value, label=None, style=None):
        self.value = value
        self.label = label 
        self.style = style
