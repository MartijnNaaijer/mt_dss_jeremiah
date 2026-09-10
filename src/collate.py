#!/usr/bin/env python3
"""
The evidence behind the page: measurement only, no HTML.

Two of the six Jeremiah scrolls, 4Q71 (4QJer b) and 4Q72a (4QJer d), are
said to carry the short edition of the book -- the text the Greek translator
had in front of him rather than the text of the Masoretic Bible.  This module
works out what can actually be shown, and separates three things that are
easy to run together:

    what is extant
    what a modern editor restored within a lacuna
    what follows from the extent of the lacuna rather than from either

The third is not a weaker kind of evidence, it is a different kind, and for
4QJer b it is the decisive one: the fragment preserves text at the end of each
line, and the distance between two of those ink runs is one line, while the
Masoretic text between the same two points needs two and a half.

Sources
-------
BHSA 2021              the Masoretic Text
ETCBC dss 2.0          the scrolls, with `rec` marking every reconstructed sign
CenterBLC lxx 1935     Rahlfs, for the Greek.  Jeremiah runs on its own
                       versification: MT 43 is Greek 50, while MT 10 is
                       Greek 10 -- with 10:6-8 and 10:10 simply absent and
                       10:9 printed before 10:5
synopse.json           Stipp, Textkritische Synopse zum Jeremiabuch, 15.
                       korrigierte interne Auflage 2021, as parsed by the
                       companion study.  Used for one thing only: which
                       Masoretic words are absent from the Old Greek.  Every
                       reading it is relied on for here has been checked
                       against Rahlfs by hand.

Nothing here is hand-entered.  Run it on its own to print the findings:

    python src/collate.py
"""

from __future__ import annotations

import difflib
import json
import os
import re
import sys
from pathlib import Path

from cfabric import Fabric

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

BHSA_TF = os.environ.get("BHSA_TF", "~/text-fabric-data/github/ETCBC/bhsa/tf/2021")
DSS_TF = os.environ.get("DSS_TF", "~/text-fabric-data/github/ETCBC/dss/tf/2.0")
LXX_TF = os.environ.get("LXX_TF", "~/text-fabric-data/CenterBLC/lxx/tf/1935")
SYNOPSE = os.environ.get(
    "SYNOPSE",
    "../dating_dtr_redaction_jeremiah_claude/deuteronomistic/results/synopse.json")

# The two passages, and the scroll that carries each.
PASSAGES = [
    {"sig": "4Q71", "name": "4QJerᵇ", "ch": 10, "lo": (9, 22), "hi": (10, 22),
     "greek_ch": 10},
    {"sig": "4Q72a", "name": "4QJerᵈ", "ch": 43, "lo": (43, 2), "hi": (43, 10),
     "greek_ch": 50},
]

SIGLA = ("4Q71", "4Q72a")          # the two manuscripts this study is about
SIGLA_MT = ("4Q70", "4Q72", "4Q72b", "2Q13")   # the four that go with the MT
CONS_SIGNS = {"cons", "numr", "foreign", "punct", "add"}
POINTS = re.compile("[֑-ֽֿ׀׃-ׇ]")
SIN_SHIN = re.compile("[ׁׂ]")
MAQQEF = "־"


def bare(s: str) -> str:
    """Consonants only, no pointing, no shin dot, no spaces -- a matching key."""
    return SIN_SHIN.sub("", POINTS.sub("", s or "")).replace(MAQQEF, "").replace(" ", "")


_LOADED = {}


def load(location, features, what):
    """Load a corpus once per process: the control reads six manuscripts."""
    if (location, features) in _LOADED:
        return _LOADED[(location, features)]
    path = Path(location).expanduser()
    if not path.is_dir():
        sys.exit(f"{what} not found at {path}\n"
                 f"Context-Fabric does not download corpora; clone the dataset and\n"
                 f"point the matching environment variable at its .tf directory.")
    api = Fabric(locations=str(path), silent="deep").load(features, silent="deep")
    if api is False:
        sys.exit(f"could not load {what} from {path} (missing features?)")
    _LOADED[(location, features)] = api
    return api


