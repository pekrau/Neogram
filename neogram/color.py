"Color and Palette classes."

__all__ = ["Color"]

import webcolors


def to_hex(value):
    "Convert value to a hex specification."
    match value:
        case str():
            if value.startswith("#"):
                return webcolors.normalize_hex(value)
            else:
                return webcolors.name_to_hex(value)
        case Color():
            return value.hex
        case (int(), int(), int()) | [int(), int(), int()]:
            return webcolors.rgb_to_hex(value)
    raise ValueError("invalid color specification")


class Color:
    "Color defined by hex, name or rgb triple. Immutable."

    def __init__(self, value):
        assert isinstance(value, (str, tuple, list, Color))
        self._hex = to_hex(value)

    def __str__(self):
        "Return the named color, if any, or the hex code."
        try:
            return self.name
        except ValueError:
            return self._hex

    def __eq__(self, other):
        match other:
            case Color():
                return self.hex == other.hex
            case str():
                return self.name == other or self.hex == other
        return False

    @property
    def hex(self):
        return self._hex

    @property
    def rgb(self):
        return tuple(webcolors.hex_to_rgb(self._hex))

    @property
    def name(self):
        "Return the name for the color. Raise ValueError if none."
        return webcolors.hex_to_name(self._hex)

    @property
    def luminance(self):
        r, g, b = self.rgb
        # From https://nemecek.be/blog/172/how-to-calculate-contrast-color-in-python
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    @property
    def best_contrast(self):
        "Return white or black that contrasts best with this color."
        if self.luminance < 140:
            return Color("white")
        else:
            return Color("black")
