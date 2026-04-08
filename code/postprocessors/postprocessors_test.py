import postprocessors as pps

def test_capture_group():
    wordlist = {"HELLO", "WORLD"}
    postprocessor = pps.CaptureGroupPostprocessor([r"H.*", r"W.*"], wordlist)

    results = postprocessor.apply("HELLOWORLD", 1)
    assert results == [("HELLO WORLD", 1)]

def test_limited_alphabet():
    postprocessor = pps.LimitedAlphabetPostprocessor("aeiou")

    result = postprocessor.apply("foobar", 1)
    assert result == []

    result = postprocessor.apply("iou", 1)
    assert result == [("iou", 1)]


def test_replacement_at_index():
    mapping = pps.BlankSpaceMapping(blankable="b", index=-3, replacewith="1{0}")
    results = mapping.apply("foobarbaz")
    assert results == ["foobarbaz", "1foobaraz"]


if __name__ == "__main__":
    test_capture_group()
    # test_limited_alphabet()
    # test_replacement_at_index()
