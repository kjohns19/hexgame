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

        @self._window.event
        def on_draw():
            self._window.clear()
            pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
            pyglet.gl.glBlendFunc(
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
            self.draw()

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

    def draw(self):
        logging.debug('Draw')
        state = util.draw.DrawState(origin=(400, 400), translation=None, scale=1)

        radian_offset = math.pi/6
        count = 10
        for x in range(-count, count):
            for y in range(-count, count):
                loc = location.Location(x, y)
                util.draw.circle(
                    state, loc.real_pos(), location.X_SCALE/2-1,
                    num_vertices=6, radian_offset=radian_offset, fill=False)

        self._world.draw(state)

        state.batch.draw()

    def update(self, dt):
        logging.debug(f'Update (dt={dt})')
        self._tick += 1
        self._world.update(self)

    def run(self):
        logging.debug('Running')
        pyglet.app.run()
