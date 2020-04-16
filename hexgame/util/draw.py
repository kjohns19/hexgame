import functools
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


class Circle:
    def __init__(self, position, radius, color=Color.WHITE,
                 num_vertices=32, radian_offset=0, fill=True, order=0):
        if num_vertices < 3:
            raise ValueError('Cannot draw circle with < 3 vertices!')
        self._batch = state().batch
        self._group = state().group(order)
        self._color = color
        self._position = position
        self._radius = radius
        self._color = color
        self._num_vertices = num_vertices
        self._radian_offset = radian_offset
        self._fill = fill
        self._visible = True
        self._create_vertex_list()

    def __del__(self):
        try:
            if self._vertices is not None:
                self._vertices.delete()
        except Exception:
            pass

    def delete(self):
        self._vertices.delete()
        self._vertices = None

    def update(self, position=None, radius=None, color=None,
               num_vertices=None, radian_offset=None, fill=None, visible=None):
        recreate_vertices = False
        update_vertices = False
        update_color = False
        if position is not None and position != self._position:
            self._position = position
            update_vertices = True
        if radius is not None and radius != self._radius:
            self._radius = radius
            update_vertices = True
        if color is not None and color != self._color:
            self._color = color
            update_color = color
        if num_vertices is not None and num_vertices != self._num_vertices:
            if num_vertices < 3:
                raise ValueError('Cannot draw circle with < 3 vertices!')
            self._num_vertices = num_vertices
            recreate_vertices = True
        if radian_offset is not None and radian_offset != self._radian_offset:
            self._radian_offset = radian_offset
            update_vertices = True
        if fill is not None and fill != self._fill:
            self._fill = fill
            recreate_vertices = True
        if visible is not None and visible != self._visible:
            self._visible = visible
            update_vertices = True

        if recreate_vertices:
            self._vertices.delete()
            self._create_vertex_list()
        else:
            if update_vertices:
                self._update_vertices()
            if update_color:
                self._update_color()

    def _create_vertex_list(self):
        def pairs():
            values = iter(range(self._num_vertices))
            first = next(values)
            prev = first
            for elem in values:
                yield (prev, elem)
                prev = elem
            yield (elem, first)

        def triangles():
            values = list(range(self._num_vertices))
            while len(values) >= 3:
                yield tuple(values[0:3])
                values.append(values[0])
                del values[0:2]

        if self._fill:
            indices = tuple(itertools.chain.from_iterable(triangles()))
            self._vertices = self._batch.add_indexed(
                self._num_vertices, pyglet.gl.GL_TRIANGLES, self._group,
                indices, 'v2f', 'c4B')
        else:
            indices = tuple(itertools.chain.from_iterable(pairs()))
            self._vertices = self._batch.add_indexed(
                self._num_vertices, pyglet.gl.GL_LINES, self._group,
                indices, 'v2f', 'c4B')

        self._update_vertices()
        self._update_color()

    def _update_vertices(self):
        if not self._visible:
            self._vertices.vertices[:] = [0, 0]*self._num_vertices
            return

        radians = (
            i * 2*math.pi/self._num_vertices + self._radian_offset
            for i in range(self._num_vertices)
        )

        x, y = self._position

        vertices = (
            (x+self._radius*math.cos(rad), y+self._radius*math.sin(rad))
            for rad in radians
        )

        self._vertices.vertices[:] = list(itertools.chain.from_iterable(vertices))

    def _update_color(self):
        self._vertices.colors[:] = self._color.values * self._num_vertices


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
