"Neogram: Two-dimensional vector (x, y). Immutable."

import math


class Vector2:
    "Two-dimensional vector (x, y). Immutable."

    @classmethod
    def from_polar(cls, r, phi):
        "Return a Vector2 instance defined by polar coordinates (radians)."
        assert isinstance(r, (float, int))
        assert isinstance(phi, (float, int))
        return Vector2(r * math.cos(phi), r * math.sin(phi))

    def __init__(self, x, y):
        assert isinstance(x, (float, int))
        assert isinstance(y, (float, int))
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"

    def __str__(self):
        return f"Vector2({self.x:g}, {self.y:g})"

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __add__(self, other):
        assert isinstance(other, Vector2)
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        assert isinstance(other, Vector2)
        return Vector2(self.x - other.x, self.y - other.y)

    def __truediv__(self, other):
        assert isinstance(other, (float, int))
        return Vector2(self.x / other, self.y / other)

    def __rmul__(self, other):
        assert isinstance(other, (float, int))
        return Vector2(other * self.x, other * self.y)

    def __float__(self):
        return abs(self)

    def __complex__(self):
        return complex(self.x, self.y)

    @property
    def normalized(self):
        return Vector2(self.x / (length := abs(self)), self.y / length)

    @property
    def r(self):
        "Return the radius part of the polar coordinates."
        return abs(self)

    @property
    def phi(self):
        "Return the angle part of the polar coordinates (radians)."
        return math.atan2(self.y, self.x)

    @property
    def polar(self):
        "Return the tuple (r, phi) for this instance (radians)."
        return (self.r, self.phi)


if __name__ == "__main__":
    v = Vector2(1, 2)
    print(v.normalized)
