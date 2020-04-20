import pyglet

from . import location
from . import util


class Entity:
    _event_listeners = []

    @staticmethod
    def add_event_listener(listener):
        Entity._event_listeners.append(listener)

    @staticmethod
    def remove_event_listener(listener):
        Entity._event_listeners.remove(listener)

    def __init__(self):
        super().__init__()
        self._loc = None
        self._layer = None
        self._sprite = None
        self.signal_event('birth')

    @property
    def loc(self):
        return self._loc

    @property
    def layer(self):
        return self._layer

    @property
    def world(self):
        return None if self._layer is None else self._layer.world

    def signal_event(self, event):
        for listener in Entity._event_listeners:
            listener(self, event)

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
            self.signal_event('death')

    def try_move(self, loc):
        assert self._layer is not None, 'Can\'t move an entity not in a layer!'
        return self._layer.move_entity(self, loc)

    def update(self, game):
        pass


class AliveMixin:
    def __init__(self, *args, max_life=None, **kwargs):
        self._life = max_life
        super().__init__(*args, **kwargs)

    def age(self, game):
        self._life -= 1
        if self._life <= 0 or game.rand.randrange(self._life) == 0:
            self.die()
            return True
        return False


class ReproducibleMixin:
    def __init__(self, *args, max_reproduce, generation, **kwargs):
        self._reproduce = max_reproduce
        self._max_reproduce = max_reproduce
        self._generation = generation
        super().__init__(*args, **kwargs)

    @property
    def generation(self):
        return self._generation

    def make_child(self, game):
        raise RuntimeError('Not implemented!')

    def try_reproduce(self, game):
        self._reproduce -= 1
        if self._reproduce <= 0 or game.rand.randrange(self._reproduce) == 0:
            dir = game.rand.choice(location.Direction.dirs())
            loc = self.loc.in_direction(dir)
            if self._layer.is_empty(loc):
                child = self.make_child(game)
                self._layer.add_entity(child, loc)
            self._reproduce = self._max_reproduce


class Creature(AliveMixin, ReproducibleMixin, Entity):
    image = pyglet.image.load('data/creature.png')
    image_diseased = pyglet.image.load('data/creature_diseased.png')

    def __init__(self, disease_resistance=50, generation=1,
                 satiation=1000, birth_cost=200):
        super().__init__(generation=generation, max_life=1000, max_reproduce=500)
        self._dir = location.Direction.E
        self._sprite = util.draw.make_sprite(Creature.image, order=2)
        self._satiation = satiation
        self._birth_cost = birth_cost
        self._health = 100
        self._diseased = False
        self._disease_resistance = disease_resistance

    @property
    def diseased(self):
        return self._diseased

    @property
    def birth_cost(self):
        return self._birth_cost

    @property
    def disease_resistance(self):
        return self._disease_resistance

    def make_child(self, game):
        self._satiation -= self._birth_cost
        child_birth_cost = max(0, self._birth_cost + game.rand.randint(-2, 2))
        child_disease_resistance = max(
            0, min(self._disease_resistance + game.rand.randint(-1, 1), 100))
        creature = Creature(
            disease_resistance=child_disease_resistance,
            generation=self.generation + 1,
            satiation=self._satiation, birth_cost=child_birth_cost)
        if self._diseased:
            creature._maybe_get_disease(game, 1/2)
        return creature

    def update(self, game):
        if self.age(game):
            return

        self._satiation -= 1 + int(self._diseased)
        if self._satiation <= 0 or game.rand.randrange(self._satiation) == 0:
            self._health -= 10 * (int(self._diseased)+1)
            if self._health <= 0:
                self.die()
                return

        plant = self.world.layer(1).get_entity(self.loc)
        if self._health < 100 and plant is not None:
            self._health += plant.nourishment//10
            self._satiation = min(1000, self._satiation + plant.nourishment)
            if plant.diseased:
                self._maybe_get_disease(game, 1/5)
            plant.die()

        self.try_reproduce(game)

        if game.rand.randrange(2):
            new_loc = self.loc.in_direction(self._dir)
            new_dir = self._dir.turn(game.rand.randint(-2, 2)//2)
            self._dir = new_dir
            old_loc = self._loc
            if self.try_move(new_loc):
                layer = game.world.layer(2)
                if self._diseased:
                    layer.add_entity(Disease(), old_loc)
                else:
                    disease = layer.get_entity(new_loc)
                    if disease is not None and isinstance(disease, Disease):
                        if self._maybe_get_disease(game, 2/3):
                            disease.die()

    def _maybe_get_disease(self, game, chance):
        adjusted_chance = chance * (101 - self._disease_resistance)/100
        if not self._diseased and game.rand.random() < adjusted_chance:
            self._diseased = True
            self.signal_event('diseased')
            self._sprite.image = Creature.image_diseased
            return True
        return False


class Plant(AliveMixin, ReproducibleMixin, Entity):
    image = pyglet.image.load('data/plant.png')
    image_diseased = pyglet.image.load('data/plant_diseased.png')

    def __init__(self, diseased=False, generation=1):
        super().__init__(generation=generation, max_life=1000, max_reproduce=100)
        image = Plant.image_diseased if diseased else Plant.image
        self._sprite = util.draw.make_sprite(image, order=1)
        self._diseased = diseased
        if self._diseased:
            self.signal_event('diseased')

    @property
    def diseased(self):
        return self._diseased

    @property
    def nourishment(self):
        return max(10, min((1000 - self._life)//5, 100))

    def make_child(self, game):
        self._life -= 100
        diseased_chance = 1/5 if self._diseased else 1/5000
        child_diseased = game.rand.random() < diseased_chance
        return Plant(diseased=child_diseased, generation=self.generation + 1)

    def update(self, game):
        if self.age(game):
            return
        self.try_reproduce(game)


class Disease(Entity):
    image = pyglet.image.load('data/disease.png')

    def __init__(self):
        super().__init__()
        self._life = 3
        self._sprite = util.draw.make_sprite(Disease.image, order=3)

    def update(self, game):
        self._life -= 1
        if self._life == 0:
            self.die()
