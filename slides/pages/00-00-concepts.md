<!--

- The more entries you solve, the more letters you have to help you solve the remaining clues
- Crossword puzzles often have a gimmick (otherwise called a "theme"), which gets uncovered as you figure out more clues

- Are most well-known for being featured in newspapers since back in the 1940s
  - But have seen a second wave of interest due to online platforms + COVID

\* with rare exceptions

-->

<!--

- Crossword puzzles are a class of single-layer word games in which the objective can be stated as:
  - Given a list of clues and boxes, write the clue's answer in its corresponding boxes. The crossword is considered solved once all of the boxes contain the right entries.
- Multiple types of puzzles are referred to as "crossword puzzles", including:
  1. American-style crosswords (quicks)
  1. British-style crosswords (cryptics)
  1. barred crosswords
  1. Criss-Cross puzzles
  1. \+ other varieties
- This presentation focuses on American-style crosswords.
- TODO: add image examples

- [Criss-Cross puzzles](https://www.puzzles.wiki/wiki/Criss-Cross)
-->

<!--

You might be a fan of Minute Cryptic, but we will not be covering this style here.

We're assuming you're creating crosswords with the intent of getting accepted by a major US publication. If you're creating a crossword for fun, you don't have to follow these principles as rigidly.

We're assuming technical help. We are not going to go pen-and-paper, though some veteran constructors suggest this.
-->

<!--

Bonus: Try writing your own crossword construction app! It's easier than it sounds. I wrote one as my capstone project for [15-112](https://www.cs.cmu.edu/~112/), an intro-level course at Carnegie Mellon University.

-->

<!--
- Word lists include content such as:
  - Dictionary terms (e.g. CROW'S NEST)
  - Idioms, sayings, and phrases (e.g. IT'S A FACT)
  - Famous names (e.g. GARY OLDMAN)
  - Abbreviated forms (e.g. TTYL)

> Note: In most crossword construction software, you can use multiple word lists at once! Combining word lists can help you get more fill coverage than using one alone.
-->

<!--
Lots of subtle gotchas here, including:

- You can get decently far by placing squares without a strong sense of purpose until autofill tells you the grid is fillable.
- I basically treat this step as depth-first search—try to fill the grid, downscore entries you encounter but don't like, and try again until you get a completed grid.


> Technical note: Crossword construction is a [constraint satisfaction problem](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem) with a lot of unsolved problems. It's cool seeing the hobbyist research done in this space! Examples:
> - [Nick Knudsen – Evolutionary Crossword Grid Shape Generation](https://nicholasknudsen.com/code)
> - [Orca: A High-Performance Crossword Filler](https://rainjacket.github.io/orca-solver/)

-->
