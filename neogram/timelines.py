"Timelines chart."

__all__ = ["Timelines", "Event", "Period", "Epoch"]

import datetime

from diagram import *
from dimension import *
from path import *
import style as style_module
from utils import N, get_text_length


class Timelines(Diagram):
    "Timelines chart; set of timelines displaying events and periods."

    DEFAULT_WIDTH = 500  # Entire diagram.
    DEFAULT_SIZE = 16  # Height of each timeline.
    DEFAULT_EPOCH = Epoch.ORDINAL

    def __init__(
        self,
        entries=None,
        style=None,
        id=None,
        title=None,
        epoch=None,
    ):
        super().__init__(entries=entries, style=style, id=id, title=title)
        assert epoch is None or isinstance(epoch, str)

        self.epoch = epoch or self.DEFAULT_EPOCH
        self.style.set_default("width", self.DEFAULT_WIDTH)
        self.style.set_default("size", self.DEFAULT_SIZE)

    def check_entry(self, entry):
        if not isinstance(entry, Temporal):
            raise ValueError("entry is not a Temporal instance")

    def svg(self):
        """Return the SVG minixml element for the diagram content.
        Sets the origin and extent of the diagram.
        """
        diagram = super().svg()

        timelines = dict()
        dimension = Dimension(width=self.style["width"])

        # Set the heights for each timeline, and the offset for legends.
        # Legends are controlled by top-level styles.
        area_height = self.height
        kwargs = dict(
            font=self.style["legend.font"],
            size=self.style["legend.font_size"],
            italic=self.style["legend.italic"],
            bold=self.style["legend.bold"],
        )
        padding = self.style["padding"]

        # Legend width has been explicitly set to a number.
        width = self.style["legend.width"]
        if width and width > 1:
            dimension.update_offset(width)

        for entry in self.entries:
            with self.style:
                self.style.update(entry.style)
                if width is True:
                    dimension.update_offset(get_text_length(entry.timeline, **kwargs))
                dimension.update_span(entry.minmax)
                if entry.timeline not in timelines:
                    self.height += padding
                    timelines[entry.timeline] = self.height
                    self.height += self.style["size"] + padding

        # Add axis lines and their labels.
        diagram += (axis := Element("g"))
        with self.style:
            self.style.set_svg_attribute(axis, "axis.stroke")
            self.style.set_svg_attribute(axis, "axis.stroke_width")
            ticks = dimension.get_ticks(self.style)
            path = Path(Vector2(ticks[0].pixel, area_height)).V(self.height)
            for tick in ticks[1:]:
                path.M(Vector2(tick.pixel, area_height)).V(self.height)
            path.M(Vector2(ticks[0].pixel, area_height)).H(self.style["width"])
            path.M(Vector2(ticks[0].pixel, self.height)).H(self.style["width"])
            axis += Element("path", d=path)
            if self.style["axis.labels"]:
                axis += (labels := Element("g"))
                with self.style:
                    self.height += self.style["legend.font_size"]
                    self.style.set_svg_text_attributes(labels, "legend")
                    self.style.set_svg_attribute(labels, "anchor", "middle")
                    for tick in ticks:
                        labels += (
                            label := Element(
                                "text", tick.label, x=tick.pixel, y=self.height
                            )
                        )
                        if tick is ticks[0]:
                            with self.style:
                                self.style.set_svg_attribute(label, "anchor", "start")
                        elif tick is ticks[-1]:
                            with self.style:
                                self.style.set_svg_attribute(label, "anchor", "end")
                    self.height += self.style["legend.descend"]

        # Add graphics for entries.
        diagram += (graphics := Element("g"))
        with self.style:
            self.style.set_svg_attribute(graphics, "stroke")
            self.style.set_svg_attribute(graphics, "stroke_width")
            self.style.set_svg_attribute(graphics, "fill")
            for entry in self.entries:
                graphics += entry.graphic_element(self.style, timelines, dimension)

        # Add labels after graphics, to render on top.
        diagram += (labels := Element("g"))
        with self.style:
            self.style.set_svg_text_attributes(labels, "label")
            for entry in self.entries:
                if entry.label:
                    labels += entry.label_element(self.style, timelines, dimension)

        # Add legends after graphics.
        if width:
            diagram += (legends := Element("g"))
            with self.style:
                self.style.set_svg_text_attributes(legends, "legend")
                for timeline in timelines:
                    legends += (legend := Element("text"))
                    legend += timeline
                    legend["x"] = self.style["padding"]
                    legend["y"] = (
                        (self.style["size"] + self.style["legend.font_size"]) / 2
                        + timelines[timeline]
                        - self.style["legend.descend"]
                    )

        self.origin = Vector2(0, 0)
        self.extent = Vector2(self.style["width"], self.height)

        return diagram

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        result = super().as_dict_content()
        if self.epoch != self.DEFAULT_EPOCH:
            result["epoch"] = str(self.epoch)
        return result


