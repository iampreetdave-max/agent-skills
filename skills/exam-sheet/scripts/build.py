"""Build one exam sheet.

    python build.py <parts_dir> --title "Subject: Revision Sheet" [--short "Subject"] [--code 3174202] [-o out.html]

Every *.html file in parts_dir is a fragment (00-intro.html, 01-ch3.html, ...). They are joined in
sorted order inside shell.html, so one chapter per file and an interrupted run loses nothing finished.
"""
import argparse
from html import escape
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("parts")
ap.add_argument("--title", required=True)
ap.add_argument("--short", help="top-bar label (default: the title)")
ap.add_argument("--code", default="", help="subject code badge (optional)")
ap.add_argument("-o", "--out", help="default: sheet.html next to the parts folder")
a = ap.parse_args()

parts = sorted(Path(a.parts).glob("*.html"))
if not parts:
    raise SystemExit(f"no .html fragments in {a.parts}")

code = f'<span class="sub">{escape(a.code)}</span>' if a.code else ""
page = (Path(__file__).with_name("shell.html").read_text(encoding="utf-8")
        .replace("<!--TITLE-->", escape(a.title))
        .replace("<!--SHORT-->", escape(a.short or a.title))
        .replace('<span class="sub"><!--CODE--></span>', code)
        .replace("<!--BODY-->", "\n".join(p.read_text(encoding="utf-8") for p in parts)))

out = Path(a.out) if a.out else Path(a.parts).resolve().parent / "sheet.html"
out.write_text(page, encoding="utf-8")
print(f"{out}  ({len(parts)} parts, {len(page):,} bytes)")
