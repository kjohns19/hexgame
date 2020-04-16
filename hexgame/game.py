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
        self._world = world.World(1)
        self._rand = random.Random()
        self._grid = self._create_grid()
        self._keys = pyglet.window.key.KeyStateHandler()
        self._view_controller = ViewController(util.draw.state().view)

        @self._window.event
        def on_draw():
            logging.debug('Draw')
            self._window.clear()
            util.draw.state().draw()

        self._window.push_handlers(self._keys)
        pyglet.clock.schedule_interval(self.update, 1/10)

    @property
    def world(self):
        return self._world

    def key_pressed(self, key):
        return self._keys[key]

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
        self._view_controller.update(self)
        self._world.update(self)

    def run(self):
        logging.debug('Running')
        pyglet.app.run()


class ViewController:
    def __init__(self, view):
        self._view = view
        self._xy_speed = (0, 0)

    def _accelerate(self, game, amount, max_speed):
        key = pyglet.window.key
        x = game.key_pressed(key.LEFT) - game.key_pressed(key.RIGHT)
        y = game.key_pressed(key.DOWN) - game.key_pressed(key.UP)
        if x and y:
            sqrt_half = math.sqrt(1/2)
            x *= sqrt_half
            y *= sqrt_half
        self._xy_speed = (
            max(-max_speed, min(self._xy_speed[0] + amount*x, max_speed)),
            max(-max_speed, min(self._xy_speed[1] + amount*y, max_speed))
        )

    def _deccelerate(self, amount):
        speed_sqr = self._xy_speed[0]**2 + self._xy_speed[1]**2
        if speed_sqr > amount**2:
            speed = math.sqrt(speed_sqr)
            x = amount * self._xy_speed[0] / speed
            y = amount * self._xy_speed[1] / speed
            self._xy_speed = (self._xy_speed[0] - x, self._xy_speed[1] - y)
        else:
            self._xy_speed = (0, 0)

    def update(self, game):
        accel = 2.5
        max_speed = 25
        self._accelerate(game, accel*2, max_speed)
        self._deccelerate(accel)
        if self._xy_speed != (0, 0):
            util.draw.state().view.translate(self._xy_speed)
