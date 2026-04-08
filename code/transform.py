from abc import ABC, abstractmethod
from typing import Tuple

class BaseTransform(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def apply(self, word: str, score: int) -> Tuple[str, int]:
        pass