# ---------------------------------------------------------------------------
# The three witnesses
# ---------------------------------------------------------------------------
def read_mt(chapters=(9, 10, 43)):
    api = load(BHSA_TF, "otype oslots book chapter verse g_word_utf8 g_cons_utf8 "
                        "trailer_utf8 lex gloss voc_lex_utf8", "BHSA")
    F, L, T = api.F, api.L, api.T
    out = {}
    for v in F.otype.s("verse"):
        bk, c, vs = T.sectionFromNode(v)
        if bk != "Jeremiah":
            continue
        c, vs = int(c), int(vs)
        if chapters and c not in chapters:
            continue
        out[(c, vs)] = [
            {"pointed": F.g_word_utf8.v(w) or "",
             "cons": F.g_cons_utf8.v(w) or "",
             "lex": F.lex.v(w),
             "gloss": F.gloss.v(w) or "",
             "trailer": F.trailer_utf8.v(w) or ""}
            for w in L.d(v, otype="word")]
    return out


def read_scroll(sig):
    """Words in manuscript order, the line they stand on, and what is extant."""
    api = load(DSS_TF, "otype oslots scroll book_etcbc chapter verse glyph type "
                       "rec unc after line fragment lex_etcbc", "DSS")
    F, L = api.F, api.L
    node = next((s for s in F.otype.s("scroll") if F.scroll.v(s) == sig), None)
    if node is None:
        sys.exit(f"scroll {sig} not in the DSS dataset")

    words, lines = [], []
    for ln in L.d(node, otype="line"):
        frag = L.u(ln, "fragment")
        start = len(words)
        slots = 0
        for w in L.d(ln, otype="word"):
            if F.book_etcbc.v(w) != "Jeremiah":
                continue
            c, v = F.chapter.v(w), F.verse.v(w)
            signs = []
            for x in L.d(w, otype="sign"):
                t, g = F.type.v(x), F.glyph.v(x) or ""
                if t in ("empty", "sep", "term"):
                    continue
                if t == "missing":
                    signs.append({"g": ".", "rec": True, "unc": False, "lost": True})
                elif t == "unc":
                    signs.append({"g": "°", "rec": F.rec.v(x) == 1,
                                  "unc": False, "traces": True})
                elif g and t in CONS_SIGNS:
                    signs.append({"g": g, "rec": F.rec.v(x) == 1,
                                  "unc": bool(F.unc.v(x))})
            slotted = [s for s in signs if not s.get("lost")]
            words.append({
                "ch": int(c) if c else None, "vs": int(v) if v else None,
                "signs": signs, "after": F.after.v(w) or "",
                "lex": F.lex_etcbc.v(w),
                "cons": "".join(s["g"] for s in signs if not s.get("traces")
                                and not s.get("lost")),
                "punct": all(s["g"] in ("׃", ":") for s in slotted) if slotted else True,
                "ink": bool(slotted) and all(not s["rec"] for s in slotted),
                "any_ink": any(not s["rec"] for s in slotted),
                "line": F.line.v(ln),
            })
            slots += len(slotted)
        if slots:
            lines.append({"nr": F.line.v(ln),
                          "frag": F.fragment.v(frag[0]) if frag else "?",
                          "slots": slots, "first": start, "last": len(words) - 1})
    return words, lines


def read_greek(chapters):
    api = load(LXX_TF, "otype oslots book chapter verse word lex gloss", "LXX")
    F, L, T = api.F, api.L, api.T
    bk = next(b for b in F.otype.s("book") if T.sectionFromNode(b)[0] == "Jer")
    out, order = {}, {}
    for v in L.d(bk, otype="verse"):
        _, c, vs = T.sectionFromNode(v)
        c, vs = int(c), int(vs)
        if c not in chapters:
            continue
        out[(c, vs)] = " ".join(F.word.v(w) for w in L.d(v, otype="word"))
        order.setdefault(c, []).append(vs)
    return out, order


