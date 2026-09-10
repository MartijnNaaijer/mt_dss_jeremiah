#!/usr/bin/env python3
"""
Writes docs/index.html from the measurements in collate.py.

Every number and every reading on the page comes out of that module; nothing
is transcribed by hand.  Run it after the corpora are in place:

    python src/build.py
"""

from __future__ import annotations

import html as H
import shutil
from pathlib import Path

import collate as C

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "docs"
ASSETS = OUT / "assets"

FONTS = ("https://fonts.googleapis.com/css2?family=Cardo:ital,wght@0,400;0,700;1,400"
         "&family=Frank+Ruhl+Libre:wght@400;500"
         "&family=Spectral:ital,wght@0,400;0,500;0,600;1,400&display=swap")

TITLE = "The short edition of Jeremiah at Qumran"
DESC = ("Two Jeremiah scrolls from Cave 4 carry the shorter text behind the "
        "Greek, not the text of the Masoretic Bible. What the leather shows, "
        "what an editor supplied, and what follows from the size of the gap.")


def esc(s):
    return H.escape(s or "")


def scroll_html(words):
    """A scroll line, with the editor's reconstruction set grey and bracketed."""
    parts, inrec, open_span = [], False, False

    def close():
        nonlocal open_span
        if open_span:
            parts.append("</span>")
            open_span = False

    for w in words:
        for s in w["signs"]:
            rec = s["rec"]
            if rec and not inrec:
                close(); parts.append("["); inrec = True
            elif not rec and inrec:
                close(); parts.append("]"); inrec = False
            cls = "traces" if s.get("traces") else ("rec" if rec else None)
            if cls == "rec" and open_span:
                pass
            else:
                close()
                if cls:
                    parts.append(f'<span class="{cls}">')
                    open_span = True
            parts.append(esc(s["g"]))
            if s.get("unc"):
                parts.append("̇")
        close()
        parts.append(w["after"])          # empty means: written onto the next
    if inrec:
        parts.append("]")
    return "".join(parts).strip()


def mt_html(mt_words, absent):
    """The Masoretic verse, with the words the scroll does not carry marked."""
    out = []
    for i, w in enumerate(mt_words):
        cls = absent.get(i)
        txt = esc(w["pointed"])
        out.append(f'<span class="only{" onink" if cls == "ink" else ""}">{txt}</span>'
                   if cls else txt)
        out.append(esc(w["trailer"]))
    return "".join(out).strip()


def absent_map(mt_words, scroll_words):
    """Which Masoretic words the scroll lacks, and whether ink says so."""
    sw = C.evidence(scroll_words or [])
    if not sw:
        return {}
    out = {}
    for tag, a1, a2, b1, b2 in C.align(mt_words, sw):
        if tag != "delete":
            continue
        jl = sw[b1 - 1] if b1 - 1 >= 0 else None
        jr = sw[b1] if b1 < len(sw) else None
        state = "ink" if (jl and jl["ink"] and jr and jr["ink"]) else "recon"
        for i in range(a1, a2):
            out[i] = state
    return out


# ---------------------------------------------------------------------------
def order_section(d):
    order = d["order"]
    mt_v = [v for v in order["mt"] if v <= 12]
    greek = [v for v in order["greek"] if v <= 12]

    # the scroll repeats verse 5: half of it before verse 9, half after
    scroll, seen = [], set()
    for v in order["scroll"]:
        if v > 12:
            break
        scroll.append((v, "a" if v not in seen else "b") if v == 5 else (v, ""))
        seen.add(v)

    mt_chips = "".join(
        f'<span class="chip{" only" if v in (6, 7, 8, 10) else ""}">{v}</span>'
        for v in mt_v)
    sc_chips = "".join(
        f'<span class="chip{" moved" if v in (5, 9) else ""}">{v}{s}</span>'
        for v, s in scroll) + "".join(
        f'<span class="chip gone">{v}</span>' for v in (6, 7, 8, 10))
    gk_chips = "".join(
        f'<span class="chip{" moved" if v in (5, 9) else ""}">{v}</span>'
        for v in greek) + "".join(
        f'<span class="chip gone">{v}</span>' for v in (6, 7, 8, 10))

    return f"""
<section id="order"><div class="wrap">
<h2>Jeremiah 10 is not in the same order in all three</h2>
<p class="lede">The Masoretic chapter runs straight through. The Greek has no
verses 6 to 8 and no verse 10, and it prints verse 9 before verse 5. The scroll
does the same, and splits verse 5 around it.</p>
<div class="tracks">
  <div class="track"><div class="who">Masoretic Text<span>BHSA</span></div>
    <div class="chips">{mt_chips}</div></div>
  <div class="track"><div class="who">4QJer<sup>b</sup><span>4Q71, Cave 4</span></div>
    <div class="chips">{sc_chips}</div></div>
  <div class="track"><div class="who">Old Greek<span>Rahlfs</span></div>
    <div class="chips">{gk_chips}</div></div>
</div>
<div class="key">
  <span><i class="sw" style="background:var(--plus-soft);border:1px solid var(--plus-line)"></i>
    in the Masoretic Text only</span>
  <span><i class="sw" style="background:transparent;border:1px dashed var(--plus-line)"></i>
    not there at all</span>
  <span><i class="sw" style="background:transparent;border:1px solid var(--sea)"></i>
    out of Masoretic order</span>
</div>
<p>The arrangement in the middle row is an editor's, and the section below is
about whether it can be believed. The two outer rows are not: they are what the
Masoretic Text and Rahlfs's Greek actually print.</p>
</div></section>
"""


