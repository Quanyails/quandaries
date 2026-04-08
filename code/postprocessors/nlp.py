import importlib.resources
import itertools
import os

import inflect
import nltk

from nltk.corpus import english_wordnet
from nltk.stem import WordNetLemmatizer
from symspellpy.symspellpy import SymSpell
from typing import override, Iterable, Tuple

from .base import BasePostprocessor

def use_symspell():
    # https://symspellpy.readthedocs.io/en/latest/examples/word_segmentation.html
    dict_path = importlib.resources.files("symspellpy") / "frequency_dictionary_en_82_765.txt"
    sym_spell = SymSpell(max_dictionary_edit_distance=0, prefix_length=7)
    sym_spell.load_dictionary(dict_path, term_index=0, count_index=1)

    return sym_spell


def use_wordnet():
    root_dir = os.path.dirname(os.path.dirname(__file__))

    nltk.data.path.append(root_dir)
    nltk.download("english_wordnet", download_dir=root_dir)
    nltk.download("wordnet", download_dir=root_dir)


class PluralizablePostprocessor(BasePostprocessor):
    def __init__(self, *, reverse: bool = False):
        self.inflect = inflect.engine()
        self.lemmatizer = WordNetLemmatizer()
        self.reverse = reverse

    def apply(self, word, score):
        # Only nouns are pluralizable
        if not english_wordnet.synsets(word, pos=english_wordnet.NOUN):
            return []

        singular = self.lemmatizer.lemmatize(word, pos=english_wordnet.NOUN)
        plural = self.inflect.plural(singular)

        has_plural = singular != plural

        if has_plural ^ self.reverse:
            return [(plural, score)]

        return []


class PunPostprocessor(BasePostprocessor):
    def __init__(self, max_similarity):
        use_wordnet()

        self.max_similarity = max_similarity

    # Check the semantic similarity of all possible definitions of a word to see if it is a good pun candidate
    # Optimally, this should capture words like TRUNK but not CAT.
    def apply(self, word, score):

        synsets = english_wordnet.synsets(word)

        # Either the entry is not a single word or the entry has one definition
        # if len(synsets) < 2:
        #     return []

        # Contrived threshold for determining good pun candidates
        if len(synsets) < 5:
            return []

        for s1, s2 in itertools.combinations(synsets, 2):
            similarity = english_wordnet.path_similarity(s1, s2)
            if similarity < self.max_similarity:
                return [(word, score)]

        return []


class SegmentationPostprocessor(BasePostprocessor):
    """
    E.g. "HOOFTENTIMES" can be divided into "HOOF TEN TIMES",
    while a naive dictionary lookup would indicate "HOOFTENTIMES"
    isn't a valid word.
    """
    def __init__(self):
        self.sym_spell = use_symspell()

    @override
    def apply(self, word, score):
        tokens = (self.sym_spell
                  # Don't autocorrect perceived misspellings
                  .word_segmentation(word, max_edit_distance=0)
                  .corrected_string
                  .upper()
                  .split(" "))

        # Verify we did not autocorrect anything in segmentation
        if "".join(tokens) != word:
            return []

        # Return entries with spaces for readability
        return [(" ".join(tokens), score)]
        # return [(word, score)]

class SegmentedSentencePostprocessor(BasePostprocessor):
    def __init__(self):
        use_wordnet()

    @override
    def apply(self, word, score):
        tokens = word.split(" ")

        # POSes consist of single-letter entries from Wordnet, as documented here:
        # https://www.nltk.org/nltk_data/
        # https://www.nltk.org/howto/wordnet.html
        last_pos = {
            synset.pos()
            for token in tokens[-1:]
            for synset in english_wordnet.synsets(token)
        }
        rest_pos = {
            synset.pos()
            for token in tokens[:-1]
            for synset in english_wordnet.synsets(token)
        }

        is_noun_phrase = "n" in last_pos
        if not is_noun_phrase:
            return []

        is_sentence = "n" in rest_pos and "v" in last_pos
        if not is_sentence:
            return []

        return [(word, score)]
