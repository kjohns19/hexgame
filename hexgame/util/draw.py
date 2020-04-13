import itertools
import math
import pyglet


class Color:
    __slots__ = ('r', 'g', 'b', 'a')

    def __init__(self, r, g, b, a=255):
        self.r, self.g, self.b, self.a = r, g, b, a

    @property
    def values(self):
        return self.r, self.g, self.b, self.a

    def interpolate(self, color, ratio):
        def interpolate_one(v1, v2):
            return round(v1 + (v2 - v1)*ratio)

        return Color(
            interpolate_one(self.r, color.r),
            interpolate_one(self.g, color.g),
            interpolate_one(self.b, color.b),
            interpolate_one(self.a, color.a))

    def replace(self, r=None, g=None, b=None, a=None):
        return Color(
            self.r if r is None else r,
            self.g if g is None else g,
            self.b if b is None else b,
            self.a if a is None else a
        )


Color.WHITE   = Color(255, 255, 255)
Color.BLACK   = Color(0, 0, 0)
Color.RED     = Color(255, 0, 0)
Color.GREEN   = Color(0, 255, 0)
Color.BLUE    = Color(0, 0, 255)
Color.YELLOW  = Color(255, 255, 0)
Color.MAGENTA = Color(255, 0, 255)
Color.CYAN    = Color(0, 255, 255)
Color.NONE    = Color(0, 0, 0, 0)


class CustomGroup(pyglet.graphics.Group):
    def __init__(self, origin, translation, scale, parent=None):
        super().__init__(parent)
        self._origin = origin
        self._translation = translation
        self._scale = scale

    def set_state(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(*self._origin, 0)
        pyglet.gl.glScalef(self._scale, self._scale, 1)
        if self._translation:
            pyglet.gl.glTranslatef(*-self._translation, 0)

    def unset_state(self):
        pyglet.gl.glPopMatrix()


class DrawState:
    def __init__(self, origin, translation, scale):
        super().__init__()
        self._origin = origin
        self._translation = translation
        self._scale = scale
        self._batch = pyglet.graphics.Batch()
        self._ordered_groups = {}

    @property
    def batch(self):
        return self._batch

    def group(self, order=0):
        order_group = self._ordered_groups.get(order)
        if order_group is None:
            order_group = pyglet.graphics.OrderedGroup(order)
            self._ordered_groups[order] = order_group
        return CustomGroup(
            self._origin, self._translation, self._scale, parent=order_group)


def circle(state, position, radius, color=Color.WHITE,
           num_vertices=32, radian_offset=0, fill=True, order=0):
    if num_vertices < 3:
        raise ValueError('Cannot draw circle with < 3 vertices!')

    radians = (
        i * 2*math.pi/num_vertices + radian_offset
        for i in range(num_vertices)
    )

    x, y = position

    edge_vertices = (
        (x+radius*math.cos(rad), y+radius*math.sin(rad))
        for rad in radians
    )

    if not fill:
        positions = list(edge_vertices)
        lines(state, positions+positions[0:2], color=color, order=order)
        return

    def pairs(iterable):
        first = next(iterable)
        prev = first
        for elem in iterable:
            yield (prev, elem)
            prev = elem
        yield (elem, first)

    vertices = (
        (x, y, *p1, *p2)
        for p1, p2 in pairs(edge_vertices)
    )
    flattened = tuple(itertools.chain.from_iterable(vertices))

    count = num_vertices*3

    state.batch.add(
        count, pyglet.gl.GL_TRIANGLES, state.group(order),
        ('v2f', flattened),
        ('c4B', color.values * count)
    )


def line(state, position1, position2, color=Color.WHITE, order=0):
    state.batch.add(
        2, pyglet.gl.GL_LINES, state.group(order),
        ('v2f', (*position1, *position2)),
        ('c4B', color.values * 2)
    )


def lines(state, positions, color=Color.WHITE, color2=None, order=0):
    if not positions:
        return

    vertices = tuple(itertools.chain.from_iterable(positions))

    if color2:
        colors = (
            color2.interpolate(color, i/(len(positions)-1 or 1)).values
            for i in range(len(positions))
        )
        color_values = tuple(itertools.chain.from_iterable(colors))
    else:
        color_values = color.values * len(positions)

    state.batch.add(
        len(positions), pyglet.gl.GL_LINE_STRIP, state.group(order),
        ('v2f', vertices),
        ('c4B', color_values)
    )
