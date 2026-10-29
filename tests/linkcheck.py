"""Live check of every shipped source's candidate links. Writes content/dead-links.json
({url: status}) for 404/410/DNS failures only; bot blocks (403/429) and timeouts are not 'dead'.
build_evidence reads it: a dead primary falls back to url_backup / opened_url (Wayback) / nothing."""
import json, sys, urllib.request, ssl, concurrent.futures as cf
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import build_evidence as be
S, D, _ = be.load_all()
urls = set()
for k in ("sources_A", "sources_B", "sources_C"):
    for r in D[k]:
        for f in ("opened_url", "url_backup", "url"):
            if r.get(f): urls.add(r[f])
ctx = ssl.create_default_context()
def chk(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (link check; Certainty site)"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r: return u, r.status
    except urllib.error.HTTPError as e: return u, e.code
    except Exception as e: return u, "ERR " + type(e).__name__ + " " + str(getattr(e, "reason", ""))[:60]
res = dict(cf.ThreadPoolExecutor(16).map(chk, sorted(urls)))
dead = {u: s for u, s in res.items() if s in (404, 410) or (isinstance(s, str) and ("Name or service" in s or "getaddrinfo" in s or "nodename" in s))}
(ROOT / "content/dead-links.json").write_text(json.dumps(dead, indent=1))
(ROOT / "tests/linkcheck-results.json").write_text(json.dumps(res, indent=1))
print(f"checked {len(res)}, dead {len(dead)}"); [print(" DEAD", s, u) for u, s in dead.items()]
