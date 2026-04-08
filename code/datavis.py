import json
import string
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotnine as p9
from typing import List

from wordlist import WordlistEntry
from wordlists import Wordlist

CONFIG_PATH = "config.json"


@dataclass(frozen=True, slots=True)
class LetterDatum:
    index: int
    l: int  # exclusive
    letter: str


def letterify(entries: List[WordlistEntry], letter: str) -> List[LetterDatum]:
    results = []

    for entry in entries:
        word = entry.word.lower()
        l = len(word)
        for i, c in enumerate(word):
            if c == letter:
                results.append(LetterDatum(index=i, l=l, letter=c))

    return results

def plot_letter_distribution(
        name: str,
        df: pd.DataFrame) -> p9.ggplot:
    """
    Inspiration:
    - https://redd.it/lowync/

    Resources used:
    - https://redd.it/gecugdu/
    - https://medium.com/codex/3ef7f8d1500e
    - https://www.stratascratch.com/blog/5-alternatives-to-matplotlib-that-make-data-visualization-a-breeze/
    """

    numbins = 12  # must be number that divides evenly

    chart = (
        p9.ggplot(df, p9.aes(x='value'))
        + p9.facet_wrap(
            '~letter',
            ncol=4,
        )
        + p9.geom_histogram(
            p9.aes(fill=p9.after_stat('count')),
            bins=numbins,
            # color='white',
        )
        + p9.labs(
            title=f"Letter distribution in{name}",
            x="% of way through word",
            y="Frequency",
        )
        + p9.scale_x_continuous(
            # labels=lambda ns: [f'{n:.0%}' for n in ns],
            # add padding on either side for bucket purposes so
            # values at 0.0 and 1.0 aren't cut off
            limits=(-0.1, 1.1),
        )
        + p9.scale_fill_gradient(low='#4400CC', high='#FF8000')
        + p9.theme_minimal()
        + p9.theme(
            axis_text_x=p9.element_blank(),  # don't show x-axis ticks
            axis_text_y=p9.element_blank(),  # don't show y-axis ticks'
            axis_title_x=p9.element_text(margin={"t": 32}),
            figure_size=(6, 10),
            panel_spacing_y=1 / 36,
            plot_title=p9.element_text(family="Calibri", linespacing=1.5, size=16),
            strip_align_x=-3.7,  # hacky way of putting label at bottom of facet
            strip_text_x=p9.element_text(size=12),
        )
    )

    return chart


def main(config_path: str, save=False):
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    file = "data/spreadthewordlist.dict"
    min_score = 50
    name = "\nspread the wordlist (2025-10-01)\nat score ≥ 50"
    out = config["out"]["frequencies"]

    raw_entries = Wordlist(path=file).extract()
    entries = [
        entry for entry in raw_entries if entry.score >= min_score
    ]

    df = pd.DataFrame()  # rows: {letter: str, value: float}

    for letter in string.ascii_lowercase:
        letter_data = letterify(entries, letter)

        rows = []
        for datum in letter_data:
            # 1/5 -> 0 -> 0%
            # 2/5 -> 1 -> 25%
            # 3/5 -> 2 -> 50%
            # 4/5 -> 3 -> 75%
            # 5/5 -> 4 -> 100%
            if datum.l > 1:
                rows.append({"letter": letter, "value": datum.index / (datum.l - 1) })

        rdf = pd.DataFrame(rows)
        df = pd.concat([df, rdf], ignore_index=True)

    p9chart = plot_letter_distribution(name, df)
    p9chart.show()

    if save:
        Path(out).mkdir(parents=True, exist_ok=True)
        p9chart.save(out)


if __name__ == "__main__":
    main(CONFIG_PATH)
