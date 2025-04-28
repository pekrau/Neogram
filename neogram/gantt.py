"Gantt chart."

__all__ = ["Gantt", "Task"]

from diagram import *
from dimension import *
from path import *
from style import stylify, destylify
from utils import N, get_text_length


class Gantt(Diagram):
    "Gantt chart."

    DEFAULT_WIDTH = 500         # Entire diagram.
    DEFAULT_HEIGHT = 16         # Each lane.

    def __init__(
        self,
        entries=None,
        id=None,
        style=None,
        epoch=Epoch.ORDINAL,  # XXX not implemented
    ):
        super().__init__(entries=entries, style=style, id=id)
        assert epoch is None or isinstance(epoch, str)

        self.style.set_default("width", self.DEFAULT_WIDTH)
        self.style.set_default("height", self.DEFAULT_HEIGHT)

    def svg(self):
        """Return the SVG minixml element for the diagram content.
        Sets the origin and extent of the diagram.
        """
        diagram = super().svg()

        lanes = dict()
        dimension = Dimension(width=self.style["width"])
        height = 0
        padding = self.style["padding"] or 0

        # Set the heights for each lane, and the offset for legends.
        for entry in self.entries:
            with self.style:
                self.style.update(entry.style)
                dimension.update_offset(
                    get_text_length(
                        entry.lane,
                        font = self.style["legend.font"],
                        size = self.style["legend.size"],
                        italic = self.style["legend.italic"],
                        bold = self.style["legend.bold"],
                    )
                )
                dimension.update_span(entry.minmax)
                if entry.lane not in lanes:
                    height += padding
                    lanes[entry.lane] = height
                    height += self.style["height"] + padding

        self.origin = Vector2(0, 0)
        self.extent = Vector2(self.style["width"], height)

        diagram += (grid := Element("g"))
        with self.style:
            # XXX Set ticks style; new style subsection required.
            ticks = dimension.get_ticks()
            path = Path(Vector2(ticks[0].pixel, 0)).V(height)
            for tick in ticks[1:]:
                path.M(Vector2(tick.pixel, 0)).V(height)
            grid += Element("path", d=path)

        # Add graphics for entries.
        diagram += (graphics := Element("g"))
        with self.style:
            self.style.set_svg_attribute(graphics, "stroke")
            self.style.set_svg_attribute(graphics, "stroke_width")
            self.style.set_svg_attribute(graphics, "fill")
            for entry in self.entries:
                graphics += entry.graphic_element(self.style, lanes, dimension)

        # Add labels after graphics, to render on top.
        diagram += (labels := Element("g"))
        with self.style:
            self.style.set_svg_text_attributes(labels, "label")
            for entry in self.entries:
                if entry.label:
                    labels += entry.label_element(self.style, lanes, dimension)

        # Add legends after graphics, to render on top.
        diagram += (legends := Element("g"))
        with self.style:
            self.style.set_svg_text_attributes(legends, "legend")
            for lane in lanes:
                legends += (legend := Element("text"))
                legend += lane
                legend["x"] = self.style["padding"]
                legend["y"] = self.style["height"] + lanes[lane]

        return diagram


class Task(Entity):
    "Task in a Gantt chart."

    def __init__(self, label, start, finish, lane=None, style=None):
        assert label and isinstance(label, str)
        assert isinstance(start, (int, float))
        assert type(start) == type(finish)
        assert lane is None or isinstance(lane, str)
        assert style is None or isinstance(style, dict)

        self.label = label
        self.start = start
        self.finish = finish
        assert self.start <= self.finish
        self.lane = lane if lane is not None else self.label
        self.style = stylify(style)

    @property
    def minmax(self):
        return (self.start, self.finish)

    def graphic_element(self, style, lanes, dimension):
        with style:
            style.update(self.style)
            elem = Element(
                "rect",
                x=N(dimension.get_pixel(self.start)),
                y=N(lanes[self.lane]),
                width=N(dimension.get_width(self.start, self.finish)),
                height=style["height"],
            )
            if rounded := style["rounded"]:
                elem["rx"] = rounded
                elem["ry"] = rounded
            style.set_svg_attribute(elem, "stroke")
            style.set_svg_attribute(elem, "stroke_width")
            style.set_svg_attribute(elem, "fill")
        return elem

    def label_element(self, style, lanes, dimension):
        with style:
            style.update(self.style)
            elem = Element(
                "text",
                x=N(dimension.get_pixel((self.start + self.finish) / 2)),
                y=N(lanes[self.lane] + style["height"] - (style["padding"] or 0)),
            )
            elem += self.label
            style.set_svg_text_attributes(elem, "label")
        return elem

    def as_dict_content(self):
        result = dict(label=self.label)
        result["start"] = self.start
        result["finish"] = self.finish
        if self.lane != self.label:
            result["lane"] = self.lange
        if self.style:
            result["style"] = destylify(self.style)
        return result