def read_stipp(chapters=None):
    """Three things from the Synopse, and a fourth is deliberately not taken.

    Taken: the Masoretic words Stipp brackets as absent from the Old Greek;
    the verses whose alexandrian column he leaves empty altogether; and the
    apparatus notes in which he cites a Judaean Desert manuscript by siglum.

    Not taken: his Greek panel.  See `greek_check` below."""
    path = Path(SYNOPSE)
    if not path.is_absolute():
        path = (REPO.parent.parent / path).resolve()
    if not path.is_file():
        print(f"  note: {path} not found, so the Old Greek column of the "
              f"agreement table is left empty", file=sys.stderr)
        return {}, [], {}, {}
    recs = json.loads(path.read_text(encoding="utf-8"))
    out, sentences, notes = {}, {}, {}
    for r in recs:
        if r["book"] != "Jeremiah" or (chapters and r["ch"] not in chapters):
            continue
        key = (r["ch"], r["v"])
        sentences.setdefault(key, []).append(r)
        for seg in r["mt"]:
            if seg["cls"] == "plus":
                txt = POINTS.sub("", seg["text"]).replace(MAQQEF, " ").strip()
                if txt:
                    out.setdefault(key, []).append(txt)
        for n in r.get("notes") or []:
            for sig in SIGLA:
                if sig in (n.get("text") or ""):
                    notes.setdefault(sig, []).append(
                        {"ch": r["ch"], "v": r["v"], "clause": r["clause"],
                         "kind": n["kind"], "text": n["text"].strip()})

    # a verse Stipp gives no alexandrian column at all: his own statement that
    # the Old Greek has nothing answering to it
    empty = sorted(k for k, rs in sentences.items()
                   if any(r["mt"] for r in rs)
                   and all(not r["og"] for r in rs)
                   and all(seg["cls"] == "plus" for r in rs for seg in r["mt"]))

    greek = {}
    for k, rs in sentences.items():
        g = " ".join(r["greek"] for r in rs if r["greek"]).strip()
        if g:
            greek[k] = g
    return out, empty, greek, notes


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------
def evidence(scroll_words):
    """The words a claim may rest on: the verse divider is not one of them."""
    return [w for w in scroll_words if not w["punct"]]


def align(mt_words, scroll_words):
    """Opcodes aligning one verse of the MT to the same verse in the scroll."""
    a = [w["lex"] for w in mt_words]
    b = [w["lex"] for w in scroll_words]
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()


def locate(mt_words, phrase):
    """Word indices of `phrase` inside a verse of the MT, or None."""
    key = bare(phrase)
    if not key:
        return None
    run, spans = "", []
    for i, w in enumerate(mt_words):
        c = bare(w["cons"])
        spans.append((len(run), len(run) + len(c), i))
        run += c
    at = run.find(key)
    if at < 0:
        return None
    end = at + len(key)
    hit = [i for lo, hi, i in spans if lo < end and hi > at]
    return (hit[0], hit[-1] + 1) if hit else None


def verdict(scroll_by_verse, ch, vs, mt_words, phrase):
    """Does the manuscript carry this Masoretic phrase, and is it extant there?

    Five outcomes.  The two that say `reconstruction` are not findings: they
    are lacunae a modern editor filled, and a filled lacuna cannot disagree
    with the text it was filled from.  `unaligned` is where the scroll breaks
    off or the two texts diverge so far that no word answers to another."""
    sw = evidence(scroll_by_verse.get(vs) or [])
    if not sw:
        return {"state": "absent-verse"}
    span = locate(mt_words, phrase)
    if span is None:
        return {"state": "not-found"}
    i1, i2 = span
    ops = align(mt_words, sw)

    kept, deleted, jl, jr = [], False, None, None
    for tag, a1, a2, b1, b2 in ops:
        if a2 <= i1 or a1 >= i2:
            continue
        if tag == "delete":
            deleted = True
            jl = sw[b1 - 1] if b1 - 1 >= 0 else None
            jr = sw[b1] if b1 < len(sw) else None
        elif tag == "equal":
            lo, hi = max(a1, i1), min(a2, i2)          # exact correspondence
            kept += sw[b1 + (lo - a1):b1 + (hi - a1)]
        else:
            return {"state": "unaligned"}              # replace / insert: no witness

    if deleted and not kept:
        on_ink = bool(jl and jl["ink"] and jr and jr["ink"])
        return {"state": "lacking-ink" if on_ink else "lacking-recon",
                "left": jl["cons"] if jl else "", "right": jr["cons"] if jr else ""}
    if not kept:
        return {"state": "unaligned"}
    text = " ".join(w["cons"] for w in kept)
    return {"state": "carries-ink" if all(w["ink"] for w in kept) else "carries-recon",
            "text": text}


def unit(words, i, back):
    """The whole graphical unit around word i: the ETCBC splits what the scribe
    wrote as one, and an empty `after` is where it must be joined again."""
    lo = hi = i
    if back:
        while lo > 0 and not words[lo - 1]["after"]:
            lo -= 1
    else:
        while hi + 1 < len(words) and not words[hi]["after"]:
            hi += 1
    return words[lo:hi + 1]


def mt_run(mt_words, lo, hi):
    """Masoretic words lo..hi as they are written, trailers and all."""
    out = ""
    for i in range(lo, hi):
        out += mt_words[i]["cons"] + (mt_words[i]["trailer"] if i < hi - 1 else "")
    return out.strip()


