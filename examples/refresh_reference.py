#!/usr/bin/env python3
"""Rebuild reference/ — the self-archiving half of the gate.

    python examples/refresh_reference.py

The petitions we capture are the *pending* queue. To say what happened to one
that left the queue, you need the rules FDA actually issued — and that list is
retained back to 1975, so it is cited rather than captured.

The join key is the petition number, which appears in both.

Committed so the charts stay deterministic and offline. Re-run when you want
the reference brought forward; it overwrites in place.
"""

import csv
import html
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "reference", "final-rules.csv")
OUT_FCN = os.path.join(ROOT, "reference", "fcn-notifications.csv")
OUT_GRAS = os.path.join(ROOT, "reference", "gras-notices.csv")
OUT_AGRAS = os.path.join(ROOT, "reference", "agras-notices.csv")
UA = "wss-food-trace/0.1 (+https://github.com/neldivad/wss-food-trace)"

# NOTE: the default view of this app is page one, not the whole set. Without
# showAll it returns 51 rows back to 2014 and looks exactly like a rolling
# window. It is not: there are 609 rows back to 1975.
URL = ("https://www.cfsanappsexternal.fda.gov/scripts/fdcc/index.cfm"
       "?set=FinalRules&showAll=true&sort=Date&order=DESC&type=basic")

# Food-contact substances left the petition route in 2001 for this one. Without
# it the rules series looks like regulation collapsing; with it, the traffic is
# simply somewhere else.
URL_FCN = ("https://www.cfsanappsexternal.fda.gov/scripts/fdcc/index.cfm"
           "?set=FCN&showAll=true&type=basic")

# The notification route for *substances* rather than food-contact materials,
# for both humans and animals. Retained in full including withdrawals, so both
# are cited rather than captured — but the repo needs them to answer its own
# questions without pointing at anything unpublished.
URL_GRAS = ("https://www.cfsanappsexternal.fda.gov/scripts/fdcc/cfc/"
            "XMLService.cfm?method=downloadxls&set=GRASNotices")
URL_AGRAS = ("https://www.fda.gov/animal-veterinary/"
             "generally-recognized-safe-gras-notification-program/"
             "current-animal-food-gras-notices-inventory")

# FDA writes its conclusion as free text with inconsistent apostrophes and
# capitalisation; classify once, here.
def outcome(letter):
    v = (letter or "").lower().replace("\u2019", "'")
    if "ceased to evaluate" in v:
        return "withdrawn"
    if "does not provide a basis" in v:
        return "rejected"
    if "no questions" in v:
        return "no questions"
    if "pending" in v:
        return "pending"
    return "other"

sys.path.insert(0, os.path.join(ROOT, "parsers"))
from _html import rows as table_rows, text as _cell_text   # noqa: E402


def clean(v):
    return _cell_text(v or "")

DATE = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, (\d{4})$")
PETITION = re.compile(r"\b((?:FAP|CAP)\s*\d[A-Z]\d+)\b")


def fetch(url, min_bytes):
    p = subprocess.run(["curl", "-sS", "-L", "--compressed", "--max-time", "180",
                        "-A", UA, url], capture_output=True)
    if p.returncode != 0 or len(p.stdout) < min_bytes:
        print(f"FAILED: rc={p.returncode} bytes={len(p.stdout)} for {url}",
              file=sys.stderr)
        return None
    return p.stdout.decode("utf-8", "replace")


def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def fcn(page):
    """Effective food-contact notifications — the route petitions moved to."""
    out = []
    for cells in table_rows(page, min_cells=4):
        if not re.match(r"^\d+$", cells[0].strip()):
            continue
        m = re.search(r"\b(?:19|20)\d{2}\b", cells[3])
        out.append({
            "fcn_no": cells[0].strip(),
            "effective_date": cells[3],
            "effective_year": m.group() if m else "",
            "substance": cells[1],
            "manufacturer": cells[2],
        })
    return out


