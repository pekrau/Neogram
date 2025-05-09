"Timelines having events and periods."

__all__ = ["Timelines", "Event", "Period"]

import constants
from diagram import *
from dimension import *
from path import *
import utils


class Timelines(Diagram):
    "Timelines having events and periods."

    SCHEMA = {
        "title": "Timelines having events and periods.",
        "type": "object",
        "properties": {
            "title": {
                "title": "Title of chart.",
                "type": "string",
            },
            "width": {
                "title": "Width of chart, in pixels.",
                "type": "number",
                "default": constants.DEFAULT_WIDTH,
                "exclusiveMinimum": 0,
            },
            "entries": {
                "title": "Entries (events, periods) in the timelines.",
                "type": "array",
                "items": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "event": {
                                    "title": "Event at a moment in time.",
                                    "type": "object",
                                    "properties": {
                                        "label": {"type": "string"},
                                        "moment": {"type": "number"},
                                        "timeline": {"type": "string"},
                                    },
                                    "required": ["label", "moment"],
                                    "additionalProperties": False,
                                },
                            },
                            "additionalProperties": False,
                        },
                        {
                            "type": "object",
                            "properties": {
                                "period": {
                                    "title": "Period of time.",
                                    "type": "object",
                                    "properties": {
                                        "label": {"type": "string"},
                                        "begin": {"type": "number"},
                                        "end": {"type": "number"},
                                        "timeline": {"type": "string"},
                                    },
                                    "required": ["label", "begin", "end"],
                                    "additionalProperties": False,
                                },
                            },
                            "additionalProperties": False,
                        },
                    ],
                },
            },
            "additionalProperties": False,
        },
        "additionalProperties": False,
    }

    def check_entry(self, entry):
        return isinstance(entry, (Event, Period))

    def data_as_dict(self):
        result = super().data_as_dict()
        if self.entries:
            result["entries"] = [e.as_dict() for e in self.entries]
        import schema

        schema.validate(result, schema=self.SCHEMA)
        return result

    def build(self):
        "Create and set the 'svg' and 'height' attributes."
        super().build()

        dimension = Dimension(width=self.width)
        timelines = dict()  # Key: timeline; value: height

        # Set the heights for each timeline, and the offset for legends.
        area_height = self.height
        kwargs = dict(
            font=constants.DEFAULT_FONT_FAMILY,
            size=constants.DEFAULT_FONT_SIZE,
        )

        for entry in self.entries:
            dimension.update_offset(utils.get_text_length(entry.timeline, **kwargs))
            dimension.update_span(entry.minmax)
            if entry.timeline not in timelines:
                self.height += constants.DEFAULT_PADDING
                timelines[entry.timeline] = self.height
                self.height += constants.DEFAULT_SIZE + constants.DEFAULT_PADDING

        # Add axis lines and their labels.
        self.svg += (axis := Element("g"))
        ticks = dimension.get_ticks()
        path = Path(Vector2(ticks[0].pixel, area_height)).V(self.height)
        for tick in ticks[1:]:
            path.M(Vector2(tick.pixel, area_height)).V(self.height)
        path.M(Vector2(ticks[0].pixel, area_height)).H(self.width)
        path.M(Vector2(ticks[0].pixel, self.height)).H(self.width)
        axis += Element("path", d=path)
        axis += (labels := Element("g"))
        labels["text-anchor"] = "middle"
        labels["stroke"] = "none"
        labels["fill"] = "black"
        self.height += constants.DEFAULT_SIZE
        for tick in ticks:
            labels += (
                label := Element("text", tick.label, x=N(tick.pixel), y=N(self.height))
            )
            if tick is ticks[0]:
                label["text-anchor"] = "start"
            elif tick is ticks[-1]:
                label["text-anchor"] = "end"
        self.height += constants.DEFAULT_FONT_DESCEND

        # Add graphics for entries.
        self.svg += (graphics := Element("g"))
        for entry in self.entries:
            graphics += entry.graphic_element(timelines, dimension)

        # Add entry labels after graphics, to render on top.
        self.svg += (labels := Element("g"))
        labels["text-anchor"] = "middle"
        labels["stroke"] = "none"
        labels["fill"] = "black"
        for entry in self.entries:
            labels += entry.label_element(timelines, dimension)

        # Add legend labels.
        self.svg += (legends := Element("g"))
        legends["stroke"] = "none"
        legends["fill"] = "black"
        for text, height in timelines.items():
            legends += (legend := Element("text", text))
            legend["x"] = N(constants.DEFAULT_PADDING)
            legend["y"] = N(
                height
                + (constants.DEFAULT_SIZE + constants.DEFAULT_FONT_SIZE) / 2
                - constants.DEFAULT_FONT_DESCEND
            )

        self.height += constants.DEFAULT_PADDING - constants.DEFAULT_FONT_DESCEND