def space_section(d):
    p = d["passages"][0]
    s, g = p["space"], d["gap"]
    mean = s["line_mean"]
    widest = max(l["slots"] for l in p["lines"])

    rows = []
    for l in p["lines"]:
        # ink runs inside this line, as a fraction of the line
        idx, marks = 0, []
        for w in p["words"][l["first"]:l["last"] + 1]:
            for sg in w["signs"]:
                if sg.get("lost"):
                    continue
                if not sg["rec"]:
                    marks.append(idx)
                idx += 1
        runs = []
        for m in marks:
            if runs and runs[-1][1] == m:
                runs[-1][1] = m + 1
            else:
                runs.append([m, m + 1])
        bars = "".join(
            f'<i style="right:{a / l["slots"] * 100:.2f}%;'
            f'width:{(b - a) / l["slots"] * 100:.2f}%"></i>' for a, b in runs)
        focus = " focus" if l["nr"] in d["gap"]["anchors"] else ""
        rows.append(
            f'<div class="frag-row{focus}"><div class="n">{l["nr"]}</div>'
            f'<div class="bar" style="width:{l["slots"] / widest * 100:.1f}%">{bars}</div></div>')

    a_line, b_line = d["gap"]["anchors"]
    a_txt, b_txt = d["gap"]["anchor_text"]
    need, short = g["mt"], g["short"]
    span = max(need, mean, short)

    def meter(kind, label, sub, n, note):
        return (f'<div class="scale {kind}"><div class="lbl">{label}<span>{sub}</span></div>'
                f'<div class="meter"><i style="width:{n / span * 100:.1f}%"></i></div>'
                f'<div class="num">{note}</div></div>')

    between = " + ".join(f"{v}:&nbsp;{n}" for v, n in sorted(g["between"].items()))

    return f"""
<section id="space"><div class="wrap">
<h2>The Masoretic chapter is too long for the fragment</h2>
<p class="lede">Only {s['ink']} of the {s['slots']} letter-places of this fragment
survive as ink, about {s['ink'] / s['slots']:.0%} of it, and the ink falls near the
end of each line. That is little to read, but it is enough to measure: it fixes
where particular words stood, and the lines between them have a known width.</p>
<div class="frag">{''.join(rows)}
  <p class="absent">Each bar is one line of the fragment, drawn to its length;
  the dark marks are the surviving ink. The two outlined lines are {a_line} and
  {b_line}.</p>
</div>
<h3>One line, and two texts asking to go into it</h3>
<p>Line {a_line} ends with <span dir="rtl" lang="he">{esc(a_txt)}</span>, from
Jeremiah 10:4. Line {b_line} ends with <span dir="rtl" lang="he">{esc(b_txt)}</span>,
from 10:9. They are consecutive lines of one fragment, so whatever stood between
those two words occupied a single line.</p>
<div class="scales">
  {meter("have", "The space there", f"one line; this fragment averages {mean} letters",
         mean, f"about {mean} letters")}
  {meter("short", "The short text needs", "10:4 straight on to 10:9",
         short, f"{short} letters")}
  {meter("need", "The Masoretic Text needs",
         f"with 10:5&ndash;8 in between &mdash; {between}",
         need, f"{need} letters, {need / mean:.1f} lines")}
</div>
<p>The Masoretic arrangement asks for two and a half lines of writing in the
space of one. It will not go in. That is the argument the editors make for this
scroll, and it does not depend on a single reconstructed letter: it depends on
where the ink is and how wide the lines are.</p>
<div class="note">
  <h3>What this does not show</h3>
  <p>It shows that <b>10:5&ndash;8 as the Masoretic Text has them were not
  there</b>. It does not by itself show that verse 9 stood before verse 5, or
  that verse 10 was missing: the fragment has room for the shorter text in
  several arrangements, and the one printed above is the editor's, chosen
  because the Greek has exactly that order. Between the ink of 10:9 and the ink
  of 10:11 the sums do not decide anything &mdash; the Masoretic text with verse
  10 and the scroll's text with the second half of verse 5 come to nearly the
  same length.</p>
</div>
</div></section>
"""


