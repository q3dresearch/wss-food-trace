"""Shared HTML-table extraction for the FDA inventories.

Every source in this repo is a rendered table with no export, so the same two
helpers serve all of them. Script bodies must be stripped before tags or their
source text lands in the output — a mistake that cost a debugging round on the
petitions parser.
"""

import html
import re

_SCRIPT = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
_CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)


def text(fragment: str) -> str:
    return " ".join(
        html.unescape(re.sub(r"<[^>]+>", " ", _SCRIPT.sub(" ", fragment))).split())


def rows(page: str, min_cells: int = 2):
    """Every table row as a list of cell strings, headers included."""
    for row in _ROW.findall(page):
        cells = [text(c) for c in _CELL.findall(row)]
        if len(cells) >= min_cells:
            yield cells
