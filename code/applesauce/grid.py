from functools import lru_cache
from typing import Literal, Tuple
from dataclasses import dataclass, replace, field
from collections import defaultdict

# Sentinel value for non-character cells
_BLOCK = "#"


@dataclass(frozen=True, order=True, slots=True)
class Coordinate:
    x: int
    y: int

    def __add__(self, other: Coordinate):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Coordinate):
        return Coordinate(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: int):
        return Coordinate(self.x * scalar, self.y * scalar)

    def __neg__(self):
        return Coordinate(-self.x, -self.y)


@dataclass(frozen=True, order=True, slots=True)
class Cell:
    c: Coordinate
    letter: str


@dataclass(frozen=True, order=True, slots=True)
class GridEntry:
    c: Coordinate
    d: Literal["A", "D"]
    word: str

    def __post_init__(self):
        if self.d not in ("A", "D"):
            raise ValueError(f"Invalid direction '{self.d}' for word '{self.word}'")

    def delta(self):
        if self.d == "A":
            return Coordinate(1, 0)
        elif self.d == "D":
            return Coordinate(0, 1)
        else:
            raise ValueError(f"Invalid direction '{self.d}' for word '{self.word}'")

    @lru_cache(maxsize=1)
    def as_cells(self):
        result = []
        delta = self.delta()
        for i, letter in enumerate(self.word):
            result.append(Cell(c=self.c + delta * i, letter=letter))
        return result

    def as_transposed(self):
        d = "A" if self.d == "D" else "D"
        return GridEntry(
            c=Coordinate(self.c.y, self.c.x),
            d=d,
            word=self.word,
        )

    def moved_by(self, c: Coordinate):
        return replace(self, c=self.c + c)


@dataclass(frozen=True, order=True, slots=True)
class Grid:
    width: int
    height: int
    entries: Tuple[GridEntry]
    degree: int = field(init=False)

    def __post_init__(self):
        hashable = frozenset(self.entries)
        object.__setattr__(self, "entries", hashable)

        object.__setattr__(self, "degree", self._get_degree())

    def as_transposed(self):
        return Grid(
            width=self.height,
            height=self.width,
            entries=[entry.as_transposed() for entry in self.entries],
        )

    def contains_collision(self):
        coordinates = defaultdict(set)

        for entry in self.entries:
            cells = entry.as_cells()
            delta = entry.delta()
            for cell in cells:
                coordinates[(cell.c.x, cell.c.y)].add(cell.letter)
            # Also count abutments as collisions
            coordinates[(cells[0].c.x - delta.x, cells[0].c.y - delta.y)].add(_BLOCK)
            coordinates[(cells[-1].c.x + delta.x, cells[-1].c.y + delta.y)].add(_BLOCK)

        for coordinate, letters in coordinates.items():
            if len(letters) > 1:
                return True

        return False

    def _get_degree(self):
        coordinates = defaultdict(list)
        for entry in self.entries:
            for cell in entry.as_cells():
                coordinates[(cell.c.x, cell.c.y)].append(cell.letter)
        return sum(1 for value in coordinates.values() if len(value) > 1)

    def __str__(self):
        l = [
            ["."] * self.width for _ in range(self.height)
        ]
        for entry in self.entries:
            for cell in entry.as_cells():
                l[cell.c.y][cell.c.x] = cell.letter
        return "\n".join(" ".join(row) for row in l)
