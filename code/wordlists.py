from dataclasses import dataclass
from typing import List, Tuple

from wordlist import WordlistEntry

@dataclass(frozen=True, slots=True)
class Wordlist:
    path: str
    delimiter: str = ";"

    def extract(self) -> List[WordlistEntry]:
        results = []

        with open(self.path, "r", encoding="utf8") as f:
            for line in f:
                word, scorestr, *_ = line.strip().split(self.delimiter)
                token = word.upper().replace(" ", "")  # normalize
                score = int(scorestr)

                results.append(WordlistEntry(word=token, score=score))
        return results


@dataclass(frozen=True, slots=True)
class WordlistMeta:
    name: str
    path: str
    range: Tuple[int, int]
    scale: float
    source: str
    updated: str
    delimiter: str = ";"

    def extract(self) -> List[WordlistEntry]:
        results = []

        with open(self.path, "r", encoding="utf8") as f:
            for line in f:
                word, scorestr, *_ = line.strip().split(self.delimiter)
                token = word.upper().replace(" ", "") # normalize
                rawscore = int(scorestr)
                score = int(rawscore * self.scale)

                results.append(WordlistEntry(word=token, score=score))
        return results
