import postprocessors.nlp as nlppps
import postprocessors.postprocessors as pps
import postprocessors.segmented as spps


def insert_anywhere(s: str, insertion: str) -> List[str]:
    results = []
    # for i in range(0, len(s) + 1):
    for i in range(1, len(s)):
        inserted = s[:i] + insertion + s[i:]
        results.append(inserted)

    return results


def is_punny(word: str, allwordlist: set, anywordlist: set) -> bool:
    tokens = word.split(" ")

    if not all(len(token) >= 2 for token in tokens):
        return False

    # Make sure tokens represent words we know
    if not all(word in allwordlist for word in tokens):
        return False

    if not any(word in anywordlist for word in tokens):
        return False
    #
    if len(tokens) > 2 or len(tokens[0]) < 4:
        return False

    return True


def no_notes(s: str, wordlist: set) -> List[str]:
    replaced = re.sub(r'DO|RE|MI|FA|SO|SOL|LA|TI', '', s)
    replacements = re.findall(r'DO|RE|MI|FA|SO|SOL|LA|TI', s)
    # replaced = re.sub(r"(MI)+(FA)+", "", s)

    if len(s) - len(replaced) < 4 or replaced not in wordlist:
        return []
    else:
        return [f"{s} | {replaced} | {replacements}"]

basic_spoonerism_postprocessors = [
    pps.LowScorePostprocessor(60),
    nlppps.SegmentationPostprocessor(),
    spps.SegmentedSpoonerismPostprocessor(dictionary=good_words),
]

blank_space_postprocessors = [
    # remove all words that contain non-alphabetic characters (mainly, numbers)
    pps.LimitedAlphabetPostprocessor("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    pps.BlankSpacePostprocessor([
        # DRAW A (at index 2)
        pps.BlankSpaceMapping(blankable="D", index=GAP, replacewith="𝒹{0}"),
        pps.BlankSpaceMapping(blankable="R", index=GAP, replacewith="𝓇{0}"),
        pps.BlankSpaceMapping(blankable="A", index=GAP, replacewith="𝒶{0}"),
        pps.BlankSpaceMapping(blankable="W", index=GAP, replacewith="𝓌{0}"),
        # skip duplicate A

        # VERSE (at index 2)

        pps.BlankSpaceMapping(blankable="V", index=GAP, replacewith="𝓋{0}"),
        pps.BlankSpaceMapping(blankable="E", index=GAP, replacewith="𝑒{0}"),
        # skip duplicate R
        pps.BlankSpaceMapping(blankable="S", index=GAP, replacewith="𝓈{0}"),
        # skip duplicate E

        # POINT (at index -3)

        pps.BlankSpaceMapping(blankable="P", index=-GAP - 1, replacewith="{0}𝓅"),
        pps.BlankSpaceMapping(blankable="O", index=-GAP - 1, replacewith="{0}𝑜"),
        pps.BlankSpaceMapping(blankable="I", index=-GAP - 1, replacewith="{0}𝒾"),
        pps.BlankSpaceMapping(blankable="N", index=-GAP - 1, replacewith="{0}𝓃"),
        pps.BlankSpaceMapping(blankable="T", index=-GAP - 1, replacewith="{0}𝓉"),

        # SPACE (at index -3)

        pps.BlankSpaceMapping(blankable="S", index=-GAP - 1, replacewith="{0}𝓈"),
        pps.BlankSpaceMapping(blankable="P", index=-GAP - 1, replacewith="{0}𝓅"),
        pps.BlankSpaceMapping(blankable="A", index=-GAP - 1, replacewith="{0}𝒶"),
        pps.BlankSpaceMapping(blankable="C", index=-GAP - 1, replacewith="{0}𝒸"),
        pps.BlankSpaceMapping(blankable="E", index=-GAP - 1, replacewith="{0}𝑒"),
    ])
]

carry_the_one_postprocessors = [
    pps.SplitDelimiterPostprocessor("ONE", good_words),
    nlppps.SegmentationPostprocessor(),
    spps.SegmentedWordFilterPostprocessor(["ANYONE", "EVERYONE", "ONE", "ONESELF", "SOMEONE"]),
]

double_schroedingers_postprocessors = [
    pps.SplitPostprocessor(lambda s: multi_schroedinger(s, 3), good_words),
]

four_of_a_mind_postprocessors = [
    pps.RegexMatchPostprocessor(r"^[A-Z]{8,}$"),
    pps.UniqueLetterPostprocessor(max_required=4, min_required=4),
]

freestyle_postprocessors = [
    pps.DoubleOccupancyPostprocessor("FREE", "STYLE", good_words),
]

geoguessr_postprocessors = [
    pps.CaptureGroupPostprocessor([r"G...*", "O...*"], good_words),
    spps.SegmentedWordFilterPostprocessor(["GO", "GOES", "GOING", "GONE"]),
    spps.SegmentedWordFilterPostprocessor(["ONTO", "OVER"]),
]

its_all_wrong_singular_postprocessors = [
    # <noun>s <verb>
    pps.SplitDelimiterPostprocessor("S", good_words, mode="either"),
    # merge A S B -> AS B
    pps.FlatMapPostprocessor(lambda ts: [ts.replace(" ", "", 1)]),
    spps.SegmentedWordFilterPostprocessor(["BACK", "DOWN", "OFF", "OUT"]),
    pps.RegexMatchPostprocessor(r"^\S+S \S+$"),
    pps.FlatMapPostprocessor(lambda ts: [] if
        nlppps.PluralizablePostprocessor().apply(ts.split(" ")[0], -1) else [ts]),
    nlppps.SegmentedSentencePostprocessor(),
]

