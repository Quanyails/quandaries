from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass(frozen=True, slots=True)
class Tag:
    name: str
    priority: int
    score: int

    def __lt__(self, other):
        # Sort by priority, then by score
        return (self.priority, self.score) < (other.priority, other.score)


@dataclass(frozen=True, slots=True)
class Tags:
    tags: List[Tag]
    mapping: Dict[str, Tag] = field(default_factory=dict)

    def __post_init__(self):
        for tag in self.tags:
            self.mapping[tag.name] = tag


    def evaluate(self, tagnames: Iterable[str]) -> int:
        tags = (self.mapping.get(tagname) for tagname in tagnames)

        return max(tags).score


@dataclass(frozen=True, slots=True)
class TagMeta:
    path: str
    delimiter: str = ","

    def extract(self):

        with open(self.path, "r") as f:
            tags = []

            for line in f:
                name, scorestr, prioritystr, *rest = line.strip().split(self.delimiter)
                score = int(scorestr)
                priority = int(prioritystr)
                tag = Tag(name=name, priority=priority, score=score)
                tags.append(tag)

        return Tags(tags=tags)
