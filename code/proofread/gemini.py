"""
Proofreads a crossword wordlist file using the Gemini API.
Outputs ONLY entries that require changes or have uncertainty notes, saving tokens.

Input format (one entry per line):
    <term>;<score>

Output format:
    <original_term>;<corrected_term>;<note>

Cost to run on Will Nediger's word list:

- Input tokens: 4.41 M * $1.50 / 1 million tokens = $6.615
- Output tokens: 7.97 M * $9.00 / 1 million tokens = $71.73
- Total token cost: $78.345

Pricing: https://ai.google.dev/gemini-api/docs/pricing#gemini-3.5-flash

"""

import asyncio
from dataclasses import dataclass
from itertools import batched, islice
from pathlib import Path
import json

import click
from google import genai
from google.genai import errors, types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

# ── Constants ────────────────────────────────────────────────────────────────

# Keep DEFAULT_BATCH_SIZE from getting too large, as this affects proofread quality
DEFAULT_BATCH_SIZE = 100
DEFAULT_MAX_CONCURRENT = 32
MODEL = "gemini-3.5-flash"
RETRY_ATTEMPTS = 4
RETRY_DELAY = 4  # Base delay in seconds for exponential backoff.

RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "old": {"type": "string"},
            "new": {"type": "string"},
            "note": {"type": "string"},
        },
        "required": ["old", "new", "note"],
    },
}

SYSTEM_PROMPT = """\
You are an exceptionally precise and highly educated proofreader for crossword puzzle word lists.
Each entry is a word, phrase, or cultural reference paired with a familiarity score.

Your task is to identify entries that have issues like missing spaces, wrong capitalization, \
missing punctuation/apostrophes, or genuine misspellings. Proofread each entry as it would \
appear in a dictionary. Do NOT capitalize words in the `new` field unless it is usually capitalized.

The input data contains some limitations. If you find one of these limitations, do NOT correct it:

- Missing accents. The following does not need to be corrected:
  - "a la" (rather than "à la")
- Missing punctuation. The following does not need to be corrected:
  - "Aachen Germany" (rather than "Aachen, Germany")
  - "J Robert Oppenheimer" (rather than "J. Robert Oppenheimer")
  - "A Bar Song Tipsy" (rather than "A Bar Song (Tipsy)")

The only punctuation we care about proofreading are the following:
  - Hyphens/dashes ("A game" -> "A-game")
  - apostrophes ("a way's away" -> "a ways away")

CRITICAL INSTRUCTION: Return ONLY entries that require a correction or where you have a note \
of uncertainty. If an entry is completely correct and you are confident, do NOT include it \
in your response at all.

Return a JSON array of objects. Each object must have exactly these fields:
  - old: the exact term from the input list
  - new: your fixed version, or the original term if you are uncertain but not correcting it
  - note: a brief explanation of the change or uncertainty

If no entries need corrections or notes, return an empty JSON array: []

Rules:
  1. Return only valid JSON matching the requested schema.
  2. `old` must exactly match the term from the input list.
  3. `new` is your fixed version. If you are uncertain but not making a correction, \
copy the original term exactly.
  4. `note` is a brief explanation of the change or an explanation of your uncertainty.
  5. Be EXTREMELY CAUTIOUS. If unsure whether something is a typo vs. an obscure valid term, \
do NOT change it, but do include it with a note flagging your uncertainty.
  6. Preserve proper capitalization and do not convert non-American spellings to American.
"""

USER_PROMPT_TEMPLATE = """\
Review these {n} wordlist entries. Return ONLY a JSON array containing entries that need \
corrections or notes.

{entries}"""


# ── Data Structures & Parsers ────────────────────────────────────────────────

@dataclass
class Entry:
    term: str
    score: str

    @staticmethod
    def from_string(line: str) -> "Entry":
        # Assumes the input is well-formed.
        # Assumes no semicolons are present in the term itself.
        term, score = line.strip().split(";")
        return Entry(term, score)

@dataclass
class ProofreadResult:
    original_term: str
    corrected_term: str
    note: str

    @staticmethod
    def from_dict(data: dict) -> "ProofreadResult":
        try:
            original = data["old"]
            corrected = data["new"]
            note = data["note"]
        except KeyError as exc:
            raise ValueError(f"Missing expected field in proofread result: {data}") from exc

        if not all(isinstance(value, str) for value in (original, corrected, note)):
            raise ValueError(f"Expected all proofread result fields to be strings: {data}")

        if not all((original.strip(), corrected.strip(), note.strip())):
            raise ValueError(f"Expected original_term, corrected_term, and note to be non-empty: {data}")

        return ProofreadResult(
            original_term=original,
            corrected_term=corrected,
            note=note,
        )

    def to_string(self) -> str:
        return ";".join((self.original_term, self.corrected_term, self.note))

# ── API Logic ────────────────────────────────────────────────────────────────

def _is_retryable(exc: Exception) -> bool:
    """Returns True if the exception is retryable."""
    if isinstance(exc, errors.APIError):
        return exc.code in (429, 503)
    return False

