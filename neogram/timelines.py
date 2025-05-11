"Timelines having events and periods."

__all__ = ["Timelines", "Event", "Period"]

import constants
from color import *
from diagram import *
from dimension import *
from path import *
import utils


class Timelines(Diagram):
    "Timelines having events and periods."

    DEFAULT_WIDTH = 600

    SCHEMA = {
        "title": __doc__,
        "$anchor": "timelines",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"$ref": "#title"},
            "width": {
                "title": "Width of chart, in pixels.",
                "type": "number",
                "default": DEFAULT_WIDTH,
                "exclusiveMinimum": 0,
            },
            "legend": {"type": "boolean", "default": False},
            "entries": {
                "title": "Entries (events, periods) in the timelines.",
                "type": "array",
                "items": {
                    "anyOf": [
                        {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "event": {
                                    "title": "Event at a moment in time.",
                                    "type": "object",
                                    "required": ["label", "moment"],
                                    "additionalProperties": False,
                                    "properties": {
                                        "label": {"type": "string"},
                                        "moment": {"type": "number"},
                                        "timeline": {"type": "string"},
                                        "color": {"type": "string", "format": "color"},
                                    },
                                },
                            },
                        },
                        {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "period": {
                                    "title": "Period of time.",
                                    "type": "object",
                                    "required": ["label", "begin", "end"],
                                    "additionalProperties": False,
                                    "properties": {
                                        "label": {"type": "string"},
                                        "begin": {"type": "number"},
                                        "end": {"type": "number"},
                                        "timeline": {"type": "string"},
                                        "color": {"type": "string", "format": "color"},
                                    },
                                },
                            },
                        },
                    ],
                },
            },
        },
    }

    def __init__(
        self,
        title=None,
        entries=None,
        width=None,
        legend=None,
    ):
        super().__init__(title=title, entries=entries)
        assert width is None or (isinstance(width, (int, float)) and width > 0)
        assert legend is None or isinstance(legend, bool)

        self.width = width or self.DEFAULT_WIDTH
        self.legend = True if legend is None else legend

    def check_entry(self, entry):
        return isinstance(entry, (Event, Period))

    def data_as_dict(self):
        result = super().data_as_dict()
        if self.width != self.DEFAULT_WIDTH:
            result["width"] = self.width
        if self.legend is not None and not self.legend:
            result["legend"] = False
        return result

    def build(self):
        "Set the 'svg' and 'height' attributes."
        super().build()

        dimension = Dimension(width=self.width)
        timelines = dict()  # Key: timeline; value: height

        # Set the heights for each timeline, and the offset for legends.
        area_height = self.height
        kwargs = dict(
            font=constants.DEFAULT_FONT_FAMILY,
            size=self.DEFAULT_FONT_SIZE,
        )

        for entry in self.entries:
            if self.legend:
                dimension.update_offset(utils.get_text_length(entry.timeline, **kwargs))
            dimension.update_span(entry.minmax)
            if entry.timeline not in timelines:
                self.height += constants.DEFAULT_PADDING
                timelines[entry.timeline] = self.height
                self.height += constants.DEFAULT_SIZE + constants.DEFAULT_PADDING

        # Add time axis lines and their labels.
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
                label := Element(
                    "text", tick.label, x=utils.N(tick.pixel), y=utils.N(self.height)
                )
            )
            if tick is ticks[0]:
                label["text-anchor"] = "start"
            elif tick is ticks[-1]:
                label["text-anchor"] = "end"
        self.height += self.DEFAULT_FONT_SIZE * constants.FONT_DESCEND

        # Add graphics for entries.
        self.svg += (graphics := Element("g"))
        for entry in self.entries:
            graphics += entry.render_graphic(timelines, dimension)

        # Add entry labels after graphics, to render on top.
        self.svg += (labels := Element("g"))
        labels["text-anchor"] = "middle"
        labels["stroke"] = "none"
        labels["fill"] = "black"
        for entry in self.entries:
            labels += entry.render_label(timelines, dimension)

        # Add legend labels.
        if self.legend:
            self.svg += (legends := Element("g"))
            legends["stroke"] = "none"
            legends["fill"] = "black"
            for text, height in timelines.items():
                legends += (legend := Element("text", text))
                legend["x"] = utils.N(constants.DEFAULT_PADDING)
                legend["y"] = utils.N(
                    height
                    + (constants.DEFAULT_SIZE + self.DEFAULT_FONT_SIZE) / 2
                    - self.DEFAULT_FONT_SIZE * constants.FONT_DESCEND
                )

        self.height += (
            constants.DEFAULT_PADDING - self.DEFAULT_FONT_SIZE * constants.FONT_DESCEND
        )


