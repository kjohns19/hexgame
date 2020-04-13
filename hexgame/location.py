import math


X_SCALE = 20
Y_SCALE = X_SCALE * math.cos(math.pi/6)


class Location:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def real_pos(self):
        xx = self._x * X_SCALE - (self._y % 2) * X_SCALE // 2
        yy = self._y * Y_SCALE
        return (xx, yy)

    def in_direction(self, dir):
        even = self._y % 2 == 0
        return Location(
            x=self._x + (dir.even_x if even else dir.odd_x),
            y=self._y + dir.y)

    def __eq__(self, loc):
        return self._x == loc._x and self._y == loc._y

    def __hash__(self):
        return hash((self._x, self._y))

    def __repr__(self):
        return f'({self._x}, {self._y})'


class Direction:
    def __init__(self, name, idx, even_x, odd_x, y):
        self.name = name
        self.idx = idx
        self.even_x = even_x
        self.odd_x = odd_x
        self.y = y

    @classmethod
    def dirs(cls):
        return cls._dirs

    def turn(self, amount):
        new_idx = (self.idx + amount) % 6
        return Direction._dirs[new_idx]

    def left(self):
        return self.turn(-1)

    def right(self):
        return self.turn(1)

    def __repr__(self):
        return self.name


Direction.E = Direction('E', 0, 1, 1, 0)
Direction.SE = Direction('SE', 1, 1, 0, 1)
Direction.SW = Direction('SW', 2, 0, -1, 1)
Direction.W = Direction('W', 3, -1, -1, 0)
Direction.NW = Direction('NW', 4, 0, -1, -1)
Direction.NE = Direction('NE', 5, 1, 0, -1)
Direction._dirs = (
    Direction.E, Direction.SE, Direction.SW, Direction.W, Direction.NW, Direction.NE
)
