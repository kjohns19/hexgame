from hexgame import location


def test_even_location():
    locs = [
        (location.Direction.E,  location.Location(1, 0)),
        (location.Direction.SE, location.Location(1, 1)),
        (location.Direction.SW, location.Location(0, 1)),
        (location.Direction.W,  location.Location(-1, 0)),
        (location.Direction.NW, location.Location(0, -1)),
        (location.Direction.NE, location.Location(1, -1))
    ]
    start = location.Location(0, 0)
    for dir, loc in locs:
        assert start.in_direction(dir) == loc


def test_odd_location():
    locs = [
        (location.Direction.E,  location.Location(1, 1)),
        (location.Direction.SE, location.Location(0, 2)),
        (location.Direction.SW, location.Location(-1, 2)),
        (location.Direction.W,  location.Location(-1, 1)),
        (location.Direction.NW, location.Location(-1, 0)),
        (location.Direction.NE, location.Location(0, 0))
    ]
    start = location.Location(0, 1)
    for dir, loc in locs:
        assert start.in_direction(dir) == loc