def ink_joins(mt_words, scroll_words):
    """Where the manuscript itself attests what did not stand in it.

    Two adjacent words that are both extant are a join: whatever the Masoretic
    Text has between them did not stand there.  It is the only kind of omission
    a manuscript can attest, since an omission within a lacuna is the editor's
    and not the scribe's."""
    sw = evidence(scroll_words)
    if not sw:
        return []
    m = {}                                   # scroll index -> Masoretic index
    for tag, a1, a2, b1, b2 in align(mt_words, sw):
        if tag == "equal":
            for k in range(a2 - a1):
                m[b1 + k] = a1 + k

    joins = []
    for j in range(len(sw) - 1):
        if not (sw[j]["ink"] and sw[j + 1]["ink"]):
            continue
        if j not in m or j + 1 not in m:
            continue
        lo, hi = m[j] + 1, m[j + 1]
        if hi <= lo:
            continue                          # the two are adjacent in the MT too
        gap = mt_run(mt_words, lo, hi)
        if not gap:
            continue
        left, right = unit(sw, j, back=True), unit(sw, j + 1, back=False)
        lt = "".join(w["cons"] for w in left)
        rt = "".join(w["cons"] for w in right)
        # A single letter is not an anchor.  The ETCBC writes a prefixed
        # particle as a word, and difflib will match a lone bet anywhere: at
        # 4Q70 14,4 it paired the bet of the manuscript's בארץ with the bet of
        # the Masoretic בעבור ten words earlier, and reported the ten words
        # between as excluded.  Both anchors and the gap must be two letters.
        if min(len(bare(lt)), len(bare(rt)), len(bare(gap))) < 2:
            continue
        joins.append({"left": lt,
                      "right": rt,
                      "left_words": left, "right_words": right,
                      "mt": gap,
                      "gloss": " ".join(mt_words[i]["gloss"] for i in range(lo, hi)).strip()})
    return joins


def space_argument(words, lines):
    """The one measurement that does not depend on any reconstruction.

    Ink survives at the end of most lines.  Between two of those ink runs the
    fragment has room for exactly one line; the question is how much text the
    Masoretic arrangement would have to fit into it."""
    slots, runs, cur = [], [], None
    for wi, w in enumerate(words):
        for s in w["signs"]:
            if s.get("lost"):
                continue
            slots.append((wi, s))
    prev = None
    for i, (wi, s) in enumerate(slots):
        if not s["rec"]:
            if cur is None:
                cur = {"start": i, "end": i, "text": "", "ch": words[wi]["ch"],
                       "vs": words[wi]["vs"], "line": words[wi]["line"]}
            elif prev is not None and wi != prev:
                # the divider, and empty means the scribe wrote the two as one:
                # תכלת וארגמן, not תכלתוארגמן and not תכלת ו ארגמן
                cur["text"] += words[prev]["after"]
            cur["end"] = i
            cur["text"] += s["g"]
            cur["vs_end"] = words[wi]["vs"]
        elif cur:
            runs.append(cur)
            cur = None
        prev = wi
    if cur:
        runs.append(cur)

    total = len(slots)
    body = [l["slots"] for l in lines[1:-1]] or [l["slots"] for l in lines]
    return {"slots": total, "ink": sum(1 for _, s in slots if not s["rec"]),
            "runs": runs, "line_mean": round(sum(body) / len(body)),
            "line_min": min(body), "line_max": max(body)}


def gap_measure(mt, runs, a_ch, a_vs, a_tail, b_ch, b_vs, b_head, between):
    """Letters the Masoretic text needs between two ink runs, against the space."""
    def verse_cons(c, v):
        return bare("".join(w["cons"] for w in mt[(c, v)]))

    a = verse_cons(a_ch, a_vs)
    i = a.find(bare(a_tail))
    b = verse_cons(b_ch, b_vs)
    j = b.find(bare(b_head))
    if i < 0 or j < 0:
        return None
    long_ = a[i + len(bare(a_tail)):] + "".join(verse_cons(a_ch, v) for v in between) + b[:j]
    short = a[i + len(bare(a_tail)):] + b[:j]
    return {"mt": len(long_), "short": len(short),
            "between": {v: len(verse_cons(a_ch, v)) for v in between}}


