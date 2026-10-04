# AGENTS.md — working on emree-study

> If you are an agent (or human) picking this project up cold, read this file
> first. It contains every decision, command, and trap. The user-facing
> overview lives in `README.md`; this file is the workshop manual.

## 1. What this is

Interactive EMREE medical-exam practice site. 120 single-best-answer vignettes
across 7 blueprint subjects, with instant marking, an exam-hold mode, a 3-hour
timer, search/filters/flags, keyboard answering, and localStorage persistence.

- **Live:** https://humaizm.github.io/emree-study/ (GitHub Pages, free CDN + HTTPS)
- **Repo:** https://github.com/humaizm/emree-study (public; this is the project home)
- **Releases:** three-part `0.x.y` only (currently `v0.21.0`). Old 1.x/2.x releases
  were deleted on purpose. Cut new ones with `gh release create v0.xx.y ...`.

## 2. Architecture (deliberately boring = durable)

```text
bank/*.json  →  tools/build_site.py  →  index.html  →  GitHub Pages
```

There is **no backend server and no database**. Do not propose adding one —
that was considered and rejected (hosting fees, patching, something to die).

| Path | Role | Edit rules |
|---|---|---|
| `bank/*.json` + `bank/manifest.json` | **Content source of truth.** 7 subject files, one manifest. | Edit freely; keep schema + rules in `bank/README.md`. |
| `tools/build_site.py` | Validator + renderer. Checks schema, sequential ids, answer-letter alignment, banned artifacts; rebuilds bank-derived regions of `index.html`. Deterministic + idempotent. | Extend validation here, not ad hoc. |
| `index.html` | The site. Bank-derived regions (rail nav, contents, chapters, global counts) are **generated**; everything else (CSS, JS, deck shell, colophon prose) is hand-maintained template copied verbatim by the builder. | Small copy/design edits directly are safe and survive rebuilds. Never hand-edit a question stem/option/answer — change the bank and rebuild. |
| `site-config.js` | Optional Firebase config (`null` = fully offline app). Public by design when filled. | Never put secrets here — none are needed. The app must behave identically with it null. |
| `firestore.rules` | Security contract for the optional sync backend. | Client payload schema must match these rules exactly (keys, types, server timestamp). |
| `docs/SYNC.md` | 5-minute Firebase setup recipe + cost/abuse notes. | Keep quota numbers truthful; update if Firebase terms change. |
| `EMREE_Past_Papers_by_Subject_Oct2026.pdf` | Companion intelligence file (exam facts, recall map). Built once from a local script; treated as a static asset here. | Don't rebuild casually; content is frozen. |
| `.github/workflows/validate.yml` | CI: runs `build_site.py --check` on every push. Page and bank cannot drift. | Don't weaken it. |
| `bank/README.md`, `README.md`, `LICENSE` | Docs. `bank/README.md` also documents the raw/jsDelivr JSON URLs (the free "API"). | Keep in sync when structure changes. |

## 3. Commands

```bash
python tools/build_site.py          # validate bank + regenerate index.html
python tools/build_site.py --check  # validate + fail if index.html differs (CI)
git push origin main                # deploys; Pages rebuilds in ~60–90s
gh api repos/humaizm/emree-study/pages/builds/latest --jq .status   # expect "built"
gh release create v0.xx.y index.html EMREE_Past_Papers_by_Subject_Oct2026.pdf --repo humaizm/emree-study --title "v0.xx.y" --notes "..."
```

Verify a deploy in a real browser (Playwright MCP): navigate to
`https://humaizm.github.io/emree-study/?v=<unique>`, snapshot for refs, click /
type / evaluate. Check console messages — **zero errors is the bar**
(the only historical blip was a favicon 404, fixed with an inline data-URI icon).

## 4. Content rules (from the medical audit — non-negotiable)

- **Original practice items only.** Never paste real exam questions. Everything is
  written from recall *patterns*. NIHS publishes no official past papers; the
  site and PDF both say so openly.
- **British spelling** throughout: oedema, anaemia, behaviour, counselling,
  optimise, oestrogen, fibre, glycaemic. The builder has no spell gate — you are it.
- Every answer letter is machine-checked against its option prefix. If you touch
  options, run the builder.
- Keep distractors plausible and explanations to one teaching point.
- Question ids are `{PREFIX}-{NN}` sequential from 01 (`IM-`, `OB-`, `PD-`,
  `SG-`, `FM-`, `PS-`, `PH-`). Stem anchors `st-q-{ID}` and localStorage state
  keyed by question id must stay stable — renumbering orphans saved progress.

## 5. UX contract (don't regress these)

