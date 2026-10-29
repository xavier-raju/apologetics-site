"""Static QA on docs/: CSP on every page, no inline executable script, no em dashes,
no Unverified rows or held quotes, no broken internal links, every external citation is a real link.
Run after build.py: python3 tests/qa_static.py"""
import re, sys, json, html
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "docs"
sys.path.insert(0, str(ROOT)); import build_evidence as be
CSP = "default-src 'self'; img-src 'self' data: https://xavier-raju.goatcounter.com; style-src 'self'; script-src 'self' https://gc.zgo.at;"
S, D, _ = be.load_all()
held_ids = [i for v in be.STATS["dropped_ids"].values() for i in v]
held_text = ["no room for doubt", "ex-quote-luckhoo"]
res = {"pages": 0, "csp_missing": [], "inline_script": [], "em_dash": [], "unverified": [], "broken": [], "style_attr": [], "moody_chicago": []}
for f in OUT.rglob("*.html"):
    t = f.read_text(); r = str(f.relative_to(OUT)); res["pages"] += 1
    if CSP not in t: res["csp_missing"].append(r)
    for m in re.finditer(r"<script\b([^>]*)>(.*?)</script>", t, re.S):
        a, body = m.group(1), m.group(2)
        if "src=" not in a and 'type="application/json"' not in a: res["inline_script"].append(r)
        if "src=" in a and not re.search(r'src="(\.\./|\./|assets/|https://gc\.zgo\.at/)', a): res["inline_script"].append(r + " foreign script")
    if re.search(r"\son[a-z]+=\"", t): res["inline_script"].append(r + " inline handler")
    own = re.sub(r"<blockquote\b.*?</blockquote>|<p class=\"verse-line\">.*?</p>|data-verse=\"[^\"]*\"|<div class=\"scripture\">.*?</div>", "", t, flags=re.S)
    if r.startswith("library/") and r.count("/") == 2: own = re.sub(r'<div class="prose reading">.*?</div><p class="btn-row">', "", own, flags=re.S)  # hosted PD text
    if "\u2014" in own or "&mdash;" in own: res["em_dash"].append(r)
    if re.search(r"Moody[^<]{0,80}Chicago|Chicago[^<]{0,80}Moody", t): res["moody_chicago"].append(r)
    for h in held_text:
        if h in t: res["unverified"].append(f"{r}: {h}")
    if r.startswith("resurrection/tester") and ("fact-card__why" in t or "Why this matters" in t): res["unverified"].append(f"{r}: why line in tester")
    if 'tag--unverified' in t: res["unverified"].append(f"{r}: Unverified label")
    if f.name != "404.html":
        for u in re.findall(r'href="([^"]+)"', t):
            u = html.unescape(u)
            if re.match(r"^(https?:|mailto:|#)", u): continue
            p = (f.parent / u.split("#")[0].split("?")[0]).resolve()
            if p.is_dir(): p = p / "index.html"
            if not p.exists(): res["broken"].append(f"{r} -> {u}")
for f in list(OUT.rglob("*.json")) + list(OUT.rglob("*.md")):
    t = f.read_text(errors="ignore")
    rel = str(f.relative_to(OUT))
    if "\u2014" in t and not (rel.startswith("data/") or rel.endswith(".md")): res["em_dash"].append(rel)  # bible data, search excerpts, hosted .md = source text
    for h in held_text:
        if h in t: res["unverified"].append(f"{f.relative_to(OUT)}: {h}")
# Unverified source urls must not appear as links on the new pages
new = [p for p in OUT.rglob("*.html") if str(p.relative_to(OUT)).startswith(("resurrection", "explore"))]
blob = "".join(p.read_text() for p in new)
conf_urls = {S.link(r) for r in S.rec.values() if str(r.get("status","")).lower() == "confirmed"}
for i in held_ids:
    try: r = S.rec[i]
    except KeyError: continue
    if r.get("url") and r["url"] not in conf_urls and f'href="{html.escape(r["url"], quote=True)}"' in blob: res["unverified"].append(f"link to Unverified source {i}")
ok = not any(v for k, v in res.items() if k != "pages")
print(json.dumps({k: (v if k == "pages" else len(v)) for k, v in res.items()}))
for k, v in res.items():
    if k != "pages" and v: print(k, v[:8])
print("PASS qa_static" if ok else "FAIL qa_static"); sys.exit(0 if ok else 1)
