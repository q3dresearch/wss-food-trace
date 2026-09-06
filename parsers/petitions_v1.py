"""Parser for `petitions.v1` — FDA food and colour additive petitions.

The page is a single HTML table of the *current* queue. Two things matter:

* ``observed_at`` comes from the page's own "as of" date, not the fetch time.
  The queue is only restated when FDA refreshes it, so stamping rows with the
  fetch second would invent movement that did not happen.
* No petitioner column is emitted. See the registry entry: names are parties
  to a public proceeding and nothing here needs them.

Absence is the point. A petition that stops appearing has been granted,
denied or withdrawn, and only the archive can tell you which.
"""

import html
import re

from wss import derive

PARSER_VERSION = "1"

_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
_CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
_PETITION = re.compile(r"^(FAP|CAP)\s+\S+")
_MONTHS = {m: i for i, m in enumerate(
    "january february march april may june july august september october "
    "november december".split(), 1)}
_ASOF = re.compile(r"Abeyance\s*[-–—]?\s*([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})")


_SCRIPT = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)


def _text(fragment):
    """Strip markup. Script bodies must go first or their source becomes text
    and lands between the heading and the date."""
    return " ".join(
        html.unescape(re.sub(r"<[^>]+>", " ", _SCRIPT.sub(" ", fragment))).split())


def _as_of(page):
    """FDA states the queue date in the heading; prefer it over fetch time.

    The date sits in its own <h3>, so it is only adjacent to the title once
    tags are stripped. Raise rather than return None: falling back to the
    fetch second would stamp an unchanged queue with a new timestamp every
    week and invent movement that never happened.
    """
    m = _ASOF.search(_text(page))
    if not m:
        raise ValueError("no 'as of' date in the page heading — layout changed")
    month = _MONTHS.get(m.group(1).lower())
    if not month:
        raise ValueError(f"unparsable month {m.group(1)!r} in the as-of date")
    return f"{m.group(3)}-{month:02d}-{int(m.group(2)):02d}T00:00:00Z"


def parse(body: bytes, ctx: derive.ParseContext):
    page = body.decode("utf-8", "replace")
    observed_at = _as_of(page)
    open_count = 0

    for row in _ROW.findall(page):
        cells = [_text(c) for c in _CELL.findall(row)]
        if len(cells) < 4 or not _PETITION.match(cells[0]):
            continue
        number, status, _petitioner, title = cells[0], cells[1], cells[2], cells[3]
        open_count += 1
        for metric, value in (
            ("status", status.lower()),
            ("petition_type", number.split()[0]),
            ("subject", title),
            ("in_queue", 1),
        ):
            yield derive.Observation(
                entity_id=number,
                metric=metric,
                value=value,
                unit="count" if metric == "in_queue" else "",
                observed_at=observed_at,
            )

    yield derive.Observation(
        entity_id="queue",
        metric="petitions_open",
        value=open_count,
        unit="count",
        observed_at=observed_at,
    )


derive.register("petitions.v1", parse, PARSER_VERSION)
