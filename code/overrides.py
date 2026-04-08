from dataclasses import dataclass
from typing import List

from tags import Tags
from wordlist import WordlistEntry


@dataclass(frozen=True, slots=True)
class OverrideMeta:
    word_path: str
    delimiter: str = ","
    is_additive: bool = False
    sort: str = ""

    def extract(self, tags: Tags) -> List[WordlistEntry]:
        seen = set()
        results = []
        with open(self.word_path, "r") as f:
            for line in f:
                word, *tagnames = line.strip().split(self.delimiter)

                if tagnames == [""]:
                    print(f"Missing tags for word: {word}")
                else:
                    token = word.upper().replace(" ", "")
                    value = tags.evaluate(tagnames)

                if token in seen:
                    print(f"Duplicate entry for word: {word}")
                else:
                    seen.add(token)
                    entry = WordlistEntry(word=token, score=value)
                    results.append(entry)
        return results