its_all_wrong_singular_formatted_postprocessors = [
    pps.RegexMatchPostprocessor(r"^\S+S \S+$"),
    spps.SegmentedWordFilterPostprocessor(["back", "down", "off", "out"]),
    pps.FlatMapPostprocessor(lambda ts: [] if
        nlppps.PluralizablePostprocessor().apply(ts.split(" ")[0], -1) else [ts]),
    nlppps.SegmentedSentencePostprocessor(),
]

its_all_wrong_plural_postprocessors = [
    # <noun> <verb>s
    pps.RegexMatchPostprocessor(r"^.*S$"),
    nlppps.SegmentationPostprocessor(),
    spps.SegmentedWordFilterPostprocessor(["CAT", "DOG"]),
    pps.RegexMatchPostprocessor(r"^.\w* .\w*S$"),
    pps.FlatMapPostprocessor(lambda ts: [ts] if all(len(t) >= 3 for t in ts.split(" ")) else []),
    # We actually want all words where the singular == plural, so the logic should be reversed.
    pps.FlatMapPostprocessor(lambda ts: [ts] if
        nlppps.PluralizablePostprocessor(reverse=True).apply(ts.split(" ")[0], -1) else []),
    nlppps.SegmentedSentencePostprocessor(),
]

its_all_wrong_plural_formatted_postprocessors = [
    # <noun> <verb>s
    pps.RegexMatchPostprocessor(r"^.\S+ .\S+S$"),
    spps.SegmentedWordFilterPostprocessor(["back", "cat", "dog"]),
    pps.FlatMapPostprocessor(lambda ts: [ts] if all(len(t) >= 3 for t in ts.split(" ")) else []),
    # We actually want all words where the singular == plural, so the logic should be reversed.
    pps.FlatMapPostprocessor(lambda ts: [ts] if
        nlppps.PluralizablePostprocessor(reverse=True).apply(ts.split(" ")[0], -1) else []),
    nlppps.SegmentedSentencePostprocessor(),
]

its_a_wash_postprocessors = [
    pps.CaptureGroupPostprocessor([r"A...*", "W...*"], good_words),
]

no_cap_postprocessors = [
    pps.RegexMatchPostprocessor(r"^NO.*$"),
    pps.FlatMapPostprocessor(lambda s: ["NO" + s]),
    nlppps.SegmentationPostprocessor(),
    spps.SegmentedWordFilterPostprocessor(["NOBODY", "NOPE", "NOWHERE", "NODE", "NOUN", "NONE", "NOTHING"]),
    # nlppps.SegmentedFilterPostprocessor(lambda s: is_punny(s, good_words, punny_words)),
]

no_notes_postprocessors = [
    pps.FlatMapPostprocessor(lambda s: no_notes(s, nifty_words)),
]

punctuated_for_emphasis_postprocessors = [
    pps.RegexMatchPostprocessor(r"^.{13}$"),
    pps.RegexMatchPostprocessor(r"^..+N..+$"),
    pps.SplitDelimiterPostprocessor(
        wordlist=non_stop_words,
        delimiter="N",
    ),
    # Make sure first and last words are different
    pps.FlatMapPostprocessor(lambda s: [] if s.split(" ")[0] == s.split(" ")[-1] else [s]),
    spps.SegmentedWordFilterPostprocessor(["DOW", "ERS", "ETS", "IRA"]),  # don't use initialisms
    spps.SegmentedWordFilterPostprocessor(["CANADIA", "ING", "ITALIA", "NORTHER", "SOUTHER", "UMBERS"]),
]

punctuated_for_emphasis_2_postprocessors = [
    pps.SplitDelimiterPostprocessor(
        wordlist=non_stop_words,
        delimiter="TO",
    ),
    spps.SegmentedWordFilterPostprocessor(["BRING", "BRINGS", "BRINGING", "BROUGHT"]),
    spps.SegmentedWordFilterPostprocessor(["BUILD", "BUILDS", "BUILDING", "BUILT"]),
    spps.SegmentedWordFilterPostprocessor(["CALL", "CALLS", "CALLING", "CALLED"]),
    spps.SegmentedWordFilterPostprocessor(["COME", "COMES", "COMING", "CAME"]),
    spps.SegmentedWordFilterPostprocessor(["GO", "GOES", "GOING", "GONE"]),
    spps.SegmentedWordFilterPostprocessor(["LEAVE", "LEAVES", "LEAVING", "LEFT"]),
    spps.SegmentedWordFilterPostprocessor(["LIVE", "LIVES", "LIVING", "LIVED"]),
    spps.SegmentedWordFilterPostprocessor(["LOVE", "LOVES", "LOVING", "LOVED"]),
    spps.SegmentedWordFilterPostprocessor(["RIP", "RIPS", "RIPPING", "RIPPED"]),
    spps.SegmentedWordFilterPostprocessor(["RISE", "RISES", "RISING", "ROSE"]),
    spps.SegmentedWordFilterPostprocessor(["TURN", "TURNS", "TURNING", "TURNED"]),
    spps.SegmentedWordFilterPostprocessor(
        ["ASTER", "ASTERS", "KENS", "MORROW", "READY", "RIGHT", "ROAD", "TIME", "YOU"]),
]

seeing_stars_postprocessors = [
    pps.SubstringPostprocessor([
        result
        for star in
        ["ALTAIR", "ANTARES", "ARCTURUS", "CASTOR", "DENEB", "ORION", "POLLUX", "RIGEL", "SIRIUS", "SPICA", "VEGA"]
        for result in insert_anywhere(star, "C")
    ])
]
