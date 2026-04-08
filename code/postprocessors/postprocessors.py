from dataclasses import dataclass
import re
import string
from typing import List, override, Iterable, Callable

from .base import BasePostprocessor


@dataclass(frozen=True, slots=True)
class BlankSpaceMapping:
    blankable: str
    index: int
    replacewith: str

    def apply(self, word: str) -> List[str]:
        results = [word]
        i = self.index
        j = i + len(self.blankable)
        if word[i:j] == self.blankable:
            spliced = word[:i] + word[j:]
            formatted = self.replacewith.format(spliced)
            results.append(formatted)
        return results

class BlankSpacePostprocessor(BasePostprocessor):
    def __init__(self, mappings: List[BlankSpaceMapping]):
        self.mappings = mappings

    def apply(self, word, score):
        results = [(word, score)]
        for mapping in self.mappings:
            mapped = mapping.apply(word)
            for mword in mapped:
                results.append((mword, score))
        return results

class CaptureGroupPostprocessor(BasePostprocessor):
    def __init__(self, patterns: List[str], wordlist: Iterable[str]):
        self.patterns = [re.compile(pattern) for pattern in patterns]
        self.wordlist = set(wordlist)

    def _recursively_capture(self, s: str, patterns: List[re.Pattern]) -> List[str]:

        if len(patterns) == 0:
            return []

        pattern, *restpatterns = patterns

        if pattern.fullmatch(s) and s in self.wordlist and len(restpatterns) == 0:
            return [s]

        # Otherwise, no match found, recurse
        for i in range(len(s)):
            prefix = s[:i]
            suffix = s[i:]

            if pattern.fullmatch(prefix) and prefix in self.wordlist:
                captured = self._recursively_capture(suffix, restpatterns)

                if captured:
                    return [prefix, *captured]

        return []

    def apply(self, word, score):
        captures = self._recursively_capture(word, self.patterns)
        return [(" ".join(captures), score)]

class FlatMapPostprocessor(BasePostprocessor):
    def __init__(self, replacer: Callable[[str], List[str]]):
        self.replacer = replacer

    def apply(self, word, score):
        results = []
        for replaced in self.replacer(word):
            results.append((replaced, score))
        return results

class LimitedAlphabetPostprocessor(BasePostprocessor):
    def __init__(self, alphabet: str, case_sensitive: bool = False):
        if case_sensitive:
            self.regex = re.compile(f"^[{alphabet}]+$")
        else:
            self.regex = re.compile(f"^[{alphabet.lower()}]+$", re.IGNORECASE)

    @override
    def apply(self, word, score):
        if self.regex.fullmatch(word):
            return [(word, score)]
        return []

class LowScorePostprocessor(BasePostprocessor):
    def __init__(self, min_score: int):
        self.min_score = min_score

    @override
    def apply(self, word, score):
        if score < self.min_score:
            return []
        return [(word, score)]

class MaxLengthPostprocessor(BasePostprocessor):
    def __init__(self, max_length: int):
        self.max_length = max_length

    @override
    def apply(self, word, score):
        if len(word) > self.max_length:
            return []
        return [(word, score)]

class RegexMatchPostprocessor(BasePostprocessor):
    def __init__(self, regex: str):
        self.regex = re.compile(regex, flags=re.IGNORECASE)

    @override
    def apply(self, word, score):
        if self.regex.fullmatch(word):
            return [(word, score)]
        return []

class SplitDelimiterPostprocessor(BasePostprocessor):
    def __init__(self, delimiter: str, wordlist: Iterable[str]):
        self.delimiter = delimiter
        self.l = len(delimiter)
        self.wordlist = set(wordlist)

    @override
    def apply(self, word, score):
        if self.delimiter not in word:
            return []

        results = []

        for i in range(len(word)):
            if word[i:i+self.l] == self.delimiter:
                before = word[0:i]
                after = word[i+self.l:]

                hasx = before in self.wordlist
                hasy = after in self.wordlist
                hasxdelimiter = before + self.delimiter in self.wordlist
                hasydelimiter = self.delimiter + after in self.wordlist
                if hasx and hasy:
                # if hasx and hasy and hasxdelimiter and hasydelimiter:
                # if hasx and hasy and (hasxdelimiter or hasydelimiter):
                # if hasx and hasy and not hasxdelimiter and not hasydelimiter:
                    split = " ".join([before, self.delimiter, after])
                    results.append((split, score))

        return results

class SubstringPostprocessor(BasePostprocessor):
    def __init__(self, substrings: List[str]):
        self.substrings = substrings

    def apply(self, word, score):
        for substring in self.substrings:
            if substring in word:
                # Highlight substring in the word by flipping the case of the substring's letters
                result = word.replace(substring, substring.swapcase())
                return [(result, score)]
        return []

class UniqueLetterPostprocessor(BasePostprocessor):

    def __init__(self, *, min_required=0, max_required=len(string.ascii_uppercase)):
        self.min_required = min_required
        self.max_required = max_required

    @override
    def apply(self, word, score):
        # Filter out strings that repeat themselves
        # Funky O(1) algorithm that checks repetition by exploiting periodicity
        if word in (f"{word}{word}"[1:-1]):
            return []

        if self.min_required <= len(set(word)) <= self.max_required:
            return [(word, score)]
        return []
