# Crossword Construction Cheat Sheet

## Common rules/limits

From the 2004 version of _Crossword Puzzle Challenges for Dummies_:

- min 39 theme entry squares (81)
- min 3-letter words (98)
- max 20 3-letter words (98)
- max 78 words (handbook, page 103)
- make "bars" to limit automatic fill? (128)
- avoid "weak connectivity", i.e. ensure no part of grid can be cut off by adding one square (98)

For 16x15: ([source](https://discord.com/channels/531538864721100861/531538865262034965/1401705262884065351)):

- max 81 words
- max 40 black squares

For 21x21:

- target 90 - 108 theme squares ([source](https://discord.com/channels/531538864721100861/531538865262034965/1362917384800829581))
- max 80 black squares

From "Rules of thumb for crossword construction" ([source](https://messaging-custom-newsletters.nytimes.com/dynamic/render?uri=nyt%3A%2F%2Fnewsletter%2F01fc2635-860c-5f4d-99b8-23866487c790&productCode=EM&isViewInBrowser=true), [archive.today](https://archive.is/44SOr), [source](https://discord.com/channels/531538864721100861/531538865262034965/1431259920686121112)):

- Try to limit # of 3-letter words and to make them real words
- Try to limit <= 40 black squares for a 15x15 and <= 80 black squares for a 21x21

Other:

- 7/2/1 rule: portion clues as 7 easy, 2 tricky, and 1 hard ([source](https://communicrossings.com/constructing-crosswords-clues))
- Avoid references to bodily functions and medical terms (e.g. URINE and ENEMA) ([source](https://www.youtube.com/watch?v=zY--b3mx7Xw&t=138s), [source 2](https://discord.com/channels/531538864721100861/926299279885230080/1260985762598621277))
- Mention alternate options for themers when submitting a theme entry or grid ([source](https://discord.com/channels/531538864721100861/531538865262034965/1433162528279498752))

Clue difficulty table:

OREO ([source](https://communicrossings.com/crosswords-choose-appropriate-difficulty#sum)):

- Monday: "Nabisco cookie," "Cookie with creme filling", "'Twist, Lick, Dunk' cookie"
- Saturday: "Snack since 1912", "It has 12 flowers on each side", "Sandwich often given a twist"

STRAP ([source](https://www.nytimes.com/article/submit-crossword-puzzles-the-new-york-times.html)):

- Monday clue: “Subway rider’s handhold”
- Wednesday clue: “Part of a bike helmet”
- Saturday clue: “What might keep a watch on you”

Also see: [Crossword Difficulty - XWord Blog](https://xwordblog.com/2025/12/26/crossword-difficulty/)

## Personal observations

Theme:

- If a theme isn't working directly, make the flaw into a feature! Examples:
  - Turn numbers that don't quite match into an "off-by-one" theme ([example](https://www.crosserville.com/archive/puzzle/38825)).
  - Manipulate themers that don't have the right length into a theme that does ([example](https://crosswordfiend.com/2019/11/07/friday-november-8-2019/#ch)).

Layout:

- Think of black squares as splitters, not walls. This way, you can think about whether inserting a black square is meaningful by understanding whether they split one word into two.
- It becomes more difficult to fill a slot the more constrained it is. Try to keep slots from spanning more than two theme entries when placing black squares ([source](https://docs.google.com/document/d/1yWKNdR-r12hoI-PG0H62o3drtga_EpDbcjYSXOg_9pY/edit?tab=t.0#heading=h.7vgh6jlorwn0)).
- Limit the number of slots that pass through the same two themers consecutively. A sequence of slots that shares two constraints each offers fewer options than a sequence of slots that is broken up by a slot that shares one constraint each.
- Cheater squares are great as a last resort. You should only use them if you have an otherwise-complete grid with only one stinker entry.
- Pay attention to chokepoints in the grid. Optimally, don't include them in the structure of your grid. If you're forced to include them, make sure the words in them are solid. If the words that go into them are, say, two-word phrases, it can be tricky to use knowledge for that entry to populate one side of the grid from the other side.
- The bigger a grid, the more individual "pain slots" will hamper your ability to complete a fill. In smaller grids, you can often get away with working _with_ a pain slot, but in bigger grids, you all but need to change themer/black square placement to mitigate these pain slots.
- When working with larger grids, you need to be increasingly mindful of which letters constrain your fill the most. Understanding letter frequencies of English words can be a boon when ensuring a grid remains unconstrained ([example infographic](https://redd.it/lowync/)). For example, it's a good idea to place letters like J and Q at the beginnings of slots and S and Y at the end.
- When hunting for good places to open up long slots on a low-word-count grid (e.g. New York Times Sunday-size crosswords), look for slots with vowels + RSTLNE.

Fill:

- If you're struggling to fill in a grid, the answer might not necessarily be "get a bigger wordlist" as much as "find a better way to construct your grid". A large wordlist is helpful to get started, but eventually, you will need to work smarter, not harder, to make good grid layouts.
- Just because publishers are looking for lively fill doesn't mean you should take every nifty word the autofill suggests. Lively fill is only lively by comparison. Embed words to your grid the same way you would a treasure hunt; it's more delightful to see a sparkly entry amid an otherwise ordinary part of the grid than to try to stuff as many sparkly entries in the grid as possible.
- Grid-killers are non-negotiable. If your grid is sparkly but is held together by a grid-killer, you're going to have to "kill your darling".
- Keep an eye out for how many words in the fill end in S. Too many words that end in S can make players feel like they are cheated out of "real" solveable squares ([source](https://discord.com/channels/531538864721100861/926299279885230080/1359976551319601335)).
- If you're forced to use a phrasal verb (a verb that takes a preposition), it's more compelling to use an option where the preposition changes the underlying meaning of the verb. E.g. ACT UP is more compelling than ACT ON.
- Watch out for pairs of entries ending in S. If an S can be substituted by a black square without changing the meaning of both intersecting entries, it's not contributing much to the puzzle—and in fact, players can often fill in the S without knowing the rest of the clue just from looking at what part of speech the clues are.
- Related to the above principle: If I need to choose between two entries ending in S, I consider it more elegant to choose the entry where the ending S is non-optional. For example, if all else were equal, I would opt for ANDES as an entry over ANTES.
- If you have 2+ equally-appealing options for fill, come back to it after you have filled out other regions of the grid. You might need one of the words in another region.
- If you have 2+ equally-appealing options for fill, consider choosing your fill based on the following criteria:
  1. How fun the fill is. ANGUS is nicer than ANGST, for example.
  1. How fun and/or flexible the entry is to clue. ACE has more options than APE (subjectively).
  1. Scrabbliness. JAW is more fun than RAW.

Cluing:

- Just because publishers are looking for lively clues doesn't mean you need to clue every entry uniquely. Too much trivia makes for an unpleasant solving experience for those out-of-the-know.
- Review clues by grid region. It can make for a tough solving experience if all of the clues in a region of a grid happen to be sports-related or movie-related.
- Try to use a lively mix of clue qualifiers. It feels repetitive if half of your clues end in "for short" or "slangily".
- Ensuring a clue is inferable is helpful for adjusting its difficulty.

Cluing specifics:

- If the only clues for a given entry take on the form "Some ____" (e.g. "Some vintage cars" for REOS), it's not very flexible to clue.
- Any clues that start with "Half of a" (e.g. NANU, TSE) feel clunky to me _unless_ both halves are in the grid. E.g. I had one fill that contained both ARO and ACE, and that was fun to pair up.
- When determining if an entry is an asset or not, write a clue for it, then imagine how your playtesters react upon finding the solution. If the reaction is "well, okay I guess", the entry is probably not an asset.

Tips for specific themes:

- There's no formal rule to how to split bookends--either have them be consistent or all varied ([source](https://discord.com/channels/531538864721100861/531538865262034965/885058181745770527)).
- Hidden words in a bookends theme should be 4+ letters long ([source](https://discord.com/channels/531538864721100861/531538865262034965/857723929354436628)).
- New York Times preferences:
  - "In general, we tend to avoid themes where inanimate objects are clued as if they are sentient." ([source](https://discord.com/channels/531538864721100861/926299279885230080/1348469570868084807))

Specific dings by outlet:

- AFAIK: Universal ([source](https://discord.com/channels/531538864721100861/753036458549444648/1446141232135929917))
- SNOT: LA Times ([source](https://discord.com/channels/531538864721100861/531538865262034965/1088953260095852564))

## General tips

- If your goal is to get published by the New York Times, construct Sunday puzzles, as Sunday puzzles have less competition ([1](https://communicrossings.com/constructing-crosswords-publish), [2](https://www.saturdayeveningpost.com/2022/10/how-i-got-my-crossword-puzzle-accepted-by-the-new-york-times/), [3](https://www.princewilliamtimes.com/news/-/article_c07a5140-ae57-11ef-b648-0ff020c40836.html)).
