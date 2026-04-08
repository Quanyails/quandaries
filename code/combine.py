import json
from typing import List, Dict
from pathlib import Path

from tags import TagMeta
from overrides import OverrideMeta
from wordlists import WordlistEntry, WordlistMeta

CONFIG_PATH = "config.json"

def extract_bases(config: Dict) -> Dict[str, int]:
    wordlists: List[List[WordlistEntry]] = []
    for wordlist_data in config["wordlists"]:
        wordlist_meta = WordlistMeta(**wordlist_data)
        wordlist = wordlist_meta.extract()
        wordlists.append(wordlist)

    combined: Dict[str, int] = {}
    for wordlist in wordlists:
        for entry in wordlist:
            word = entry.word
            score = entry.score

            if word in combined:
                combined[word] = max(combined[word], score)
            else:
                combined[word] = score
    return combined


def extract_extended(config: Dict) -> Dict[str, int]:
    ewordlists: List[List[WordlistEntry]] = []
    for ewordlist_data in config["extended"]:
        ewordlist_meta = WordlistMeta(**ewordlist_data)
        ewordlist = ewordlist_meta.extract()
        ewordlists.append(ewordlist)

    ecombined: Dict[str, int] = {}
    for ewordlist in ewordlists:
        for entry in ewordlist:
            word = entry.word
            score = entry.score

            if word in ecombined:
                ecombined[word] = max(ecombined[word], score)
            else:
                ecombined[word] = score
    return ecombined


def extract_overrides(config: Dict) -> Dict[str, int]:
    # Apply overrides
    tags = TagMeta(path=config["score_path"]).extract()

    override_lists: List[List[WordlistEntry]] = []
    for f in Path(config["overrides"]["path"]).glob("*.txt"):
        override_meta = OverrideMeta(word_path=str(f))
        override_list = override_meta.extract(tags)

        # additions = set(override.word for override in override_list) - set(combined)
        # if additions and not override_meta.is_additive:
        #     for word in sorted(additions):
        #         print(f"Warning: Cannot override unknown word: {word}")

        override_lists.append(override_list)

    ocombined = {}
    for override_list in override_lists:
        for override in override_list:
            word = override.word
            score = override.score
            ocombined[word] = score

    return ocombined

def main(config_path: str, *,
         combine_bases: bool = True,
         combine_extended: bool = False,
         combine_overrides: bool = True,
         ):

    with open(config_path, "r") as f:
        config = json.loads(f.read())

    bcombined = extract_bases(config) if combine_bases else {}
    ecombined = extract_extended(config) if combine_extended else {}
    ocombined = extract_overrides(config) if combine_overrides else {}

    # Write results to target files
    if bcombined:
        with open(config["out"]["base"], "w") as f:
            for word, score in sorted(bcombined.items()):
                f.write(f"{word};{score}\n")

    if ocombined:
        with open(config["out"]["overrides"], "w") as f:
            for word, score in sorted({**ocombined}.items()):
                f.write(f"{word};{score}\n")

    if bcombined and ocombined:
        with open(config["out"]["combined"], "w") as f:
            for word, score in sorted({**bcombined, **ocombined}.items()):
                f.write(f"{word};{score}\n")

    if ecombined and bcombined and ocombined:
        with open(config["out"]["extended"], "w") as f:
            for word, score in sorted({**ecombined, **bcombined, **ocombined}.items()):
                f.write(f"{word};{score}\n")

if __name__ == "__main__":
    main(CONFIG_PATH,
         combine_bases=False,
         combine_extended=False,
         combine_overrides=True,
         )
