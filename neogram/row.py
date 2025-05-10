"Diagrams arranged in a row."

__all__ = ["Row"]

from diagram import *


class Row(Diagram):

    DEFAULT_FONT_SIZE = 18
    DEFAULT_ALIGN = "center"

    SCHEMA = {
        "title": "Diagrams stacked in a row.",
        "$anchor": "row",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"$ref": "#title"},
            "width": {"$ref": "#width"},
            "align": {
                "title": "Align diagrams vertically within the row.",
                "enum": ["bottom", "center", "top"],
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
        width=None,
        entries=None,
        align=None,
    ):
        super().__init__(title=title, width=width, entries=entries)
        assert align is None or isinstance(align, str)

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
        super().build()

        for entry in self.entries:
            entry.build()

        x = 0
        max_height = max([e.height for e in self.entries])

        for entry in self.entries:
            match self.align:
                case "bottom":
                    y = self.height + max_height - entry.height
                case "center":
                    y = self.height + (max_height - entry.height) / 2
                case "top":
                    y = self.height
                case _:
                    raise ValueError(f"invalid value for 'align': '{self.align}'")
            self.svg += Element(
                "g", entry.svg, transform=f"translate({x}, {y})"
            )
            x += entry.width + constants.DEFAULT_PADDING

        self.height += max_height

register(Row)