def greek_check(stipp_greek, rahlfs):
    """Stipp's Greek panel against Rahlfs, verse by verse.

    The panel is not used to set the Greek on the page, and this is why.  In
    Jeremiah 43 it agrees with Rahlfs throughout.  In Jeremiah 10 it does not,
    and it fails in one specific way: the Greek of 10:5 and of 10:9 come out
    against each other's Hebrew.  That is where the two editions are
    transposed, and a Greek panel laid out against a Hebrew column in Masoretic
    order has nowhere else to put them.  Stipp marks the transposition himself,
    with his star and a margin reference, so the fault is in reading the panel
    and not in the edition -- but it falls on the two verses this study turns
    on, so Rahlfs is used instead, where the Greek keeps its own order."""
    rows = []
    for (ch, gch) in ((10, 10), (43, 50)):
        for (c, v) in sorted(k for k in stipp_greek if k[0] == ch):
            st = stipp_greek[(c, v)]
            here = _sim(st, rahlfs.get((gch, v), ""))
            best = max(((_sim(st, t), k[1]) for k, t in rahlfs.items() if k[0] == gch),
                       default=(0.0, None))
            rows.append({"ref": f"{c}:{v}", "greek_ref": f"{gch}:{v}",
                         "sim": round(here, 3),
                         "best": best[1], "best_sim": round(best[0], 3),
                         "ok": here >= 0.90})
    return {"rows": rows,
            "ok": sum(1 for r in rows if r["ok"]),
            "n": len(rows),
            "misplaced": [r for r in rows if not r["ok"]]}


_ACC = re.compile(r"[^\w]+", re.UNICODE)


def _sim(a, b):
    import difflib
    import unicodedata

    def norm(s):
        s = unicodedata.normalize("NFD", s or "")
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
        return _ACC.sub("", s).lower()

    a, b = norm(a), norm(b)
    return difflib.SequenceMatcher(a=a, b=b).ratio() if a and b else 0.0


# ---------------------------------------------------------------------------
def collate():
    mt = read_mt()
    greek, gorder = read_greek({10, 50})
    stipp, stipp_empty, stipp_greek, stipp_notes = read_stipp({10, 43})

    data = {"passages": [], "stipp": bool(stipp)}
    for p in PASSAGES:
        words, lines = read_scroll(p["sig"])
        by_verse = {}
        for w in words:
            if w["vs"]:
                by_verse.setdefault(w["vs"], []).append(w)

        space = space_argument(words, lines)

        # every Masoretic word the scroll does not carry, with the state of the join
        omissions = []
        for (c, vs) in sorted(k for k in mt if k[0] == p["ch"]):
            sw = evidence(by_verse.get(vs) or [])
            if not sw:
                continue
            for tag, a1, a2, b1, b2 in align(mt[(c, vs)], sw):
                if tag != "delete":
                    continue
                txt = " ".join(mt[(c, vs)][i]["cons"] for i in range(a1, a2)).strip()
                if not txt:
                    continue
                jl = sw[b1 - 1] if b1 - 1 >= 0 else None
                jr = sw[b1] if b1 < len(sw) else None
                omissions.append({
                    "vs": vs, "mt": txt,
                    "gloss": " ".join(mt[(c, vs)][i]["gloss"] for i in range(a1, a2)),
                    "left": jl["cons"] if jl else "", "right": jr["cons"] if jr else "",
                    "ink": bool(jl and jl["ink"] and jr and jr["ink"]),
                })

        # what the extant text excludes, verse by verse
        joins = []
        for (c, vs) in sorted(k for k in mt if k[0] == p["ch"]):
            for jn in ink_joins(mt[(c, vs)], by_verse.get(vs) or []):
                pluses = stipp.get((c, vs), [])
                jn["greek"] = ("lacks" if any(bare(jn["mt"]) == bare(ph) for ph in pluses)
                               else "has")
                joins.append({"vs": vs, **jn})

        # Stipp's Masoretic pluses in this chapter, tested against the scroll
        tested = []
        for (c, vs), phrases in sorted(stipp.items()):
            if c != p["ch"]:
                continue
            for ph in phrases:
                if (c, vs) not in mt or len(bare(ph)) < 2:
                    continue
                v = verdict(by_verse, c, vs, mt[(c, vs)], ph)
                tested.append({"vs": vs, "phrase": ph, **v})

        data["passages"].append({
            **{k: p[k] for k in ("sig", "name", "ch", "lo", "hi", "greek_ch")},
            "words": words, "lines": lines, "space": space,
            "omissions": omissions, "stipp_tested": tested, "joins": joins,
        })

    # the order of the verses, in each witness
    p0 = data["passages"][0]
    seen, scroll_order = set(), []
    for w in p0["words"]:
        if w["ch"] == 10 and w["vs"]:
            if not scroll_order or scroll_order[-1] != w["vs"]:
                scroll_order.append(w["vs"])
            seen.add(w["vs"])
    data["order"] = {
        "mt": sorted({k[1] for k in mt if k[0] == 10 and k[1] <= 13}),
        "scroll": scroll_order,
        "greek": [v for v in gorder[10] if v <= 13],
    }

    # the decisive gap: from the ink of 10:4 to the ink of 10:9, one line apart
    data["gap"] = gap_measure(mt, p0["space"]["runs"],
                              10, 4, "יחזקום",
                              10, 9, "תכלת", [5, 6, 7, 8])
    runs = p0["space"]["runs"]
    a = next(r for r in runs if r["ch"] == 10 and r["vs"] == 4)
    b = next(r for r in runs if r["ch"] == 10 and r["vs"] == 9)
    data["gap"]["anchors"] = [a["line"], b["line"]]
    data["gap"]["anchor_text"] = [a["text"], b["text"]]
    data["gap"]["slots"] = b["start"] - a["end"] - 1
    data["mt"] = {f"{c}:{v}": mt[(c, v)] for (c, v) in mt}
    data["greek"] = {f"{c}:{v}": t for (c, v), t in greek.items()}
    data["greek_order"] = gorder
    data["stipp_pluses"] = {f"{c}:{v}": ph for (c, v), ph in stipp.items()}
    data["stipp_empty"] = [f"{c}:{v}" for c, v in stipp_empty]
    data["stipp_notes"] = stipp_notes
    data["greek_check"] = greek_check(stipp_greek, greek)
    return data


