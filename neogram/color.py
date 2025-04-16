"Neogram: Color and Palette classes."

import itertools

import webcolors


def to_hex(value):
    "Convert value to a hex specification."
    if isinstance(value, str):
        if value.startswith("#"):
            return webcolors.normalize_hex(value)
        else:
            return webcolors.name_to_hex(value)
    elif isinstance(value, Color):
        return value.hex
    elif isinstance(value, (tuple, list)) and len(value) == 3:
        return webcolors.rgb_to_hex(value)
    else:
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


class Palette:
    "Ordered set of colors."

    def __init__(self, *colors):
        self.colors = []
        for color in colors:
            self.add(Color(to_hex(color)))

    def __iadd__(self, other):
        self.add(other)
        return self

    def add(self, color):
        self.colors.append(color)

    def cycle(self):
        "Return an eternally cycling iterator over the current colors."
        return itertools.cycle(self.colors[:])
