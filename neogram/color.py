"Neogram: Color and Palette classes."

from icecream import ic

import itertools

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

    def best_contrast(self):
        "Return white or black that contrasts best with this color."
        if self.luminance < 140:
            return Color("white")
        else:
            return Color("black")


class Palette:
    "Ordered set of colors."

    def __init__(self, *colors):
        self.colors = []
        for color in colors:
            self.add(Color(to_hex(color)))

    def __repr__(self):
        return f"Palette({', '.join([str(c) for c in self.colors])})"

    def __iadd__(self, other):
        self.add(other)
        return self

    def __len__(self):
        return len(self.colors)

    def __eq__(self, other):
        if isinstance(other, Palette):
            if len(self) != len(other):
                return False
            return all([c1 == c2 for c1, c2 in zip(self.colors, other.colors)])

    def __iter__(self):
        return iter(self.colors)

    def add(self, color):
        self.colors.append(color)

    def cycle(self):
        "Return an eternally cycling iterator over the current colors."
        return itertools.cycle(self.colors[:])