def report(d):
    gc = d["greek_check"]
    print("=" * 72)
    print(f"Stipp's Greek panel against Rahlfs: {gc['ok']} of {gc['n']} verses agree")
    for r in gc["misplaced"]:
        print(f"  {r['ref']}: {r['sim']:.2f} against Greek {r['greek_ref']}, "
              f"but {r['best_sim']:.2f} against Greek {r['best']}")
    print(f"Stipp gives no alexandrian column at all: {', '.join(d['stipp_empty'])}")
    for sig, ns in d["stipp_notes"].items():
        print(f"Stipp's apparatus cites {sig} at "
              f"{', '.join(str(n['ch']) + ':' + str(n['v']) for n in ns)}")
    print("=" * 72)
    print("Jeremiah 10, order of the verses")
    for k in ("mt", "scroll", "greek"):
        print(f"  {k:7s} " + " ".join(str(v) for v in d["order"][k]))
    g = d["gap"]
    print()
    print("The space argument for 4QJer b")
    s = d["passages"][0]["space"]
    print(f"  fragment: {s['ink']} of {s['slots']} letter slots survive as ink "
          f"({s['ink'] / s['slots']:.0%})")
    print(f"  line length: mean {s['line_mean']}, {s['line_min']}-{s['line_max']} slots")
    an = d["gap"]["anchors"]
    print(f"  the ink of 10:4 is on line {an[0]}, the ink of 10:9 on line {an[1]} "
          f"-- consecutive lines of one fragment")
    print(f"  the Masoretic text needs {g['mt']} letters there "
          f"({g['mt'] / s['line_mean']:.1f} lines); without 10:5-8 it needs {g['short']}")
    print(f"  {g['between']}")
    for p in d["passages"]:
        print()
        print(f"{p['name']} ({p['sig']}), Jeremiah {p['ch']}")
        s = p["space"]
        print(f"  {s['ink']} of {s['slots']} letter slots survive as ink "
              f"({s['ink'] / s['slots']:.0%})")
        print("  joins -- the Masoretic words the extant text excludes:")
        for jn in p["joins"]:
            print(f"    {p['ch']}:{jn['vs']:<3d} {jn['left']} | {jn['right']}"
                  f"   MT has [{jn['mt']}]   Old Greek {jn['greek']} it")
        print("  Stipp's Masoretic pluses tested:")
        for t in p["stipp_tested"]:
            if t["state"] in ("lacking-ink", "carries-ink"):
                print(f"    {p['ch']}:{t['vs']:<3d} {t['phrase']:22s} {t['state']}")
    print("=" * 72)


if __name__ == "__main__":
    report(collate())
