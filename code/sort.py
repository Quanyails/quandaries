import json

CONFIG_PATH = "config.json"

PREP = [
    "after",
    "as",
    "at",
    "atop",
    "by",
    "down",
    "far",  # really?
    "for",
    "in",
    "into",
    "it", # really?
    "near",
    "of",
    "on",
    "out",
    "to",
    "up",
]

def prepkey(word: str):
    try:
        p = next(prep for prep in PREP if word.endswith(prep))
    except StopIteration as e:
        raise ValueError(f"No preposition found for word: {word}") from e
    return p, word

def main(config_path: str):
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    for override in config["overrides"]["data"]:
        with open(override["word_path"], "r") as f:
            words = f.read().splitlines()

        if "sort" in override and override["sort"] == "length":
            sorted_words = sorted(words, key=lambda w: len(w.split(",")[0]))
        if "sort" in override and override["sort"] == "prep":
            sorted_words = sorted(words, key=lambda w: prepkey(w.split(",")[0]))
        else:
            sorted_words = sorted(words)

        with open(override["word_path"], "w") as f:
            f.write("\n".join(sorted_words))

if __name__ == "__main__":
    main(CONFIG_PATH)
