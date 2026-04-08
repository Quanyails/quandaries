from typing import List

from grid import Grid, GridEntry, Coordinate

def fit_grid(entries: List[GridEntry]) -> Grid:
    xs = [cell.c.x for entry in entries for cell in entry.as_cells()]
    ys = [cell.c.y for entry in entries for cell in entry.as_cells()]
    minx = min(xs)
    maxx = max(xs)
    miny = min(ys)
    maxy = max(ys)

    offset = -Coordinate(minx, miny)

    return Grid(
        entries=[entry.moved_by(offset) for entry in entries],
        width=maxx - minx + 1,
        height=maxy - miny + 1,
    )

def merge_grids(grid1: Grid, grid2: Grid) -> Grid | None:
    wordset1 = {entry.word: entry for entry in grid1.entries}
    assert len(wordset1) == len(grid1.entries), "Can't merge grids with duplicate words in grid 1."
    wordset2 = {entry.word: entry for entry in grid2.entries}
    assert len(wordset2) == len(grid2.entries), "Can't merge grids with duplicate words in grid 2."

    offsets = set()
    for word in wordset1.keys() & wordset2.keys():
        entry1 = wordset1[word]
        entry2 = wordset2[word]

        # Can't merge grids with the same word in different directions
        directions_match = entry1.d == entry2.d
        if not directions_match:
            return None

        offset = entry2.c - entry1.c
        offsets.add(offset)

    # All offsets must match for merge to be possible
    if len(offsets) != 1:
        return None

    offset = -next(iter(offsets))
    # Combine entries in a way that ensures dupes are removed
    e1 = {entry for entry in grid1.entries}
    e2 = {entry.moved_by(offset) for entry in grid2.entries}
    combined_entries = list(e1 | e2)

    # Create a grid that fits the combined entries
    merged_grid = fit_grid(combined_entries)

    # Make sure none of the different entries overlap
    if merged_grid.contains_collision():
        return None

    return merged_grid
