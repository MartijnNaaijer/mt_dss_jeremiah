# The short edition of Jeremiah at Qumran

One published page. Not a software project — a text-critical argument that
happens to be computed. Two scripts, both run by hand, both kept so the page can
be rebuilt from the corpora.

```
CLAUDE.md              this file
src/collate.py         the measurement. Writes no HTML. `python src/collate.py`
                       prints the findings as text
src/control.py         the null: the same two functions run over the whole book
                       on the four Masoretic-type manuscripts. Needs synopse.json
src/build.py           turns those findings into docs/index.html
src/assets/site.css    copied to docs/assets/ on every build
docs/                  what GitHub Pages serves: index.html + assets/site.css
LICENSE                CC BY-NC 4.0, the official plain-text legal code, verbatim
```

Published at **https://martijnnaaijer.github.io/mt_dss_jeremiah** from `docs/`,
by `.github/workflows/pages.yml` (Settings → Pages → Source = GitHub Actions).

**Sibling repository, same conventions, same author, same licence:**
`../mt_dss_hebrew_bible`, the whole Hebrew Bible verse by verse against every
Judaean Desert manuscript that reaches it, 969 pages. Both descend from
`MartijnNaaijer/samuel`, which covers Samuel alone. Commits in both are authored
`Martijn N <martijn.naayer@chello.nl>`; the session's own email is not the one
to use.

## The question, and the answer

Jeremiah comes down in two editions, the Masoretic about an eighth longer than
the Vorlage of the Greek. Four of the six Jeremiah manuscripts from the Judaean
Desert go with the Masoretic Text. **4QJerᵇ (4Q71) and 4QJerᵈ (4Q72a) do not.**

**They do not carry the same kind of evidence, and merging them would be
dishonest.** That is the finding the page is built around.

| | 4QJerᵇ, Jer 9:22–10:22 | 4QJerᵈ, Jer 43:2–10 |
|---|---|---|
| extant | 114 of 1,114 letter slots, **10%** | 219 of 485, **45%** |
| lines / ink runs | 13 / 15 | 9 / 24 |
| **joins** (two adjacent extant words) | **0** | **4** |
| the argument is | extent | the extant text |

**The control passes** (`src/control.py`, run over all 52 chapters). Of the
bracketed Masoretic pluses each manuscript can answer for on extant text,
4QJerᵈ omits **3 of 4**; the four Masoretic-type manuscripts — 4Q70, 4Q72,
4Q72b, 2Q13 — omit **0 of 42**. Fisher exact **p = 0.00026**. In the whole book
those four produce **one** join between them, 4QJerᶜ at 21:7 omitting
ומן־הרעב, which Stipp does not bracket: their own accident, not an agreement
with the Greek. **The test does find omissions there; it never finds one over a
Masoretic plus.** That is what makes this a null and not silence.

## The one rule

**A lacuna filled from the Masoretic Text cannot be evidence against the
Masoretic Text.** This is rule 6 of the parent project, and here it is
structural rather than advisory: `verdict()` and `ink_joins()` return
`lacking-recon` / `carries-recon` for anything standing inside a restoration,
and the page never counts those as findings.

Three states, kept apart everywhere, in the prose as in the code:

- **extant** — letters preserved in the manuscript (`rec` is not 1)
- **restored** — letters an editor supplied within a lacuna
- **extent** — what follows from the size of the lacuna, and from neither

## What each scroll actually shows

**4QJerᵇ has no join at all.** Its 114 extant letters sit in 15 runs, none
contiguous, all near the end of a line. The famous order — 9 before 5, no 6–8,
no 10 — is **entirely the editor's restoration** in this transcription. Do not
present it as read off the manuscript; the page's first section says so twice.

What can be measured is extent. The extant text of 10:4 is on line 5 and that of
10:9 on line 6, consecutive lines of one fragment, so one line stood between
them:

| | letters |
|---|---:|
| the space there (fragment mean, range 56–112) | **96** |
| 10:4 running straight on to 10:9 | 49 |
| the Masoretic Text, with 10:5–8 between (70+33+56+30) | **238** |

238 letters into a line of 96 is 2.5 lines. That settles that 10:5–8 as the
Masoretic Text has them were not there. **It settles nothing about the order of
what was**, and between the extant text of 10:9 and that of 10:11 the sums
decide nothing either: Masoretic with 10:10 and the scroll with 10:5b come to
nearly the same length. Say so; do not let the page drift into claiming the
transposition is measured.

