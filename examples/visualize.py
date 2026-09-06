#!/usr/bin/env python3
"""Render charts from the archive as SVG. Stdlib only.

    python examples/visualize.py

  queue-composition.svg   what the 32 open petitions ask for, and their status
  the-gate-moved.svg      food-contact left the petition route in 2001 — it did not stop
  animal-vs-human.svg     animal ingredients clear at two thirds the human rate
  who-files.svg           the gate is a long tail, not a concentrated industry
  practice-effect.svg     clearance rises with filing experience — but not smoothly

One capture answers one question: what is in the queue right now. The questions
this archive exists for — how long petitions sit, when they flip between
"under review" and "held in abeyance", and which vanish without a matching
final rule — need a second capture and then a third. They arrive on their own.
"""

from __future__ import annotations

import csv
import glob
import math
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "charts")

BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
INK, MUTE, GRID = "#1c2530", "#6b7684", "#dfe4ea"
FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,"
        "sans-serif")

REMOVE = re.compile(r"\brevoke|\bremove|\bprohibit|\bban\b|\bdelete", re.I)
PETITION_CLASS = {"A": "Food additive", "B": "Food contact",
                  "C": "Colour additive", "M": "Irradiation"}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def txt(x, y, s, size=12, fill=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{esc(s)}</text>')


def rect(x, y, w, h, fill, op=1.0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" '
            f'height="{max(h,0):.1f}" fill="{fill}" fill-opacity="{op}"/>')


def circ(x, y, r, fill, stroke="none", sw=1):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def wrap(text, width_px, per_char=6.15):
    out, cur = [], ""
    for w in str(text).split():
        t = (cur + " " + w).strip()
        if len(t) * per_char > width_px and cur:
            out.append(cur); cur = w
        else:
            cur = t
    if cur:
        out.append(cur)
    return out


def load(source_id="fda.additives.petitions"):
    """Latest state of one source -> {entity: {metric: value}} + its as-of date.

    Read every partition and filter by source, never by filename: partitions are
    keyed on observed_at, so a source that stamps rows from the page lands in a
    different file from one that falls back to fetch time. Taking the newest
    file gets you whichever source happened to be observed last.
    """
    files = sorted(glob.glob(os.path.join(ROOT, "derived", "observations", "*.csv")))
    if not files:
        raise SystemExit("no observations — run `wss derive` first")
    rows = [r for f in files
            for r in csv.DictReader(open(f, encoding="utf-8"))
            if r["source_id"] == source_id]
    if not rows:
        raise SystemExit(f"no observations for {source_id}")
    latest = max(r["observed_at"] for r in rows)
    by = defaultdict(dict)
    for r in rows:
        if r["observed_at"] == latest and r["entity_id"] != "queue":
            by[r["entity_id"]][r["metric"]] = r["value"]
    return by, latest[:10]


def petition_class(number):
    m = re.match(r"(FAP|CAP)\s+\d([A-Z])", number)
    return PETITION_CLASS.get(m.group(2), "Other") if m else "Other"


def queue_composition(by, as_of, path):
    ask = {k: ("remove" if REMOVE.search(v.get("subject", "")) else "add")
           for k, v in by.items()}
    groups = [("add", "Asks FDA to permit or expand a use", BLUE),
              ("remove", "Asks FDA to revoke, remove or prohibit one", ORANGE)]
    W, L, R, TOP, ROWH = 1080, 300, 60, 210, 116
    PW = W - L - R
    H = TOP + ROWH * len(groups) + 250
    N = len(by)

    b = [txt(40, 44, "Abeyance only happens to one kind of petition", 21, INK,
             weight="600")]
    for i, ln in enumerate(wrap(
            f"All {N} food and colour additive petitions open at FDA on {as_of}, "
            f"by what they ask for and where they sit.", W - 90)):
        b.append(txt(40, 70 + i * 18, ln, 12.5, MUTE))
    b.append(rect(40, 103, 11, 11, INK, 0.30))
    b.append(txt(59, 112, "lighter = held in abeyance", 11.5, MUTE))
    b.append(rect(232, 103, 11, 11, INK, 0.75))
    b.append(txt(251, 112, "darker = under review", 11.5, MUTE))

    for i, (key, label, col) in enumerate(groups):
        y = TOP + i * ROWH
        rows = [k for k in by if ask[k] == key]
        ab = sum(1 for k in rows if by[k]["status"] == "held in abeyance")
        ur = len(rows) - ab
        for j, ln in enumerate(wrap(label, L - 40)):
            b.append(txt(L - 26, y + 16 + j * 17, ln, 12.5, INK, "end"))
        b.append(txt(L - 26, y + 58, f"{len(rows)} petitions", 11.5, MUTE, "end"))
        unit = PW / N
        x = L
        for n, shade, name in ((ab, 0.45, "held in abeyance"), (ur, 0.9, "under review")):
            if not n:
                continue
            w = unit * n
            b.append(rect(x, y, w, 62, col, shade))
            b.append(txt(x + 12, y + 30, str(n), 19, "#ffffff", weight="700"))
            if w > 128:
                b.append(txt(x + 12, y + 50, name, 11, "#ffffff"))
            x += w
        b.append(txt(x + 12, y + 34,
                     f"{100*ab/len(rows):.0f}% in abeyance", 12, MUTE))

    cls = Counter(petition_class(k) for k in by)
    cy = TOP + ROWH * len(groups) + 26
    b.append(txt(40, cy, "By petition class:  " + "  ·  ".join(
        f"{k} {v}" for k, v in cls.most_common()), 12, MUTE))

    ny = cy + 40
    b.append(txt(40, ny, "Why this is structural, not a bias finding", 13, INK,
                 weight="600"))
    para = ("FDA defines abeyance as the state a petition sits in until the "
            "petitioner supplies information FDA has asked for, requests a "
            "decision on what is already filed, or withdraws. It is a queue for "
            "petitions where the petitioner owes data — which is what proving a "
            "new additive safe involves, and is not what asking FDA to revoke "
            "someone else's additive involves. So the split above is close to a "
            "definition rather than a discovery, and “held in abeyance” "
            "must not be read as a neutral measure of delay when these two "
            "groups are compared later.")
    for j, ln in enumerate(wrap(para, W - 90)):
        b.append(txt(40, ny + 22 + j * 18, ln, 12.5, MUTE))

    b.append(txt(40, H - 18, f"Source: FDA Office of Food Additive Safety, "
                 f"petitions under review or held in abeyance, as of {as_of}. "
                 f"Captured by wss-food-trace; petitioner names are not collected.",
                 10.5, MUTE))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" '
           f'fill="#ffffff"/>' + "".join(b) + "</svg>")
    open(path, "w", encoding="utf-8").write(svg)


