import logging
import math
import pyglet
import random

from . import location
from . import util
from . import world


class Game:
    def __init__(self, window):
        self._window = window
        self._tick = 0
        self._world = world.World(1)
        self._rand = random.Random()
        self._grid = self._create_grid()

        @self._window.event
        def on_draw():
            logging.debug('Draw')
            self._window.clear()
            util.draw.state().draw()

        pyglet.clock.schedule_interval(self.update, 1/10)

    @property
    def world(self):
        return self._world

    @property
    def tick(self):
        return self._tick

    @property
    def rand(self):
        return self._rand

    def _create_grid(self):
        grid = []
        count = 10
        radian_offset = math.pi/6
        for y in range(-count, count):
            row = []
            for x in range(-count, count):
                loc = location.Location(x, y)
                row.append(util.draw.Circle(
                    loc.real_pos(), location.X_SCALE/2-1,
                    num_vertices=6, radian_offset=radian_offset,
                    fill=False))
            grid.append(row)
        return grid

    def update(self, dt):
        logging.debug(f'Update (dt={dt})')
        self._tick += 1
        self._world.update(self)

    def run(self):
        logging.debug('Running')
        pyglet.app.run()
