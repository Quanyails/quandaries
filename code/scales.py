from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Scale:
    xrange: Tuple[int, int] = field(default_factory=lambda: [0, 1])
    yrange: Tuple[int, int] = field(default_factory=lambda: [0, 1])

    scale: float = field(init=False)

    def __post_init__(self):
        [xmin, xmax] = self.xrange
        [ymin, ymax] = self.yrange
        xscale = xmax - xmin
        yscale = ymax - ymin

        self.scale = yscale / xscale

    def lerp(self, value):
        [xmin] = self.xrange
        [ymin] = self.yrange
        return (value - xmin) * self.scale + ymin
