class World:
    class Layer:
        def __init__(self, world, index):
            self._ents = {}
            self._world = world
            self._index = index

        @property
        def index(self):
            return self._index

        @property
        def world(self):
            return self._world

        def get_entity(self, loc):
            ''' Return the entity at the location, or None if there isn't one '''
            return self._ents.get(loc)

        def add_entity(self, ent, loc):
            ''' Attempt to add an entity to the layer at the specific location

            Returns True if the entity was added
            '''
            assert ent._layer is None, 'Trying to add entity already in layer!'
            added = (self._ents.setdefault(loc, ent) is ent)
            if added:
                ent._loc = loc
                ent._layer = self
                ent._update_position()
            return added

        def move_entity(self, ent, loc):
            assert ent._layer is self, 'Trying to move entity not in layer!'
            if self.is_empty(loc):
                del self._ents[ent.loc]
                self._ents[loc] = ent
                ent._loc = loc
                ent._update_position()
                return True
            return False

        def is_empty(self, loc):
            ''' Returns True if there is no entity at the location '''
            return self.get_entity(loc) is None

        def remove_entity(self, ent):
            assert ent._layer is self, 'Trying to remove entity not in layer!'
            del self._ents[ent._loc]
            ent._loc = None
            ent._layer = None
            ent._update_position()

        def entities(self):
            return self._ents.values()

    def __init__(self, num_layers):
        self._layers = [World.Layer(self, i) for i in range(num_layers)]

    def layer(self, index):
        return self._layers[index]

    def update(self, game):
        layer_ents = [(layer, list(layer.entities())) for layer in self._layers]
        for layer, ents in layer_ents:
            for ent in ents:
                if ent._layer is layer:
                    ent.update(game)
