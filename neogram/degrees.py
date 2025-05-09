"Angle specified in degrees. Immutable."

__all__ = ["Degrees"]

import math
import functools


@functools.total_ordering
class Degrees:
    "Handle angle specified in degrees, yields value in radians."

    @classmethod
    def from_radians(cls, radians):
        assert isinstance(radians, (int, float))
        return Degrees(180.0 * radians / math.pi)

    def __init__(self, degrees):
        assert isinstance(degrees, (int, float))
        self._degrees = degrees

    def __add__(self, other):
        assert isinstance(other, (int, float, Degrees))
        if isinstance(other, Degrees):
            return Degrees(self.degrees + other.degrees)
        else:
            return Degrees(self.degrees + other)

    def __sub__(self, other):
        assert isinstance(other, (int, float, Degrees))
        if isinstance(other, Degrees):
            return Degrees(self.degrees - other.degrees)
        else:
            return Degrees(self.degrees - other)

    def __mul__(self, other):
        assert isinstance(other, (int, float))
        return Degrees(other * self.degrees)

    def __rmul__(self, other):
        assert isinstance(other, (int, float))
        return Degrees(other * self.degrees)

    def __truediv__(self, other):
        assert isinstance(other, (int, float))
        return Degrees(self.degrees / other)

    def __lt__(self, other):
        assert isinstance(other, (int, float, Degrees))
        if isinstance(other, Degrees):
            return self._degrees < other._degrees
        elif isinstance(other, (int, float)):
            return self._degrees < other
        return self._degrees < other._degrees

    def __eq__(self, other):
        if isinstance(other, Degrees):
            return self._degrees == other._degrees
        elif isinstance(other, (int, float)):
            return self._degrees == other
        else:
            return False

    def __neg__(self):
        return Degrees(-self.degrees)

    def __float__(self):
        "Angle in radians."
        return self.degrees * math.pi / 180.0

    def __repr__(self):
        return f"Degrees({self.degrees:g})"

    @property
    def degrees(self):
        return self._degrees

    @property
    def radians(self):
        return float(self)

    def normalized(self):
        "Return the angle normalized to within [-180, 180]."
        if (degrees := self.degrees % 360.0) > 180.0:
            degrees -= 360.0
        if degrees < -180.0:
            degrees += 360.0
        return Degrees(degrees)
