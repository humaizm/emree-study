# Question bank — the backend

This folder **is** the backend. There is no server, no database, no API process
to maintain. Content lives here as versioned JSON; `tools/build_site.py`
renders it into `index.html`; GitHub Pages serves the result worldwide for free.

## Layout

```text
bank/
  manifest.json   # subjects, counts, weights, version — the index
  im.json         # Internal Medicine & Emergency (IM-01 …)
  ob.json         # Obstetrics & Gynaecology    (OB-01 …)
  pd.json         # Paediatrics                 (PD-01 …)
  sg.json         # Surgery, Ortho & Trauma     (SG-01 …)
  fm.json         # Family Medicine, Ethics     (FM-01 …)
  ps.json         # Psychiatry                  (PS-01 …)
  ph.json         # Public Health & Biostats    (PH-01 …)
```

## Question schema

```json
{
  "id": "IM-04",
  "subject": "IM",
  "stem": "Man develops an itchy, well-demarcated scaly rash …?",
  "options": ["A. Cellulitis", "B. Allergic contact dermatitis (nickel)", "C. Psoriasis", "D. Tinea corporis", "E. Scabies"],
  "answer": "B",
  "explanation": "Recall: rash limited to the contact site …"
}
```

Rules enforced by `tools/build_site.py` (and by CI on every push):

- `id` must be `{PREFIX}-{NN}` with NN sequential from 01 — no gaps, no duplicates.
- Exactly 5 options, prefixed `A. ` through `E. ` in order.
- `answer` must be one of A–E **and** must match the letter of the correct option.
- No empty stems or explanations; no drafting artifacts (banned-phrase list in the builder).
- British spelling throughout (oesophagus-free zone: oedema, anaemia, behaviour, counselling, optimise).
- **Original practice items only.** Never paste real exam questions here. Everything in
  this bank is written from recall *patterns*, not reproduced from any paper.

## How to add questions

1. Append to the subject file with the next sequential id.
2. Bump `count` for the subject and `total` in `manifest.json`.
3. Run `python tools/build_site.py` and open `index.html` to eyeball it.
4. Commit and push. CI runs `build_site.py --check` — if the page and the bank
   ever disagree, the push fails loudly instead of shipping a broken quiz.

## Raw access (the free API)

Because the repo is public, every file is fetchable with zero backend:

- `https://raw.githubusercontent.com/humaizm/emree-study/main/bank/im.json`
- `https://cdn.jsdelivr.net/gh/humaizm/emree-study@main/bank/manifest.json`

## Provenance

Seeded October 2026 from the audited EMREE practice set (120 questions,
2012–2025 recall patterns). See the repo README for the honesty note:
NIHS publishes no official past papers; these are study items, not leaks.
