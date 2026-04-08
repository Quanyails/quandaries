# Constraint Solver Requirements

Grid dimensions constraints:

- Output:
- min width
- max width
- min height
- max height
- min sum of min + height
- max sum of min + height

Black squares constraints:

- enforce symmetries (cuts search space down by half/quarter):
  - rotational
  - left-right
  - top-down
  - tl to br
  - bl to tr

- dedupe transpositions (bool) but NOT rotation
- max black squares

Slot constraints:

- min word length = 3
- max word length
- add # theme entries
- add theme entry lengths

Slots constraints:

- min word count
- max word count
- max 3-letter words = 20

Implementation:

- limit results to "bars" consisting of alternating sequences of black/white runs that work in either direction
- identify bars as unique sequences of (span, starting index)

Additional settings:

- can entries intersect (bool)
- can entries stack (bool)
- can perpendicular entries be longer than theme entries (bool)
- degree of connectivity (int)
  - I.e. how many squares you need to turn black to disconnect any region of the grid from any other region of the grid.

- cap at # grids shown (1000)
