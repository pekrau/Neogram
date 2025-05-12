"Diagrams arranged in a row."

__all__ = ["Row"]

from diagram import *


class Row(Diagram):

    DEFAULT_FONT_SIZE = 18
    DEFAULT_ALIGN = constants.MIDDLE

    SCHEMA = {
        "title": __doc__,
        "$anchor": "row",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {
                "title": "Title of the column diagram.",
                "$ref": "#text",
            },
            "align": {
                "title": "Align diagrams vertically within the row.",
                "enum": constants.VERTICAL_ALIGN,
                "default": DEFAULT_ALIGN,
            },
            "entries": {
                "title": "Component diagrams in the row.",
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "timelines": {"$ref": "#timelines"},
                        "piechart": {"$ref": "#piechart"},
                        "column": {"$ref": "#column"},
                        "row": {"$ref": "#row"},
                    },
                },
            },
        },
    }

    def __init__(
        self,
        title=None,
        entries=None,
        align=None,
    ):
        super().__init__(title=title, entries=entries)
        assert align is None or (
            isinstance(align, str) and align in constants.VERTICAL_ALIGN
        )

        self.align = align or self.DEFAULT_ALIGN

    def check_entry(self, entry):
        return isinstance(entry, Diagram)

    def data_as_dict(self):
        result = super().data_as_dict()
        if self.align != self.DEFAULT_ALIGN:
            result["align"] = self.align
        return result

    def build(self):
        "Set the 'svg' and 'height' attributes."
        for entry in self.entries:
            entry.build()

        self.width = sum([e.width for e in self.entries])

        super().build()

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
            x += entry.width + constants.DEFAULT_PADDING

        self.height += max_height


register(Row)
