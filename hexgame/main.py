import argparse
import logging.config
import pyglet

from .game import Game
from .entity import Creature, Plant
from . import location


def main():
    args = parse_args()
    init_logging(args.verbose)
    config = pyglet.gl.Config(alpha_size=8)
    window = pyglet.window.Window(config=config, width=1300, height=1100)
    game = Game(window)
    for x in range(-20, 21):
        for y in range(-20, 21):
            loc = location.Location(x, y)
            game.world.layer(1).add_entity(Plant(), loc)
    for x in range(-1, 2):
        for y in range(-1, 2):
            loc = location.Location(x, y)
            game.world.layer(0).add_entity(Creature(), loc)
    game.run()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Verbose output')
    args = parser.parse_args()
    return args


def init_logging(verbose):
    level = 'DEBUG' if verbose else 'INFO'
    logging.config.dictConfig({
        'version': 1,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': level,
                'stream': 'ext://sys.stdout'
            }
        },
        'formatters': {
            'default': {
                'format':
                    '%(asctime)s %(filename)s:%(lineno)s:%(levelname)s: %(message)s'
            }
        },
        'root': {
            'level': level,
            'handlers': ['console']
        }
    })


if __name__ == '__main__':
    main()
