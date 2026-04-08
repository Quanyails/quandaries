import csv
from dataclasses import dataclass
from typing import List

from tags import Tags
from wordlist import WordlistEntry
from transforms import TRANSFORMS


@dataclass(frozen=True, slots=True)
class OverrideMeta:
    word_path: str
    delimiter: str = ","
    is_additive: bool = False
    sort: str = ""

    def extract(self, tags: Tags) -> List[WordlistEntry]:
        seen = set()
        results = []
        with open(self.word_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=self.delimiter)

            for rawword, *tagnames in reader:

                if tagnames == [""]:
                    print(f"Missing tags for word: {rawword}")
                else:
                    rawscore = tags.evaluate(tagnames)

                word, score = TRANSFORMS["NORMALIZE"].apply(rawword, rawscore)

                if word in seen:
                    print(f"Duplicate entry for word: {word}")
                else:
                    seen.add(word)
                    entry = WordlistEntry(word=word, score=score)
                    results.append(entry)
        return results
