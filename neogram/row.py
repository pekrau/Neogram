"Diagrams arranged in a row."

__all__ = ["Row"]

from diagram import *


class Row(Container):

    ALIGN_VALUES = constants.VERTICAL

    DEFAULT_TITLE_FONT_SIZE = 22
    DEFAULT_ALIGN = constants.MIDDLE
    DEFAULT_PADDING = 10

    SCHEMA = {
        "title": __doc__,
        "$anchor": "row",
        "type": "object",
        "required": ["entries"],
        "additionalProperties": False,
        "properties": {
            "title": {
                "title": "Title of the column diagram.",
                "$ref": "#text",
            },
            "align": {
                "title": "Align diagrams vertically within the row.",
                "enum": ALIGN_VALUES,
                "default": DEFAULT_ALIGN,
            },
            "entries": {
                "title": "Component diagrams in the row.",
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    # The allowed diagram properties are loaded below.
                    "properties": {},
                },
            },
        },
    }

    # Load the allowed diagram properties.
    SCHEMA["properties"]["entries"]["items"]["properties"].update(
        dict([(k, {"$ref": f"#{k}_ref"}) for k in constants.COMPOSABLE_DIAGRAMS])
    )

    def build(self):
        """Create the SVG elements in the 'svg' attribute. Adds the title, if given.
        Set the 'svg' and 'height' attributes.
        Sets the 'width' attribute.
        """
        for entry in self.entries:
            entry.build()

        self.width = sum([e.width for e in self.entries])
        self.width += (len(self.entries) - 1) * self.DEFAULT_PADDING

        super().build()
        self.height += self.DEFAULT_PADDING

        x = 0
        max_height = max([e.height for e in self.entries])

        for entry in self.entries:
            match self.align:
                case constants.BOTTOM:
                    y = self.height + max_height - entry.height
                case constants.MIDDLE:
                    y = self.height + (max_height - entry.height) / 2
                case constants.TOP:
                    y = self.height
            self.svg += Element("g", entry.svg, transform=f"translate({x}, {y})")
            x += entry.width + self.DEFAULT_PADDING

        self.height += max_height


register(Row)