def load_reference():
    ref = os.path.join(ROOT, "reference")
    rules = list(csv.DictReader(open(os.path.join(ref, "final-rules.csv"),
                                     encoding="utf-8")))
    fcn = list(csv.DictReader(open(os.path.join(ref, "fcn-notifications.csv"),
                                   encoding="utf-8")))
    return rules, fcn


def petition_kind(no):
    m = re.match(r"(FAP|CAP)\s*\d([A-Z])", no or "")
    return {"A": "food additive", "B": "food contact",
            "C": "colour", "M": "irradiation"}.get(m.group(2) if m else "", "other")


def the_gate_moved(rules, fcn, path):
    """One lane closed and a bigger one opened — the same year."""
    LO, HI = 1990, 2026
    span = list(range(LO, HI + 1))
    contact = Counter(); other = Counter()
    for r in rules:
        y = int(r["rule_year"])
        if not LO <= y <= HI:
            continue
        (contact if petition_kind(r["petition_no"]) == "food contact" else other)[y] += 1
    notif = Counter(int(r["effective_year"]) for r in fcn
                    if r["effective_year"] and LO <= int(r["effective_year"]) <= HI)

    W, L, R, TOP, PH = 1180, 76, 44, 210, 300
    PW = W - L - R
    BW = PW / len(span)
    H = TOP + PH + 236
    # bars are stacked, so the scale must come from the stacked total
    MAX = max(contact[y] + other[y] + notif[y] for y in span)
    Y = lambda v: TOP + PH - PH * v / MAX

    b = [txt(40, 44, "The gate did not close — one lane did", 21, INK, weight="600")]
    for i, ln in enumerate(wrap(
            "Food-contact substances stopped arriving as food additive petitions in 2001 "
            "and started arriving as notifications instead. Same substances, faster route, "
            "more of them.", W - 90)):
        b.append(txt(40, 70 + i * 18, ln, 12.5, MUTE))
    lx = 40
    for c, lab in ((ORANGE, "food-contact petitions granted"),
                   (BLUE, "food-contact notifications effective"),
                   (MUTE, "all other petitions granted")):
        b.append(rect(lx, 113, 11, 11, c, 0.9))
        b.append(txt(lx + 17, 122.5, lab, 11.5, MUTE))
        lx += 17 + len(lab) * 6.15 + 26

    for g in range(0, MAX + 1, 20):
        b.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W-R}" y2="{Y(g):.1f}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        b.append(txt(L - 10, Y(g) + 4, str(g), 10.5, MUTE, "end"))
    b.append(txt(L - 10, TOP - 14, "per year", 10.5, MUTE, "end"))

    for i, y in enumerate(span):
        x = L + i * BW + BW * 0.14
        w = BW * 0.72
        base = TOP + PH
        for cnt, col, op in ((other[y], MUTE, 0.5), (contact[y], ORANGE, 0.9),
                             (notif[y], BLUE, 0.85)):
            if cnt:
                h = PH * cnt / MAX
                b.append(rect(x, base - h, w, h, col, op))
                base -= h
        if y % 5 == 0:
            b.append(txt(x + w / 2, TOP + PH + 18, str(y), 10.5, MUTE, "middle"))
    b.append(f'<line x1="{L}" y1="{TOP+PH}" x2="{W-R}" y2="{TOP+PH}" '
             f'stroke="{INK}" stroke-width="1.4"/>')

    xc = L + (2000 - LO) * BW
    b.append(f'<line x1="{xc:.1f}" y1="{TOP-8}" x2="{xc:.1f}" y2="{TOP+PH}" '
             f'stroke="{VIOLET}" stroke-width="1.3" stroke-dasharray="5 4"/>')
    b.append(txt(xc - 8, TOP - 12, "2000 — first effective notification",
                 11, VIOLET, "end"))

    ny = TOP + PH + 56
    b.append(txt(40, ny, "Why this matters for reading any of these series",
                 13, INK, weight="600"))
    para = (f"Counting granted petitions alone, food additive rulemaking looks like it "
            f"collapsed: {sum(contact.values())+sum(other.values())} rules in this window, "
            f"but only {sum(v for y,v in other.items() if y>=2006)+sum(v for y,v in contact.items() if y>=2006)} "
            f"of them after 2005. The 1997 FDA Modernization Act created a notification "
            f"route for food-contact substances, and from 2000 they used it: "
            f"{sum(notif.values()):,} notifications became effective, against "
            f"{sum(contact.values())} food-contact petitions granted in the same window. "
            f"The traffic did not stop — it changed doors, and only one door is in the "
            f"petition data.")
    for j, ln in enumerate(wrap(para, W - 90)):
        b.append(txt(40, ny + 22 + j * 18, ln, 12.5, MUTE))

    b.append(txt(40, H - 18, "Source: FDA Office of Food Additive Safety — final rules "
                 "and effective FCS notifications, both retained by the publisher and "
                 "held in reference/. Chart: examples/visualize.py", 10.5, MUTE))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#ffffff"/>'
           + "".join(b) + "</svg>")
    open(path, "w", encoding="utf-8").write(svg)
    return sum(contact.values()), sum(notif.values())