class _Entry(Entity):
    "Abstract entry in a timelines chart."

    DEFAULT_FONT_SIZE = Timelines.DEFAULT_FONT_SIZE

    def __init__(self, label, timeline=None, color=None):
        assert isinstance(label, str)
        assert timeline is None or isinstance(timeline, str)
        assert color is None or isinstance(color, str)

        self.label = label
        self.timeline = timeline or label
        self.color = color

    def data_as_dict(self):
        result = {"label": self.label}
        if self.timeline != self.label:
            result["timeline"] = self.timeline
        if self.color:
            result["color"] = self.color
        return result

    @property
    def minmax(self):
        raise NotImplementedError

    def render_graphic(self, timelines, dimension):
        raise NotImplementedError

    def render_label(self, timelines, dimension):
        raise NotImplementedError


class Event(_Entry):
    "Event at a given moment in a timeline."

    def __init__(self, label, moment, timeline=None, color=None):
        super().__init__(label=label, timeline=timeline, color=color)
        assert isinstance(moment, (int, float))

        self.moment = moment

    def data_as_dict(self):
        result = super().data_as_dict()
        result["moment"] = self.moment
        return result

    @property
    def minmax(self):
        return self.moment

    def render_graphic(self, timelines, dimension):
        elem = Element(
            "ellipse",
            cx=utils.N(dimension.get_pixel(self.moment)),
            cy=utils.N(timelines[self.timeline] + constants.DEFAULT_SIZE / 2),
            rx=constants.DEFAULT_SIZE / 5,
            ry=constants.DEFAULT_SIZE / 2,
        )
        elem["stroke"] = "none"
        elem["fill"] = self.color or "black"
        return elem

    def render_label(self, timelines, dimension):
        elem = Element(
            "text",
            self.label,
            x=utils.N(
                dimension.get_pixel(self.moment) + constants.DEFAULT_SIZE / 5 + 1
            ),
            y=utils.N(
                timelines[self.timeline]
                + (constants.DEFAULT_SIZE + self.DEFAULT_FONT_SIZE) / 2
                - self.DEFAULT_FONT_SIZE * constants.FONT_DESCEND
            ),
        )
        elem["text-anchor"] = "start"
        return elem


class Period(_Entry):
    "Period of time in a timeline."

    def __init__(self, label, begin, end, timeline=None, color=None):
        super().__init__(label=label, timeline=timeline, color=color)
        assert isinstance(begin, (int, float))
        assert isinstance(end, (int, float))

        self.begin = begin
        self.end = end

    def data_as_dict(self):
        result = super().data_as_dict()
        result["begin"] = self.begin
        result["end"] = self.end
        return result

    @property
    def minmax(self):
        return (self.begin, self.end)

    def render_graphic(self, timelines, dimension):
        elem = Element(
            "rect",
            x=utils.N(dimension.get_pixel(self.begin)),
            y=utils.N(timelines[self.timeline]),
            width=utils.N(dimension.get_width(self.begin, self.end)),
            height=constants.DEFAULT_SIZE,
        )
        elem["fill"] = self.color or "white"
        return elem

    def render_label(self, timelines, dimension):
        elem = Element(
            "text",
            self.label,
            x=utils.N(dimension.get_pixel((self.begin + self.end) / 2) + 1),
            y=utils.N(
                timelines[self.timeline]
                + (constants.DEFAULT_SIZE + self.DEFAULT_FONT_SIZE) / 2
                - self.DEFAULT_FONT_SIZE * constants.FONT_DESCEND
            ),
        )
        elem["text-anchor"] = "middle"
        if self.color:
            elem["fill"] = Color(self.color).best_contrast
        return elem


register(Timelines)
register(Event)
register(Period)