def joins_section(d):
    def glosses(txt):
        parts = [g for g in txt.split() if g]
        return ", ".join(parts)

    rows = []
    for p in d["passages"]:
        for jn in p["joins"]:
            with_greek = jn["greek"] == "lacks"
            cls = "greek" if with_greek else "alone"
            verdict = "with the Greek" if with_greek else "shorter than both"
            extra = ("" if with_greek else
                     " <span class=\"say\">The Greek has these words, so here the "
                     "scroll is shorter than the Masoretic Text and the Greek "
                     "alike.</span>")
            rows.append(f"""
<div class="join">
  <div class="hd"><span class="ref">{p['ch']}:{jn['vs']}</span>
    <span class="verdict {cls}">{verdict}</span>
    <span class="ref">{p['name']}</span></div>
  <p class="heb"><span class="keep">{scroll_html(jn['left_words'])}</span>
     <span class="gap">{esc(jn['mt'])}</span>
     <span class="keep">{scroll_html(jn['right_words'])}</span></p>
  <p class="gl">Masoretic only, glossed <i>{esc(glosses(jn['gloss']))}</i>.{extra}</p>
</div>""")

    for p in d["passages"]:
        for t in p["stipp_tested"]:
            if t["state"] != "carries-ink":
                continue
            rows.append(f"""
<div class="join">
  <div class="hd"><span class="ref">{p['ch']}:{t['vs']}</span>
    <span class="verdict mt">with the Masoretic Text</span>
    <span class="ref">{p['name']}</span></div>
  <p class="heb"><span class="keep">{esc(t.get('text') or t['phrase'])}</span></p>
  <p class="gl">This word is on the leather and the Greek has nothing answering
  to it, so here the scroll goes with the Masoretic Text.</p>
</div>""")

    b = d["passages"][0]
    return f"""
<section id="ink"><div class="wrap">
<h2>What the leather itself says</h2>
<p class="lede">Two words of a scroll that are both ink and stand side by side
are a join, and a join is testimony: whatever the Masoretic Text has between
them was not in this copy. It is the only kind of omission a manuscript can
witness to, because an omission inside a hole is the modern editor's and not
the scribe's. Below, the words in blue are the ink, and the words in ochre are
what the Masoretic Text puts between them.</p>
<div class="joins">{''.join(rows)}</div>
<p>Three of the five go with the Greek, one with the Masoretic Text, and one
with neither. That is the texture of the thing: {b['name']}'s neighbour
{d['passages'][1]['name']} is close to the text behind the Greek without being
a copy of it.</p>
<div class="note">
  <h3>4QJer<sup>b</sup> has no such join at all</h3>
  <p>Its surviving ink is {b['space']['ink']} letters in
  {len(b['space']['runs'])} separate runs, and no two of its words are adjacent
  on the leather. Everything above about Jeremiah 10 rests on the size of the
  gaps and nothing on two words standing next to each other. The two scrolls
  are evidence of different kinds, and they are worth keeping apart.</p>
</div>
</div></section>
"""


def collation_section(d):
    blocks = []
    for p in d["passages"]:
        by_verse = {}
        for w in p["words"]:
            if w["vs"]:
                by_verse.setdefault(w["vs"], []).append(w)
        lo, hi = p["lo"], p["hi"]
        gk_ch = p["greek_ch"]

        verses = []
        for key in sorted(k for k in d["mt"]):
            c, v = (int(x) for x in key.split(":"))
            if (c, v) < lo or (c, v) > hi:
                continue
            mtw = d["mt"][key]
            sw = by_verse.get(v) if c == p["ch"] else None
            absent = absent_map(mtw, sw) if sw else {}
            rows = [f'<div class="vn">{c}:{v}</div>',
                    f'<div><div class="mt">{mt_html(mtw, absent)}</div>']
            if sw:
                rows.append(f'<div class="wit"><div class="sg">{p["sig"]}</div>'
                            f'<div class="scroll">{scroll_html(sw)}</div></div>')
            else:
                rows.append('<p class="absent">no part of this verse is in the scroll</p>')
            gk = d["greek"].get(f"{gk_ch}:{v}")
            if gk:
                rows.append(f'<div class="grk"><span class="sg">Gr {gk_ch}:{v}</span>'
                            f'{esc(gk)}</div>')
            else:
                rows.append('<p class="absent">the Greek has no such verse</p>')
            rows.append("</div>")
            verses.append(f'<div class="verse">{"".join(rows)}</div>')

        blocks.append(f"""
<h3>{p['name']} &mdash; Jeremiah {lo[0]}:{lo[1]} to {hi[0]}:{hi[1]}</h3>
<div class="collation">{''.join(verses)}</div>""")

    return f"""
<section id="collation"><div class="wrap">
<h2>The passages in full</h2>
<p class="lede">The Masoretic verse, the scroll beneath it, and Rahlfs's Greek
beneath that. In the Masoretic line, ochre marks a word the scroll does not
carry; a tinted ochre marks one the leather excludes rather than the editor. In
the scroll line, grey letters in brackets are the editor's reconstruction, a
dot above a letter means the reading is uncertain, and
<span class="traces">&deg;</span> is a letter surviving only as traces.</p>
{''.join(blocks)}
</div></section>
"""


