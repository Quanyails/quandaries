from abc import ABC, abstractmethod
from typing import List, Tuple


class BasePostprocessor(ABC):

    @abstractmethod
    def apply(self, word: str, score: int) -> List[Tuple[str, int]]:
        pass