- **Practice mode:** answering marks instantly (green/red + teaching point).
- **Exam mode:** answering records neutrally ("Answered — held for grading");
  scores/dots/labels count *answered*, never correct. Feedback returns on
  switching to Practice or Show all. Never leak the letter in exam mode.
- **Reset** always warns first (modal with counts; Esc/backdrop cancels, focus
  starts on Cancel). It clears answers, flags, search, filter, and timer.
- **Progress safety:** auto-save indicator in the deck; Export downloads
  `emree-progress-*.json`; Import validates then asks before overwriting;
  Copy-link encodes all answers+flags in the URL hash (`v1…~…`, tilde separator
  — a `.` separator was tried and collides with the unanswered marker).
  Shared links auto-apply on empty devices, ask otherwise, then strip the hash.
- **Timer** persists across reloads (paused, never auto-resumes — deliberate).
- **Online sync (optional):** offline-first; local is primary, Firestore is the
  roaming copy; newest timestamp wins; debounced pushes; device keys link
  devices. With no config, the sync UI shows local-only and no SDK loads.
- **Hide all** hides every teaching point, including answered ones.
- **Keyboard** `1–5`/`A–E` answers the *nearest displayed* question and scrolls
  it into view; `/` focuses search. Must work at page top (dead zone there was
  a real shipped bug).
- **Print** reveals all teaching points, hides chrome and status pills.
- Reduced-motion users get instant scroll; 375px viewport must not overflow
  horizontally (`overflow-x: clip` + `minmax(0,1fr)` grids).
- Design tokens: every color/font references `var(--…)` — no inline hex/OKLCH,
  no extra font families (Fraunces display, Plex Sans body, JetBrains Mono
  readouts only). No emojis in UI. No italic headers.

## 6. Standing decisions (don't relitigate without asking)

- **No custom domain.** A domain is rented, never owned — yearly fees and renewal
  risk are the opposite of durable, and nothing here is free-er than github.io.
  The user explicitly accepted this after the tradeoff was stated.
- **Repo name stays `emree-study`.** Renaming breaks the shared Pages URL (old
  one 404s — verified). Visible branding ("EMREE Question Bank") is independent
  of the repo slug.
- **localStorage keys stay.** `emree-ledger-v2` (progress), `emree-sync-pid`
  (device key), `emree-local-ts` (last-write clock for sync merge). Renaming any
  of them wipes or strands users' data.
- **Release style is `0.x.y` only**, one release at a time if the user says so.
  Retag procedure: `gh release delete <tag> --repo humaizm/emree-study --yes
  --cleanup-tag`, then create the new one on the same commit.
- Version in `bank/manifest.json` tracks releases.

## 7. Traps that already bit (read before scripting)

- **Windows PowerShell quoting:** never `python -c` with nested quotes — write a
  `.py` file in the Temp dir and run it. Same for any inline JSON.
- **Console mojibake:** PowerShell renders some Unicode (— · ≥) as `�`.
  The bytes are fine. When diffing, compare with `backslashreplace` or
  codepoints — never trust glyph rendering, and never "fix" a `�` you only saw
  in terminal output.
- **`git show` decoding:** use raw bytes + explicit `.decode("utf-8")`, never
  `text=True` (locale is cp1252 and will fake-corrupt the comparison).
- **Diffing this HTML:** chapters are giant single lines — line diffs are useless.
  Compare semantically (parse questions/regions) or byte-compare; the builder's
  `--check` already does the latter.
- **The `write` tool and non-ASCII:** literals like `—`/`·` occasionally arrive
  mangled in generated scripts. Prefer `\u2014`-style escapes inside scripts
  you generate, and verify codepoints after writing.
- **Temp-dir scripts are scratch:** builders/checkers live in
  `C:\Users\humai\AppData\Local\Temp\opencode\` and must be deleted when done.
  Only `tools/` in the repo is permanent.
- **Browser-test hygiene:** bust cache with a fresh `?v=` per deploy; note that
  localStorage (mode, answers, flags) persists across your test sessions on the
  same origin — Reset first or you will misread results. Pages needs ~60–90s
  after push before testing; poll the builds API.
- **Playwright MCP refs** expire on re-render; re-snapshot before clicking after
  any state change. `browser_evaluate` is best for assertions (counts, text).

## 8. History in one paragraph

Built Oct 2026: research → PDF intelligence file → 120 original vignettes →
full medical audit (caught a wrong answer letter, a drafting artifact, a
coverage gap, ~20 wording fixes) → Hallmark redesign (Feature Stack: sticky
study deck + ledger) → live browser bug-hunt (10 fixes incl. exam-mode leak,
reset/filter, keyboard dead zone) → JSON bank backend + builder + CI →
renamed Study Ledger → Question Bank → repo renamed to `emree-study`.
Releases hold frozen snapshots; git history holds the blow-by-blow.
