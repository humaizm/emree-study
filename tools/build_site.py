"""Build the static site from the question bank. The single source of truth.

Usage:
    python tools/build_site.py          # validate bank + regenerate index.html
    python tools/build_site.py --check  # validate + fail if index.html differs (used by CI)

Design rules (durability):
  - bank/*.json + bank/manifest.json are the ONLY content inputs.
  - index.html regions derived from the bank are replaced deterministically;
    everything else (CSS, JS, deck shell, colophon prose) is copied byte-for-byte.
  - Running the build twice in a row must produce zero diff (idempotent).
"""
from pathlib import Path
import html as htmlmod
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "bank"
INDEX = ROOT / "index.html"

SHORT = {"IM": "IM", "OB": "OBG", "PD": "Peds", "SG": "Surgery",
         "FM": "Family+Ethics", "PS": "Psych", "PH": "Public Health"}
BANNED = ["carbamazepine? No", "Placeholder", "CENTOR-like",
          "Avoid rectal invasive", "smoking protects so recommend",
          "(autonomy not listed", "hemiarthroplasty/DHS", "Normal recent EF",
          "macular oedema? Refer"]


def esc(s: str) -> str:
    return htmlmod.escape(s, quote=True)


def load_bank():
    manifest = json.loads((BANK / "manifest.json").read_text(encoding="utf-8"))
    subjects = []
    total = 0
    for s in manifest["subjects"]:
        items = json.loads((ROOT / s["file"]).read_text(encoding="utf-8"))
        assert isinstance(items, list) and items, s["code"]
        seen = set()
        for i, q in enumerate(items, start=1):
            assert set(q) == {"id", "subject", "stem", "options", "answer", "explanation"}, (s["code"], i)
            assert q["subject"] == s["code"], (s["code"], i)
            assert q["id"] == f"{s['qprefix']}-{i:02d}", (s["code"], i)  # sequential, no gaps
            assert q["id"] not in seen, q["id"]
            seen.add(q["id"])
            assert isinstance(q["options"], list) and len(q["options"]) == 5, (q["id"],)
            assert q["answer"] in "ABCDE", (q["id"],)
            assert q["options"][ord(q["answer"]) - 65].startswith(q["answer"] + "."), (q["id"],)
            assert q["stem"].strip() and q["explanation"].strip(), (q["id"],)
            blob = q["stem"] + " " + " ".join(q["options"]) + " " + q["explanation"]
            for bad in BANNED:
                assert bad not in blob, (q["id"], bad)
        assert len(items) == s["count"], (s["code"], len(items), s["count"])
        subjects.append((s, items))
        total += len(items)
    assert total == manifest["total"], (total, manifest["total"])
    return manifest, subjects, total


def render_rail(subjects):
    out = []
    for s, items in subjects:
        out.append(
            f'<a class="rail-sub" href="#sec-{s["code"]}" data-goto="{s["code"]}">'
            f'<span class="rail-sub-name"><span class="rail-code">{s["code"]}</span>{esc(s["title"])}</span>'
            f'<span class="rail-sub-meta"><span id="railcount-{s["code"]}">0/{len(items)}</span>'
            f'<span class="dots" id="dots-{s["code"]}"></span></span></a>')
    return "".join(out)


def render_toc(subjects):
    links = " · ".join(f'<a href="#sec-{s["code"]}">{esc(s["title"])}</a>' for s, _ in subjects)
    return f"<p>Contents — {links}.</p>"


def render_item(code, qid, stem, opts, ans, expl):
    parts = []
    for o in opts:
        letter = o.strip()[0]
        otext = o[2:].strip() if len(o) > 2 and o[1] == "." else o
        parts.append(
            f'<label class="choice" data-letter="{esc(letter)}">'
            f'<input type="radio" name="{esc(qid)}" value="{esc(letter)}">'
            f'<span class="choice-key" aria-hidden="true">{esc(letter)}</span>'
            f'<span class="choice-txt">{esc(otext)}</span>'
            f'<span class="choice-mark" aria-hidden="true"></span></label>')
    blob = esc((stem + " " + " ".join(opts)).lower())
    return (
        f'<div class="item" id="q-{esc(qid)}" data-code="{esc(code)}" data-answer="{esc(ans)}" '
        f'data-text="{blob}" role="group" aria-labelledby="st-q-{esc(qid)}">'
        f'<div class="item-top"><span class="item-id">{esc(qid)}</span>'
        f'<span class="item-status" aria-live="polite">Unanswered</span>'
        f'<button type="button" class="flag" aria-pressed="false" title="Flag for review">Flag</button></div>'
        f'<p class="stem" id="st-q-{esc(qid)}">{esc(stem)}</p>'
        f'<div class="choices">{"".join(parts)}</div>'
        f'<p class="verdict" hidden></p>'
        f'<div class="teach" hidden><span class="teach-label">Teaching point</span>'
        f'<p><strong>Answer: {esc(ans)}.</strong> {esc(expl)}</p></div>'
        f'<div class="item-foot"><button type="button" class="tlink reveal-one">Show answer</button>'
        f'<button type="button" class="tlink clear-one">Clear</button></div>'
        f'</div>')


