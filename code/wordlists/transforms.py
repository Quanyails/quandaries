from anyascii import anyascii
from typing import override, Tuple
from unicodedata import combining, normalize

from transform import BaseTransform

class HalveTransform(BaseTransform):
    @override
    def name(self):
        return "HALVE"

    @override
    def apply(self, word, score: int):
        return (word, score // 2)


class NedigerTransform(BaseTransform):
    @override
    def name(self):
        return "NEDIGER"

    @override
    def apply(self, word, score: int):
        if len(word) < 8:
            match score:
                case 99:
                    rescore = 50
                case 51:
                    rescore = 40
                case 49: # words that are not family-friendly
                    rescore = 10
                case 25:
                    rescore = 30
                case _:
                    rescore = score
        else:
            match score:
                case 99:
                    rescore = 50
                case 51:
                    rescore = 42
                case 49: # words that are not family-friendly
                    rescore = 10
                case 25:
                    rescore = 30
                case _:
                    rescore = score
        return (word, rescore)

class NormalizeTransform(BaseTransform):
    @override
    def name(self):
        return "NORMALIZE"

    @override
    def apply(self, word, score: int):
        # decomposed = normalize("NFKD", word)
        # recomposed = "".join(c for c in decomposed if not combining(c))
        # normalized = ("".join(c for c in recomposed if c.isalnum())).upper()
        transliterated = anyascii(word)
        normalized = "".join(c for c in transliterated if c.isalnum()).upper()
        return (normalized, score)


class NoopTransform(BaseTransform):
    @override
    def name(self):
        return "NOOP"

    @override
    def apply(self, word, score: int):
        return (word, score)

class XwiTransform(BaseTransform):
    @override
    def name(self):
        return "XWI"

    @override
    def apply(self, word, score: int):
        match score:
            case 60:
                return (word, 50)
            case _:
                return (word, score)


TRANSFORMS = {
    transform.name(): transform for transform in [
        HalveTransform(),
        NedigerTransform(),
        NormalizeTransform(),
        NoopTransform(),
        XwiTransform(),
    ]
}