def main():
    p = subprocess.run(["curl", "-sS", "-L", "--compressed", "--max-time", "180",
                        "-A", UA, URL], capture_output=True)
    if p.returncode != 0 or len(p.stdout) < 200_000:
        print(f"FAILED: rc={p.returncode} bytes={len(p.stdout)}", file=sys.stderr)
        return 1
    page = p.stdout.decode("utf-8", "replace")

    out = []
    for cells in table_rows(page, min_cells=4):
        m = DATE.match(cells[0].strip())
        if not m:
            continue
        pet = PETITION.search(cells[1] or "")
        out.append({
            "rule_date": cells[0].strip(),
            "rule_year": m.group(1),
            "petition_no": re.sub(r"\s+", " ", pet.group(1)) if pet else "",
            "petitioner": cells[2],
            "subject": cells[3],
            "cfr_section": cells[4] if len(cells) > 4 else "",
        })
    if len(out) < 400:
        print(f"FAILED: only {len(out)} rules parsed — expected ~600; "
              f"did the default (paginated) view get served?", file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(out[0]))
        w.writeheader()
        w.writerows(out)
    with_pet = sum(1 for r in out if r["petition_no"])
    yrs = sorted(r["rule_year"] for r in out)
    print(f"wrote {len(out)} final rules -> {OUT}")
    print(f"  {yrs[0]}-{yrs[-1]}; {with_pet} ({100*with_pet/len(out):.0f}%) "
          f"carry a petition number and can be joined to the queue")

    # --- human GRAS notices: a real CSV behind an Excel content type
    p = subprocess.run(["curl", "-sS", "-L", "--compressed", "--max-time", "180",
                        "-A", UA, URL_GRAS], capture_output=True)
    if p.returncode != 0 or len(p.stdout) < 400_000:
        print(f"FAILED gras: rc={p.returncode} bytes={len(p.stdout)}", file=sys.stderr)
        return 1
    raw = p.stdout.decode("latin-1")
    gras = []
    for r in csv.DictReader(io.StringIO(raw.split("\n", 2)[2])):
        num = re.search(r"\d+", r.get("GRAS Notice (GRN) No.") or "")
        if not num:
            continue
        gras.append({
            "grn": num.group(),
            "substance": clean(r.get("Substance")),
            "notifier": clean(r.get("Notifier")),
            "closure_date": (r.get("Date of closure") or "").strip(),
            "outcome": outcome(r.get("FDA's Letter")),
        })
    write(OUT_GRAS, gras)
    print(f"wrote {len(gras)} human GRAS notices -> {OUT_GRAS}")

    # --- animal GRAS notices: rendered table, no export
    page = fetch(URL_AGRAS, 10_000)
    if page is None:
        return 1
    agras = []
    for cells in table_rows(page, min_cells=7):
        m = re.match(r"\s*(\d+)", cells[0])
        if not m:
            continue
        agras.append({
            "agrn": m.group(1),
            "notifier": cells[1],
            "substance": cells[2],
            "intended_use": cells[3],
            "species": cells[4],
            "filed": cells[5],
            "outcome": outcome(cells[6]),
        })
    if len(agras) < 50:
        print(f"FAILED agras: only {len(agras)} rows", file=sys.stderr)
        return 1
    write(OUT_AGRAS, agras)
    print(f"wrote {len(agras)} animal GRAS notices -> {OUT_AGRAS}")

    page = fetch(URL_FCN, 800_000)
    if page is None:
        return 1
    rows = fcn(page)
    if len(rows) < 1200:
        print(f"FAILED: only {len(rows)} notifications — expected ~1760",
              file=sys.stderr)
        return 1
    write(OUT_FCN, rows)
    dated = [r["effective_year"] for r in rows if r["effective_year"]]
    print(f"wrote {len(rows)} FCN notifications -> {OUT_FCN}")
    print(f"  {min(dated)}-{max(dated)}; {len(rows)-len(dated)} undated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
