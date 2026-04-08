# Concepts

## Formal definitions

- Character: A symbol $A$ through $Z$.
- Word: A finite, ordered string of Characters.
  - Example: $(H, E, L, L, O)$
- Vector: A non-negative pair of integers $(x, y)$ in the XY coordinate plane.
  - Example: $(1, 0)$
- Coordinate: A Vector representing a location on the XY coordinate plane.
- Delta: A Vector representing a change in direction on the XY coordinate plane. A Delta alters the value of a Coordinate.
- Direction: A token `Across` or `Down` representing a Delta of $(1, 0)$ or $(0, 1)$, respectively.
- Entry: A 3-tuple consisting of a Word, Coordinate, and Direction. An Entry occupies XY coordinates starting from Coordinate, moving in Direction, for the length of Word.
  - In layman's terms, it represents a horizontal/vertical line segment in which each every integer point on that line is associated with a given Character.
- Intersection Point: A Character-Coordinate pair.
- Intersection: A list of Intersection Points $a$ of length ≥ 1 and a list of Entries $e$ of length ≥ 2 in which all Entries share one Character $c$ in $a$ and each Character $c$ in $a$ is used by exactly one $e$ with Direction `Across` and one `Entry` with Direction `Down`. The Words in an Intersection must be unique.
- Degree: The # of Intersection Points in a given Intersection.
- Symmetrical Pair: A pair of Intersections in which the Entries in each Intersection are symmetric relative to each other. The constraint of symmetry ensures each Intersection in this pair has the same Degree, and so we can say that the Degree of a Symmetrical Pair equals the Degree of either of its Intersections. The Intersections in a Symmetrical Pair are allowed to share Words.

## Theory

The key finding by which this script finds symmetrical pairs 
of interlocking words is this:

Symmetrical Pairs form a recurrence relation. In other words, we are able to find higher-degree Symmetrical Pairs by performing a union on Entries in lower-degree Symmetrical Pairs. More crucially, we are able to find Symmetrical Pairs of degree $n$ by checking the unions on all 2-combinations of Symmetrical Pairs of degree $n - 1$.

Thus, by generating a list of all Symmetrical Pairs with Degree 1, we can use these Degree-1 Symmetrical Pairs to construct all Symmetrical Pairs of Degree 2, 3, and so on in sequence until have constructed Symmetrical Pairs with the highest Degree available.

From here, we remove any Symmetrical Pairs that have the same word in both Intersections. We can either remove the Symmetrical Pair outright from our set of results or, possibly, we are able to create a valid Intersection by creating a union between both Intersections.