**4QJerᵈ has four joins, and they do not all point one way.** Plus one Masoretic
plus it carries on extant text. Five data points, three verdicts:

| | Masoretic Text | 4QJerᵈ | |
|---|---|---|---|
| 43:6 | רב־טבחים | lacks | with the Greek |
| 43:6 | בן־שׁפן | lacks | with the Greek |
| 43:7 | עד | lacks | with the Greek |
| 43:9 | בית־פרעה | lacks | **shorter than both** |
| 43:9 | אשׁר | carries | **with the Masoretic Text** |

**It is close to the Vorlage of the Greek without being a copy of it.** Report
that texture; rounding it to "4QJerᵈ agrees with the Greek" is the one way this
page could become false.

## Data

| Source | Notes |
|---|---|
| BHSA 2021 | `~/text-fabric-data/github/ETCBC/bhsa/tf/2021`, `$BHSA_TF` |
| dss 2.0 | `~/text-fabric-data/github/ETCBC/dss/tf/2.0`, `$DSS_TF`. `rec == 1` on a **sign** is the restoration flag |
| lxx 1935 | `~/text-fabric-data/CenterBLC/lxx/tf/1935`, `$LXX_TF`. Rahlfs |
| `synopse.json` | `$SYNOPSE`, default `../dating_dtr_redaction_jeremiah_claude/deuteronomistic/results/synopse.json`, resolved from two levels above the repository. Written by the parent project's `parse_synopse.py` from Stipp's *Textkritische Synopse zum Jeremiabuch*, **15. korrigierte interne Auflage** (2021). **Optional**: without it the page builds and the Old Greek column of the agreement table is empty |

**Versification.** MT Jer 43 = Greek 50, one verse to one verse. MT Jer 10 =
Greek 10, but Rahlfs prints 1 2 3 4 **9 5** 11 and has **no 6, 7, 8 or 10**.
That is why the two chapters are handled by different mappings in `PASSAGES`.

## Faults, each learned by getting it wrong here

1. **`after` is the divider, and empty means the next word is written onto this
   one.** The ETCBC splits a prefixed particle and an Aramaic emphatic ending
   into words of their own. Forcing a space shipped Jer 10:11 as
   `כ דנה תאמרון להום אלהי א די שמי א ו ארק א לא עבדו`, and the author caught it
   on the live page. Append `w["after"]`, never `w["after"] or " "`. The sibling
   repository never had this; it was copied wrong into this one.
2. **A difflib `equal` block must be indexed word for word, and a `replace`
   block is not evidence.** Taking a whole opcode block gave `43:9 אשׁר` as
   restored when it is extant, and `43:10 עבדי` as *carried on extant text* when
   the only scroll word aligned there was the verse divider. `verdict()` maps
   `b1 + (i − a1)` inside an `equal` block and returns `unaligned` for anything
   else.
3. **The transcription carries the verse divider as a word of its own**, where
   BHSA puts it in the trailer. Left in the alignment it answers to nothing and
   becomes a false witness — it was the "extant" in fault 2. `evidence()` drops
   it, and every claim is computed on that view.
4. **A one-letter plus is not usable evidence.** Stipp's list for these
   chapters is full of ו, ם, ל, ך, and each would have entered the table as a
   finding. `len(bare(ph)) < 2` filters them; two letters are kept, which is
   what keeps 43:7 עד in.
5. **Quote graphical units, not ETCBC words.** A join printed `אחיקם | ו` and
   `פתח | ב`, where the reader needs `אחיקם | ואת` and `בפתח | בתחפנחס`.
   `unit()` walks out to the divider on both sides.
6. **A quoted unit may itself contain restored letters.** Blue means extant on
   this page, so they are set grey and bracketed inside it: 43:7 shows
   `[ו]י̇באו̇`, where only יבאו is extant. Do not let a colour claim more than
   the data.
