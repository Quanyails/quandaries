from typing import override, Tuple

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
        match score:
            case 99:
                rescore = 50
            case 51:
                rescore = 40
            case 49:
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
        normalized = "".join(c for c in word.upper() if c.isalnum())
        return (normalized, score)


class NoopTransform(BaseTransform):
    @override
    def name(self):
        return "NOOP"

    @override
    def apply(self, word, score: int):
        return (word, score)

TRANSFORMS = {
    transform.name(): transform for transform in [
        HalveTransform(),
        NedigerTransform(),
        NormalizeTransform(),
        NoopTransform(),
    ]
}
