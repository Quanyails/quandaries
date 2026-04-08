from grid import Grid, GridEntry, Coordinate
from grids import fit_grid, merge_grids

def test_fit_grid():
    entries = [GridEntry(
        c=Coordinate(-1, 2),
        d="A",
        word="HELLO",
    )]

    expected = Grid(
        entries=[GridEntry(
            c=Coordinate(0, 0),
            d="A",
            word="HELLO",
        )],
        width=5,
        height=1,
    )

    assert fit_grid(entries) == expected

def test_merge_grids():
    grid1 = Grid(
        entries=[GridEntry(
            c=Coordinate(0, 2),
            d="A",
            word="XAXBX",
        ), GridEntry(
            c=Coordinate(1, 0),
            d="D",
            word="AAAAA",
        )],
        width=5,
        height=5,
    )

    grid2 = Grid(
        entries=[GridEntry(
            c=Coordinate(0, 2),
            d="A",
            word="XAXBX",
        ), GridEntry(
            c=Coordinate(3, 0),
            d="D",
            word="BBBBB",
        )],
        width=5,
        height=5,
    )

    expected = Grid(
        entries=[GridEntry(
            c=Coordinate(0, 2),
            d="A",
            word="XAXBX",
        ), GridEntry(
            c=Coordinate(1, 0),
            d="D",
            word="AAAAA",
        ), GridEntry(
            c=Coordinate(3, 0),
            d="D",
            word="BBBBB",
        )],
        width=5,
        height=5,
    )

    assert merge_grids(grid1, grid2) == expected


if __name__ == "__main__":
    test_fit_grid()
    test_merge_grids()
