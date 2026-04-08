"""
claude.py

Proofreads a crossword wordlist file using the Anthropic API.
Handles entries that may be missing spaces, wrong/missing capitalisation,
missing apostrophes, or misspelled — including all-caps mangled forms like
TISTHESEASON → 'tis the season.

Input format (one entry per line):
    <term>;<score>

Output format:
    <corrected_term>;<score>           (if unchanged or no note)
    <corrected_term>;<score>;<note>    (if Claude left a note)

Lines that are unchanged are written identically to the input, making the
output directly diffable against the source.

If the script is interrupted, re-running it on the same output file will
automatically resume from where it left off by comparing line counts.
"""

import itertools
import sys
import time
from pathlib import Path

import anthropic
import click

# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_BATCH_SIZE = 150
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2048
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds; multiplied by attempt number

SYSTEM_PROMPT = """\
You are a meticulous proofreader for crossword puzzle word lists.
Each entry is a word, phrase, or cultural reference paired with a familiarity \
score (higher = more widely known).

Fix each entry's text. The vast majority of entries will be in English. \
Foreign words and phrases will appear when they are at least moderately well-known \
(e.g. French, Latin, Spanish loanwords or common phrases). Entries may have any \
combination of these problems:
  - Missing spaces (e.g. "TISTHESEASON" → "'tis the season")
  - Wrong or missing capitalisation (e.g. "newyorkcity" → "New York City")
  - Missing apostrophes or punctuation ("ITS A WONDERFUL LIFE" → "It's a Wonderful Life")
  - Genuine misspellings

Output format — return ONLY lines in this exact format, one per input entry, same order:
    <corrected_term>;<score>;<optional note>

Rules:
  1. Output ONLY the lines described above — no JSON, no markdown, no explanation.
  2. <corrected_term> is your best corrected version, or the original if no fix is needed.
  3. <score> must be copied exactly from the input, unchanged.
  4. <optional note>: include a brief note when you made a change OR are uncertain. \
If the entry is fine and you are confident, leave it empty — do not include a trailing \
semicolon in that case. So a confident unchanged entry is just: <term>;<score>
  5. Be CAUTIOUS. If unsure whether something is a typo vs. an intentional style choice \
or obscure proper noun, do NOT change it — copy it through as-is and add a note flagging \
your uncertainty. Low-score entries (≤35) deserve extra caution.
  6. Preserve proper capitalisation: brand names, proper nouns, film/book/song titles, etc.
  7. Do NOT convert non-American English spellings to American English. \
"colour", "theatre", "realise" are correct if that is the intended spelling.
"""

USER_PROMPT_TEMPLATE = """\
Proofread these {n} wordlist entries and return one output line per entry in the \
same order. Format: <corrected_term>;<score>;<optional note> \
(omit the trailing semicolon and note if the entry is correct and you are confident).

{entries}"""


# ── Parsing helpers ──────────────────────────────────────────────────────────

def parse_input_line(line: str) -> tuple[str, str] | None:
    """Parse '<term>;<score>\\n' → (term, score), or None for blank/malformed lines."""
    try:
        term, score, *_ = line.split(";")
        return term, score
    except Exception as e:
        print(f"Error parsing input line: {e}")
        return None


def parse_output_line(line: str) -> tuple[str, str, str] | None:
    """
    Parse a single line from Claude's response:
        '<corrected>;<score>'            → (corrected, score, "")
        '<corrected>;<score>;<note>'     → (corrected, score, note)
    The note may itself contain semicolons; only the first two are split on.
    Returns None for blank/malformed lines.
    """
    def parse_output_line(line: str) -> tuple[str, str, str] | None:
        """Parse a single line from the API's response."""
        try:
            term, score, *rest = line.split(";")
            return term, score, "".join(rest)
        except Exception as e:
            print(f"Error parsing output line: {e}")
            return None


def format_output_line(corrected: str, score: str, note: str) -> str:
    """Serialise a proofread result back to a file line (no trailing newline)."""
    if note:
        return f"{corrected};{score};{note}"
    return f"{corrected};{score}"


# ── File helpers ─────────────────────────────────────────────────────────────

def count_lines(path) -> int:
    """Count total lines in a file without loading it into memory."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


def count_nonempty_lines(path) -> int:
    """Count non-empty lines in a file (used to find the resume point)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except FileNotFoundError:
        return 0


# ── API call ─────────────────────────────────────────────────────────────────

