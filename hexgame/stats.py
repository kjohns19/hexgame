import collections

from . import entity


class EntityStats:
    def __init__(self):
        self._counts = collections.defaultdict(int)
        entity.Entity.add_event_listener(self._event_handler)

    def _event_handler(self, ent, event):
        ent_type = type(ent).__name__
        if event == 'create':
            self._counts[ent_type] += 1
        elif event == 'die':
            self._counts[ent_type] -= 1

    def print_stats(self):
        print(' '.join(str(count) for count in self._counts.values()))
