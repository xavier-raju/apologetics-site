#!/usr/bin/env python3
"""Headless QA: console errors, horizontal overflow, small tap targets at 360/375/412/1280px.
Usage: python qa.py http://127.0.0.1:8765/apologetics-site/   (needs playwright + chromium)"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
BASE = sys.argv[1].rstrip("/") + "/"
SITE = pathlib.Path(__file__).parent / "docs"
OUT = pathlib.Path(__file__).parent / "_qa"; OUT.mkdir(exist_ok=True)
routes = sorted(str(p.parent.relative_to(SITE)).replace(".", "") for p in SITE.rglob("index.html"))
routes = [r + "/" if r else "" for r in routes]
SIZES = [(320, 640), (360, 740), (375, 812), (412, 915), (1280, 800)]
TAP_JS = """() => [...document.querySelectorAll('a,button,input,[role=button],summary,[tabindex="0"]')].filter(e=>{
  const r=e.getBoundingClientRect(); if(!r.width||!r.height) return false;
  if(e.closest('.menu[hidden],[hidden]')) return false;
  if(e.tagName==='A'){ // inline exception (WCAG 2.5.8) only for links inside running text
    const blk=e.closest('p,li,td,figcaption,blockquote');
    if(blk && !e.matches('.points-to-jesus__more') && !blk.matches('.source-list li, .q-link')){const all=blk.textContent.replace(/\\s+/g,' ').trim().length;
      const lk=[...blk.querySelectorAll('a')].reduce((n,a)=>n+a.textContent.trim().length,0); if(all-lk>40 && (all-lk)/all>0.4) return false;}}
  return r.height<44 || r.width<44 }).map(e=>(e.className||e.tagName)+':'+e.textContent.trim().slice(0,30)+' '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height))"""
res = {"pages": len(routes), "errors": [], "overflow": [], "tap": {}}
with sync_playwright() as p:
    try: b = p.chromium.launch()
    except Exception: b = p.chromium.launch(channel="chrome")  # bundled Chromium missing: use system Chrome
    for w, h in SIZES:
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
        pg = ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        for r in routes:
            errs.clear()
            pg.goto(BASE + r, wait_until="networkidle")
            pg.wait_for_timeout(150)
            if r == "ask/":
                pg.fill("#ask-q", "did jesus exist"); pg.wait_for_timeout(400)
            ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            if ow > 0: res["overflow"].append(f"{w}px {r or 'home'} +{ow}px")
            for e in errs: res["errors"].append(f"{w}px {r or 'home'}: {e}")
            if w < 1000:
                t = pg.evaluate(TAP_JS)
                if t: res["tap"][f"{w} {r or 'home'}"] = t[:6]
        for r, name in [("", "home"), ("answers/", "answers"), ("prophecy/isaiah-53/", "prophecy-isaiah-53"), ("library/", "library"), ("map/", "map")]:
            pg.goto(BASE + r, wait_until="networkidle")
            pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-in'))"); pg.wait_for_timeout(900)
            if w in (375, 1280): pg.screenshot(path=str(OUT / f"{name}-{w}.png"), full_page=(name == "home"))
        ctx.close()
    b.close()
(OUT / "qa-results.json").write_text(json.dumps(res, indent=2))
print(json.dumps({"pages": res["pages"], "console_errors": len(res["errors"]), "overflow": res["overflow"][:10], "tap_pages": len(res["tap"])}, indent=1))
for e in res["errors"][:10]: print("ERR", e)
for k, v in list(res["tap"].items())[:8]: print("TAP", k, v)
