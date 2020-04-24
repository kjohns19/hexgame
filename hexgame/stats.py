from . import entity


class EntityStats:
    def __init__(self):
        ent_types = ['Creature', 'Plant']
        common_fields = ['Count', 'Births', 'Deaths', 'Generation', 'Diseased']

        self._ents = set()
        self._delta_stats = [
            ent_type + field
            for ent_type in ent_types
            for field in ['Births', 'Deaths']
        ]
        self._ent_minmax_fields = {
            'Creature': [
                ('BirthCost', lambda ent: ent.birth_cost),
                ('Resistance', lambda ent: ent.disease_resistance)]
        }
        stat_names = [
            ent_type + field
            for ent_type in ent_types
            for field in common_fields
        ] + [
            ent_type + minmax + field
            for ent_type, fields in self._ent_minmax_fields.items()
            for minmax in ['Min', 'Max']
            for field, _ in fields
        ]
        self._stats = {stat: 0 for stat in stat_names}

        entity.Entity.add_event_listener(
            self._handler_births, ent_types, ['birth'])
        entity.Entity.add_event_listener(
            self._handler_deaths, ent_types, ['death'])
        entity.Entity.add_event_listener(
            self._handler_disease, ent_types, ['diseased', 'disease_cured'])

    def _handler_births(self, ent, event, value):
        self._ents.add(ent)
        ent_type = type(ent).__name__
        self._stats[ent_type + 'Births'] += 1
        self._stats[ent_type + 'Count'] += 1
        self._stats[ent_type + 'Generation'] = max(
            self._stats[ent_type + 'Generation'], ent.generation)

    def _handler_deaths(self, ent, event, value):
        self._ents.remove(ent)
        ent_type = type(ent).__name__
        if ent.diseased:
            self._stats[ent_type + 'Diseased'] -= 1
        self._stats[ent_type + 'Deaths'] += 1
        self._stats[ent_type + 'Count'] -= 1

    def _handler_disease(self, ent, event, value):
        ent_type = type(ent).__name__
        if event == 'diseased':
            self._stats[ent_type + 'Diseased'] += 1
        else:
            self._stats[ent_type + 'Diseased'] -= 1

    def print_header(self):
        print(' '.join(self._stats.keys()))

    def print_stats(self):
        def min_max(field_func):
            min_val = None
            max_val = None
            for ent in self._ents:
                if isinstance(ent, entity.Creature):
                    val = field_func(ent)
                    min_val = val if min_val is None else min(min_val, val)
                    max_val = val if max_val is None else max(max_val, val)
            return min_val, max_val if min_val is not None else (0, 0)

        for ent_type, fields in self._ent_minmax_fields.items():
            for field_name, field_func in fields:
                min_val, max_val = min_max(field_func)
                self._stats[ent_type + 'Min' + field_name] = min_val
                self._stats[ent_type + 'Max' + field_name] = max_val

        print(' '.join(str(v) for v in self._stats.values()))

        # Reset 'delta' stats to 0
        for delta_stat in self._delta_stats:
            self._stats[delta_stat] = 0
