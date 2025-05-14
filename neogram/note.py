"Textual note with header, body and footer text."

__all__ = ["Note"]

import constants
from diagram import *
from dimension import *
from path import *
import utils


class Note(Diagram):
    "Textual note with header, body and footer text."

    DEFAULT_WIDTH = 200
    DEFAULT_FRAME = 5
    DEFAULT_COLOR = "gold"
    DEFAULT_BACKGROUND = "lightyellow"
    DEFAULT_LINE = 1
    DEFAULT_RADIUS = 10

    SCHEMA = {
        "title": __doc__,
        "$anchor": "note",
        "type": "object",
        "additionalProperties": False,
        "minProperties": 1,
        "properties": {
            "header": {
                "title": "Header of the note.",
                "$ref": "#text",
            },
            "body": {
                "title": "Body of the note.",
                "$ref": "#text",
            },
            "footer": {
                "title": "Footer of the note.",
                "$ref": "#text",
            },
            "width": {
                "title": "Width of chart, in pixels.",
                "type": "number",
                "default": DEFAULT_WIDTH,
                "exclusiveMinimum": 0,
            },
            "frame": {
                "title": "Thickness of the frame.",
                "type": "number",
                "minimum": 0,
                "default": DEFAULT_FRAME,
            },
            "color": {
                "title": "Color of the note frame and lines.",
                "type": "string",
                "format": "color",
                "default": DEFAULT_COLOR,
            },
            "radius": {
                "title": "Radius of the frame edge curvature.",
                "type": "number",
                "default": DEFAULT_RADIUS,
                "minimum": 0,
            },
            "line": {
                "title": "Thickness of lines between sections.",
                "type": "number",
                "minimum": 0,
                "default": DEFAULT_LINE,
            },
            "background": {
                "title": "Background color of the note.",
                "type": "string",
                "format": "color",
                "default": DEFAULT_BACKGROUND,
            },
        },
    }

    def __init__(
        self,
        header=None,
        body=None,
        footer=None,
        width=None,
        frame=None,
        color=None,
        radius=None,
        line=None,
        background=None,
    ):
        super().__init__()
        assert header is None or isinstance(header, (str, dict))
        assert body is None or isinstance(body, (str, dict))
        assert footer is None or isinstance(footer, (str, dict))
        assert width is None or isinstance(width, (int, float))
        assert frame is None or isinstance(frame, (int, float))
        assert color is None or isinstance(color, str)
        assert radius is None or isinstance(radius, (int, float))
        assert line is None or isinstance(line, (int, float))
        assert background is None or isinstance(background, str)

        self.header = header
        self.body = body
        self.footer = footer
        self.width = width or self.DEFAULT_WIDTH
        self.frame = self.DEFAULT_FRAME if frame is None else frame
        self.color = color or self.DEFAULT_COLOR
        self.radius = self.DEFAULT_RADIUS if radius is None else radius
        self.line = self.DEFAULT_LINE if line is None else line
        self.background = background or self.DEFAULT_BACKGROUND

    def data_as_dict(self):
        result = {}  # Reimplement; do not extend from Diagram.
        if self.header:
            result["header"] = self.header
        if self.body:
            result["body"] = self.body
        if self.footer:
            result["footer"] = self.footer
        if self.frame != self.DEFAULT_FRAME:
            result["frame"] = self.frame
        if self.color != self.DEFAULT_COLOR:
            result["color"] = self.color
        if self.radius != self.DEFAULT_RADIUS:
            result["radius"] = self.radius
        if self.line != self.DEFAULT_LINE:
            result["line"] = self.line
        if self.background != self.DEFAULT_BACKGROUND:
            result["background"] = self.background
        return result

    def data_as_dict_entries(self):
        return {}

    def build(self):
        """Create the SVG elements in the 'svg' attribute. Adds the title, if given.
        Set the 'svg' and 'height' attributes.
        Requires the 'width' attribute.
        """
        assert hasattr(self, "width")

        super().build()
        self.svg += (
            rect := Element(
                "rect",
                x=self.frame / 2,
                y=self.frame / 2,
                rx=self.radius,
                ry=self.radius,
                width=self.width - self.frame,
                fill=self.background,
                stroke=self.color,
            )
        )
        rect["stroke-width"] = self.frame

        self.height = 2 * constants.DEFAULT_PADDING

        header, height = self.get_text(self.header)
        if header:
            self.svg += header
            self.height += height + constants.DEFAULT_PADDING
            if self.line:
                self.height += constants.DEFAULT_PADDING

        body, height = self.get_text(self.body)
        if body:
            if self.line and header:
                self.svg += (
                    line := Element(
                        "line",
                        x1=0,
                        y1=utils.N(self.height),
                        x2=utils.N(self.width),
                        y2=utils.N(self.height),
                        stroke=self.color,
                    )
                )
                line["stroke-width"] = utils.N(self.line)
                self.height += self.line

            self.svg += body
            self.height += height + constants.DEFAULT_PADDING
            if self.line:
                self.height += constants.DEFAULT_PADDING

        footer, height = self.get_text(self.footer)
        if footer:
            if self.line and (body or (header and not body)):
                # self.height += constants.DEFAULT_PADDING
                self.svg += (
                    line := Element(
                        "line",
                        x1=0,
                        y1=utils.N(self.height),
                        x2=utils.N(self.width),
                        y2=utils.N(self.height),
                        stroke=self.color,
                    )
                )
                line["stroke-width"] = utils.N(self.line)
                self.height += self.line

            self.svg += footer
            self.height += height + constants.DEFAULT_PADDING

        # self.height += constants.DEFAULT_PADDING
        rect["height"] = utils.N(self.height)
        self.height += self.frame

    def get_text(self, text):
        "Return tuple (g with text elements, height)."
        if not text:
            return None, 0
        result = Element("g", stroke="none")
        if isinstance(text, dict):
            result["fill"] = text.get("color") or "black"
            placement = text.get("placement") or constants.CENTER
            match placement:
                case constants.LEFT:
                    offset = (
                        -self.width / 2 + self.frame / 2 + constants.DEFAULT_PADDING
                    )
                    result["text-anchor"] = constants.START
                case constants.CENTER:
                    offset = 0
                    result["text-anchor"] = constants.MIDDLE
                case constants.RIGHT:
                    offset = (
                        +self.width / 2 - 3 * self.frame / 2 - constants.DEFAULT_PADDING
                    )
                    result["text-anchor"] = constants.END
            try:
                size = text["size"]
                result["font-size"] = utils.N(size)
            except KeyError:
                size = self.DEFAULT_FONT_SIZE
            if text.get("bold"):
                result["font-weight"] = "bold"
            if text.get("italic"):
                result["font-style"] = "italic"
            lines = text["text"].split("\n")
        else:
            result["fill"] = "black"
            offset = 0
            result["text-anchor"] = "middle"
            size = self.DEFAULT_FONT_SIZE
            lines = text.split("\n")
        height = 0
        for line in lines:
            result += Element("text", line, x=0, y=utils.N(height))
            height += size
        x = (self.frame + self.width) / 2 + offset
        y = self.height + size + constants.DEFAULT_PADDING
        result["transform"] = f"translate({utils.N(x)}, {utils.N(y)})"
        height += size * constants.FONT_DESCEND
        return result, height


register(Note)