def animal_vs_human(path):
    """Q10 — the same instrument, two very different pass rates."""
    ref = os.path.join(ROOT, "reference")
    human = list(csv.DictReader(open(os.path.join(ref, "gras-notices.csv"),
                                     encoding="utf-8")))
    animal = list(csv.DictReader(open(os.path.join(ref, "agras-notices.csv"),
                                      encoding="utf-8")))
    ORDER = [("no questions", "FDA has no questions", BLUE),
             ("withdrawn", "withdrawn at notifier's request", ORANGE),
             ("rejected", "no basis for a GRAS determination", VIOLET)]

    sets = []
    for name, rows in (("Animal food", animal), ("Human food", human)):
        c = Counter(r["outcome"] for r in rows)
        closed = sum(v for k, v in c.items() if k != "pending")
        sets.append((name, c, closed, len(rows)))

    W, L, R, TOP, ROWH = 1080, 176, 300, 208, 118
    PW = W - L - R
    H = TOP + ROWH * len(sets) + 232

    b = [txt(40, 44, "The same instrument, two very different gates",
             21, INK, weight="600")]
    for i, ln in enumerate(wrap(
            "Every GRAS notice FDA has closed, human and animal, by the conclusion "
            "FDA reached. Pending notices are excluded — they have no outcome yet.",
            W - 90)):
        b.append(txt(40, 70 + i * 18, ln, 12.5, MUTE))
    lx = 40
    for _, lab, col in ORDER:
        b.append(rect(lx, 111, 11, 11, col, 0.9))
        b.append(txt(lx + 17, 120.5, lab, 11.5, MUTE))
        lx += 17 + len(lab) * 6.15 + 26

    for i, (name, c, closed, total) in enumerate(sets):
        y = TOP + i * ROWH
        b.append(txt(L - 22, y + 26, name, 14, INK, "end", weight="600"))
        b.append(txt(L - 22, y + 46, f"{closed:,} closed", 11.5, MUTE, "end"))
        b.append(txt(L - 22, y + 62, f"of {total:,} filed", 11.5, MUTE, "end"))
        x = L
        for key, _, col in ORDER:
            n = c.get(key, 0)
            if not n:
                continue
            w = PW * n / closed
            b.append(rect(x, y, w, 66, col, 0.9))
            if w > 74:
                b.append(txt(x + 12, y + 30, f"{100*n/closed:.1f}%", 19,
                             "#ffffff", weight="700"))
                b.append(txt(x + 12, y + 50, f"{n:,}", 11.5, "#ffffff"))
            x += w
        clear = 100 * c.get("no questions", 0) / closed
        b.append(txt(L + PW + 18, y + 34, f"{clear:.1f}% cleared", 13, INK,
                     weight="600"))

    ah, hh = sets[0], sets[1]
    a_wd = 100 * ah[1]["withdrawn"] / ah[2]
    h_wd = 100 * hh[1]["withdrawn"] / hh[2]
    ny = TOP + ROWH * len(sets) + 40
    b.append(txt(40, ny, "What is and is not safe to say here", 13, INK, weight="600"))
    para = (f"The withdrawal gap is the solid part: {a_wd:.1f}% against {h_wd:.1f}%, "
            f"about {abs(a_wd-h_wd)/ (a_wd*(100-a_wd)/ah[2])**0.5:.1f} standard errors "
            f"on {ah[2]} closed animal notices. Real, not noise. The rejection gap runs "
            f"the same way but rests on {ah[1]['rejected']} events, so quote it as "
            f"\u201c{ah[1]['rejected']} of {ah[2]}\u201d rather than as a multiple. "
            f"And neither number explains itself: a lower pass rate could mean stricter "
            f"review, weaker submissions, or a thinner evidence base to draw on. FDA "
            f"announced in August 2024 that it was evaluating both animal programmes.")
    for j, ln in enumerate(wrap(para, W - 90)):
        b.append(txt(40, ny + 22 + j * 18, ln, 12.5, MUTE))

    b.append(txt(40, H - 18, "Source: FDA GRAS Notice Inventory (human) and Animal "
                 "Food GRAS Notices Inventory, both in reference/. Outcome is FDA's "
                 "own letter text, classified verbatim. Chart: examples/visualize.py",
                 10.5, MUTE))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#ffffff"/>'
           + "".join(b) + "</svg>")
    open(path, "w", encoding="utf-8").write(svg)
    return sets


