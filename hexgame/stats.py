import collections

from . import entity


class EntityStats:
    def __init__(self):
        self._counts = collections.defaultdict(self._initial_values)
        self._ent_types = ['Creature', 'Plant']
        self._delta_stats = ['Births', 'Deaths']
        entity.Entity.add_event_listener(self._event_handler)

    def _event_handler(self, ent, event):
        counts = self._counts[type(ent).__name__]
        if event == 'birth':
            counts['Births'] += 1
            counts['Count'] += 1
            counts['Generation'] = max(counts['Generation'], ent.generation)
        elif event == 'death':
            counts['Deaths'] += 1
            counts['Count'] -= 1

    def _initial_values(self):
        return {'Count': 0, 'Births': 0, 'Deaths': 0, 'Generation': 0}

    def print_header(self):
        column_names = self._initial_values().keys()

        def ent_type_columns(ent_type):
            return ' '.join(ent_type + col for col in column_names)

        print(' '.join(ent_type_columns(ent_type) for ent_type in self._ent_types))

    def print_stats(self):
        def ent_type_stats(ent_type):
            return ' '.join(str(val) for val in self._counts[ent_type].values())

        print(' '.join(ent_type_stats(ent_type) for ent_type in self._ent_types))

        # Reset 'delta' stats to 0
        for counts in self._counts.values():
            for delta_stat in self._delta_stats:
                counts[delta_stat] = 0