def call_api(client: anthropic.Anthropic, batch: list[tuple[str, str]]) -> list[str]:
    """
    Send a batch of (term, score) pairs to Claude.
    Returns a list of raw output lines (one per input entry).
    Retries up to RETRY_ATTEMPTS times on transient errors.
    Raises SystemExit on unrecoverable failure so the caller can abort cleanly.
    """
    entries_text = "\n".join(f"{term};{score}" for term, score in batch)
    prompt = USER_PROMPT_TEMPLATE.format(n=len(batch), entries=entries_text)

    last_exc = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            lines = [l for l in raw.splitlines() if l.strip()]

            if len(lines) != len(batch):
                raise ValueError(
                    f"Expected {len(batch)} output lines, got {len(lines)}"
                )
            return lines

        except (ValueError, anthropic.APIError, anthropic.RateLimitError) as exc:
            last_exc = exc
            is_rate_limit = isinstance(exc, anthropic.RateLimitError)
            click.echo(
                f"\n  [attempt {attempt}/{RETRY_ATTEMPTS}] "
                f"{'Rate limited' if is_rate_limit else 'Error'}: {exc}",
                err=True,
            )
            if attempt < RETRY_ATTEMPTS:
                delay = RETRY_DELAY * attempt * (3 if is_rate_limit else 1)
                click.echo(f"  Retrying in {delay}s…", err=True)
                time.sleep(delay)

    click.echo(
        f"\nFatal: API call failed after {RETRY_ATTEMPTS} attempts: {last_exc}\n"
        f"The output file is intact up to this point. Re-run the same command to resume.",
        err=True,
    )
    sys.exit(1)


# ── CLI ───────────────────────────────────────────────────────────────────────

@click.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--output", "-o",
    default=None,
    help="Output file path. Defaults to <input_stem>_proofread.txt",
)
@click.option(
    "--batch-size", "-b",
    default=DEFAULT_BATCH_SIZE,
    show_default=True,
    help="Number of entries per API call.",
)
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    default=None,
    help="Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.",
)
def main(input_file, output, batch_size, api_key):
    """
    Proofread a crossword wordlist file using Claude.

    INPUT_FILE should contain one entry per line in the format:

        term;score

    The script is safe to interrupt and re-run — it compares the number of
    lines already written to the output file against the input, and resumes
    from that point automatically.
    """

    input_path = Path(input_file)
    output_path = Path(output) if output else input_path.with_name(
        f"{input_path.stem}_proofread.txt"
    )

    # Count total input lines without loading the file (for the progress bar)
    total = count_lines(input_path)
    click.echo(f"Input:  {input_path}  ({total:,} lines)")
    click.echo(f"Output: {output_path}")

    # Determine resume point: how many lines has the output already received?
    resume_from = count_nonempty_lines(output_path)
    if resume_from > 0:
        if resume_from >= total:
            click.echo("Output file already complete — nothing to do.")
            return
        click.echo(
            f"Resuming from line {resume_from + 1:,} "
            f"({total - resume_from:,} lines remaining)."
        )
    else:
        click.echo("Starting fresh.")

    client = anthropic.Anthropic(api_key=api_key)

    # Accumulators
    # batch holds (term, score) pairs for the current API call
    # pending holds (line_index, output_line) for lines ready to write,
    # keyed so we always flush them in ascending line order.
    batch: list[tuple[str, str]] = []
    pending: dict[int, str] = {}  # line_index → output line string
    next_to_write = resume_from  # the next line index we must write before advancing

    reviewed = 0
    changed = 0

    def flush_pending(out_file):
        """Write all consecutively available lines from pending, in order."""
        nonlocal next_to_write
        while next_to_write in pending:
            out_file.write(pending.pop(next_to_write) + "\n")
            next_to_write += 1

    def process_batch(out_file, batch_indices: list[int]):
        """Call the API for the current batch and flush results."""
        nonlocal reviewed, changed
        results = call_api(client, batch)  # aborts on failure
        for (term, score), line_idx, out_line in zip(batch, batch_indices, results):
            parsed = parse_output_line(out_line)
            if parsed is None:
                # Malformed API output — pass original through with a note
                pending[line_idx] = f"{term};{score};WARNING: unparseable API response"
            else:
                corrected, out_score, note = parsed
                # Use the input score authoritatively (don't trust Claude to copy it right)
                pending[line_idx] = format_output_line(corrected, score, note)
                if corrected != term:
                    changed += 1
        reviewed += len(batch)
        flush_pending(out_file)

    with open(output_path, "a", encoding="utf-8") as out_file:
        with open(input_path, "r", encoding="utf-8") as in_file:
            # Skip lines already processed in a previous run
            lines_iter = itertools.islice(in_file, resume_from, None)
            batch_indices: list[int] = []

            with click.progressbar(
                    length=total - resume_from,
                    label="Proofreading",
                    show_pos=True,
            ) as bar:
                for i, raw in enumerate(lines_iter, start=resume_from):
                    parsed = parse_input_line(raw)

                    if parsed is None:
                        # Blank or malformed line — goes straight to pending
                        pending[i] = raw.rstrip("\n")
                        flush_pending(out_file)
                        bar.update(1)
                        continue

                    term, score = parsed
                    batch.append((term, score))
                    batch_indices.append(i)

                    if len(batch) >= batch_size or i == total - 1:
                        process_batch(out_file, batch_indices)
                        bar.update(len(batch))
                        batch.clear()
                        batch_indices.clear()
                        time.sleep(0.25)  # gentle pacing

    click.echo(
        f"\nDone. Reviewed {reviewed:,} entries — "
        f"{changed:,} changed, {reviewed - changed:,} unchanged."
    )
    click.echo(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