class Temporal(Entity):
    "Abstract temporal entry in a timeline."

    def __init__(self, label, timeline=None, style=None):
        assert label and isinstance(label, str)
        assert timeline is None or isinstance(timeline, str)
        assert style is None or isinstance(style, dict)

        self.label = label
        self.timeline = timeline if timeline is not None else label
        self.style = style_module.stylify(style)

    @property
    def minmax(self):
        raise NotImplementedError

    def graphic_element(self, style, timelines, dimension):
        raise NotImplementedError

    def label_element(self, style, timelines, dimension):
        raise NotImplementedError

    def as_dict(self):
        return {self.__class__.__name__.casefold(): self.as_dict_content()}

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        result = dict(label=self.label)
        if self.timeline:
            result["timeline"] = self.timeline
        if self.style:
            result["style"] = style_module.destylify(self.style)
        return result


class Event(Temporal):
    "Event in a timeline. An instant."

    def __init__(self, label, moment, timeline=None, style=None):
        super().__init__(label, timeline=timeline, style=style)
        assert isinstance(moment, (int, float))
        self.moment = moment

    @property
    def minmax(self):
        return self.moment

    def graphic_element(self, style, timelines, dimension):
        with style:
            style.update(self.style)
            # XXX adjust label for marker style width
            elem = Element(
                "ellipse",
                cx=N(dimension.get_pixel(self.moment)),
                cy=N(timelines[self.timeline] + style["size"] / 2),
                rx=style["size"] / 5,
                ry=style["size"] / 2,
            )
            style.set_svg_attribute(elem, "stroke")
            style.set_svg_attribute(elem, "stroke_width")
            style.set_svg_attribute(elem, "fill")
        return elem

    def label_element(self, style, timelines, dimension):
        with style:
            style.update(self.style)
            # XXX label adjust for marker style width
            elem = Element(
                "text",
                self.label,
                x=N(dimension.get_pixel(self.moment) + 1),
                y=N(
                    timelines[self.timeline]
                    + (style["size"] + style["label.font_size"]) / 2
                    - style["label.descend"]
                ),
            )
            style.set_svg_text_attributes(elem, "label")
            match style["label.anchor"]:
                case "start":
                    elem["transform"] = "translate(5,0)"
                case "end":
                    elem["transform"] = "translate(-5,0)"
            if style["label.contrast"]:
                style.set_svg_attribute(
                    elem, "fill", value=style["fill"].best_contrast()
                )
        return elem

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        result = super().as_dict_content()
        if isinstance(self.moment, (datetime.date, datetime.datetime)):
            result["moment"] = self.moment.isoformat()
        else:
            result["moment"] = self.moment
        return result


class Period(Temporal):
    "Period in a timeline. Has a duration."

    def __init__(self, label, begin, end, timeline=None, style=None):
        super().__init__(label, timeline=timeline, style=style)
        assert isinstance(begin, (int, float))
        assert isinstance(end, (int, float))
        self.begin = begin
        self.end = end

    @property
    def minmax(self):
        return (self.begin, self.end)

    def graphic_element(self, style, timelines, dimension):
        with style:
            style.update(self.style)
            elem = Element(
                "rect",
                x=N(dimension.get_pixel(self.begin)),
                y=N(timelines[self.timeline]),
                width=N(dimension.get_width(self.begin, self.end)),
                height=style["size"],
            )
            if rounded := style["rounded"]:
                elem["rx"] = rounded
                elem["ry"] = rounded
            style.set_svg_attribute(elem, "stroke")
            style.set_svg_attribute(elem, "stroke_width")
            style.set_svg_attribute(elem, "fill")
        return elem

    def label_element(self, style, timelines, dimension):
        with style:
            style.update(self.style)
            elem = Element(
                "text",
                x=N(dimension.get_pixel((self.begin + self.end) / 2)),
                y=N(
                    timelines[self.timeline]
                    + (style["size"] + style["label.font_size"]) / 2
                    - style["label.descend"]
                ),
            )
            elem += self.label
            style.set_svg_text_attributes(elem, "label")
        return elem

    def as_dict_content(self):
        result = super().as_dict_content()
        if isinstance(self.begin, (datetime.date, datetime.datetime)):
            result["begin"] = self.begin.isoformat()
            result["end"] = self.end.isoformat()
        else:
            result["begin"] = self.begin
            result["end"] = self.end
        return result


SCHEMA = {
    "title": "Timelines",
    "description": "Timelines containing events and periods.",
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
                    "event": {
                        "type": "object",
                        "properties": {
                            "moment": {
                                "type": "number",
                            },
                            "label": {
                                "type": "string",
                            },
                            "timeline": {
                                "type": "string",
                            },
                            "style": {"$ref": "#/$defs/style"},
                        },
                        "required": ["moment"],
                        "additionalProperties": False,
                    },
                    "period": {
                        "type": "object",
                        "properties": {
                            "begin": {
                                "type": "number",
                            },
                            "end": {
                                "type": "number",
                            },
                            "label": {
                                "type": "string",
                            },
                            "timeline": {
                                "type": "string",
                            },
                            "style": {"$ref": "#/$defs/style"},
                        },
                        "required": ["begin", "end"],
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
