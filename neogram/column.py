"Diagrams stacked in a column."

__all__ = ["Column"]

from diagram import *


class Column(Container):

    ALIGN_VALUES = constants.HORIZONTAL

    DEFAULT_TITLE_FONT_SIZE = 22
    DEFAULT_ALIGN = constants.CENTER
    DEFAULT_PADDING = 10

    SCHEMA = {
        "title": __doc__,
        "$anchor": "column",
        "type": "object",
        "required": ["entries"],
        "additionalProperties": False,
        "properties": {
            "title": {
                "title": "Title of the column diagram.",
                "$ref": "#text",
            },
            "align": {
                "title": "Align diagrams horizontally within the column.",
                "enum": ALIGN_VALUES,
                "default": DEFAULT_ALIGN,
            },
            "entries": {
                "title": "Component diagrams in the column.",
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
        dict([(k, {"$ref": f"#{k}_ref"}) for k in constants.DIAGRAMS])
    )

    def build(self):
        """Create the SVG elements in the 'svg' attribute. Adds the title, if given.
        Set the 'svg' and 'height' attributes.
        Sets the 'width' attribute.
        """
        for entry in self.entries:
            entry.build()

        self.width = max([e.width for e in self.entries])

        super().build()

        height = self.height
        self.height += sum([e.height for e in self.entries])
        self.height += (len(self.entries) - 1) * self.DEFAULT_PADDING

        for entry in self.entries:
            match self.align:
                case constants.LEFT:
                    x = 0
                case constants.CENTER:
                    x = (self.width - entry.width) / 2
                case constants.RIGHT:
                    x = self.width - entry.width
            self.svg += Element("g", entry.svg, transform=f"translate({x}, {height})")
            height += entry.height + self.DEFAULT_PADDING


register(Column)
