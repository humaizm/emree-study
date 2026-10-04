# EMREE Study Ledger — 120 Questions by Subject

**Live:** https://humaizm.github.io/emree-study-ledger/
**Companion PDF:** https://humaizm.github.io/emree-study-ledger/EMREE_Past_Papers_by_Subject_Oct2026.pdf

Interactive EMREE practice: 120 single-best-answer vignettes across the 7 NIHS
blueprint subjects, with instant marking, exam-hold mode, 3-hour timer, search,
flags, keyboard answering, and progress that persists in the browser.

> **Honest note.** NIHS publishes no official past papers. Every item here is an
> original practice question written from 2012–2025 student recall *patterns* —
> not leaked exam material. See `EMREE_Past_Papers_by_Subject_Oct2026.pdf`
> for the full intelligence file (exam facts, recall-source map, study plan).

## How this stays alive with zero maintenance

There is no backend server and no database. The architecture is deliberately boring:

```text
bank/*.json  →  tools/build_site.py  →  index.html  →  GitHub Pages (free CDN)
```

- **`bank/`** — the question bank and the only content source of truth.
  Versioned, reviewable, fetchable as raw JSON. Documented in `bank/README.md`.
- **`tools/build_site.py`** — validates the bank (schema, sequential ids,
  answer-letter alignment, banned artifacts) and renders `index.html`.
  Deterministic and idempotent: same bank, same bytes.
- **`.github/workflows/validate.yml`** — runs the validator on every push.
  The site and the bank cannot drift apart silently.
- **Releases** — frozen snapshots (`v1.0-audited`, `v1.1-fixed`, …) so any
  version stays downloadable forever.

Adding questions: edit a subject JSON, bump `bank/manifest.json`, run
`python tools/build_site.py`, push. CI does the worrying.

## Project layout

```text
index.html                                # the site (generated — don't hand-edit)
EMREE_Past_Papers_by_Subject_Oct2026.pdf  # companion intelligence file
bank/                                     # question bank backend
tools/build_site.py                       # validator + site builder
.github/workflows/validate.yml            # drift guard
LICENSE                                   # MIT
```
