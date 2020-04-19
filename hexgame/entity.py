import pyglet

from . import location
from . import util


class Entity:
    def __init__(self):
        super().__init__()
        self._loc = None
        self._layer = None
        self._sprite = None

    @property
    def loc(self):
        return self._loc

    @property
    def layer(self):
        return self._layer

    @property
    def world(self):
        return None if self._layer is None else self._layer.world

    def _update_position(self):
        if self._sprite is not None:
            if self._loc is None:
                self._sprite.visible = False
            else:
                pos = self._loc.real_pos()
                self._sprite.update(x=pos[0], y=pos[1])
                self._sprite.visible = True

    def die(self):
        if self._layer is not None:
            self._layer.remove_entity(self)
            self._sprite.delete()

    def try_move(self, loc):
        assert self._layer is not None, 'Can\'t move an entity not in a layer!'
        return self._layer.move_entity(self, loc)

    def update(self, game):
        pass


class AliveMixin:
    def __init__(self, *args, max_life=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._life = max_life

    def age(self, game):
        self._life -= 1
        if self._life <= 0 or game.rand.randrange(self._life) == 0:
            self.die()
            return True
        return False


class ReproducibleMixin:
    def __init__(self, *args, max_reproduce, **kwargs):
        super().__init__(*args, **kwargs)
        self._reproduce = max_reproduce
        self._max_reproduce = max_reproduce

    def make_child(self):
        raise RuntimeError('Not implemented!')

    def try_reproduce(self, game):
        self._reproduce -= 1
        if self._reproduce <= 0 or game.rand.randrange(self._reproduce) == 0:
            dir = game.rand.choice(location.Direction.dirs())
            loc = self.loc.in_direction(dir)
            if self._layer.is_empty(loc):
                child = self.make_child()
                self._layer.add_entity(child, loc)
            self._reproduce = self._max_reproduce


class Creature(AliveMixin, ReproducibleMixin, Entity):
    image = pyglet.image.load('data/creature.png')

    def __init__(self, satiation=1000):
        super().__init__(max_life=1000, max_reproduce=500)
        self._dir = location.Direction.E
        self._sprite = util.draw.make_sprite(Creature.image, order=2)
        self._satiation = satiation
        self._health = 100

    def make_child(self):
        self._satiation -= 100
        return Creature(self._satiation)

    def update(self, game):
        if self.age(game):
            return

        self._satiation -= 1
        if self._satiation <= 0 or game.rand.randrange(self._satiation) == 0:
            self._health -= 10
            if self._health <= 0:
                self.die()
                return

        plant = self.world.layer(1).get_entity(self.loc)
        if self._health < 100 and plant is not None:
            self._health += plant.nourishment//10
            self._satiation = min(1000, self._satiation + plant.nourishment)
            plant.die()

        self.try_reproduce(game)

        if game.rand.randrange(2):
            new_loc = self.loc.in_direction(self._dir)
            new_dir = self._dir.turn(game.rand.randint(-2, 2)//2)
            self._dir = new_dir
            self.try_move(new_loc)


class Plant(AliveMixin, ReproducibleMixin, Entity):
    image = pyglet.image.load('data/plant.png')

    def __init__(self):
        super().__init__(max_life=1000, max_reproduce=100)
        self._sprite = util.draw.make_sprite(Plant.image, order=1)

    @property
    def nourishment(self):
        return max(10, min((1000 - self._life)//5, 100))

    def make_child(self):
        self._life -= 100
        return Plant()

    def update(self, game):
        if self.age(game):
            return
        self.try_reproduce(game)
