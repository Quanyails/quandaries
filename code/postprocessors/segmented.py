from typing import override, Iterable, Tuple

from .base import BasePostprocessor


class SegmentedSpoonerismPostprocessor(BasePostprocessor):
    # Handles basic letter-same spoonerisms.
    # Does not handle cases where phonetics remain the same but letters alter.

    def __init__(self, dictionary: Iterable[str], include_y: bool = False):
        self.dictionary = set(dictionary)
        self.vowels = set("AEIOUY") if include_y else set("AEIOU")

    def _cluster(self, s: str) -> Tuple[str, str]:
        for i, c in enumerate(s):
            if c in self.vowels:
                return s[:i], s[i:]
        return s, ""

    @override
    def apply(self, word, score):
        tokens = word.split(" ")

        # Spoonerisms can only be two words in length
        if len(tokens) != 2:
            return []

        t1, t2 = tokens

        c1, r1 = self._cluster(t1)
        c2, r2 = self._cluster(t2)

        # No clusters created
        if not all((c1, r1, c2, r2)):
            return []

        # Spoonerisms must have different consonant beginnings
        # Spoonerisms cannot be rhyming words
        if t1 == t2 or c1 == c2 or r1 == r2:
            return []

        sp1 = f"{c2}{r1}"
        sp2 = f"{c1}{r2}"

        if sp1 in self.dictionary and sp2 in self.dictionary:
            return [(f"{word} -> {sp1} {sp2}", score)]

        return []


class SegmentedWordFilterPostprocessor(BasePostprocessor):
    def __init__(self, excluded: Iterable[str]):
        self.excluded = set(word.upper() for word in excluded)

    @override
    def apply(self, word, score):
        tokens = word.split(" ")

        if self.excluded.intersection(tokens):
            return []
        return [(word, score)]