7. **Stipp's Greek panel cannot be read across a transposition.** See below.
8. **A single letter is not an anchor.** The ETCBC writes a prefixed particle as
   a word, and difflib will match a lone bet anywhere: at 4Q70 14:4 it paired the
   bet of the manuscript's בארץ with the bet of the Masoretic בעבור ten words
   earlier and reported the ten words between as excluded. `ink_joins()` now
   requires both anchors **and** the gap to be two letters or more. It removed
   three of the four joins the Masoretic-type manuscripts had and none of
   4QJerᵈ's, so it narrows the claim rather than widening it. Found by running
   the control, not by reading the page.
9. **The Pages workflow fails on the first push**, at `actions/configure-pages`,
   because Pages is not yet enabled. Enable it (`build_type: workflow`), then
   re-run. Not a fault in the workflow.

## Stipp's Synopse: what it can carry, and what it cannot

**Not the Greek.** The panel is aligned colon by colon and would be the natural
text to set. Checked against Rahlfs verse by verse over both passages it agrees
on **32 of 34**. The exceptions are **10:5 and 10:9, which carry each other's
Greek** — 0.29 against their own verse, 0.99 against the other's. That is
exactly where the two editions are transposed, and it is the fault of reading
the panel and not of the edition: Stipp marks the transposition with his star
and a margin cross-reference. But a Greek panel laid out against a Hebrew column
running in Masoretic order cannot show the Greek's own order, and that order is
what the page's first section is about. **The Greek is Rahlfs.** `greek_check()`
recomputes this on every run; if it ever reports more than these two, look
before trusting the page.

**Yes to three other things**, and only the Synopse has them:

- which Masoretic words the Old Greek lacks (`cls == "plus"`), the basis of the
  whole agreement table;
- the verses whose alexandrian column Stipp leaves **empty altogether** —
  **10:6, 10:7, 10:8, 10:10** — his own statement that the Old Greek has nothing
  answering to them. The page had been inferring this from Rahlfs having no such
  verse numbers; it now has two independent witnesses;
- **his apparatus names 4Q71 at 10:4, 10:5, 10:6, 10:10, 10:11 and 10:15.** He
  read this manuscript, and at the two verses that matter most.

**Do not quote the wording of a marginal note.** `parse_synopse.py` takes the
margin apart into spans, so the siglum and the place are reliable while the
wording around them need not be whole — `; 6–8  4Q71` is a fragment of a longer
note, and fault (17) of the parent project shows what happens when a `>` is read
out of such a span. Nothing on the page rests on a note's wording.

## Vocabulary

**Reader-facing prose is text criticism, not archaeology.** Write **extant**,
**restored** / **restoration**, **lacuna**, **the manuscript**. Do **not** write
*leather*, *hole*, or *ink on leather* — all three were on the published page
until 2026-09-10 and were corrected on the author's instruction. Internal
identifiers and CSS token names are not what a reader meets and need not be
renamed; `--leather`, `ink`, `ink_joins` and `carries-ink` survive on purpose.

## What must never be "fixed"

- **The verse order of 4QJerᵇ is not evidence, and the page must keep saying
  so.** It reads well and it is almost certainly right; it is still restoration.
- **The two counter-cases at 43:9 stay on the page.** They are what makes the
  rest of it believable.
- **The apparatus wording stays unquoted.** See above.
- **Rahlfs stays the Greek** unless `greek_check()` says the panel is sound at
  10:5 and 10:9, which would mean the parent project's `_place_greek()` had
  learned to see a transposition.

## Open

- The transposition itself is untested. Stipp's star marks it and Rahlfs prints
  it, but nothing here measures whether 10:5b fits where the editor puts it
  better than 10:10 does. The two lengths are within a few letters, which is why
  the page declines to decide; a proper test would need the column width from
  DJD XV rather than the fragment's own mean.
- **Done 2026-09-10: the control, `src/control.py`.** See the table above. Two
  things to keep in mind about it. The short-edition side rests on **4 decidable
  cases**, all of them in 4QJerᵈ — 4QJerᵇ contributes none, having no join in
  the book — so the p value is carried by a very small numerator against a large
  clean denominator. And "decidable" counts only a plus with extant text on both
  sides: 42 of several hundred. The four are more extant in absolute terms, but
  most of the pluses in the verses they reach fall in lacunae.
- The apparatus notes are read but only counted. Parsing them properly would
  need `parse_synopse.py` to keep a margin note whole, which is a change in the
  parent project and not here.
- No test suite. The sibling `mt_greek_jeremiah` has 70; this has the figures
  `collate.py` prints, and a change that moves one of them is silent.