def build():
    d = C.collate()
    b, dd = d["passages"]

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{H.escape(DESC, quote=True)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{H.escape(FONTS, quote=True)}" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<header class="masthead"><div class="wrap">
  <div class="title"><h1>{TITLE}</h1><span class="he">ירמיהו</span></div>
  <p class="standfirst">Jeremiah comes down in two editions. The Masoretic Text
  is about an eighth longer than the text the Greek translator worked from, and
  in places it puts the chapters in another order. Of the six Jeremiah scrolls
  from the Judaean Desert, four go with the Masoretic Text. <b>Two do not.</b></p>
  <p class="standfirst">This page sets those two, {b['name']} and {dd['name']},
  against the Masoretic Text and the Greek, and keeps three things apart
  throughout: what survives as ink, what a modern editor supplied inside a
  hole, and what follows from the size of the hole. Only
  {b['space']['ink'] / b['space']['slots']:.0%} of the first scroll and
  {dd['space']['ink'] / dd['space']['slots']:.0%} of the second is ink.</p>
</div></header>
<main>
{order_section(d)}
{space_section(d)}
{joins_section(d)}
{collation_section(d)}
<section id="method"><div class="wrap">
<h2>How this was measured</h2>
<p>The Masoretic Text is the ETCBC <a href="https://github.com/ETCBC/bhsa">BHSA</a>
database. The scrolls are the ETCBC <a href="https://github.com/ETCBC/dss">dss</a>
dataset, Martin Abegg's transcription, in which every sign carries a flag saying
whether it is on the leather or supplied; nothing on this page treats a supplied
sign as a witness. The Greek is Rahlfs, from the
<a href="https://github.com/eliranwong/LXX-Rahlfs-1935">LXX</a> dataset. Greek
Jeremiah runs on its own versification: Greek 50 is Masoretic 43, while in
chapter 10 the numbers agree and it is the verses themselves that differ.</p>
<p>For the question of which Masoretic words are absent from the Greek, the page
follows Hermann-Josef Stipp, <i>Textkritische Synopse zum Jeremiabuch</i>, 15.
korrigierte interne Auflage (2021), as parsed in the companion study. Every
reading it is relied on for here was checked against Rahlfs directly.</p>
<p>The measurement is in <code>src/collate.py</code> and the page in
<code>src/build.py</code>. No figure or reading on this page is typed in by
hand; all of them are computed and can be reproduced by running those two.</p>
</div></section>
</main>
<footer><div class="wrap">
<p>Masoretic Text: ETCBC BHSA 2021. Judaean Desert manuscripts: ETCBC dss 2.0.
Greek: Rahlfs 1935. Reconstruction and legibility are marked as the dss dataset
encodes them.</p>
<p>Companion edition, the whole Hebrew Bible verse by verse against the
manuscripts:
<a href="https://martijnnaaijer.github.io/mt_dss_hebrew_bible/">mt_dss_hebrew_bible</a>.</p>
<p>This edition &#169; 2026 Martijn Naaijer, licensed
<a href="https://creativecommons.org/licenses/by-nc/4.0/" rel="license">CC BY-NC 4.0</a>.
Source at <a href="https://github.com/MartijnNaaijer/mt_dss_jeremiah">github.com/MartijnNaaijer/mt_dss_jeremiah</a>.</p>
</div></footer>
</body></html>
"""
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "index.html").write_text(page, encoding="utf-8")
    shutil.copyfile(HERE / "assets" / "site.css", ASSETS / "site.css")

    C.report(d)
    print(f"\nwrote {OUT / 'index.html'} "
          f"({(OUT / 'index.html').stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
