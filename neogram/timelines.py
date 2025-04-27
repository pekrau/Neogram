"Timelines chart."

__all__ = ["Timelines", "Event", "Period", "Epoch"]

import datetime
import enum

from diagram import *
from dimension import *
from path import *
from style import stylify, destylify
from utils import N, get_text_length


class Epoch(enum.StrEnum):
    ORDINAL = "Ordinal"
    DATE = "Julian date"
    DATETIME = "Julian date and time"


class Timelines(Diagram):
    "Timelines chart; set of timelines."

    DEFAULT_WIDTH = 500  # Entire diagram.
    DEFAULT_HEIGHT = 16  # Each timeline.

    def __init__(
        self,
        id=None,
        klass=None,
        style=None,
        epoch=Epoch.ORDINAL,
        entries=None,
    ):
        assert epoch is None or isinstance(epoch, str)
        assert entries is None or isinstance(entries, (tuple, list))

        super().__init__(id=id, klass=klass, style=style)
        if "width" not in self.style:
            self.style["width"] = self.DEFAULT_WIDTH
        if "height" not in self.style:
            self.style["height"] = self.DEFAULT_HEIGHT

        self.epoch = epoch
        self.entries = []
        if entries:
            for entry in entries:
                self.append(entry)

    def __iadd__(self, other):
        self.append(other)
        return self

    def append(self, entry):
        if isinstance(entry, dict):
            key, items = list(entry.items())[0] # Always only one entry in this dict.
            if key == "event":
                entry = Event(**items)
            elif key == "period":
                entry = Period(**items)
            else:
                raise ValueError(f"unknown entry '{key}'")
        assert isinstance(entry, (Event, Period))
        self.entries.append(entry)

    def viewbox(self):
        height = 0
        padding = self.style["padding"] or 0
        timelines = set()
        for entry in self.entries:
            if entry.timeline not in timelines:
                with self.style:
                    self.style.update(entry.style)
                    height += self.style["height"] + 2 * padding
                timelines.add(entry.timeline)
        return (Vector2(0, 0), Vector2(self.style["width"], height))

    def svg(self):
        "Return the SVG minixml element for the diagram content."
        diagram = super().svg()
        self.style.set_svg_attribute(diagram, "stroke")
        self.style.set_svg_attribute(diagram, "stroke_width")

        timelines = dict()
        dimension = Dimension(width=self.style["width"])
        height = 0
        padding = self.style["padding"] or 0

        for entry in self.entries:
            dimension.offset = max(
                dimension.offset, get_text_length(entry.timeline, 14, "sans")
            )
            dimension.span = entry.value()
            if entry.timeline not in timelines:
                height += padding
                timelines[entry.timeline] = height
                with self.style:
                    self.style.update(entry.style)
                    height += self.style["height"] + padding

        diagram += (container := Element("g"))
        with self.style as style:
            # XXX Set ticks style; new style subsection required.
            ticks = dimension.get_ticks()
            path = Path(Vector2(ticks[0].x, 0)).V(height)
            for tick in ticks[1:]:
                path.M(Vector2(tick.x, 0)).V(height)
            container += Element("path", d=path)

        # Add graphics for entries.
        diagram += (container := Element("g"))
        with self.style:
            self.style.set_svg_attribute(container, "stroke")
            self.style.set_svg_attribute(container, "stroke_width")
            self.style.set_svg_attribute(container, "fill")
            for entry in self.entries:
                container += entry.graphic_element(self.style, timelines, dimension)

        # Add labels after graphics, to be visible.
        diagram += (container := Element("g"))
        with self.style:
            self.style.set_svg_text_attributes(container, "label")
            for entry in self.entries:
                if entry.label:
                    container += entry.label_element(self.style, timelines, dimension)

        # ### Add legends after graphics, to be visible.
        return diagram

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        result = super().as_dict_content()
        result["epoch"] = str(self.epoch)
        result["entries"] = [e.as_dict() for e in self.entries]
        return result


class Entry:
    "Abstract entry in a timeline."

    def __init__(self, label, timeline=None, style=None):
        assert label and isinstance(label, str)
        assert timeline is None or isinstance(timeline, str)
        assert style is None or isinstance(style, dict)

        self.label = label
        self.timeline = timeline if timeline is not None else label
        self.style = stylify(style)

    def value(self):
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
            result["style"] = destylify(self.style)
        return result


class Event(Entry):
    "Event in a timeline. An instant."

    def __init__(self, label, moment, timeline=None, style=None):
        super().__init__(label, timeline=timeline, style=style)
        self.moment = moment

    def value(self):
        return self.moment

    def graphic_element(self, style, timelines, dimension):
        with style:
            style.update(self.style)
            elem = Element(
                "circle",
                cx=N(dimension.get_x(self.moment)),
                cy=N(timelines[self.timeline] + style["height"] / 2),
                r=5,
            )
            style.set_svg_attribute(elem, "stroke")
            style.set_svg_attribute(elem, "stroke_width")
            style.set_svg_attribute(elem, "fill")
        return elem

    def label_element(self, style, timelines, dimension):
        with style:
            style.update(self.style)
            elem = Element(
                "text",
                x=N(dimension.get_x(self.moment)),
                y=N(
                    timelines[self.timeline] + style["height"] - (style["padding"] or 0)
                ),
            )
            elem += self.label
            style.set_svg_text_attributes(elem, "label")
            match style["label.anchor"]:
                case "start":
                    elem["transform"] = "translate(5,0)"
                case "end":
                    elem["transform"] = "translate(-5,0)"
        return elem

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        result = super().as_dict_content()
        if isinstance(self.moment, (datetime.date, datetime.datetime)):
            result["moment"] = self.moment.isoformat()
        else:
            result["moment"] = self.moment
        return result


class Period(Entry):
    "Period in a timeline. Has a duration."

    def __init__(self, label, begin, end, timeline=None, style=None):
        super().__init__(label, timeline=timeline, style=style)
        self.begin = begin
        self.end = end

    def value(self):
        return (self.begin, self.end)

    def graphic_element(self, style, timelines, dimension):
        with style:
            style.update(self.style)
            elem = Element(
                "rect",
                x=N(dimension.get_x(self.begin)),
                y=N(timelines[self.timeline]),
                width=N(dimension.get_width(self.begin, self.end)),
                height=style["height"],
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
                x=N(dimension.get_x((self.begin + self.end) / 2)),
                y=N(
                    timelines[self.timeline] + style["height"] - (style["padding"] or 0)
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


if __name__ == "__main__":
    bp = Epoch.BP
    ic(isinstance(bp, str))
    ic(bp.name == "BP")
    ic(str(bp))
    ic(Epoch("Before Present"))
