[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

# The short edition of Jeremiah at Qumran

Jeremiah comes down in two editions. The Masoretic Text is about an eighth
longer than the text the Greek translator worked from, and in places it puts
the material in another order. Of the six Jeremiah scrolls from the Judaean
Desert, four go with the Masoretic Text. **Two do not.**

This is a single page setting those two — **4QJerᵇ** (4Q71, Jeremiah 10) and
**4QJerᵈ** (4Q72a, Jeremiah 43) — against the Masoretic Text and the Greek.

https://martijnnaaijer.github.io/mt_dss_jeremiah

## The point of it

Only 10% of 4QJerᵇ and 45% of 4QJerᵈ is extant; the rest of what a
transcription prints is a modern editor's restoration, and a restoration
supplied from the Masoretic Text cannot then be evidence against it. The page keeps three
things apart throughout, and says of every claim which of them it rests on:

- **extant** — letters preserved in the manuscript
- **restored** — letters an editor supplied within a lacuna
- **extent** — what follows from the size of the lacuna, and from neither of the above

The two scrolls turn out to carry evidence of two different kinds, and the page
is built around that rather than around a single claim.

### 4QJerᵇ: the argument is extent

Its extant text is 114 letters in 15 discrete runs, none of them contiguous,
so no two of its words stand side by side in the manuscript. Nothing about the
arrangement of Jeremiah 10 can be read off it directly.

What can be measured is this. What survives falls near the end of each line,
which fixes where particular words stood. Line 5 ends with `הב ייפהו במקבות`, from
10:4; line 6 ends with `תכלת וארגמן`, from 10:9. They are consecutive lines of
one fragment, so whatever stood between those two words took up a single line —
about 96 letters, on this fragment's own average.

| | letters |
| --- | ---: |
| the space there | about 96 |
| 10:4 running straight on to 10:9 | 49 |
| the Masoretic Text, with 10:5–8 in between | **238** |

The Masoretic arrangement asks for two and a half lines of writing in the space
of one. That settles that verses 5 to 8 as the Masoretic Text has them were not
there. It does not by itself settle the order of what was, and the page says so.

### 4QJerᵈ: the argument is the extant text

Two adjacent words that are both extant are a **join**, and a join is
testimony: whatever the Masoretic Text has between them did not stand in this
copy. It is the only kind of omission a manuscript can attest. There are
five such places in Jeremiah 43, and they do not all point the same way.

| | the Masoretic Text has | the scroll | |
| --- | --- | --- | --- |
| 43:6 | רב טבחים | lacks it | with the Greek |
| 43:6 | בן שׁפן | lacks it | with the Greek |
| 43:7 | עד | lacks it | with the Greek |
| 43:9 | בית פרעה | lacks it | shorter than both |
| 43:9 | אשׁר | carries it | with the Masoretic Text |

Three of the five go with the Greek, one with the Masoretic Text, and one with
neither. 4QJerᵈ is close to the text behind the Greek without being a copy of
it, and the page reports that rather than rounding it off.

### The control

Three omissions in one manuscript is three data points. The other four Jeremiah
manuscripts from the Judaean Desert are of the Masoretic type, so they are the
null: if the join test reads the shape of a text rather than the shape of the
damage, they should *carry* the pluses that 4QJerᵈ omits. `src/control.py` runs
the same two functions over all 52 chapters.

| | decidable pluses | carries | omits |
| --- | ---: | ---: | ---: |
| 4QJerᵈ (4Q72a) | 4 | 1 | **3** |
| 4QJerᵇ (4Q71) | 0 | 0 | 0 |
| 4QJerᶜ (4Q72) | 21 | 21 | 0 |
| 4QJerᵃ (4Q70) | 17 | 17 | 0 |
| 2QJer (2Q13) | 3 | 3 | 0 |
| 4QJerᵉ (4Q72b) | 1 | 1 | 0 |

Not one of the 42 bracketed pluses the Masoretic-type four could answer for is
missing from them, against 3 of 4 in the short-edition pair. Fisher's exact test
gives **p = 0.00026**.

It is a null and not silence: in the whole book those four produce **one** join,
4QJerᶜ at 21:7, omitting ומן־הרעב — which Stipp does not bracket, so the Greek
has it. Their own accident, most likely an eye slipping from one מן to the next.
The test does find omissions there. It never finds one over a Masoretic plus.

## Sources & credits

- **Masoretic Text:** the ETCBC [BHSA](https://github.com/ETCBC/bhsa) dataset,
  version 2021.
- **Judaean Desert manuscripts:** the ETCBC [dss](https://github.com/ETCBC/dss)
  dataset, version 2.0 (Martin Abegg's transcription), in which every sign
  carries a flag saying whether it is extant or restored.
- **Greek:** Rahlfs 1935, from the
  [LXX](https://github.com/eliranwong/LXX-Rahlfs-1935) dataset. Greek Jeremiah
  runs on its own versification: Greek 50 is Masoretic 43, while in chapter 10
  the numbers agree and it is the verses themselves that differ.

  Not the Synopse's own Greek panel, though it is aligned sentence by sentence and
  would be the natural text to set. Checked against Rahlfs verse by verse over
  both passages it agrees on 32 of 34; the two exceptions are 10:5 and 10:9,
  which carry each other's Greek. That is where the two editions are
  transposed, and it is the fault of reading the panel rather than of the
  edition — Stipp marks the transposition with his star and a margin
  reference. But a Greek panel laid out against a Hebrew column in Masoretic
  order cannot show the Greek's own order, and that order is what the first
  section of the page is about.
- For **which Masoretic words are absent from the Greek**, the page follows
  Hermann-Josef Stipp, *Textkritische Synopse zum Jeremiabuch*, 15. korrigierte
  interne Auflage (2021), as parsed in the companion study. Every reading it is
  relied on for was checked against Rahlfs directly. Two further things come
  from it: the four verses of Jeremiah 10 whose alexandrian column Stipp leaves
  empty altogether (6, 7, 8, 10), which is his own statement that the Old Greek
  has nothing answering to them; and the places where his apparatus names 4Q71,
  among them 10:6 and 10:10. The parse takes his margin apart into spans, so
  the siglum and the place are reliable while the wording around them may not
  be whole, and nothing rests on the wording of a marginal note.
- All three corpora are read with [Context-Fabric](https://context-fabric.ai),
  the successor to [Text-Fabric](https://github.com/annotation/text-fabric).

Please consult and respect the licence and attribution terms of those datasets
before reusing this material.

## How it was made

`src/collate.py` is the measurement and writes no HTML; `src/build.py` turns
its output into `docs/index.html`. No figure or reading on the page is typed in
by hand. Run the measurement on its own to see the findings as a table:

```bash
pip install -r requirements.txt

git clone --depth 1 https://github.com/ETCBC/dss.git
git clone --depth 1 https://github.com/ETCBC/bhsa.git

python src/collate.py          # the evidence, as text
python src/control.py          # the null, as text
python src/build.py            # both, as the page
```

`BHSA_TF`, `DSS_TF` and `LXX_TF` override the corpus locations, which default
to the usual `~/text-fabric-data` cache. `SYNOPSE` points at the parsed Stipp
data; without it the page builds, and the column saying whether the Greek has a
reading is left empty.

## Companion

The whole Hebrew Bible verse by verse against the manuscripts that preserve it:
[mt_dss_hebrew_bible](https://github.com/MartijnNaaijer/mt_dss_hebrew_bible).

## Licence

The short edition of Jeremiah at Qumran © 2026 by Martijn Naaijer is licensed
under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). The full
legal code is in [LICENSE](LICENSE).

You may share and adapt this material for non-commercial purposes, giving
credit and indicating any changes.

That covers this repository's own work: `src/collate.py`, `src/build.py`, the
stylesheet, and the page they produce. It does not cover the text and
morphology those pages reproduce, which come from the ETCBC BHSA and dss
datasets and from Rahlfs, and carry the terms of those datasets. Check them
before reusing the material itself.
