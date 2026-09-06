"""Parser for `notgras.v1` — substances FDA determined are not GRAS.

The inventory has no date column, so the only thing an archive adds is *when*
a substance appeared on it. Each capture therefore asserts presence; a
substance absent from a later capture has been delisted, which would itself be
newsworthy.
"""

from wss import derive

from ._html import rows

PARSER_VERSION = "1"


def parse(body: bytes, ctx: derive.ParseContext):
    page = body.decode("utf-8", "replace")
    seen = 0
    for cells in rows(page, min_cells=3):
        cas, substance, other = cells[0], cells[1], cells[2]
        if not substance or substance.lower().startswith("substance"):
            continue          # header row
        seen += 1
        for metric, value in (("listed", 1),
                              ("cas_number", cas),
                              ("other_names", other)):
            yield derive.Observation(
                entity_id=substance,
                metric=metric,
                value=value,
                unit="count" if metric == "listed" else "",
            )
    if not seen:
        raise ValueError("no not-GRAS rows parsed — page layout changed")
    yield derive.Observation(entity_id="inventory", metric="substances_listed",
                             value=seen, unit="count")


derive.register("notgras.v1", parse, PARSER_VERSION)