def who_files(path):
    """Who actually uses the notification route — a long tail, not a cartel."""
    def key(s):
        return re.sub(r"[^a-z]", "", (s or "").lower())[:14]

    sets = []
    for label, f in (("Human food", "gras-notices.csv"),
                     ("Animal food", "agras-notices.csv")):
        rows = list(csv.DictReader(open(os.path.join(ROOT, "reference", f),
                                        encoding="utf-8")))
        n = Counter(key(r["notifier"]) for r in rows)
        disp = {}
        for r in rows:
            disp.setdefault(key(r["notifier"]), r["notifier"])
        sets.append((label, n, disp, len(rows)))

    W, L, R, TOP = 1160, 250, 400, 196
    PW, BANDH = W - L - R, 132
    H = TOP + BANDH * len(sets) + 200

    b = [txt(40, 44, "The gate is a long tail, not a concentrated industry",
             21, INK, weight="600")]
    for i, ln in enumerate(wrap(
            "Every GRAS notice ever filed, grouped by how many its notifier has filed "
            "in total. Most companies appear once and never again.", W - 90)):
        b.append(txt(40, 70 + i * 18, ln, 12.5, MUTE))

    for si, (label, n, disp, total) in enumerate(sets):
        top = TOP + si * BANDH
        dist = Counter(n.values())
        buckets = [("filed once", dist[1] * 1),
                   ("2", dist[2] * 2), ("3", dist[3] * 3),
                   ("4-6", sum(dist[k] * k for k in (4, 5, 6))),
                   ("7+", sum(dist[k] * k for k in dist if k >= 7))]
        b.append(txt(L - 22, top + 6, label, 15, INK, "end", weight="600"))
        b.append(txt(L - 22, top + 26, f"{len(n)} notifiers", 11.5, MUTE, "end"))
        b.append(txt(L - 22, top + 42, f"{total:,} notices", 11.5, MUTE, "end"))
        x = L
        for j, (lab, cnt) in enumerate(buckets):
            w = PW * cnt / total
            col = ORANGE if j == 0 else BLUE
            b.append(rect(x, top - 12, w, 52, col, 0.9 - j * 0.13))
            if w > 60:
                b.append(txt(x + 11, top + 12, f"{100*cnt/total:.0f}%", 17,
                             "#ffffff", weight="700"))
                b.append(txt(x + 11, top + 30, lab, 10.5, "#ffffff"))
            x += w
        b.append(txt(L, top + 60, "share of all notices, by how many that notifier filed",
                     10.5, MUTE))

        b.append(txt(L + PW + 26, top - 2, "most frequent filers", 11.5, INK,
                     weight="600"))
        for j, (k, v) in enumerate(n.most_common(6)):
            b.append(txt(L + PW + 26, top + 18 + j * 17,
                         f"{v:>3}   {disp[k][:30]}", 11, MUTE))

    ny = TOP + BANDH * len(sets) + 26
    b.append(txt(40, ny, "Why this cuts against the obvious story", 13, INK,
                 weight="600"))
    hn, _, _, htot = sets[0][0], None, None, sets[0][3]
    h = sets[0]
    once = Counter(h[1].values())[1]
    top10 = sum(v for _, v in h[1].most_common(10))
    para = (f"{once} of {len(h[1])} human-food notifiers filed exactly once, and the "
            f"ten most frequent between them account for {100*top10/h[3]:.0f}% of all "
            f"notices. That is not the shape of a captured process run by a handful of "
            f"incumbents — it is mostly one-off filers who never come back. Whatever is "
            f"wrong with the GRAS route, \u201ca few big companies use it repeatedly\u201d "
            f"is not the description. The animal side is smaller and slightly more "
            f"concentrated, but the same shape.")
    for j, ln in enumerate(wrap(para, W - 90)):
        b.append(txt(40, ny + 22 + j * 18, ln, 12.5, MUTE))

    b.append(txt(40, H - 18, "Source: FDA GRAS and Animal Food GRAS notice inventories, "
                 "in reference/. Notifier names are normalised on their first 14 letters, "
                 "so a renamed subsidiary may split. Chart: examples/visualize.py",
                 10.5, MUTE))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#ffffff"/>'
           + "".join(b) + "</svg>")
    open(path, "w", encoding="utf-8").write(svg)
    return sets