def render_chapters(subjects):
    out = []
    for s, items in subjects:
        rows = "".join(render_item(s["code"], q["id"], q["stem"], q["options"], q["answer"], q["explanation"])
                        for q in items)
        out.append(
            f'<section class="chapter" id="sec-{s["code"]}" data-code="{s["code"]}">'
            f'<div class="chap-head"><h2>{esc(s["title"])}</h2>'
            f'<p>{len(items)} questions · {s["weight_pct"]}% of the paper · {esc(s["blurb"])}</p>'
            f'<p class="chap-score"><span id="score-{s["code"]}">0 / {len(items)}</span> '
            f'<span class="score-word">correct</span></p></div>'
            f'<div class="items">{rows}</div></section>')
    return "".join(out)


def sub_once(t, old, new, label):
    assert t.count(old) == 1, f"anchor not unique/found: {label}"
    return t.replace(old, new, 1)


def build(manifest, subjects, total):
    t = INDEX.read_text(encoding="utf-8")

    # 1. rail nav
    a = t.index('<nav aria-label="Subjects">') + len('<nav aria-label="Subjects">')
    b = t.index('</nav>', a)
    t = t[:a] + render_rail(subjects) + t[b:]

    # 2. contents paragraph
    a = t.index('<p>Contents — ')
    b = t.index('</p>', a) + len('</p>')
    t = t[:a] + render_toc(subjects) + t[b:]

    # 3. chapters through </main>
    a = t.index('<section class="chapter"')
    b = t.index('</main>', a)
    t = t[:a] + render_chapters(subjects) + "\n" + t[b:]

    # 4. global counts
    t = sub_once(t, "<title>EMREE Study Ledger — 120 Questions by Subject</title>",
                 f"<title>EMREE Study Ledger — {total} Questions by Subject</title>", "title")
    t = sub_once(t, f"· {120} questions · {7} subjects ·",
                 f"· {total} questions · {len(subjects)} subjects ·", "issue")
    t = sub_once(t, '<div class="stat"><b>120</b><span>single-best-answer vignettes</span></div>',
                 f'<div class="stat"><b>{total}</b><span>single-best-answer vignettes</span></div>', "stat-n")
    t = sub_once(t, '<div class="stat"><b>7</b><span>blueprint subjects, weakest first</span></div>',
                 f'<div class="stat"><b>{len(subjects)}</b><span>blueprint subjects, weakest first</span></div>', "stat-s")
    t = sub_once(t, '<div class="score-big"><span id="big">0 / 120</span></div>',
                 f'<div class="score-big"><span id="big">0 / {total}</span></div>', "big")
    t = sub_once(t, 'aria-valuemax="120"', f'aria-valuemax="{total}"', "meter")
    breakdown = " · ".join(f'{SHORT[s["code"]]} {len(items)}' for s, items in subjects)
    t = sub_once(t, "120 original vignettes: IM 24 · OBG 18 · Peds 18 · Surgery 18 · Family+Ethics 18 · Psych 12 · Public Health 12",
                 f"{total} original vignettes: {breakdown}", "colophon-counts")
    t = sub_once(t, "CBT 120 in 3 h", f"CBT {total} in 3 h", "colophon-cbt")
    return t


def main():
    manifest, subjects, total = load_bank()
    print(f"bank OK: {total} questions across {len(subjects)} subjects")
    new = build(manifest, subjects, total)
    old = INDEX.read_text(encoding="utf-8")
    if "--check" in sys.argv:
        if new != old:
            import difflib
            diff = list(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm=""))
            print(f"DRIFT: index.html differs from bank in {len(diff)} diff lines (showing first 20):")
            print("\n".join(diff[:20]))
            sys.exit(1)
        print("check OK: index.html matches bank")
    else:
        INDEX.write_text(new, encoding="utf-8")
        print("index.html rebuilt from bank")


if __name__ == "__main__":
    main()
