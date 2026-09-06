"""Parser for `afic.v1` — FDA Animal Food Ingredient Consultations.

Two tables on one page with different final columns: pending consultations end
in a Status, completed ones end in FDA's letter. Both are folded into a single
`status` metric so a consultation moving between them reads as a status change
rather than as a disappearance.

The page carries no "as of" date, so observed_at is left unset and the engine
stamps each row with the manifest row's fetch time. That is correct here:
identical bytes dedupe, so an observation only exists per *stored* capture.
"""

import re

from wss import derive

from ._html import rows

PARSER_VERSION = "1"

_AFIC = re.compile(r"^\d{3,4}$")


def parse(body: bytes, ctx: derive.ParseContext):
    page = body.decode("utf-8", "replace")
    seen = 0
    for cells in rows(page, min_cells=7):
        number, firm, substance, use, species, date, outcome = cells[:7]
        if not _AFIC.match(number):
            continue
        seen += 1
        status = "complete" if "complete" in outcome.lower() else outcome.lower()
        for metric, value in (
            ("status", status),
            ("firm", firm),
            ("substance", substance),
            ("intended_use", use),
            ("intended_species", species),
            ("posted_or_completed", date),
            ("in_inventory", 1),
        ):
            yield derive.Observation(
                entity_id=f"AFIC {number}",
                metric=metric,
                value=value,
                unit="count" if metric == "in_inventory" else "",
            )
    if not seen:
        raise ValueError("no AFIC rows parsed — page layout changed")
    yield derive.Observation(entity_id="inventory", metric="consultations_listed",
                             value=seen, unit="count")


derive.register("afic.v1", parse, PARSER_VERSION)
