from tags import Tag, Tags

def test_equal_priority():
    tag1 = Tag(name="tag1", priority=0, score=1)
    tag2 = Tag(name="tag2", priority=0, score=2)
    tags = Tags([tag1, tag2])
    assert tags.evaluate(["tag1", "tag2"]) == 2

def test_unequal_priority():
    tag1 = Tag(name="tag1", priority=0, score=1)
    tag2 = Tag(name="tag2", priority=1, score=0)
    tags = Tags([tag1, tag2])
    assert tags.evaluate(["tag1", "tag2"]) == 0

if __name__ == "__main__":
    test_equal_priority()
    test_unequal_priority()
