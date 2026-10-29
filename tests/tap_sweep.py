"""Strict 44x44 tap sweep on every route at 320/375/412/1280. Links inside running text are exempt (WCAG 2.5.8 inline);
standalone links, buttons, inputs and summaries are not. python3 tests/tap_sweep.py http://127.0.0.1:8933/"""
import sys, re, json, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[1]
TAP_JS = re.search(r'TAP_JS = """(.*?)"""', (ROOT / "qa.py").read_text(), re.S).group(1).replace("\\\\", "\\")
SITE = ROOT / "docs"; B = sys.argv[1].rstrip("/") + "/"
routes = sorted(("" if p.parent == SITE else str(p.parent.relative_to(SITE)) + "/") for p in SITE.rglob("index.html"))
bad = {}
with sync_playwright() as p:
    try: b = p.chromium.launch()
    except Exception: b = p.chromium.launch(channel="chrome")
    for w, h in [(320, 640), (375, 812), (412, 915), (1280, 800)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        for r in routes:
            pg.goto(B + r, wait_until="domcontentloaded"); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
            t = pg.evaluate(TAP_JS)
            if t: bad[f"{w} {r or 'home'}"] = t[:5]
        pg.close()
    b.close()
print(json.dumps({"routes": len(routes), "widths": 4, "failing": len(bad)})); [print(k, v) for k, v in list(bad.items())[:30]]
sys.exit(1 if bad else 0)
