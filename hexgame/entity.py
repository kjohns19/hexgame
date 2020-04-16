# import logging

from . import location
from . import util


class Entity:
    def __init__(self):
        self._dir = location.Direction.E
        self._color = util.draw.Color.WHITE
        self._circle = util.draw.Circle(
            position=(0, 0), radius=location.X_SCALE//2,
            color=self._color)

        self._loc = None
        self._layer = None

    @property
    def loc(self):
        return self._loc

    @loc.setter
    def loc(self, value):
        self._loc = value
        if self._loc is None:
            self._circle.update(visible=False)
        else:
            self._circle.update(position=self._loc.real_pos(), visible=True)

    @property
    def location(self):
        return self._loc

    def try_move(self, loc):
        assert self._layer is not None, 'Can\'t move an entity not in a layer!'
        return self._layer.move_entity(self, loc)

    def update(self, game):
        new_loc = self._loc.in_direction(self._dir)
        new_dir = self._dir.turn(game.rand.randint(-2, 2)//2)
        self._dir = new_dir
        self.try_move(new_loc)