def _wilson(k, n, z=1.96):
    """Wilson interval — the normal approximation misbehaves near the ends."""
    if not n:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


def practice_effect(path):
    """Does filing more often mean clearing more often? Mostly, not smoothly."""
    def key(s):
        return re.sub(r"[^a-z]", "", (s or "").lower())[:14]

    BUCKETS = [("filed once", lambda c: c == 1),
               ("2-3 times", lambda c: 2 <= c <= 3),
               ("4-9 times", lambda c: 4 <= c <= 9),
               ("10 or more", lambda c: c >= 10)]
    series = []
    for label, f, col in (("Human food", "gras-notices.csv", INK),
                          ("Animal food", "agras-notices.csv", MUTE)):
        rows = list(csv.DictReader(open(os.path.join(ROOT, "reference", f),
                                        encoding="utf-8")))
        n = Counter(key(r["notifier"]) for r in rows)
        pts = []
        for name, test in BUCKETS:
            sub = [r for r in rows
                   if test(n[key(r["notifier"])]) and r["outcome"] != "pending"]
            if len(sub) < 10:
                continue
            k = sum(1 for r in sub if r["outcome"] == "no questions")
            lo, hi = _wilson(k, len(sub))
            pts.append((name, 100 * k / len(sub), lo, hi, len(sub)))
        closed = [r for r in rows if r["outcome"] != "pending"]
        base = 100 * sum(1 for r in closed if r["outcome"] == "no questions") / len(closed)
        series.append((label, pts, base, col))

    W, L, R, TOP, ROWH = 1120, 214, 300, 216, 46
    PW = W - L - R
    LO, HI = 25, 100
    X = lambda v: L + PW * (v - LO) / (HI - LO)
    total = sum(len(p) for _, p, _, _ in series)
    H = TOP + ROWH * total + 108 * len(series) + 150

    b = [txt(40, 44, "Clearance rises with practice — but not smoothly",
             21, INK, weight="600")]
    for i, ln in enumerate(wrap(
            "Share of closed GRAS notices where FDA had no questions, grouped by how "
            "many notices that notifier has ever filed. Bars are 95% Wilson intervals.",
            W - 90)):
        b.append(txt(40, 70 + i * 18, ln, 12.5, MUTE))

    y = TOP
    for label, pts, base, col in series:
        b.append(txt(40, y - 22, label, 14, INK, weight="600"))
        for g in range(30, 101, 10):
            b.append(f'<line x1="{X(g):.1f}" y1="{y-14:.1f}" x2="{X(g):.1f}" '
                     f'y2="{y + ROWH*len(pts) - 12:.1f}" stroke="{GRID}" stroke-width="1"/>')
            b.append(txt(X(g), y - 20, f"{g}%", 10.5, MUTE, "middle"))
        b.append(f'<line x1="{X(base):.1f}" y1="{y-14:.1f}" x2="{X(base):.1f}" '
                 f'y2="{y + ROWH*len(pts) - 12:.1f}" stroke="{VIOLET}" '
                 f'stroke-width="1.3" stroke-dasharray="4 3"/>')
        b.append(txt(X(base), y + ROWH * len(pts) + 4, f"all {base:.1f}%",
                     10.5, VIOLET, "middle"))
        for i, (name, rate, lo, hi, n_) in enumerate(pts):
            ry = y + i * ROWH + 8
            b.append(txt(L - 18, ry + 4, name, 12.5, INK, "end"))
            b.append(txt(L - 18, ry + 19, f"n={n_}", 10.5, MUTE, "end"))
            b.append(f'<line x1="{X(lo):.1f}" y1="{ry:.1f}" x2="{X(hi):.1f}" '
                     f'y2="{ry:.1f}" stroke="{col}" stroke-width="2.2"/>')
            for v in (lo, hi):
                b.append(f'<line x1="{X(v):.1f}" y1="{ry-5:.1f}" x2="{X(v):.1f}" '
                         f'y2="{ry+5:.1f}" stroke="{col}" stroke-width="2.2"/>')
            b.append(circ(X(rate), ry, 5.5, col))
            b.append(txt(X(hi) + 12, ry + 4, f"{rate:.1f}%", 12, INK, weight="600"))
        y += ROWH * len(pts) + 108

    ny = y - 66
    b.append(txt(40, ny, "Read the intervals, not the ranking", 13, INK, weight="600"))
    para = ("The top and bottom of the human series are genuinely apart: filing ten or "
            "more times clears 90.7% against 75.1% for two-to-three, which is 4.0 "
            "standard errors. But the sequence is not a ladder — one-time filers beat "
            "the 2-3 group by 6.3 points, and that gap is only 2.3 standard errors. "
            "Whatever practice buys, it does not accumulate evenly, and the simplest "
            "story — file more, learn more, clear more — does not survive its own second "
            "row. The animal series has no gradient at all and intervals three times "
            "wider; on 86 closed notices it cannot resolve one.")
    for j, ln in enumerate(wrap(para, W - 90)):
        b.append(txt(40, ny + 22 + j * 18, ln, 12.5, MUTE))

    b.append(txt(40, H - 18, "Source: FDA GRAS and Animal Food GRAS notice inventories, "
                 "in reference/. Pending notices excluded. Buckets with fewer than 10 "
                 "closed notices omitted. Chart: examples/visualize.py", 10.5, MUTE))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#ffffff"/>'
           + "".join(b) + "</svg>")
    open(path, "w", encoding="utf-8").write(svg)
    return series


def main():
    os.makedirs(OUT, exist_ok=True)
    by, as_of = load()
    p = os.path.join(OUT, "queue-composition.svg")
    queue_composition(by, as_of, p)
    print(f"{len(by)} petitions as of {as_of} -> {p}")

    rules, fcn = load_reference()
    p2 = os.path.join(OUT, "the-gate-moved.svg")
    c, n = the_gate_moved(rules, fcn, p2)
    print(f"{c} food-contact petitions vs {n} notifications 1990-2026 -> {p2}")

    p4 = os.path.join(OUT, "who-files.svg")
    for label, n, _, total in who_files(p4):
        print(f"  {label}: {len(n)} notifiers, {total} notices")
    print(f"-> {p4}")

    p5 = os.path.join(OUT, "practice-effect.svg")
    practice_effect(p5)
    print(f"-> {p5}")

    p3 = os.path.join(OUT, "animal-vs-human.svg")
    for name, _, closed, total in animal_vs_human(p3):
        print(f"  {name}: {closed} closed of {total}")
    print(f"-> {p3}")


if __name__ == "__main__":
    main()
