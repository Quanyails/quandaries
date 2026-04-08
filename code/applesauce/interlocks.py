from typing import List, Set
from dataclasses import dataclass
from collections import Counter

from grid import Grid
from grids import merge_grids
from symmetrical_pair import SymmetricalPair
from symmetrical_pairs import find_trunk_pairs, find_trunk_branch_pairs, find_branch_pairs, find_next_degree_pairs


@dataclass(frozen=True, slots=True)
class InterlockResult:
    grids: Set[Grid]
    pairs: Set[SymmetricalPair]


def boldify(s: str):
    return f"\033[1m{s}\033[0m"


def find_interlocks(words: List[str]) -> List[SymmetricalPair]:
    word_lengths = Counter(len(word) for word in words)
    trunks = [word for word in words if word_lengths[len(word)] == 1]
    branches = [word for word in words if word_lengths[len(word)] > 1]

    print(f"Pairable entries found: {branches}")
    print(f"Unpairable entries found: {trunks}")

    print("Evaluating interlocks...")

    trunk_pairs = find_trunk_pairs(words) if len(words) >= 2 else []
    trunk_branch_pairs = find_trunk_branch_pairs(trunks, branches) if trunks and len(branches) >= 2 else []
    branch_pairs = find_branch_pairs(branches) if len(branches) >= 4 else []

    degree_2_pairs = [
        *trunk_pairs,
        *trunk_branch_pairs,
        *branch_pairs,
    ]

    degree_pair_groups: List[List[SymmetricalPair]] = [
        degree_2_pairs,
    ]

    while next_degree_pairs := find_next_degree_pairs(degree_pair_groups[-1]):
        degrees = {grid.degree for pair in next_degree_pairs for grid in (pair.first, pair.second)}
        for degree in sorted(degrees):
            pairs = [pair for pair in next_degree_pairs if pair.first.degree == degree and pair.second.degree == degree]
            print(f"Evaluated {len(pairs)} interlocks(s) of degree {degree}...")
            degree_pair_groups.append(pairs)
    print()

    return [pair for pairs in degree_pair_groups for pair in pairs]

def dedupe_pair_entries(pairs: List[SymmetricalPair]) -> InterlockResult:
    # Dedupe pairs with repeated words, either by merging the pair or filtering them out.
    # This can cause the max degree of interlock found to go down.
    merged_grids: Set[Grid] = set()
    deduped_pairs: Set[SymmetricalPair] = set()

    for pair in pairs:
        merged = merge_grids(pair.first, pair.second)
        if merged and merged not in merged_grids and merged.as_transposed() not in merged_grids:
            merged_grids.add(merged)
        else:
            words1 = {entry.word for entry in pair.first.entries}
            words2 = {entry.word for entry in pair.second.entries}
            if not (words1 & words2):
                deduped_pairs.add(pair)
    return InterlockResult(
        grids=merged_grids,
        pairs=deduped_pairs
    )

def normalize_dimensions(interlock_result: InterlockResult) -> InterlockResult:
    normalized_grids = []
    normalized_pairs = []

    for grid in interlock_result.grids:
        # Transpose grid if height > width
        if grid.height > grid.width:
            normalized_grids.append(grid.as_transposed())
        else:
            normalized_grids.append(grid)

    for pair in interlock_result.pairs:
        # Transpose grid if height > width
        if pair.first.height > pair.first.width:
            normalized_pair = SymmetricalPair(
                first=pair.first.as_transposed(),
                second=pair.second.as_transposed(),
                symmetry=pair.symmetry,
            )
            normalized_pairs.append(normalized_pair)
        else:
            normalized_pairs.append(pair)

    return InterlockResult(
        grids=normalized_grids,
        pairs=normalized_pairs,
    )

def trim_evens(interlock_result: InterlockResult) -> InterlockResult:
    trimmed = []
    for grid in interlock_result.grids:
        if grid.width % 2 == 0 or grid.height % 2 == 0:
            continue
        trimmed.append(grid)
    return InterlockResult(
        grids=trimmed,
        pairs=interlock_result.pairs,
    )

def print_result(interlock_result: InterlockResult, shallow=True):
    if interlock_result.grids or interlock_result.pairs:
        if shallow:
            print("Showing highest-degree interlocks only.")
            print()
        else:
            print("Showing all interlocks.")
            print()
    else:
        print("No interlocks found.")
        print()

    # Sort from smallest to largest grid
    sorted_grids = sorted(interlock_result.grids, key=lambda g: g.width + g.height)
    sorted_pairs = sorted(interlock_result.pairs, key=lambda p: p.first.width + p.first.height)
    degrees = sorted({grid.degree for grid in sorted_grids} | {pair.first.degree for pair in sorted_pairs})

    for degree in reversed(degrees):
        grids = [g for g in sorted_grids if g.degree == degree]
        if grids:
            print(boldify(f"Found {len(grids)} viable grid(s) of degree {degree}"))
            print()
            for i, grid in enumerate(grids):
                print(f"Grid #{i + 1} w/ degree {degree} ({grid.width}x{grid.height})")
                print()
                print(grid)
                print()
                print()

        pairs = [p for p in sorted_pairs if p.first.degree == degree]
        if pairs:
            print(boldify(f"Found {len(pairs)} viable pairs of degree {degree}"))
            print()
            for i, pair in enumerate(pairs):
                print(f"Pair #{i + 1} w/ degree {degree} ({pair.first.width}x{pair.first.height}):")
                print()
                print(pair)
                print()
                print()

        if shallow:
            break


def main(words: List[str], show_all: bool = False):
    interlocks = find_interlocks(words)
    interlocks = dedupe_pair_entries(interlocks)
    # interlocks = trim_evens(interlocks)
    interlocks = normalize_dimensions(interlocks)
    print_result(interlocks, shallow=not show_all)


if __name__ == "__main__":
    # main(
    #     words=["AMBULANCECHASER", "ACCESSCODE", "ALLEYCAT", "ALCAPONE", "ALARMCLOCK", "AREACLOSED", "ALBUMCOVER"],
    # )
    # main(
    #     words=["GREATOUTDOORS", "GOLDENOREO", "GARYOLDMAN", "GIANTOTTER", "GREENONION"],
    # )
    main(
        words=["nervousrex","styxfigure","loxstockandbarrel","chexrepublic","youmakemesix","betterluxnexttime","flaxjacket","texsupport"],
        show_all=True,
    )
