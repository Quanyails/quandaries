from dataclasses import dataclass
from typing import List, Tuple

from wordlist import WordlistEntry
from transforms import TRANSFORMS

@dataclass(frozen=True, slots=True)
class Wordlist:
    path: str
    delimiter: str = ";"

    def extract(self) -> List[WordlistEntry]:
        results = []

        with open(self.path, "r", encoding="utf8") as f:
            for line in f:
                rawword, scorestr, *_ = line.strip().split(self.delimiter)
                rawscore = int(scorestr)
                word, score = TRANSFORMS["NORMALIZE"].apply(rawword, rawscore)

                results.append(WordlistEntry(word=word, score=score))
        return results


@dataclass(frozen=True, slots=True)
class WordlistMeta:
    name: str
    path: str
    range: Tuple[int, int]
    transform: str
    source: str
    updated: str
    delimiter: str = ";"

    def extract(self) -> List[WordlistEntry]:
        results = []

        wordlist = Wordlist(self.path, self.delimiter)
        extracted = wordlist.extract()

        for entry in extracted:
            word, score = TRANSFORMS[self.transform].apply(entry.word, entry.score)
            results.append(WordlistEntry(word=word, score=score))

        return results