class _Entry(Entity):
    "Abstract entry in a timelines chart."

    def __init__(self, label, timeline=None):
        assert isinstance(label, str)
        assert timeline is None or isinstance(timeline, str)

        self.label = label
        self.timeline = timeline or label

    @property
    def minmax(self):
        raise NotImplementedError

    def graphic_element(self, timelines, dimension):
        raise NotImplementedError

    def label_element(self, timelines, dimension):
        raise NotImplementedError

    def data_as_dict(self):
        result = {"label": self.label}
        if self.timeline != self.label:
            result["timeline"] = self.timeline
        return result


class Event(_Entry):
    "Event at a given moment in a timeline."

    def __init__(self, label, moment, timeline=None):
        super().__init__(label=label, timeline=timeline)
        assert isinstance(moment, (int, float))

        self.moment = moment

    @property
    def minmax(self):
        return self.moment

    def graphic_element(self, timelines, dimension):
        elem = Element(
            "ellipse",
            cx=N(dimension.get_pixel(self.moment)),
            cy=N(timelines[self.timeline] + constants.DEFAULT_SIZE / 2),
            rx=constants.DEFAULT_SIZE / 5,
            ry=constants.DEFAULT_SIZE / 2,
        )
        return elem

    def label_element(self, timelines, dimension):
        elem = Element(
            "text",
            self.label,
            x=N(dimension.get_pixel(self.moment) + constants.DEFAULT_SIZE / 5 + 1),
            y=N(
                timelines[self.timeline]
                + (constants.DEFAULT_SIZE + constants.DEFAULT_FONT_SIZE) / 2
                - constants.DEFAULT_FONT_DESCEND
            ),
        )
        elem["text-anchor"] = "start"
        return elem

    def data_as_dict(self):
        result = super().data_as_dict()
        result["moment"] = self.moment
        return result


class Period(_Entry):
    "Period of time in a timeline."

    def __init__(self, label, begin, end, timeline=None):
        super().__init__(label=label, timeline=timeline)
        assert isinstance(begin, (int, float))
        assert isinstance(end, (int, float))

        self.begin = begin
        self.end = end

    @property
    def minmax(self):
        return (self.begin, self.end)

    def graphic_element(self, timelines, dimension):
        elem = Element(
            "rect",
            x=N(dimension.get_pixel(self.begin)),
            y=N(timelines[self.timeline]),
            width=N(dimension.get_width(self.begin, self.end)),
            height=constants.DEFAULT_SIZE,
        )
        return elem

    def label_element(self, timelines, dimension):
        elem = Element(
            "text",
            self.label,
            x=N(dimension.get_pixel((self.begin + self.end) / 2) + 1),
            y=N(
                timelines[self.timeline]
                + (constants.DEFAULT_SIZE + constants.DEFAULT_FONT_SIZE) / 2
                - constants.DEFAULT_FONT_DESCEND
            ),
        )
        elem["text-anchor"] = "middle"
        return elem

    def data_as_dict(self):
        result = super().data_as_dict()
        result["begin"] = self.begin
        result["end"] = self.end
        return result


register(Timelines)
register(Event)
register(Period)
