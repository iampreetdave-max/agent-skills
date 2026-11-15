"""Check a built sheet: python verify.py sheet.html   (exits 1 on any problem)

Always, stdlib only: unclosed or stray tags; every <svg> has a viewBox and role="img"; every
url(#id) inside an SVG is defined in that same SVG (a missing marker silently drops arrowheads).

If Playwright is installed (pip install playwright && playwright install chromium) it also loads the
page in headless Chromium: JS errors, broken #anchors, duplicate ids, sidebar coverage, images that
fail or lack alt text, and SVG text clipped outside its viewBox or overlapping other text.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track",
        "wbr", "path", "circle", "rect", "line", "polyline", "polygon", "ellipse", "stop", "use"}
OPTIONAL_END = {"p", "li", "td", "th", "tr", "dt", "dd"}


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errs = [], []

    def handle_starttag(self, t, a):
        if t not in VOID:
            self.stack.append((t, self.getpos()[0]))

    def handle_startendtag(self, t, a):
        pass

    def handle_endtag(self, t):
        if t in VOID:
            return
        if self.stack and self.stack[-1][0] == t:
            self.stack.pop()
        elif any(s[0] == t for s in self.stack):
            while self.stack[-1][0] != t:
                o, ln = self.stack.pop()
                if o not in OPTIONAL_END:
                    self.errs.append(f"unclosed <{o}> from line {ln}")
            self.stack.pop()
        else:
            self.errs.append(f"stray </{t}> at line {self.getpos()[0]}")


def static(html):
    p = Tags()
    p.feed(html)
    errs = p.errs[:20]
    for i, svg in enumerate(re.findall(r"<svg\b.*?</svg>", html, re.S)):
        head = svg.split(">", 1)[0]
        ids = set(re.findall(r'\bid="([^"]+)"', svg))
        for ref in sorted(set(re.findall(r"url\(#([^)]+)\)", svg)) - ids):
            errs.append(f"svg #{i}: url(#{ref}) is not defined inside the same <svg>")
        if "viewBox" not in head:
            errs.append(f"svg #{i}: no viewBox")
        if 'role="img"' not in head:
            errs.append(f"svg #{i}: no role=\"img\"")
    return errs


PROBE = r"""() => {
  const out = {nav: document.querySelectorAll('#toc a').length,
               topics: document.querySelectorAll('.topic').length,
               broken: [], dups: [], clipped: [], overlap: [],
               badimg: [...document.images].filter(i => !i.naturalWidth).map(i => i.getAttribute('src')),
               noalt: [...document.images].filter(i => !i.alt).map(i => i.getAttribute('src'))};
  const seen = {};
  document.querySelectorAll('[id]').forEach(e => { if (seen[e.id]) out.dups.push(e.id); seen[e.id] = 1; });
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    const id = decodeURIComponent(a.getAttribute('href').slice(1));
    if (id && !document.getElementById(id)) out.broken.push(id);
  });
  document.querySelectorAll('svg[viewBox]').forEach((svg, i) => {
    const R = svg.getBoundingClientRect();
    if (R.width < 2) return;
    const lab = (svg.getAttribute('aria-label') || '#' + i).slice(0, 50);
    const texts = [...svg.querySelectorAll('text')];
    texts.forEach(t => {
      const r = t.getBoundingClientRect();
      if (r.width && (r.left < R.left - 2 || r.right > R.right + 2 || r.top < R.top - 2 || r.bottom > R.bottom + 2))
        out.clipped.push(lab + ' :: ' + t.textContent.slice(0, 40));
    });
    for (let a = 0; a < texts.length; a++) for (let b = a + 1; b < texts.length; b++) {
      const p = texts[a].getBoundingClientRect(), q = texts[b].getBoundingClientRect();
      const ix = Math.min(p.right, q.right) - Math.max(p.left, q.left);
      const iy = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top);
      if (ix > 3 && iy > 3) out.overlap.push(lab + ' :: "' + texts[a].textContent.slice(0, 25) + '" x "' + texts[b].textContent.slice(0, 25) + '"');
    }
  });
  return out;
}"""


def browser(path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, []
    js = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1400, "height": 900})
        pg.on("pageerror", lambda e: js.append(str(e)))
        pg.goto(path.resolve().as_uri())
        pg.evaluate("document.querySelectorAll('img[loading]').forEach(i => i.loading = 'eager')")
        pg.wait_for_load_state("load")
        pg.wait_for_timeout(800)
        r = pg.evaluate(PROBE)
        b.close()
    errs = ["JS error: " + e for e in js]
    errs += ["broken anchor #" + x for x in r["broken"]]
    errs += ["duplicate id " + x for x in r["dups"]]
    errs += ["clipped text: " + x for x in r["clipped"]]
    errs += ["overlapping text: " + x for x in r["overlap"]]
    errs += ["image failed to load: " + str(x) for x in r["badimg"]]
    errs += ["image without alt text: " + str(x) for x in r["noalt"]]
    if r["nav"] < r["topics"]:
        errs.append(f"sidebar has {r['nav']} links for {r['topics']} topics")
    return r, errs


def main(path):
    path = Path(path)
    html = path.read_text(encoding="utf-8")
    errs = static(html)
    r, more = browser(path)
    errs += more
    layout = f"{r['topics']} topics, {r['nav']} sidebar links" if r else "layout NOT checked (playwright not installed)"
    print(f"{path.name}: {html.count('<svg')} svgs, {layout}, {len(errs)} problems")
    for e in errs:
        print("  -", e)
    return 1 if errs else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1]))
