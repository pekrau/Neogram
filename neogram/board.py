"Diagram to place diagrams at specified positions. Must be a top-level diagram."

__all__ = ["Board"]

from diagram import *


class Board(Diagram):
    """Diagram to place diagrams at specified positions.
    Must be a top-level diagram.
    """

    DEFAULT_TITLE_FONT_SIZE = 36

    SCHEMA = {
        "title": __doc__,
        "$anchor": "board",
        "type": "object",
        "required": ["entries"],
        "additionalProperties": False,
        "properties": {
            "title": {
                "title": "Title of the board.",
                "$ref": "#text",
            },
            "entries": {
                "title": "Diagrams at specified positions.",
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["x", "y"],
                    "minProperties": 3,
                    "maxProperties": 4,
                    "additionalProperties": False,
                    "properties": {
                        "x": {
                            "title": "Absolute position in board. Zero at left.",
                            "type": "number",
                            "minimum": 0,
                        },
                        "y": {
                            "title": "Absolute position in board. Zero at top.",
                            "type": "number",
                            "minimum": 0,
                        },
                        "scale": {
                            "title": "Scaling of diagram.",
                            "type": "number",
                            "exclusiveMinimum": 0,
                            "default": 1,
                        },
                        # The allowed diagram properties are loaded below.
                    },
                },
            },
        },
    }

    # Load the allowed diagram properties.
    SCHEMA["properties"]["entries"]["items"]["properties"].update(
        dict([(k, {"$ref": f"#{k}_ref"}) for k in constants.COMPOSABLE_DIAGRAMS])
    )

    def append(self, *entry, **fields):
        "Append the entry to the diagram."
        assert not entry or (len(entry) == 1 and isinstance(entry[0], dict))
        assert bool(fields) ^ bool(entry)
        if entry:
            entry = entry[0]
        else:
            entry = fields
        self.check_entry(entry)
        self.entries.append(entry)

    def check_entry(self, entry):
        if not isinstance(entry, dict):
            raise ValueError(f"invalid entry for board: {entry}; not a dict")
        for key in constants.COMPOSABLE_DIAGRAMS:
            data = entry.get(key)
            if data:
                # No need to use 'memo' here; board cannot refer to another board.
                if isinstance(data, dict):
                    data = parse(key, entry[key])
                entry["diagram"] = data
                break
        else:
            raise ValueError(f"invalid entry for board: {entry}")

    def data_as_dict_entries(self):
        result = []
        for entry in self.entries:
            entry2 = {"x": entry["x"], "y": entry["y"]}
            if scale := entry.get("scale"):
                entry2["scale"] = scale
            entry2.update(entry["diagram"].as_dict())
            result.append(entry2)
        return {"entries": result}

    def build(self):
        """Create the SVG elements in the 'svg' attribute.
        Set the 'svg' and 'height' attributes.
        Sets the 'width' attribute.
        """
        for entry in self.entries:
            entry["diagram"].build()

        self.width = 0
        for entry in self.entries:
            diagram = entry["diagram"]
            scale = entry.get("scale") or 1
            self.width = max(self.width, entry["x"] + scale * diagram.width)

        super().build()

        offset = self.height
        for entry in self.entries:
            diagram = entry["diagram"]
            scale = entry.get("scale") or 1
            transform = []
            try:
                transform.append(f"scale({entry['scale']})")
            except KeyError:
                pass
            transform.append(f"translate({entry['x']}, {entry['y'] + offset})")
            g = Element("g", transform=" ".join(transform))
            g.append(diagram.svg)
            self.svg += g
            self.height = max(self.height, entry["y"] + offset + scale * diagram.height)


register(Board)
