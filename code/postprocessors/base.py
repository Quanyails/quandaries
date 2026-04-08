from abc import ABC
from typing import List, Tuple


class BasePostprocessor(ABC):
    def apply(self, word: str, score: int) -> List[Tuple[str, int]]:
        pass
