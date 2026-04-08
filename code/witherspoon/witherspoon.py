import puz

from collections import Counter, defaultdict
from typing import Iterable, Dict

def normalize(s: str):
    # map ' -> ""
    # map - -> " "
    replaced = s.upper().replace("'", "").replace("-", " ")

    return "".join(c for c in replaced if c.isalnum() or c.isspace())

def find_cross_references(entries: Iterable[str], wordlist: Dict[str, int]):
    word_index = defaultdict(set)
    for word in wordlist.keys():
        for token in word.split(" "):
            word_index[token].add(word)

    word_counts = Counter()
    for entry in entries:
        matching_words = word_index[entry]
        for word in matching_words:
            word_counts[word] += 1

    # We have found a match if # of tokens in the word = # of instances > 1 found
    found = set()
    for word, count in word_counts.items():
        found_needed = len(word.split(" "))
        if found_needed > 1 and count >= found_needed:
            found.add(word)

    return found


def main(puz_file: str, wordlist_file: str):
    # Make wordlist
    normalized_wordlist = {}
    with open(wordlist_file) as f:
        for line in f:
            rawword, scorestr = line.strip().split(";")
            word = normalize(rawword)
            normalized_wordlist[word] = int(scorestr)

    # Extract all entries from puzzle
    # This assumes there are no dupes in the entries
    puzzle = puz.read(puz_file)
    clues = puzzle.clue_numbering()
    entries = {
        normalize(clue.solution) for clue in clues.across
    } | {
        normalize(clue.solution) for clue in clues.down
    }

    found = find_cross_references(entries, normalized_wordlist)

    if found:
        print("Found cross-references:")
        print()

        for word in sorted(found):
            print(f"{word} {normalized_wordlist[word]}")


if __name__ == "__main__":
    puz_file = "tmp.puz"
    wordlist_file = "../wordlists/in/nediger.txt"
    main(puz_file, wordlist_file)
