from dataclasses import dataclass
from typing import Literal

from grid import Grid, GridEntry, Coordinate


@dataclass(frozen=True, slots=True)
class Intersected:
    index: int
    word: str

    def __str__(self):
        exploded = list(self.word)
        exploded[self.index] = f"({exploded[self.index]})"
        return "".join(exploded)


@dataclass(frozen=True, slots=True)
class Intersection:
    first: Intersected
    second: Intersected

    def as_grid(self):
        trunk = self.first
        branch = self.second

        width = len(trunk.word)
        height = len(branch.word)

        tentry = GridEntry(
            c=Coordinate(0, branch.index % len(branch.word)),
            d="A",
            word=trunk.word,
        )
        bentry = GridEntry(
            c=Coordinate(trunk.index % len(trunk.word), 0),
            d="D",
            word=branch.word,
        )

        grid = Grid(
            entries=[tentry, bentry],
            width=width,
            height=height,
        )
        return grid


@dataclass(frozen=True, slots=True)
class SymmetricalPair:
    first: Grid
    second: Grid
    symmetry: Literal["R"]

    def __post_init__(self):
        assert self.first.width == self.second.width, f"Expected grids to have same width, got {self.first.width} and {self.second.width}"
        assert self.first.height == self.second.height, f"Expected grids to have same height, got {self.first.height} and {self.second.height}"
        assert self.first.degree == self.second.degree, f"Expected grids to have same degree, got {self.first.degree} and {self.second.degree}"

    def get_shared(self):
        w1 = {entry.word for entry in self.first.entries}
        w2 = {entry.word for entry in self.second.entries}
        return list(w1 & w2)

    def variations(self):
        cpair = SymmetricalPair(
            first=self.second,
            second=self.first,
            symmetry=self.symmetry,
        )
        tpair = SymmetricalPair(
            first=self.first.as_transposed(),
            second=self.second.as_transposed(),
            symmetry=self.symmetry,
        )
        ctpair = SymmetricalPair(
            first=self.second.as_transposed(),
            second=self.first.as_transposed(),
            symmetry=self.symmetry,
        )
        return [
            self,
            cpair,
            tpair,
            ctpair,
        ]

    def __str__(self):
        combined = []
        for l1, l2 in zip(str(self.first).splitlines(), str(self.second).splitlines()):
            combined.append(f"{l1}  |  {l2}")
        return "\n".join(combined)
