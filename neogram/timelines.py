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
        "required": ["entries"],
        "additionalProperties": False,
        "properties": {
            "title": {
                "title": "Title of the timelines diagram.",
                "$ref": "#text",
            },
            "width": {
                "title": "Width of diagram, in pixels.",
                "type": "number",
                "default": DEFAULT_WIDTH,
                "exclusiveMinimum": 0,
            },
            "legend": {
                "title": "Display legend.",
                "type": "boolean",
                "default": True,
            },
            "axis": {
                "title": "Time axis specification.",
                "oneOf": [
                    {
                        "title": "Display default time axis.",
                        "type": "boolean",
                        "default": True,
                    },
                    {
                        "title": "Time axis details.",
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "absolute": {
                                "title": "Display absolute values for ticks.",
                                "type": "boolean",
                                "default": False,
                            },
                            "color": {
                                "title": "Color of tick lines.",
                                "type": "string",
                                "format": "color",
                                "default": "gray",
                            },
                            "caption": {
                                "title": "Time axis description.",
                                "type": "string",
                            },
                        },
                    },
                ],
            },
            "entries": {
                "title": "Entries in the timelines.",
                "type": "array",
                "items": {
                    "anyOf": [
                        {
                            "title": "Event specification in the timeline.",
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "event": {
                                    "title": "Event at an instant in time.",
                                    "type": "object",
                                    "required": ["label", "instant"],
                                    "additionalProperties": False,
                                    "properties": {
                                        "label": {
                                            "title": "Description of the event.",
                                            "type": "string",
                                        },
                                        "instant": {
                                            "title": "Time of the event.",
                                            "oneOf": [
                                                {
                                                    "title": "Exact time.",
                                                    "type": "number",
                                                },
                                                {
                                                    "title": "Imprecise time.",
                                                    "$ref": "#fuzzy_number",
                                                },
                                            ],
                                        },
                                        "timeline": {
                                            "title": "Timeline to place the event in.",
                                            "type": "string",
                                        },
                                        "marker": {
                                            "title": "Marker for event.",
                                            "enum": constants.MARKERS,
                                            "default": constants.ELLIPSE,
                                        },
                                        "color": {
                                            "title": "Color of the event marker.",
                                            "type": "string",
                                            "format": "color",
                                            "default": "black",
                                        },
                                        "placement": {
                                            "title": "Placement of event label.",
                                            "enum": constants.PLACEMENTS,
                                            "default": constants.RIGHT,
                                        },
                                        "fuzzy": {
                                            "title": "Error bar marker for fuzzy number.",
                                            "type": "boolean",
                                            "default": True,
                                        },
                                    },
                                },
                            },
                        },
                        {
                            "title": "Period specification in the timeline.",
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "period": {
                                    "title": "Period of time.",
                                    "type": "object",
                                    "required": ["label", "begin", "end"],
                                    "additionalProperties": False,
                                    "properties": {
                                        "label": {
                                            "title": "Description of the period.",
                                            "type": "string",
                                        },
                                        "begin": {
                                            "title": "Starting time of the period.",
                                            "oneOf": [
                                                {
                                                    "title": "Exact time.",
                                                    "type": "number",
                                                },
                                                {
                                                    "title": "Imprecise time.",
                                                    "$ref": "#fuzzy_number",
                                                },
                                            ],
                                        },
                                        "end": {
                                            "title": "Ending time of the period.",
                                            "oneOf": [
                                                {
                                                    "title": "Exact time.",
                                                    "type": "number",
                                                },
                                                {
                                                    "title": "Imprecise time.",
                                                    "$ref": "#fuzzy_number",
                                                },
                                            ],
                                        },
                                        "timeline": {
                                            "title": "Timeline to place the period in.",
                                            "type": "string",
                                        },
                                        "color": {
                                            "title": "Color of the period graphic.",
                                            "type": "string",
                                            "format": "color",
                                            "default": "white",
                                        },
                                        "placement": {
                                            "title": "Placement of period label.",
                                            "enum": constants.PLACEMENTS,
                                            "default": constants.CENTER,
                                        },
                                        "fuzzy": {
                                            "title": "Marker to use for fuzzy number.",
                                            "enum": constants.FUZZY_MARKERS,
                                            "default": constants.ERROR,
                                        },
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
        axis=None,
    ):
        super().__init__(title=title, entries=entries)
        assert width is None or (isinstance(width, (int, float)) and width > 0)
        assert legend is None or isinstance(legend, bool)
        assert axis is None or isinstance(axis, (bool, dict))

        self.width = width or self.DEFAULT_WIDTH
        self.legend = True if legend is None else legend
        self.axis = True if axis is None else axis

    def check_entry(self, entry):
        if not isinstance(entry, (Event, Period)):
            raise ValueError(
                f"invalid entry for board: {entry}; not an Event or Period"
            )

    def data_as_dict(self):
        result = super().data_as_dict()
        if self.width != self.DEFAULT_WIDTH:
            result["width"] = self.width
        if self.legend is not None and not self.legend:
            result["legend"] = False
        return result

    def build(self):
        """Create the SVG elements in the 'svg' attribute. Adds the title, if given.
        Set the 'svg' and 'height' attributes.
        Requires the 'width' attribute.
        """
        assert hasattr(self, "width")

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

        # Time axis lines and their labels.
        if self.axis:
            if isinstance(self.axis, dict):
                absolute = bool(self.axis.get("absolute"))
                color = self.axis.get("color") or "gray"
                caption = self.axis.get("caption")
            else:
                absolute = False
                color = "gray"
                caption = None
            self.svg += (axis := Element("g"))
            ticks = dimension.get_ticks(absolute=absolute)
            path = Path(ticks[0].pixel, area_height).V(self.height)
            for tick in ticks[1:]:
                path.M(tick.pixel, area_height).V(self.height)
            path.M(ticks[0].pixel, area_height).H(self.width)
            path.M(ticks[0].pixel, self.height).H(self.width)
            axis += Element("path", d=path, stroke=color)

            axis += (labels := Element("g"))
            labels["text-anchor"] = "middle"
            labels["stroke"] = "none"
            labels["fill"] = "black"
            self.height += self.DEFAULT_FONT_SIZE
            for tick in ticks:
                labels += (
                    label := Element(
                        "text",
                        tick.label,
                        x=utils.N(tick.pixel),
                        y=utils.N(self.height),
                    )
                )
                if tick is ticks[0]:
                    label["text-anchor"] = "start"
                elif tick is ticks[-1]:
                    label["text-anchor"] = "end"
            self.height += self.DEFAULT_FONT_SIZE * (1 + constants.FONT_DESCEND)

            # Time axis caption, if any.
            if caption:
                labels += Element(
                    "text",
                    caption,
                    x=utils.N(
                        dimension.get_pixel((dimension.first + dimension.last) / 2)
                    ),
                    y=self.height,
                )
            self.height += self.DEFAULT_FONT_SIZE * constants.FONT_DESCEND

        # Graphics for entries.
        self.svg += (graphics := Element("g"))
        for entry in self.entries:
            graphics += entry.render_graphic(timelines, dimension)

        # Entry labels after graphics, to render on top.
        self.svg += (labels := Element("g"))
        labels["text-anchor"] = "middle"
        labels["stroke"] = "none"
        labels["fill"] = "black"
        for entry in self.entries:
            if label := entry.render_label(timelines, dimension):
                labels += label

        # Legend labels.
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

    def render_graphic_error(self, instant, timelines, dimension):
        "Get the error bars for the fuzzy instant."
        assert isinstance(instant, dict)
        x = dimension.get_pixel(instant["value"])
        result = Element("g", stroke="black")
        try:  # If 'low' is given, then ignore 'error'.
            xlow = dimension.get_pixel(instant["low"])
        except KeyError:
            xlow = dimension.get_pixel(instant["value"] - instant.get("error", 0))
        result += Element(
            "path",
            d=Path(xlow, timelines[self.timeline] + 0.25 * constants.DEFAULT_SIZE)
            .v(0.5 * constants.DEFAULT_SIZE)
            .m(0, -0.25 * constants.DEFAULT_SIZE)
            .H(x),
        )
        try:  # If 'high' is given, then ignore 'error'.
            xhigh = dimension.get_pixel(instant["high"])
        except KeyError:
            xhigh = dimension.get_pixel(instant["value"] + instant.get("error", 0))
        result += Element(
            "path",
            d=Path(xhigh, timelines[self.timeline] + 0.25 * constants.DEFAULT_SIZE)
            .v(0.5 * constants.DEFAULT_SIZE)
            .m(0, -0.25 * constants.DEFAULT_SIZE)
            .H(x),
        )
        return result


class Event(_Entry):
    "Event at a given instant in a timeline."

    DEFAULT_PLACEMENT = constants.RIGHT
    DEFAULT_MARKER = constants.ELLIPSE

    def __init__(
        self,
        label,
        instant,
        timeline=None,
        marker=None,
        color=None,
        placement=None,
        fuzzy=None,
    ):
        super().__init__(label=label, timeline=timeline, color=color)
        assert isinstance(instant, (int, float, dict))
        assert marker is None or marker in constants.MARKERS
        assert placement is None or placement in constants.PLACEMENTS
        assert fuzzy is None or isinstance(fuzzy, bool)

        self.instant = instant
        self.marker = marker or self.DEFAULT_MARKER
        self.placement = placement or self.DEFAULT_PLACEMENT
        self.fuzzy = fuzzy is None or fuzzy

    def data_as_dict(self):
        result = super().data_as_dict()
        result["instant"] = self.instant
        if self.marker != self.DEFAULT_MARKER:
            result["marker"] = self.marker
        if self.placement != self.DEFAULT_PLACEMENT:
            result["placement"] = self.placement
        if not self.fuzzy:
            result["fuzzy"] = False
        return result

    @property
    def minmax(self):
        if isinstance(self.instant, dict):
            return (
                self.instant.get("low", self.instant["value"]),
                self.instant.get("high", self.instant["value"]),
            )
        else:
            return self.instant

    def render_graphic(self, timelines, dimension):
        if isinstance(self.instant, dict):
            x = dimension.get_pixel(self.instant["value"])
        else:
            x = dimension.get_pixel(self.instant)
        match self.marker:
            case constants.CIRCLE:
                self.label_x_offset = constants.DEFAULT_SIZE / 2
                elem = Element(
                    "circle",
                    cx=utils.N(x),
                    cy=utils.N(timelines[self.timeline] + constants.DEFAULT_SIZE / 2),
                    r=constants.DEFAULT_SIZE / 2,
                )
            case constants.ELLIPSE:
                self.label_x_offset = constants.DEFAULT_SIZE / 5
                elem = Element(
                    "ellipse",
                    cx=utils.N(x),
                    cy=utils.N(timelines[self.timeline] + constants.DEFAULT_SIZE / 2),
                    rx=constants.DEFAULT_SIZE / 5,
                    ry=constants.DEFAULT_SIZE / 2,
                )
            case constants.SQUARE:
                self.label_x_offset = constants.DEFAULT_SIZE / 2
                elem = Element(
                    "rect",
                    x=utils.N(x - constants.DEFAULT_SIZE / 2),
                    y=utils.N(timelines[self.timeline]),
                    width=utils.N(constants.DEFAULT_SIZE),
                    height=utils.N(constants.DEFAULT_SIZE),
                )
            case constants.PYRAMID:
                self.label_x_offset = constants.DEFAULT_SIZE / 2
                path = (
                    Path(x, timelines[self.timeline])
                    .L(
                        x - constants.DEFAULT_SIZE / 2,
                        timelines[self.timeline] + constants.DEFAULT_SIZE,
                    )
                    .h(constants.DEFAULT_SIZE)
                    .Z()
                )
                elem = Element("path", d=path)
            case constants.TRIANGLE:
                self.label_x_offset = constants.DEFAULT_SIZE / 2
                path = (
                    Path(x, timelines[self.timeline] + constants.DEFAULT_SIZE)
                    .L(
                        x - constants.DEFAULT_SIZE / 2,
                        timelines[self.timeline],
                    )
                    .h(constants.DEFAULT_SIZE)
                    .Z()
                )
                elem = Element("path", d=path)
            case constants.NONE:
                self.label_x_offset = 0
                elem = Element("g")
        elem["stroke"] = "none"
        elem["fill"] = self.color or "black"

        # Get error bars if fuzzy value; place below marker itself.
        if self.fuzzy and isinstance(self.instant, dict):
            elem = Element(
                "g", self.render_graphic_error(self.instant, timelines, dimension), elem
            )
        return elem

    def render_label(self, timelines, dimension):
        if not self.label:
            return None
        if not isinstance(self.instant, dict):
            x = dimension.get_pixel(self.instant)

        match self.placement:

            case constants.LEFT:
                if isinstance(self.instant, dict):
                    value = ["value"]
                    try:
                        value = self.instant["low"]
                    except KeyError:
                        value = self.instant["value"] - self.instant.get("error", 0)
                        x = dimension.get_pixel(value)
                x -= self.label_x_offset + constants.DEFAULT_PADDING
                anchor = "end"

            case constants.CENTER:
                anchor = "middle"

            case constants.RIGHT:
                if isinstance(self.instant, dict):
                    value = ["value"]
                    try:
                        value = self.instant["high"]
                    except KeyError:
                        value = self.instant["value"] + self.instant.get("error", 0)
                        x = dimension.get_pixel(value)
                x += self.label_x_offset + constants.DEFAULT_PADDING
                if self.marker == constants.NONE:
                    anchor = "middle"
                else:
                    anchor = "start"
                anchor = "start"

        label = Element(
            "text",
            self.label,
            x=utils.N(x),
            y=utils.N(
                timelines[self.timeline]
                + (constants.DEFAULT_SIZE + self.DEFAULT_FONT_SIZE) / 2
                - self.DEFAULT_FONT_SIZE * constants.FONT_DESCEND
            ),
        )
        label["text-anchor"] = anchor
        return label


class Period(_Entry):
    "Period of time in a timeline."

    DEFAULT_PLACEMENT = constants.CENTER
    DEFAULT_FUZZY = constants.ERROR

    def __init__(
        self, label, begin, end, timeline=None, color=None, placement=None, fuzzy=None
    ):
        super().__init__(label=label, timeline=timeline, color=color)
        assert isinstance(begin, (int, float, dict))
        assert isinstance(end, (int, float, dict))
        assert placement is None or placement in constants.PLACEMENTS
        assert fuzzy is None or isinstance(fuzzy, str)

        self.begin = begin
        self.end = end
        self.placement = placement or self.DEFAULT_PLACEMENT
        self.fuzzy = fuzzy or self.DEFAULT_FUZZY

    def data_as_dict(self):
        result = super().data_as_dict()
        result["begin"] = self.begin
        result["end"] = self.end
        if self.placement != self.DEFAULT_PLACEMENT:
            result["placement"] = self.placement
        if self.fuzzy != self.DEFAULT_FUZZY:
            result["fuzzy"] = self.fuzzy
        return result

    @property
    def minmax(self):
        if isinstance(self.begin, dict):
            low = self.begin.get("low", self.begin["value"])
        else:
            low = self.begin
        if isinstance(self.end, dict):
            high = self.end.get("high", self.end["value"])
        else:
            high = self.end
        return (low, high)

    def render_graphic(self, timelines, dimension):
        # Simple case: do not show fuzzy values, or no fuzzy values.
        if (
            self.fuzzy == constants.NONE
            and not isinstance(self.begin, dict)
            and not isinstance(self.end, dict)
        ):
            result = Element(
                "rect",
                x=utils.N(dimension.get_pixel(self.begin)),
                y=utils.N(timelines[self.timeline]),
                width=utils.N(dimension.get_width(self.begin, self.end)),
                height=constants.DEFAULT_SIZE,
            )
            result["fill"] = self.color or "white"

        # Fuzzy value(s) to be shown.
        else:
            if isinstance(self.begin, dict):
                begin = self.begin["value"]
                try:  # If 'low' is given, then ignore 'error'.
                    low1 = self.begin["low"]
                except KeyError:
                    low1 = begin - self.begin.get("error", 0)
                try:  # If 'high' is given, then ignore 'error'.
                    high1 = self.begin["high"]
                except KeyError:
                    high1 = begin + self.begin.get("error", 0)
                x1 = dimension.get_pixel(low1)
                x2 = dimension.get_pixel(high1)
            else:
                begin = self.begin
                x1 = x2 = dimension.get_pixel(begin)

            if isinstance(self.end, dict):
                end = self.end["value"]
                try:  # If 'low' is given, then ignore 'error'.
                    low2 = self.end["low"]
                except KeyError:
                    low2 = end - self.end.get("error", 0)
                try:  # If 'high' is given, then ignore 'error'.
                    high2 = self.end["high"]
                except KeyError:
                    high2 = end + self.end.get("error", 0)
                x3 = dimension.get_pixel(low2)
                x4 = dimension.get_pixel(high2)
            else:
                end = self.end
                x3 = x4 = dimension.get_pixel(end)

            # The fuzzy regions overlap; adjust.
            if x2 > x3:
                x2 = (x2 + x3) / 2
                x3 = x2

            # Graphics depends on how to show fuzzy values.
            result = Element("g")
            y = timelines[self.timeline]

            match self.fuzzy:

                case constants.ERROR:
                    result += Element(
                        "rect",
                        x=utils.N(dimension.get_pixel(begin)),
                        y=utils.N(y),
                        width=utils.N(dimension.get_width(begin, end)),
                        height=constants.DEFAULT_SIZE,
                        fill=self.color or "white",
                    )
                    if isinstance(self.begin, dict):
                        result += self.render_graphic_error(
                            self.begin, timelines, dimension
                        )
                    if isinstance(self.end, dict):
                        result += self.render_graphic_error(
                            self.end, timelines, dimension
                        )

                case constants.WEDGE:
                    path = (
                        Path(x2, y)
                        .L(x1, y + constants.DEFAULT_SIZE / 2)
                        .L(x2, y + constants.DEFAULT_SIZE)
                    )
                    if x2 < x3:
                        path.H(x3)
                    path.L(x4, y + constants.DEFAULT_SIZE / 2)
                    path.L(x3, y)
                    path.Z()
                    result += Element("path", d=path, fill=self.color or "white")

                case constants.GRADIENT:
                    # The constant-color part of the period.
                    if x2 < x3:
                        # The filled rectangle.
                        result += Element(
                            "rect",
                            x=x2,
                            y=utils.N(y),
                            width=utils.N(x3 - x2),
                            height=constants.DEFAULT_SIZE,
                            stroke="none",
                            fill=self.color or "white",
                        )
                        # The lines at the long edges of the filled rectangle.
                        result += Element(
                            "path",
                            d=Path(x2, y).H(x3).m(0, constants.DEFAULT_SIZE).H(x2),
                            stroke="black",
                        )
                    # The left gradient of the period.
                    if x1 < x2:
                        result += (defs := Element("defs"))
                        # The gradient-filled rectangle.
                        id1 = next(utils.unique_id)
                        defs += (fill1 := Element("linearGradient", id=id1))
                        fill1 += (stop := Element("stop", offset=0))
                        stop["stop-color"] = self.color or "white"
                        stop["stop-opacity"] = 0
                        fill1 += (stop := Element("stop", offset=1))
                        stop["stop-color"] = self.color or "white"
                        stop["stop-opacity"] = 1
                        result += Element(
                            "rect",
                            x=x1,
                            y=utils.N(y),
                            width=utils.N(x2 - x1),
                            height=constants.DEFAULT_SIZE,
                            stroke="none",
                            fill=f"url(#{id1})",
                        )
                        # Lines at the long edges of the gradient-filled rectangle.
                        id2 = next(utils.unique_id)
                        defs += (stroke1 := Element("linearGradient", id=id2))
                        stroke1 += (stop := Element("stop", offset=0))
                        stop["stop-color"] = "black"
                        stop["stop-opacity"] = 0
                        stroke1 += (stop := Element("stop", offset=1))
                        stop["stop-color"] = "black"
                        stop["stop-opacity"] = 1
                        result += Element(
                            "path",
                            d=Path(x1, y).H(x2).m(0, constants.DEFAULT_SIZE).H(x1),
                            stroke=f"url(#{id2})",
                        )

                    else:
                        # Path line at beginning of rectangle.
                        result += Element(
                            "line",
                            x1=utils.N(x1),
                            y1=utils.N(y),
                            x2=utils.N(x1),
                            y2=utils.N(y + constants.DEFAULT_SIZE),
                            stroke="black",
                        )

                    # The right gradient of the period.
                    if x3 < x4:
                        result += (defs := Element("defs"))
                        id3 = next(utils.unique_id)
                        defs += (fill2 := Element("linearGradient", id=id3))
                        fill2 += (stop := Element("stop", offset=0))
                        stop["stop-color"] = self.color or "white"
                        stop["stop-opacity"] = 1
                        fill2 += (stop := Element("stop", offset=1))
                        stop["stop-color"] = self.color or "white"
                        stop["stop-opacity"] = 0
                        # The gradient-filled rectangle.
                        result += Element(
                            "rect",
                            x=utils.N(x3),
                            y=utils.N(y),
                            width=utils.N(x4 - x3),
                            height=constants.DEFAULT_SIZE,
                            stroke="none",
                            fill=f"url(#{id3})",
                        )
                        # Lines at the long edges of the gradient-filled rectangle.
                        id4 = next(utils.unique_id)
                        defs += (stroke2 := Element("linearGradient", id=id4))
                        stroke2 += (stop := Element("stop", offset=0))
                        stop["stop-color"] = "black"
                        stop["stop-opacity"] = 1
                        stroke2 += (stop := Element("stop", offset=1))
                        stop["stop-color"] = "black"
                        stop["stop-opacity"] = 0
                        result += Element(
                            "path",
                            d=Path(x3, y).H(x4).m(0, constants.DEFAULT_SIZE).H(x3),
                            stroke=f"url(#{id4})",
                        )

                    else:
                        # Path line at end of rectangle.
                        result += Element(
                            "line",
                            x1=utils.N(x3),
                            y1=utils.N(y),
                            x2=utils.N(x3),
                            y2=utils.N(y + constants.DEFAULT_SIZE),
                            stroke="black",
                        )

                case constants.TAPER:
                    raise NotImplementedError
        return result

    def render_label(self, timelines, dimension):
        if not self.label:
            return None
        if isinstance(self.begin, dict):
            begin = self.begin["value"]
            try:
                low = self.begin["low"]
            except KeyError:
                low = begin - self.begin.get("error", 0)
        else:
            begin = self.begin
            low = begin
        if isinstance(self.end, dict):
            end = self.end["value"]
            try:
                high = self.end["low"]
            except KeyError:
                high = end + self.end.get("error", 0)
        else:
            end = self.end
            high = end

        color = "black"
        match self.placement:

            case constants.LEFT:
                x = dimension.get_pixel(low) - constants.DEFAULT_PADDING
                anchor = "end"

            case constants.CENTER:
                x = dimension.get_pixel((begin + end) / 2)
                anchor = "middle"
                if self.color:
                    color = Color(self.color).best_contrast

            case constants.RIGHT:
                x = dimension.get_pixel(high) + constants.DEFAULT_PADDING
                anchor = "start"

        label = Element(
            "text",
            self.label,
            x=utils.N(x),
            y=utils.N(
                timelines[self.timeline]
                + (constants.DEFAULT_SIZE + self.DEFAULT_FONT_SIZE) / 2
                - self.DEFAULT_FONT_SIZE * constants.FONT_DESCEND
            ),
            fill=color,
        )
        label["text-anchor"] = anchor
        return label


register(Timelines)
register(Event)
register(Period)