@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=RETRY_DELAY, min=RETRY_DELAY, max=RETRY_DELAY * RETRY_ATTEMPTS * 4),
    reraise=True
)
async def call_api(client: genai.Client, lines: list[str]) -> list[str]:
    """
    Sends a batch to Gemini and validates the response.
    Empty response text means no entries in the batch need changes.
    Malformed or missing response text returns the original entries with warning notes.
    Retryable API errors are retried with exponential backoff.
    """

    entries = [Entry.from_string(line) for line in lines]
    terms = {e.term for e in entries}

    entries_text = "\n".join(f"{e.term};{e.score}" for e in entries)
    prompt = USER_PROMPT_TEMPLATE.format(n=len(entries), entries=entries_text)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.0,
        response_mime_type="application/json",
        response_schema=RESPONSE_SCHEMA,
    )

    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config,
    )

    is_malformed = False
    out_entries = []
    # If the proofread output is malformed, skip it with a warning.
    # Temperature is set to 0, so the output should be deterministic,
    # i.e. retrying proofreading should never succeed.
    if response.text is None:
        is_malformed = True
    elif response.text.strip() == "": # no changes need to be made
        pass
    else:
        try:
            raw_results = json.loads(response.text)
            if not isinstance(raw_results, list):
                raise ValueError(f"Expected a JSON array, got {type(raw_results).__name__}")

            for raw_result in raw_results:
                if not isinstance(raw_result, dict):
                    click.echo(f"Warning: Expected a JSON object, got {raw_result}")
                result = ProofreadResult.from_dict(raw_result)
                if result.original_term in terms:
                    out_entries.append(result)
                else:
                    click.echo(f"Warning: {result.original_term} not found in entries")
        except (json.JSONDecodeError, ValueError) as e:
            is_malformed = True
            click.echo(f"Error parsing proofread output: {e}")

    if is_malformed:
        out_entries = [
            ProofreadResult(original_term=entry.term, corrected_term=entry.term, note="WARNING: Could not parse proofread output")
            for entry in entries
        ]

    return [entry.to_string() for entry in out_entries]

# ── Async logic ──────────────────────────────────────────────────────────────────────

async def process(client: genai.Client,
                  input_path: Path,
                  output_path: Path,
                  resume_from: int,
                  resume_to: int,
                  batch_size: int,
                  max_concurrent: int) -> int:
    reviewed = resume_from

    with input_path.open("r", encoding="utf-8") as in_file, \
         output_path.open("a", encoding="utf-8") as out_file:

        # Skip lines we've already processed
        lines_iter = islice(in_file, resume_from, resume_to)
        concurrent_batch_size = batch_size * max_concurrent

        with click.progressbar(
            length=resume_to - resume_from,
            label="Proofreading...",
            show_pos=True,
        ) as bar:
            for concurrent_lines in batched(lines_iter, concurrent_batch_size):
                tasks = []
                for chunk in batched(concurrent_lines, batch_size):
                    click.echo(f"Processing chunk: {chunk[0]}")
                    tasks.append(call_api(client, chunk))
                concurrent_results = await asyncio.gather(*tasks)

                flat_lines = [line for lines in concurrent_results for line in lines]

                if flat_lines:
                    out_file.write("\n".join(flat_lines) + "\n")
                    out_file.flush()

                reviewed += len(concurrent_lines)
                bar.update(len(concurrent_lines))
                await asyncio.sleep(0.2)
    return reviewed

# ── CLI ──────────────────────────────────────────────────────────────────────

@click.command()
@click.option(
    "--api-key",
    default=None,
    envvar="GEMINI_API_KEY",
    help="Gemini API key. Falls back to GEMINI_API_KEY env var.",
    required=True,
)
@click.option(
    "--batch-size", "-b",
    default=DEFAULT_BATCH_SIZE,
    help="Number of entries per API call.",
    show_default=True,
    type=click.IntRange(min=1),
)
@click.option(
    "--max-concurrent", "-m",
    default=DEFAULT_MAX_CONCURRENT,
    help="Maximum number of concurrent API calls.",
    show_default=True,
    type=click.IntRange(min=1),
)
@click.option(
    "--resume-from", "-rf",
    default=0,
    help="Zero-indexed line number in the input file to resume processing from.",
    show_default=True,
    type=click.IntRange(min=0),
)
@click.option(
    "--resume-to", "-rt",
    default=None,
    help="Zero-indexed line number in the input file to resume processing to.",
    show_default=True,
    type=click.IntRange(min=0),
)
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path(dir_okay=False))
def main(api_key,
         batch_size,
         max_concurrent,
         resume_from,
         resume_to,
         input_file,
         output_file):
    input_path = Path(input_file)
    output_path = Path(output_file)

    # Fast line counting
    with input_path.open("r", encoding="utf-8") as infile:
        num_lines = sum(1 for _ in infile)

    resume_from = 74398
    resume_to = resume_to or num_lines

    if output_path.exists() and output_path.stat().st_size > 0:
        with output_path.open("rb") as outfile:
            outfile.seek(-1, 2)
            if outfile.read(1) != b"\n":
                raise click.ClickException("Warning: Output file does not end with a newline. Please inspect/fix it before resuming.")

    click.echo(f"Input:  {input_path}  ({num_lines:,} lines)")
    click.echo(f"Output: {output_path}  (resuming from line {resume_from + 1} to {resume_to + 1})")

    if resume_from >= num_lines:
        click.echo("Output file already complete — nothing to do.")
        return
    elif resume_from > 0:
        click.echo(f"Resuming from line {resume_from + 1:,} ({resume_to - resume_from:,} remaining).")

    client = genai.Client(api_key=api_key)
    # for model in client.models.list()
    #   print(model.name)

    try:
        reviewed = asyncio.run(process(client, input_path, output_path, resume_from, resume_to, batch_size, max_concurrent))
    except errors.APIError as e:
        click.echo("Failed to proofread entries.", err=True)
        raise

    click.echo(
        f"Done. Processed through input line {reviewed:,}"
    )
    click.echo(f"Output written to: {output_path}")

if __name__ == "__main__":
    main()
