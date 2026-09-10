#!/usr/bin/env python3
"""
The null: run the same instrument on the manuscripts where the effect must be absent.

`collate.py` reports that 4QJer d omits three Masoretic pluses across a join --
two extant words standing side by side, with the Masoretic reading between them
and no room for it -- and that the Old Greek lacks all three.  On its own that
is three data points and no way to tell a finding from an artefact of the
method.

Four of the six Jeremiah manuscripts from the Judaean Desert are of the
Masoretic type: 4Q70 (4QJer a), 4Q72 (4QJer c), 4Q72b (4QJer e) and 2Q13
(2QJer).  If the join test measures the shape of a text, they should behave the
opposite way: where Stipp brackets a Masoretic plus, they should CARRY it, on
extant text, and they should rarely join across one.  If instead they omit
pluses at about the same rate as 4QJer d, the test is measuring damage or
alignment noise and not the edition, and the page's central table means nothing.

The test is the same two functions, unchanged, over the whole book:

    ink_joins()   two adjacent extant words, and what the Masoretic Text puts
                  between them
    verdict()     for one bracketed Masoretic plus: does this manuscript carry
                  it, is it absent, and is either answer on extant text?

Only decidable cases are counted.  A plus inside a lacuna is not evidence in
either direction -- that is the rule the whole study rests on -- so the
denominator is the pluses a manuscript can actually answer for.

    python src/control.py
"""

from __future__ import annotations

import collections
import sys

import collate as C

SIGLA = {
    "4Q71": "4QJerᵇ", "4Q72a": "4QJerᵈ",              # the short-edition pair
    "4Q70": "4QJerᵃ", "4Q72": "4QJerᶜ",               # the Masoretic-type four
    "4Q72b": "4QJerᵉ", "2Q13": "2QJer",
}
SHORT = ("4Q71", "4Q72a")


def run():
    mt = C.read_mt(chapters=None)                     # all 52 chapters
    stipp, _empty, _greek, _notes = C.read_stipp()

    rows = []
    for sig, name in SIGLA.items():
        words, lines = C.read_scroll(sig)
        by_verse = {}
        for w in words:
            if w["vs"] and w["ch"]:
                by_verse.setdefault((w["ch"], w["vs"]), []).append(w)

        slots = sum(1 for w in words for s in w["signs"] if not s.get("lost"))
        extant = sum(1 for w in words for s in w["signs"]
                     if not s.get("lost") and not s["rec"])

        # 1. every bracketed Masoretic plus this manuscript can answer for
        state = collections.Counter()
        omitted, carried = [], []
        for (c, v), phrases in stipp.items():
            sw = by_verse.get((c, v))
            if not sw or (c, v) not in mt:
                continue
            for ph in phrases:
                if len(C.bare(ph)) < 2:
                    continue
                r = C.verdict({v: sw}, c, v, mt[(c, v)], ph)
                state[r["state"]] += 1
                if r["state"] == "lacking-ink":
                    omitted.append((c, v, ph))
                elif r["state"] == "carries-ink":
                    carried.append((c, v, ph))

        # 2. every join, and whether the Old Greek lacks what it excludes
        joins = collections.Counter()
        join_list = []
        for (c, v), sw in sorted(by_verse.items()):
            if (c, v) not in mt:
                continue
            for jn in C.ink_joins(mt[(c, v)], sw):
                pluses = stipp.get((c, v), [])
                marked = any(C.bare(jn["mt"]) == C.bare(p) for p in pluses)
                joins["greek-lacks" if marked else "greek-has"] += 1
                join_list.append({"ch": c, "vs": v, "marked": marked, **jn})

        decidable = state["lacking-ink"] + state["carries-ink"]
        rows.append({
            "sig": sig, "name": name, "short": sig in SHORT,
            "slots": slots, "extant": extant,
            "verses": len(by_verse),
            "decidable": decidable,
            "omits": state["lacking-ink"], "carries": state["carries-ink"],
            "rate": state["lacking-ink"] / decidable if decidable else None,
            "joins_greek": joins["greek-lacks"], "joins_other": joins["greek-has"],
            "omitted": omitted, "carried": carried, "join_list": join_list,
            "state": dict(state),
        })
    return rows


def report(rows):
    print("=" * 78)
    print("Bracketed Masoretic pluses each manuscript can answer for")
    print(f"{'':9s} {'':9s} {'extant':>13s} {'verses':>7s} {'decidable':>10s} "
          f"{'omits':>6s} {'carries':>8s} {'omitted':>8s}")
    for r in sorted(rows, key=lambda r: (not r["short"], r["sig"])):
        rate = f"{r['rate']:.0%}" if r["rate"] is not None else "   --"
        mark = "*" if r["short"] else " "
        print(f"{mark}{r['name']:8s} {r['sig']:9s} "
              f"{r['extant']:6d}/{r['slots']:<6d} {r['verses']:7d} {r['decidable']:10d} "
              f"{r['omits']:6d} {r['carries']:8d} {rate:>8s}")
    print("  * the two said to carry the short edition")

    short = [r for r in rows if r["short"]]
    mt_type = [r for r in rows if not r["short"]]
    so, sd = sum(r["omits"] for r in short), sum(r["decidable"] for r in short)
    mo, md = sum(r["omits"] for r in mt_type), sum(r["decidable"] for r in mt_type)
    print()
    print(f"  short edition pair : {so} of {sd} pluses omitted"
          + (f" ({so / sd:.0%})" if sd else ""))
    print(f"  Masoretic-type four: {mo} of {md} pluses omitted"
          + (f" ({mo / md:.0%})" if md else ""))
    if sd and md:
        print(f"  Fisher exact p = {fisher(so, sd - so, mo, md - mo):.3g}")

    print()
    print("Joins, and whether the Old Greek lacks what each excludes")
    for r in sorted(rows, key=lambda r: (not r["short"], r["sig"])):
        tot = r["joins_greek"] + r["joins_other"]
        share = f"{r['joins_greek'] / tot:.0%}" if tot else "  --"
        print(f"  {r['name']:8s} {r['joins_greek']:4d} of {tot:4d} joins are over a "
              f"bracketed plus  ({share})")

    print()
    print("The pluses each manuscript omits across a join")
    for r in sorted(rows, key=lambda r: (not r["short"], r["sig"])):
        if not r["omitted"]:
            print(f"  {r['name']:8s} none")
            continue
        for c, v, ph in r["omitted"]:
            print(f"  {r['name']:8s} {c}:{v} {ph}")
    print("=" * 78)


def fisher(a, b, c, d):
    """Two-sided Fisher exact test on [[a, b], [c, d]], standard library only."""
    from math import comb
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def p(x):
        return comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)

    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    obs = p(a)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= obs * (1 + 1e-9)))


if __name__ == "__main__":
    if C.read_stipp() == ({}, [], {}, {}):
        sys.exit("this control needs synopse.json; set $SYNOPSE")
    report(run())
