"Diagrams stacked in a column."

__all__ = ["Column"]

from diagram import *
import utils


class Column(Diagram):

    DEFAULT_FONT_SIZE = 18
    DEFAULT_ALIGN = "center"

    SCHEMA = {
        "title": "Diagrams stacked in a column.",
        "$anchor": "column",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"$ref": "#title"},
            "width": {"$ref": "#width"},
            "align": {
                "title": "Align diagrams horizontally within the column.",
                "enum": ["left", "center", "right"],
                "default": DEFAULT_ALIGN,
            },
            "entries": {
                "title": "Component diagrams in the column.",
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "timelines": {"$ref": "#timelines"},
                        "piechart": {"$ref": "#piechart"},
                        "column": {"$ref": "#column"},
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

        for entry in self.entries:
            match self.align:
                case "left":
                    x = 0
                case "center":
                    x = (self.width - entry.width) / 2
                case "right":
                    x = self.width - entry.width
                case _:
                    raise ValueError(f"invalid value for 'align': '{self.align}'")
            self.svg += Element(
                "g", entry.svg, transform=f"translate({x}, {self.height})"
            )
            self.height += entry.height + constants.DEFAULT_PADDING


register(Column)
