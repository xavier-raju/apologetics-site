"""Rule 1: nothing Unverified (or ship:false) may reach the output, at any depth.
Run: python3 tests/test_unverified.py   (exit 1 on failure)"""
import json, sys, tempfile, shutil, os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_evidence as be

SECRET = "ZZ-FAKE-UNVERIFIED-QUOTE-7731"
fails = []
def check(cond, msg):
    if not cond: fails.append(msg)

# 1. unit: scrub drops nested quote / acceptance / acquittals_claim / ship:false rows
row = {"id": "fact-x", "status": "Confirmed", "quote": {"text": SECRET, "status": "Unverified"},
       "acceptance": {"figure": SECRET, "status": "unverified"}, "acquittals_claim": {"text": SECRET, "status": "Unverified"},
       "deep": {"inner": [{"q": SECRET, "status": "Unverified"}, {"q": "keep", "status": "Confirmed"}]}}
out = be.scrub([row, {"id": "hold", "ship": False, "text": SECRET}, {"id": "bad", "status": "Unverified", "text": SECRET}], "t")
s = json.dumps(out)
check(SECRET not in s, "scrub let a nested Unverified value through")
check(len(out) == 1 and out[0]["deep"]["inner"] == [{"q": "keep", "status": "Confirmed"}], "scrub dropped too much or too little")
try: be.assert_clean(out); 
except SystemExit: fails.append("assert_clean rejected clean data")

# 2. end to end: copy the team data, plant a nested Unverified quote on a Confirmed fact, build, grep the output
tmp = Path(tempfile.mkdtemp())
ev = tmp / "ev"
src = Path(os.environ.get("EVIDENCE_DIR", "/workspace/jesus-evidence"))
for d in ("luke/resurrection", "matthew/b", "mark"):
    (ev / d).mkdir(parents=True)
    for f in (src / d).glob("*.json"): shutil.copy(f, ev / d / f.name)
fp = ev / "luke/resurrection/facts.json"; facts = json.loads(fp.read_text())
conf = next(f for f in facts if f["status"] == "Confirmed")
conf["quote"] = {"text": SECRET, "source_id": conf["source_ids"][0], "status": "Unverified"}
conf["extra"] = {"nested": {"acceptance": {"figure": SECRET, "status": "Unverified"}}}
fp.write_text(json.dumps(facts))
outdir = tmp / "out"
env = dict(os.environ, EVIDENCE_DIR=str(ev), CERTAINTY_OUT=str(outdir))
r = subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=ROOT, env=env, capture_output=True, text=True)
check(r.returncode == 0, "fixture build failed: " + r.stdout[-400:] + r.stderr[-400:])
leaked = [str(p) for p in outdir.rglob("*") if p.is_file() and p.suffix in (".html", ".json", ".md") and SECRET in p.read_text(errors="ignore")]
check(not leaked, f"fake Unverified quote reached the output: {leaked[:3]}")
check(any(SECRET not in p.read_text() and conf["title"][:20] in p.read_text() for p in outdir.glob("resurrection/index.html")), "the Confirmed fact itself should still ship")
shutil.rmtree(tmp)
print("FAIL\n" + "\n".join(fails) if fails else "PASS test_unverified (unit + end-to-end)")
sys.exit(1 if fails else 0)
