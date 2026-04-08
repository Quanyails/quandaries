import importlib.resources
import json

from collections import defaultdict

from symspellpy import SymSpell, Verbosity

MAX_TYPOS_EXPECTED = 3

def spellcheck(config_path: str):
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    dict_path = importlib.resources.files("symspellpy") / "frequency_dictionary_en_82_765.txt"
    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    sym_spell.load_dictionary(dict_path, term_index=0, count_index=1)

    entries = []

    with open("data/nediger.txt", "r") as f:
        for line in f:
            word, score, *_ = line.strip().split(";")
            key = word
            value = int(score)
            entries.append((key, value))

    typos = []

    for (word, score) in entries:
        tokens = word.split(" ")

        for token in tokens:
            suggestions = sym_spell.lookup(
                token, Verbosity.CLOSEST, max_edit_distance=2, transfer_casing=True)
            if suggestions: # potential typo
                suggestion = suggestions[0].term
                if token != suggestion:
                    typos.append((word, token, suggestion))

    mapping = defaultdict(list)

    for word, token, suggestion in typos:
        mapping[f"{token} > {suggestion}"].append(word)

    with open(config["out"]["postprocessed"], "w") as f:
        for token_suggestion, words in sorted(mapping.items()):
            if len(words) < MAX_TYPOS_EXPECTED:
                f.write(f"{token_suggestion}: {', '.join(words)}\n")

if __name__ == "__main__":
    spellcheck("config.json")
