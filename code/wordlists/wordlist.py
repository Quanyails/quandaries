from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WordlistEntry:
    word: str
    score: int
