"Diagrams stacked in a column."

__all__ = ["Column"]

from diagram import *


class Column(Diagram):

    DEFAULT_FONT_SIZE = 18
    DEFAULT_ALIGN = constants.CENTER

    SCHEMA = {
        "title": __doc__,
        "$anchor": "column",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"$ref": "#title"},
            "align": {
                "title": "Align diagrams horizontally within the column.",
                "enum": constants.HORIZONTAL_ALIGN,
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
            isinstance(align, str) and align in constants.HORIZONTAL_ALIGN
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

        self.width = max([e.width for e in self.entries])

        super().build()

        for entry in self.entries:
            match self.align:
                case constants.LEFT:
                    x = 0
                case constants.CENTER:
                    x = (self.width - entry.width) / 2
                case constants.RIGHT:
                    x = self.width - entry.width
            self.svg += Element(
                "g", entry.svg, transform=f"translate({x}, {self.height})"
            )
            self.height += entry.height


register(Column)
