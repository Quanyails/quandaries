from grid import Grid, GridEntry, Coordinate
from textwrap import dedent


def test_str():
    entry1 = GridEntry(c=Coordinate(1, 0), d="D", word="HELLO")
    entry2 = GridEntry(c=Coordinate(0, 4), d="A", word="WORLD")
    grid = Grid(entries=[entry1, entry2], width=5, height=5)

    expected = dedent("""
    . H . . .
    . E . . .
    . L . . .
    . L . . .
    W O R L D
    """).strip()

    assert str(grid) == expected


def test_no_collision():
    entry1 = GridEntry(c=Coordinate(1, 0), d="D", word="HELLO")
    entry2 = GridEntry(c=Coordinate(0, 4), d="A", word="WORLD")
    grid = Grid(entries=[entry1, entry2], width=5, height=5)

    assert not grid.contains_collision()


def test_collision():
    entry1 = GridEntry(c=Coordinate(0, 0), d="D", word="HELLO")
    entry2 = GridEntry(c=Coordinate(0, 4), d="A", word="WORLD")
    grid = Grid(entries=[entry1, entry2], width=5, height=5)

    assert grid.contains_collision()


def test_transpose():
    entry1 = GridEntry(c=Coordinate(1, 0), d="D", word="HELLO")
    entry2 = GridEntry(c=Coordinate(0, 4), d="A", word="WORLD")
    grid = Grid(entries=[entry1, entry2], width=5, height=5)

    tentry1 = GridEntry(c=Coordinate(0, 1), d="A", word="HELLO")
    tentry2 = GridEntry(c=Coordinate(4, 0), d="D", word="WORLD")
    tgrid = Grid(entries=[tentry1, tentry2], width=5, height=5)

    assert grid.as_transposed() == tgrid


if __name__ == "__main__":
    test_str()
    test_no_collision()
    test_collision()
    test_transpose()
