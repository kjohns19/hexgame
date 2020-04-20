import functools
import pyglet


class ViewGroup(pyglet.graphics.Group):
    def __init__(self, translation=None, parent=None):
        super().__init__(parent)
        self._translation = translation or (0, 0)

    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, value):
        self._translation = value or (0, 0)

    def translate(self, xy):
        self._translation = (
            self._translation[0] + xy[0],
            self._translation[1] + xy[1]
        )

    def set_state(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(self._translation[0], self._translation[1], 0)

    def unset_state(self):
        pyglet.gl.glPopMatrix()


class DrawState:
    def __init__(self):
        super().__init__()
        self._batch = pyglet.graphics.Batch()
        self._view = ViewGroup(translation=(400, 400))
        self._ordered_groups = {}

    @property
    def batch(self):
        return self._batch

    @property
    def view(self):
        return self._view

    def draw(self):
        self._batch.draw()

    def group(self, order=0):
        order_group = self._ordered_groups.get(order)
        if order_group is None:
            order_group = pyglet.graphics.OrderedGroup(order, self._view)
            self._ordered_groups[order] = order_group
        return order_group


@functools.lru_cache(1)
def state():
    return DrawState()


def make_sprite(image, *args, order=0, **kwargs):
    batch = state().batch
    group = state().group(order)
    return pyglet.sprite.Sprite(image, *args, batch=batch, group=group, **kwargs)
