from itertools import combinations, permutations, product
from typing import List, Set, Tuple

from grids import merge_grids
from symmetrical_pair import Intersected, Intersection, SymmetricalPair

def _find_intersecting_pairs_inner(trunk1: str, trunk2: str, branch1: str, branch2: str) -> List[SymmetricalPair]:
    intersecting_pairs: Set[Tuple[Intersection, Intersection]] = set()

    assert len(trunk1) == len(trunk2), f"Trunk lengths must be equal, got {len(trunk1)} and {len(trunk2)}"
    assert len(branch1) == len(branch2), f"Branch lengths must be equal, got {len(branch1)} and {len(branch2)}"

    for i in range(len(trunk1)):
        tchar1 = trunk1[i]
        tchar2 = trunk2[-i - 1]

        for j in range(len(branch1)):
            bchar1 = branch1[j]
            bchar2 = branch2[-j - 1]

            if tchar1 == bchar1 and tchar2 == bchar2:
                hb1 = Intersected(j, branch1)
                hb2 = Intersected(-j - 1 % len(branch2), branch2)
                hc1 = Intersected(i, trunk1)
                hc2 = Intersected(-i - 1 % len(trunk2), trunk2)

                i1 = Intersection(
                    first=hc1,
                    second=hb1,
                )
                i2 = Intersection(
                    first=hc2,
                    second=hb2,
                )
                intersecting_pairs.add((i1, i2))

    symmetrical_pairs: Set[SymmetricalPair] = set()

    for i1, i2 in intersecting_pairs:
        g1 = i1.as_grid()
        g2 = i2.as_grid()
        pair = SymmetricalPair(g1, g2, symmetry="R")

        # Only keep one variation of each symmetrical pair
        if not set(pair.variations()) & symmetrical_pairs:
            symmetrical_pairs.add(pair)

    return list(symmetrical_pairs)


def find_trunk_pairs(trunks: List[str], branches: List[str]) -> List[SymmetricalPair]:
    assert len(branches) >= 2, f"Must have at least two branches, instead received {len(branches)}"
    assert len(set(branches)) == len(
        branches), f"Branches must be unique, instead received {len(set(branches))} unique branches"

    all_symmetrical_pairs: Set[SymmetricalPair] = set()

    for trunk in trunks:
        for branch1, branch2 in permutations(branches, 2):
            # Skip unequal pairs
            if len(branch1) != len(branch2):
                continue
            symmetrical_pairs = _find_intersecting_pairs_inner(trunk, trunk, branch1, branch2)
            all_symmetrical_pairs.update(symmetrical_pairs)

    return list(all_symmetrical_pairs)


def find_branch_pairs(branches: List[str]) -> List[SymmetricalPair]:
    assert len(branches) >= 4, f"Must have at least four branches, instead received {len(branches)}"
    assert len(set(branches)) == len(
        branches), f"Branches must be unique, instead received {len(set(branches))} unique branches"

    all_symmetrical_pairs: Set[SymmetricalPair] = set()

    for b1, b2, b3, b4 in permutations(branches, 4):
        # Skip unequal pairs
        if len(b1) != len(b2) or len(b3) != len(b4):
            continue
        symmetrical_pairs = _find_intersecting_pairs_inner(b1, b2, b3, b4)
        all_symmetrical_pairs.update(symmetrical_pairs)

    return list(all_symmetrical_pairs)


def _find_next_degree_pair(pair1: SymmetricalPair, pair2: SymmetricalPair) -> SymmetricalPair | None:
    symmetries = {pair1.symmetry, pair2.symmetry}
    assert len(symmetries) == 1, f"Can't merge pairs with different symmetries: {pair1.symmetry} and {pair2.symmetry}"
    symmetry = next(iter(symmetries))

    first1, second1 = pair1.first, pair1.second
    first2, second2 = pair2.first, pair2.second

    assert first1.degree == first2.degree, f"Can't merge pairs with different degrees: {first1.degree} and {first2.degree}"
    assert second1.degree == second2.degree, f"Can't merge pairs with different degrees: {second1.degree} and {second2.degree}"

    merged1 = merge_grids(first1, first2)
    if not merged1:
        return None

    merged2 = merge_grids(second1, second2)
    if not merged2:
        return None

    # Merges must be distinct from original grids
    existing = (first1, second1, first2, second2)
    if merged1 in existing or merged2 in existing:
        return None

    # Merges must remain symmetrical
    if not (merged1.width == merged2.width and merged1.height == merged2.height):
        return None

    assert merged1.degree > first1.degree, f"Expected merged pair degree to be greater than {first1.degree}, instead received {merged1.degree}"
    assert merged2.degree > second2.degree, f"Expected merged pair degree to be greater than {second2.degree}, instead received {merged2.degree}"
    assert merged1.degree == merged2.degree, f"Expected merged pair degree to be equal to {merged1.degree}, instead received {merged2.degree}"

    result = SymmetricalPair(
        first=merged1,
        second=merged2,
        symmetry=symmetry,
    )

    return result


def find_next_degree_pairs(symmetrical_pairs: List[SymmetricalPair]) -> List[SymmetricalPair]:
    next_degree_pairs: Set[SymmetricalPair] = set()

    for pair1, pair2 in combinations(symmetrical_pairs, 2):
        for parvar1, parvar2 in product(pair1.variations(), pair2.variations()):
            next_degree_pair = _find_next_degree_pair(parvar1, parvar2)
            if next_degree_pair and not set(next_degree_pair.variations()) & next_degree_pairs:
                next_degree_pairs.add(next_degree_pair)

    return list(next_degree_pairs)
