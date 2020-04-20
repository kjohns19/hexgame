import collections

from . import entity


class EntityStats:
    def __init__(self):
        self._counts = collections.defaultdict(self._initial_values)
        self._ents = set()
        self._ent_types = ['Creature', 'Plant']
        self._delta_stats = ['Births', 'Deaths']
        self._ent_extra_fields = {
            'Creature': [
                ('BirthCost', lambda ent: ent.birth_cost),
                ('Resistance', lambda ent: ent.disease_resistance)]
        }
        entity.Entity.add_event_listener(self._event_handler)

    def _event_handler(self, ent, event):
        ent_type = type(ent).__name__
        if ent_type not in self._ent_types:
            return
        counts = self._counts[ent_type]
        if event == 'birth':
            self._ents.add(ent)
            counts['Births'] += 1
            counts['Count'] += 1
            counts['Generation'] = max(counts['Generation'], ent.generation)
        elif event == 'death':
            if ent.diseased:
                counts['Diseased'] -= 1
            self._ents.remove(ent)
            counts['Deaths'] += 1
            counts['Count'] -= 1
        elif event == 'diseased':
            counts['Diseased'] += 1

    def _initial_values(self):
        return {'Count': 0, 'Births': 0, 'Deaths': 0, 'Generation': 0, 'Diseased': 0}

    def print_header(self):
        column_names = self._initial_values().keys()

        def ent_type_columns(ent_type):
            return ' '.join(ent_type + col for col in column_names)

        ent_extra_field_names = []
        for ent_type, fields in self._ent_extra_fields.items():
            for field_name, field_func in fields:
                ent_extra_field_names.append(f'{ent_type}{field_name}Min')
                ent_extra_field_names.append(f'{ent_type}{field_name}Max')

        print(
            ' '.join(ent_extra_field_names),
            ' '.join(ent_type_columns(ent_type) for ent_type in self._ent_types))

    def print_stats(self):
        def ent_type_stats(ent_type):
            return ' '.join(str(val) for val in self._counts[ent_type].values())

        def min_max(field_func):
            min_val = None
            max_val = None
            for ent in self._ents:
                if isinstance(ent, entity.Creature):
                    val = field_func(ent)
                    min_val = val if min_val is None else min(min_val, val)
                    max_val = val if max_val is None else max(max_val, val)
            return min_val, max_val if min_val is not None else (0, 0)

        ent_extra_values = []
        for ent_type, fields in self._ent_extra_fields.items():
            for field_name, field_func in fields:
                min_val, max_val = min_max(field_func)
                ent_extra_values.append(min_val)
                ent_extra_values.append(max_val)

        print(
            ' '.join(str(val) for val in ent_extra_values),
            ' '.join(ent_type_stats(ent_type) for ent_type in self._ent_types))

        # Reset 'delta' stats to 0
        for counts in self._counts.values():
            for delta_stat in self._delta_stats:
                counts[delta_stat] = 0
