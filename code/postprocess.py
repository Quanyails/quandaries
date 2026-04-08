import copy
import json
import re
from typing import Tuple, List, Dict

import postprocessors.nlp as nlppps
import postprocessors.postprocessors as pps
import postprocessors.segmented as spps

CONFIG_PATH = "config.json"
GAP = 2

type Entry = Tuple[str, int]

def multi_schroedinger(s: str, degree: int) -> List[str]:
    results = []
    l = len(s)
    is_divisible = l % degree == 0
    if is_divisible:
        interval = l // degree
        for i in range(0, l, interval):
            results.append(s[i:i + interval])
    return results


def main(config_path: str):
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    entries: List[Entry] = []
    # with open(config["out"]["combined"], "r") as f:
    with open("data/nediger.txt", "r") as f:
        for line in f:
            word, score, *_ = line.strip().split(";")
            key = word
            value = int(score)
            entries.append((key, value))

    # pun_postprocessor = nlppps.PunPostprocessor(max_similarity=0.1)
    good_words = set(word for word, score in entries if score >= 48)
    nifty_words = set(word for word, score in entries if score >= 43)
    # punny_words = set(word for word, score in entries if pun_postprocessor.apply(word, score))
    non_stop_words = [word for word, score in entries if len(word) >= 3 and score >= 45]

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

    postprocessors = [
        # pps.LowScorePostprocessor(48),
        pps.LowScorePostprocessor(43),
        *its_all_wrong_plural_formatted_postprocessors,
    ]

    postprocesseds: List[List[Entry]] = [copy.deepcopy(entries)]
    for postprocessor in postprocessors:
        wcurrent = postprocesseds[-1]
        wnext: List[Entry] = []
        for word, score in wcurrent:
            result = postprocessor.apply(word, score)
            wnext.extend(result)
        # Remove duplicates
        deduped: Dict[str, int] = {}
        for word, score in wnext:
            deduped[word] = score
        postprocesseds.append(list(deduped.items()))

    with open(config["out"]["postprocessed"], "w", encoding="utf8") as f:
        for word, score in sorted(postprocesseds[-1]):
            f.write(f"{word};{score}\n")


if __name__ == "__main__":
    main(CONFIG_PATH)
