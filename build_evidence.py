"""Weekend build (v10): Resurrection section and repo explorers, built from the team's data.

Reads (never writes) the team's data files:
  A  Luke     $EVIDENCE/luke/resurrection/{sources,facts,theories,appearances,exhibits}.json
  B  Matthew  $EVIDENCE/matthew/b/{sources,life,prophecy,gospels,dating}.json   (sources.json is canonical)
  C  Mark     $EVIDENCE/mark/{voices,sources_c,id-map}.json
Hard rules enforced here (see weekend-plan-final.md):
  1. scrub(): any object or row with status Unverified or ship:false is dropped, at any depth.
     A nested object citing (source_id) a source that is not Confirmed is dropped as well.
  2. The theory tester counts Confirmed facts only.
  3. Every point carries a status label and a citation; url_backup wins; link_ok false = no link;
     every source id must resolve (aliases, id-map, duplicate_of) or the build fails.
  4. Only host-tagged public-domain text is hosted (we host no new full texts here).
"""
import json, os, re, math
from pathlib import Path

EVIDENCE = Path(os.environ.get("EVIDENCE_DIR", "/workspace/jesus-evidence"))
STATS = {"shipped": {}, "dropped": {}, "dropped_ids": {}, "dropped_cites": 0, "nested_dropped": []}

class BuildError(SystemExit): pass
_dl = Path(__file__).resolve().parent / "content/dead-links.json"
DEAD = set(json.loads(_dl.read_text())) if _dl.exists() else set()  # from tests/linkcheck.py (404/410/DNS only)

# ------------------------------------------------------------------ rule 1: scrub
def is_unverified(o):
    return isinstance(o, dict) and (str(o.get("status", "")).strip().lower() == "unverified" or o.get("ship") is False)

def scrub(o, path="", src_ok=None, log=None):
    """Return a copy of o with every Unverified / ship:false object removed at any depth.
    src_ok(id) -> bool: nested objects that cite a non-Confirmed source_id are removed too."""
    log = STATS["nested_dropped"] if log is None else log
    if isinstance(o, list):
        out = []
        for i, x in enumerate(o):
            if is_unverified(x) or (src_ok and isinstance(x, dict) and path and "source_id" in x and x["source_id"] and not src_ok(x["source_id"])):
                log.append(f"{path}[{i}]{'#' + str(x.get('id')) if x.get('id') else ''}"); continue
            out.append(scrub(x, f"{path}[{i}]", src_ok, log))
        return out
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if is_unverified(v) or (src_ok and isinstance(v, dict) and v.get("source_id") and not src_ok(v["source_id"])):
                log.append(f"{path}.{k}"); continue
            out[k] = scrub(v, f"{path}.{k}", src_ok, log)
        return out
    return o

def assert_clean(o, where="output"):
    if isinstance(o, list):
        for x in o: assert_clean(x, where)
    elif isinstance(o, dict):
        if is_unverified(o): raise BuildError(f"BUILD FAILED: Unverified object reached {where}: {o.get('id')}")
        for v in o.values(): assert_clean(v, where)

# ------------------------------------------------------------------ sources registry
class Sources:
    def __init__(self):
        self.rec, self.alias = {}, {}
    def add(self, r, origin):
        r = dict(r); r["_origin"] = origin
        i = r["id"]
        if i in self.rec:  # same id in two files (e.g. LK008 copied by Mark): keep the first, fill gaps
            for k, v in r.items(): self.rec[i].setdefault(k, v)
        else: self.rec[i] = r
        for a in (r.get("aliases") or []) + ([r["slug"]] if r.get("slug") else []):
            self.alias.setdefault(a, i)
    def resolve(self, sid):
        seen = set()
        while True:
            if sid in seen: raise BuildError(f"BUILD FAILED: alias loop at {sid}")
            seen.add(sid)
            if sid in self.rec:
                d = self.rec[sid].get("duplicate_of")
                if d and d in self.rec: sid = d; continue
                return self.rec[sid]
            if sid in self.alias: sid = self.alias[sid]; continue
            raise BuildError(f"BUILD FAILED: unresolved source id '{sid}'")
    def confirmed(self, sid):
        return str(self.resolve(sid).get("status", "")).lower() == "confirmed"
    def link(self, r):
        """Primary link: opened_url, then url_backup, then url (link_ok is stale for reopened sources).
        Exception: a page we read but whose TLS certificate is invalid is cited without a link."""
        if "certificate" in str(r.get("verify_note") or "").lower() and "invalid" in str(r.get("verify_note") or "").lower(): return None
        for u in (r.get("opened_url"), r.get("url_backup"), r.get("url")):
            if u and u not in DEAD: return u
        return None
    def backup(self, r):
        """Second link shown beside the primary when the source has a distinct backup."""
        b = r.get("url_backup")
        return b if b and b != self.link(r) else None
    def label(self, r):
        a, t, y = r.get("author"), r.get("title") or r.get("citation") or r["id"], r.get("year")
        return ", ".join(str(x) for x in (a, t, y) if x)

def load_all():
    L = lambda p: json.loads((EVIDENCE / p).read_text())
    S = Sources()
    for r in L("luke/resurrection/sources.json"): S.add(r, "A")
    bs = L("matthew/b/sources.json"); bs = bs["sources"] if isinstance(bs, dict) else bs
    for r in bs: S.add(r, "B")
    for r in L("mark/sources_c.json"): S.add(r, "C")
    for k, v in L("mark/id-map.json").items(): S.alias.setdefault(k, v)
    raw = {
        "facts": L("luke/resurrection/facts.json"), "theories": L("luke/resurrection/theories.json"),
        "appearances": L("luke/resurrection/appearances.json"), "exhibits": L("luke/resurrection/exhibits.json"),
        "life": L("matthew/b/life.json"), "prophecy": L("matthew/b/prophecy.json"),
        "gospels": L("matthew/b/gospels.json"), "dating": L("matthew/b/dating.json"),
    }
    vj = L("mark/voices.json"); raw["voices"] = vj["voices"]; meta_c = vj.get("meta", {})
    raw["sources_A"] = L("luke/resurrection/sources.json"); raw["sources_B"] = bs; raw["sources_C"] = L("mark/sources_c.json")
    # every id anywhere must resolve (fail the build otherwise), before anything is dropped
    def walk_ids(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("source_ids", "dating_source_ids", "cross_ref_c") and isinstance(v, list): [S.resolve(x) for x in v]
                elif k == "source_id" and isinstance(v, str) and v: S.resolve(v)
                elif k == "range_source" and isinstance(v, str) and re.match(r"^[A-Z]{1,2}\d+$", v): S.resolve(v)
                else: walk_ids(v)
        elif isinstance(o, list): [walk_ids(x) for x in o]
    for k, v in raw.items():
        if not k.startswith("sources_"): walk_ids(v)
    D = {}
    ok = lambda sid: S.confirmed(sid)
    for k, v in raw.items():
        before = len(v)
        clean = scrub(v, k, None if k.startswith("sources_") else ok)
        STATS["dropped"][k] = before - len(clean)
        STATS["dropped_ids"][k] = [x.get("id") for x in v if is_unverified(x)]
        STATS["shipped"][k] = len(clean)
        assert_clean(clean, k)
        D[k] = clean
    return S, D, meta_c

# ------------------------------------------------------------------ helpers
def no_internal(t):
    """Strip internal row ids and team notes from prose that ships."""
    t = re.sub(r"\s*\((?:see )?(?:ex|fact|th|app|LK|MK)[-\w]*\)", "", t or "")
    return t

def sentences_without(t, *needles):
    parts = re.split(r"(?<=[.!?])\s+", t or "")
    return " ".join(p for p in parts if not any(n.lower() in p.lower() for n in needles))

def run(B):
    esc, status_tag, page, page_head, index, ARROW, verse_btn, slug = B.esc, B.status_tag, B.page, B.page_head, B.index, B.ARROW, B.verse_btn, B.slug
    S, D, meta_c = load_all()
    # strip internal team notes from prose at build time (pages and search index alike)
    NOTES = ("Draws only on", "site's current list", "we recommend", "held back", "survey found")
    for k in ("facts", "exhibits", "theories", "appearances"):
        for row_ in D[k]:
            for fld in ("short", "deep"):
                if row_.get(fld): row_[fld] = sentences_without(no_internal(row_[fld]), *NOTES)
    col_label = meta_c.get("column_label", "What critics grant")
    # Gospel Bot slot: optional "why this matters" lines, content/why.json {fact_id: text} (or a `why` field on the fact).
    wp = B.ROOT / "content/why.json"
    WJ = json.loads(wp.read_text()) if wp.exists() else {}
    WHY = scrub(WJ.get("why", WJ), "why") if isinstance(WJ, dict) else {}
    WMETA = WJ.get("meta", {}) if isinstance(WJ, dict) else {}
    STATS["why_lines"] = 0
    def why_html(f):
        w = f.get("why") or WHY.get(f["id"])
        if isinstance(w, str): w = {"text": w}
        if not w or not w.get("text"): return ""
        STATS["why_lines"] += 1
        q = f'<figure class="quote quote--inline"><blockquote>{B.esc_src(w["quote"])}</blockquote><figcaption>{esc(w.get("ref", ""))}</figcaption></figure>' if w.get("quote") else ""
        return f'<aside class="fact-card__why" aria-label="Why this matters, a reflection"><p class="answer__label">Why this matters <span class="tag tag--neutral">Reflection, not evidence</span></p><p>{esc(w["text"])}</p>{q}<p class="small muted">Drafted by Gospel Bot, checked by the team. Not counted in the theory tester.</p></aside>'


    def cites(ids, root, fallback=None, cls="source-list"):
        items, seen = [], set()
        for sid in ids or []:
            r = S.resolve(sid)
            if r["id"] in seen: continue
            seen.add(r["id"])
            if str(r.get("status", "")).lower() != "confirmed": STATS["dropped_cites"] += 1; continue
            u = S.link(r); lab = S.label(r)
            pg = r.get("page_or_timestamp")
            extra = f'<span class="muted"> · {esc(pg)}</span>' if pg and len(str(pg)) < 90 else ""
            bk = S.backup(r)
            items.append(f'<li>{B.link(lab, u, root) if u else esc(lab) + " <span class=muted>(link unavailable)</span>"}{f" <span class=muted>·</span> {B.link("Backup copy", bk, root)}" if bk else ""}{extra}</li>')
        if not items and fallback:
            u, lab = fallback
            if u: items.append(f"<li>{B.link(lab, u, root)}</li>")
        return f'<ul class="{cls}">{"".join(items)}</ul>' if items else ""

    # ---------------------------------------------------------------- facts
    facts = D["facts"]; F = {f["id"]: f for f in facts}
    core = [f for f in facts if f["status"] == "Confirmed"]
    other = [f for f in facts if f["status"] != "Confirmed" and f["id"] != "fact-empty-tomb"]
    tomb = F.get("fact-empty-tomb")
    TAGMAP = {"appearance_to_500": "fact-appearances-to-disciples"}
    concessions = {}
    for v in D["voices"]:
        if v.get("role") not in ("skeptic", "critical_scholar"): continue
        for a in v.get("accepts", []):
            fid = TAGMAP.get(a["fact_tag"], "fact-" + a["fact_tag"].replace("_", "-"))
            concessions.setdefault(fid, []).append((v, a))
    for f in facts:  # facts may point at Mark's sources directly
        for sid in f.get("cross_ref_c", []) or []:
            for v in D["voices"]:
                for a in v.get("accepts", []):
                    if S.resolve(a["source_id"])["id"] == S.resolve(sid)["id"] and (v, a) not in concessions.get(f["id"], []):
                        concessions.setdefault(f["id"], []).append((v, a))

    def conc_html(fid, root):
        cs = concessions.get(fid, [])
        if not cs: return ""
        li = []
        for v, a in cs:
            r = S.resolve(a["source_id"]); u = S.link(r)
            li.append(f'<li><blockquote class="conc__q">{esc(a["exact_quote"])}</blockquote><p class="small muted"><strong>{esc(v["name"])}</strong>, {esc(v.get("label") or v.get("role","").replace("_"," "))}. {B.link(S.label(r), u, root) if u else esc(S.label(r))}</p></li>')
        return f'<div class="fact-card__sec"><p class="answer__label">{esc(col_label)}</p><ul class="conc">{"".join(li)}</ul></div>'

    def quote_html(f, root):
        q = f.get("quote")
        if not q: return ""
        r = S.resolve(q["source_id"]); u = S.link(r)
        att = f'{esc(q["attribution"])}. ' if q.get("attribution") else ""
        return f'<figure class="quote quote--inline"><blockquote>{B.esc_src(q["text"])}</blockquote><figcaption>{att}{B.link(S.label(r), u, root) if u else esc(S.label(r))}{" · " + esc(q["page"]) if q.get("page") else ""}</figcaption></figure>'

    def fact_card(f, root, n=None, extra=""):
        fid = f["id"]; deep_id = fid + "-deep"
        num = f'<span class="fact-card__n">{n:02d}</span>' if n else ""
        return f'''<article class="fact-card reveal" id="{esc(fid)}" data-fact>
  <div class="fact-card__front"><div class="card__meta">{num}{status_tag(f["status"])}</div>
    <h3 class="fact-card__title">{esc(f["title"])}</h3>
    <p class="answer__label">30-second version</p><p>{esc(no_internal(f["short"]))}</p>{extra}
    <button class="btn btn--ghost btn--sm fact-card__toggle" type="button" data-fact-toggle aria-expanded="false" aria-controls="{esc(deep_id)}">Go deeper {ARROW}</button></div>
  <div class="fact-card__deep" id="{esc(deep_id)}">
    <p class="answer__label">Go deeper</p><p>{esc(no_internal(f.get("deep_override") or f["deep"]))}</p>
    {quote_html(f, root)}{conc_html(fid, root)}{why_html(f) if f.get("_why_slot") else ""}
    <div class="fact-card__sec"><p class="answer__label">Sources</p>{cites(f.get("source_ids"), root, (f.get("source_url"), "Source"))}</div>
    <button class="btn btn--link btn--sm fact-card__toggle" type="button" data-fact-toggle aria-expanded="true" aria-controls="{esc(deep_id)}">Back to the 30-second version</button></div>
</article>'''

    # rule 6: empty tomb as its own Contested card, Habermas's count of arguments, not a poll
    if tomb:
        t = dict(tomb)
        deep = sentences_without(t["deep"], "survey found", "site's current list", "we recommend")
        deep += (" Habermas reports a count of arguments in the scholarly literature since 1975, not a formal poll:"
                 " about 75% of the publications he counted favor one or more arguments for the empty tomb, and about 25% favor one or more against it.")
        t["deep_override"] = deep; t["_why_slot"] = True
        acc = t.get("acceptance")
        fig = f'<p class="tomb__fig"><span class="tomb__n">~75 / 25</span><span class="small muted">Habermas&apos;s count of arguments in the literature since 1975, not a poll</span></p>' if acc else ""
        tomb_html = fact_card(t, "../", extra=fig)
    else: tomb_html = ""

    def chapters(root, cur=""):
        ch = [("resurrection/", "The five facts"), ("resurrection/tester/", "Theory tester"), ("resurrection/timeline/", "Easter to Pentecost"),
              ("resurrection/courtroom/", "The courtroom"), ("resurrection/voices/", "Voices")]
        return '<nav class="chapters" aria-label="Resurrection chapters"><ol>' + "".join(
            f'<li><a href="{root}{r}"{" aria-current=page" if r == cur else ""}><span class="chapters__n">{i}</span>{esc(l)}</a></li>' for i, (r, l) in enumerate(ch, 1)) + "</ol></nav>"

    for f in core: f["_why_slot"] = True
    root = "../"
    hub = B.page_head("The resurrection", "Five facts almost every historian grants, one strong but contested fact, and every main theory weighed against them. Tap a card for the 30-second version, then go deeper.", [("Resurrection", "/resurrection/")], root, eyebrow="The core case") + f'''
<div class="wrap section">{chapters(root, "resurrection/")}
  <h2>The five Confirmed facts</h2><p class="muted measure">These are the facts Gary Habermas calls minimal facts: each is granted by nearly all scholars who write on the subject, sceptics included. Only these five count in the theory tester.</p>
  <div class="stack facts">{"".join(fact_card(f, root, i) for i, f in enumerate(core, 1))}</div>
  <h2 class="mt">The empty tomb</h2><p class="muted measure">Strong, but not near-unanimous, so it gets its own card and is never counted as evidence in the tester.</p>
  <div class="stack facts">{tomb_html}</div>
  <h2 class="mt">Also discussed, and contested</h2><p class="muted measure">Shown with their label. None of these is used as evidence in the tester.</p>
  <div class="stack facts">{"".join(fact_card(f, root) for f in other)}</div>
  <p class="btn-row mt"><a class="btn" href="tester/">Test the theories {ARROW}</a><a class="btn btn--ghost" href="courtroom/">Walk through the case</a></p>
</div>'''
    page("resurrection/", "The resurrection", hub, page_js="res")
    for f in core + ([tomb] if tomb else []) + other:
        index("Resurrection", f["title"], f"resurrection/#{f['id']}", f"{f['short']} {f['deep']}", snippet=f["short"], status=f["status"])

    # ---------------------------------------------------------------- tester (rule 2)
    rt = "../../"
    core_ids = [f["id"] for f in core]
    VERD = {"explains": ("Explains", "ok"), "partial": ("Partly", "warn"), "fails": ("Fails", "bad")}
    chips, panels = [], []
    for i, th in enumerate(D["theories"]):
        grid = {k: v for k, v in (th.get("grid") or {}).items() if k in core_ids}  # Confirmed facts only
        n_ex = sum(1 for v in grid.values() if v["verdict"] == "explains"); n_pa = sum(1 for v in grid.values() if v["verdict"] == "partial")
        rows = "".join(f'''<li class="verdict verdict--{VERD[grid[fid]["verdict"]][1]}"><span class="verdict__tag" aria-hidden="true">{ {"explains":"✓","partial":"~","fails":"✕"}[grid[fid]["verdict"]] }</span>
          <div><p class="verdict__fact"><a href="../#{esc(fid)}">{esc(F[fid]["title"])}</a></p><p><strong>{VERD[grid[fid]["verdict"]][0]}.</strong> {esc(grid[fid]["reason"])}</p>
          <div class="small muted">{cites([grid[fid]["source_id"]], rt, cls="source-list source-list--inline") if grid[fid].get("source_id") else ""}</div></div></li>''' for fid in core_ids if fid in grid)
        chips.append(f'<button class="chip" type="button" data-theory="{esc(th["id"])}" aria-pressed="{"true" if i == 0 else "false"}">{esc(th["name"])}</button>')
        panels.append(f'''<section class="theory card" id="{esc(th["id"])}"{" data-active" if i == 0 else ""}><div class="card__meta">{status_tag(th["status"])}<span>Our argued judgment</span></div>
          <h2 class="card__title">{esc(th["name"])}</h2><p>{esc(no_internal(th["short"]))}</p>
          <p class="score" aria-live="polite"><strong>Explains {n_ex} of {len(core_ids)}</strong> Confirmed facts{f", partly {n_pa}" if n_pa else ""}.</p>
          <ol class="verdicts">{rows}</ol>
          <details class="sources"><summary>Go deeper</summary><p>{esc(no_internal(th["deep"]))}</p>{cites(th.get("source_ids"), rt, (th.get("source_url"), "Source"))}</details></section>''')
        index("Resurrection", th["name"], f"resurrection/tester/#{th['id']}", f"{th['short']} {th['deep']}", snippet=th["short"], status=th["status"])
    notc = "".join(f'<li>{status_tag(f["status"])} {esc(f["title"])}</li>' for f in ([tomb] if tomb else []) + other)
    body = B.page_head("Theory tester", "Pick a theory. See which of the five Confirmed facts it explains, partly explains, or fails to explain, and why.", [("Resurrection", "/resurrection/"), ("Theory tester", "/resurrection/tester/")], rt, eyebrow="Resurrection") + f'''
<div class="wrap section">{chapters(rt, "resurrection/tester/")}<div class="tester" data-tester>
  <div class="chips tester__chips" role="group" aria-label="Choose a theory">{"".join(chips)}</div>
  <div class="tester__panels">{"".join(panels)}</div></div>
  <details class="sources legend mt"><summary>Not counted as evidence</summary><p class="small muted">These are shown on the facts page with their label. The tester weighs only Confirmed facts.</p><ul class="plain">{notc}</ul></details></div>'''
    page("resurrection/tester/", "Theory tester", body, page_js="res")

    # ---------------------------------------------------------------- timeline + map
    ABBR = {"mt": "matthew", "matt": "matthew", "mk": "mark", "lk": "luke", "jn": "john", "1 cor": "1 corinthians", "gal": "galatians", "rev": "revelation"}
    def chaps(refs):
        out = set()
        for ref in refs:
            for part in re.split(r"[;,]\s*", ref):
                m = re.match(r"\s*((?:[1-3] )?[A-Za-z]+)\.?\s+(\d+)", part)
                if m: out.add((ABBR.get(m.group(1).lower(), m.group(1).lower()), int(m.group(2))))
        return out
    apps = sorted(D["appearances"], key=lambda a: (a.get("day") is None, a.get("day") or 0))
    life = sorted([x for x in D["life"] if 140 <= x.get("n", 0) <= 175], key=lambda x: x["n"])
    before = [x for x in life if x["phase"].startswith(("The final", "Arrest"))]
    after = [x for x in life if x not in before]
    attach = {a["id"]: [] for a in apps}; loose = []
    for x in after:
        cx = chaps(x["passages"]); hit = None
        for a in apps:
            if cx & chaps([a["passage"]]): hit = a["id"]; break
        (attach[hit].append(x) if hit else loose.append(x))
    def life_li(x, root):
        refs = " ".join(verse_btn(p) for p in x["passages"])
        return f'''<li class="tl-life"><div class="card__meta">{status_tag(x["status"])}<span>Life of Jesus {x["n"]}</span></div><p class="tl-life__t"><strong>{esc(x["title"])}</strong></p><p class="small">{esc(x["short"])}</p><p class="refs small">{refs}</p>
          <details class="sources"><summary>Go deeper</summary><p>{esc(x["deep"])}</p>{cites(x.get("source_ids"), root, (x.get("url"), "0xSero repo, life of Jesus catalogue"))}</details></li>'''
    def app_li(a, root):
        dl = f'Day {a["day"]} · {a["weekday"]}' if a.get("day") else "Day not stated"
        ls = f' {status_tag("Framing")}<span class="small muted">location</span>' if a.get("location_status") == "Framing" else ""
        sub = "".join(life_li(x, root) for x in attach.get(a["id"], []))
        return f'''<li class="tl-item reveal" id="{esc(a["id"])}"><p class="timeline__date">{esc(dl)} {status_tag(a["status"])}{ls}</p>
          <h3 class="timeline__title">{esc(a["who"])}</h3><p>{esc(a["where"])} · {verse_btn(a["passage"].split(";")[0])}</p>
          <details class="sources"><summary>Go deeper</summary><p>{esc(no_internal(a["deep"]))}</p>{cites(a.get("source_ids"), root, (a.get("source_url"), "Source"))}</details>
          {f'<ul class="tl-sub">{sub}</ul>' if sub else ""}</li>'''
    # map: simple inline SVG, equirectangular, Jerusalem area + Galilee + Damascus
    pts = [a for a in apps if isinstance(a.get("lat"), (int, float))]
    places = {}
    for a in pts:
        k = (round(a["lat"], 2), round(a["lon"], 2)); places.setdefault(k, []).append(a)
    W, H = 360, 400; la0, la1, lo0, lo1 = 31.65, 33.62, 34.55, 36.4
    xy = lambda la, lo: (20 + (lo - lo0) / (lo1 - lo0) * (W - 40), 20 + (la1 - la) / (la1 - la0) * (H - 40))
    NAME = lambda ps: ps[0]["where"].split(",")[-1].strip().replace("(Galilee)", "").strip() if len(ps) == 1 else "Jerusalem"
    marks = []
    for k, ps in places.items():
        x, y = xy(*k); fr = all(p["status"] == "Framing" or p.get("location_status") == "Framing" for p in ps)
        nm = {"app-emmaus": "Emmaus (Framing)", "app-ascension": "Mount of Olives (Framing)", "app-galilee-sea": "Sea of Tiberias", "app-paul": "Damascus road"}.get(ps[0]["id"], NAME(ps)) if len(ps) == 1 else "Jerusalem"
        anc, dx = ("end", -10) if ps[0]["id"] in ("app-emmaus", "app-paul") else ("start", 10)
        dy = 20 if ps[0]["id"] == "app-ascension" else (-12 if ps[0]["id"] == "app-emmaus" else 4)
        marks.append(f'<g class="rmap__pin{" is-framing" if fr else ""}"><circle cx="{x:.1f}" cy="{y:.1f}" r="{5 if len(ps) > 1 else 4}"/><text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anc}">{esc(nm)}{f" · {len(ps)}" if len(ps) > 1 else ""}</text></g>')
    gx, gy = xy(32.82, 35.59)
    rmap = f'''<figure class="rmap"><svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="rmap-t"><title id="rmap-t">Schematic map of the appearances: Jerusalem, Emmaus, the Mount of Olives, the Sea of Galilee and the Damascus road</title>
  <ellipse class="rmap__sea" cx="{gx:.1f}" cy="{gy:.1f}" rx="10" ry="16"/><path class="rmap__river" d="M{gx:.1f} {gy + 16:.1f} C {gx + 4:.1f} {gy + 80:.1f}, {gx - 6:.1f} {gy + 160:.1f}, {xy(31.75, 35.55)[0]:.1f} {xy(31.75, 35.55)[1]:.1f}"/>
  <text class="rmap__region" x="{xy(33.0, 35.25)[0]:.1f}" y="{xy(33.0, 35.25)[1]:.1f}">GALILEE</text><text class="rmap__region" x="{xy(31.95, 35.0)[0]:.1f}" y="{xy(31.95, 35.0)[1]:.1f}">JUDEA</text>
  {"".join(marks)}</svg><figcaption class="small muted">Schematic, not to scale. Coordinates from Luke&apos;s appearances data (OpenBible.info). Dashed rings mark Framing locations: the place is traditional or implied, not stated. Not mapped (place not stated): {esc(", ".join(a["who"] for a in apps if a not in pts))}.</figcaption></figure>'''
    body = B.page_head("Easter to Pentecost", "Fifty days, counted with Easter Sunday as day 1: the Ascension falls on day 40 and Pentecost on day 50. Each appearance is matched to the life-of-Jesus entries that tell it.", [("Resurrection", "/resurrection/"), ("Timeline and map", "/resurrection/timeline/")], rt, eyebrow="Resurrection") + f'''
<div class="wrap section">{chapters(rt, "resurrection/timeline/")}{rmap}
  <details class="sources"><summary>The week before: from the last supper to the burial ({len(before)} entries)</summary><ul class="tl-sub">{"".join(life_li(x, rt) for x in before)}</ul></details>
  <ol class="timeline tl">{"".join(app_li(a, rt) for a in apps)}</ol>
  {f'<h2 class="mt">After Pentecost</h2><ul class="tl-sub">{"".join(life_li(x, rt) for x in loose)}</ul>' if loose else ""}</div>'''
    page("resurrection/timeline/", "Easter to Pentecost", body)
    STATS["timeline"] = {"appearances": len(apps), "life_entries": len(life), "life_attached": sum(len(v) for v in attach.values()), "life_before": len(before), "life_loose": len(loose), "mapped": len(pts)}

    # ---------------------------------------------------------------- courtroom
    ex = D["exhibits"]; steps = sorted([e for e in ex if e.get("step")], key=lambda e: e["step"]); bio = next((e for e in ex if e["id"] == "ex-bio-luckhoo"), None)
    if bio:  # rule 7: Contested, Wikipedia only
        if bio["status"] != "Contested": raise BuildError("BUILD FAILED: Luckhoo bio card must be Contested")
        for sid in bio["source_ids"]:
            if "wikipedia.org" not in (S.resolve(sid).get("url") or ""): raise BuildError("BUILD FAILED: Luckhoo bio card may cite Wikipedia only")
    if any(e["id"] == "ex-quote-luckhoo" for e in ex): raise BuildError("BUILD FAILED: ex-quote-luckhoo must never ship")
    st = []
    for e in steps:
        fl = ", ".join(f'<a href="../#{esc(fid)}">{esc(F[fid]["title"])}</a>' for fid in e.get("fact_ids", []) if fid in F)
        st.append(f'''<li class="step reveal" id="{esc(e["id"])}"><span class="step__n">{e["step"]}</span><div class="card"><div class="card__meta">{status_tag(e["status"])}<span>Step {e["step"]} of {len(steps)}</span></div>
          <h2 class="card__title">{esc(e["title"])}</h2><p>{esc(no_internal(e["short"]))}</p>
          <details class="sources"><summary>Go deeper</summary><p>{esc(no_internal(sentences_without(e["deep"], "Draws only on")))}</p>{f'<p class="small">Facts on the table: {fl}</p>' if fl else ""}{cites(e.get("source_ids"), rt, (e.get("source_url"), "Source"))}</details></div></li>''')
    bio_html = ""
    if bio:
        deep = sentences_without(no_internal(bio["deep"]), "held back", "245")
        ac = bio.get("acquittals_claim")
        bio_html = f'''<article class="card bio reveal" id="ex-bio-luckhoo"><div class="card__meta">{status_tag(bio["status"])}<span>The lawyer</span></div><h2 class="card__title">{esc(bio["title"])}</h2>
          <p>{esc(bio["short"])}</p><details class="sources"><summary>Go deeper</summary><p>{esc(deep)}</p>
          {f'<p>{status_tag(ac["status"])} {esc(ac["text"])}.</p>' if ac else ""}{cites(bio["source_ids"], rt)}</details></article>'''
    body = B.page_head("The courtroom", "You are the jury. Eight steps, each resting only on facts from the hub, then the standard of proof. Step through, then decide.", [("Resurrection", "/resurrection/"), ("Courtroom", "/resurrection/courtroom/")], rt, eyebrow="Resurrection") + f'''
<div class="wrap section measure-wide">{chapters(rt, "resurrection/courtroom/")}<ol class="steps">{"".join(st)}</ol>{bio_html}
  <p class="btn-row mt"><a class="btn" href="../tester/">Now test the theories {ARROW}</a></p></div>'''
    page("resurrection/courtroom/", "The courtroom", body)
    for e in steps: index("Resurrection", e["title"], f"resurrection/courtroom/#{e['id']}", e["short"] + " " + e["deep"], snippet=e["short"])

    # ---------------------------------------------------------------- voices
    ROLE = {"skeptic": "Sceptic", "critical_scholar": "Critical scholar", "scholar": "Scholar", "early_witness": "Early Christian writer"}
    vc = []
    for v in D["voices"]:
        def ql(items, kind):
            out = []
            for a in items:
                r = S.resolve(a["source_id"]); u = S.link(r)
                out.append(f'<li><blockquote class="conc__q">{esc(a["exact_quote"])}</blockquote><p class="small muted">{B.link(S.label(r), u, rt) if u else esc(S.label(r))}{" · " + esc(a["locator"]) if a.get("locator") else ""}</p></li>')
            return f'<div class="voice__col"><p class="answer__label">{kind}</p><ul class="conc">{"".join(out)}</ul></div>' if out else ""
        hl = '<span class="tag tag--hosted">Public domain</span>' if v.get("host_or_link") == "host" else '<span class="tag tag--link">Link only</span>'
        deb = v.get("debate"); dt = v.get("dating_text")
        vc.append(f'''<article class="card voice reveal" id="{esc(v["id"])}" data-tags="{esc(v.get("role",""))}"><div class="card__meta">{status_tag(v["status"])}<span>{esc(v.get("label") or ROLE.get(v.get("role"), ""))}</span>{hl}</div>
          <h2 class="card__title">{esc(v["name"])}</h2><p class="small muted">{esc(v["who"])}</p><p>{esc(v["short_30s"])}</p>
          <div class="voice__cols">{ql(v.get("accepts", []), "Accepts")}{ql(v.get("denies", []), "Denies")}</div>
          {f'<p class="small">Debate: {esc(deb["date"])}, {esc(deb["venue"])}. {cites([deb["source_id"]], rt, cls="source-list source-list--inline")}</p>' if deb else ""}
          {f'<p class="small">{status_tag("Contested")} Dating: {esc(dt)}</p>{cites(v.get("dating_source_ids"), rt)}' if dt else ""}
          <details class="sources"><summary>Go deeper</summary><p>{esc(v["deep"])}</p></details></article>''')
        index("Voices", v["name"], f"resurrection/voices/#{v['id']}", v["short_30s"] + " " + v["deep"], snippet=v["short_30s"], status=v["status"])
    roles = []
    for v in D["voices"]:
        if v.get("role") not in roles: roles.append(v.get("role"))
    chips = '<button class="chip" type="button" data-filter="*" aria-pressed="true">All</button>' + "".join(f'<button class="chip" type="button" data-filter="{esc(r)}" aria-pressed="false">{esc(ROLE.get(r, r))}</button>' for r in roles)
    body = B.page_head("Voices", "Sceptics, critical scholars and early Christian writers, each with what they accept and what they deny, in their own short words and linked to the source.", [("Resurrection", "/resurrection/"), ("Voices", "/resurrection/voices/")], rt, eyebrow="Resurrection") + f'''
<div class="wrap section" data-filter-scope>{chapters(rt, "resurrection/voices/")}<div class="chips" role="group" aria-label="Filter voices">{chips}</div><p class="muted small" data-filter-count aria-live="polite"></p><div class="grid grid--2">{"".join(vc)}</div></div>'''
    page("resurrection/voices/", "Voices", body)

    # ---------------------------------------------------------------- explorers (one shared component)
    def explorer(route, title, intro, items, facets, label, extra_top="", root="../../"):
        chips = '<button class="chip" type="button" data-filter="*" aria-pressed="true">All</button>' + "".join(f'<button class="chip" type="button" data-filter="{esc(slug(f))}" aria-pressed="false">{esc(f)}</button>' for f in facets)
        body = B.page_head(title, intro, [("Explore", "/explore/"), (title, "/" + route)], root, eyebrow="Explore More") + f'''
<div class="wrap section">{extra_top}<div class="explorer" data-filter-scope>
  <div class="lib-controls"><label class="sr-only" for="q-{slug(title)}">Search {esc(title)}</label><div class="field">{B.ICON_S}<input id="q-{slug(title)}" type="search" placeholder="Search {esc(label)}" data-filter-search autocomplete="off"></div>
  <div class="chips" role="group" aria-label="Filter">{chips}</div></div>
  <p class="muted small" data-filter-count aria-live="polite"></p><ul class="lib-list">{"".join(items)}</ul><p class="empty" data-filter-empty hidden>Nothing matches. Try a shorter search or clear the filter.</p></div></div>'''
        page(route, title, body, page_js="library")
    def row(tags, text, meta, h, body_html):
        return f'<li class="lib-item ex-item" data-tags="{esc(" ".join(slug(t) for t in tags if t))}" data-text="{esc(text.lower())}"><div><div class="card__meta">{meta}</div><h2 class="lib-item__title">{h}</h2>{body_html}</div></li>'
    R = "../../"
    # sources
    srcs = D["sources_B"]; items = []
    for s in srcs:
        u = S.link(s); dup = s.get("duplicate_of")
        h = B.link(s.get("title") or s["citation"][:90], u, R) if u else esc(s.get("title") or s["citation"][:90])
        meta = f'{status_tag(s["status"])}<span class="tag tag--link">Link only</span><span>{esc(s["id"])}</span><span>· {esc(s.get("section"))}</span>'
        bk = S.backup(s)
        bh = (f'<p class="small">{B.link("Backup copy", bk, R)}</p>' if bk else "") + f'<p class="small muted">{esc(s["citation"])}</p><p class="small">{esc(s["short"])}</p>' + (f'<p class="small">Same work as {esc(dup)}.</p>' if dup else "") + ('<p class="small muted">Cited without a link: the page matches, but its security certificate is invalid.</p>' if not u else "") + f'<p class="small muted">Opened by {esc(s.get("opened_by"))}, {esc(s.get("opened_at") or "")}</p>'
        items.append(row([s.get("section"), s["status"]], f'{s["id"]} {s["citation"]} {s["short"]}', meta, h, bh))
    secs = sorted({s.get("section") for s in srcs if s.get("section")})
    explorer("explore/sources/", "Sources", f"Every reference in the 0xSero repo that someone on our team opened and matched: {len(srcs)} shown, {STATS['dropped']['sources_B']} held back as Unverified.", items, secs + ["Confirmed"], "sources", extra_top='<section class="block ack"><h2>Acknowledgement</h2><p>With thanks to <strong>0xSero</strong>, whose open research report, <a href="https://github.com/0xSero/all-historical-evidence-of-jesus-christ" rel="noopener" target="_blank">All Historical Evidence of Jesus Christ</a>, gathered the references behind these explorers.</p></section>')
    # life
    items = []
    for x in sorted(D["life"], key=lambda x: x["n"]):
        refs = " ".join(verse_btn(p) for p in x["passages"])
        items.append(row([x["phase"], x["status"]], f'{x["n"]} {x["title"]} {x["short"]} {" ".join(x["passages"])}', f'{status_tag(x["status"])}<span>{x["n"]}</span><span>· {esc(x["phase"])}</span>', esc(x["title"]),
            f'<p class="small">{esc(x["short"])}</p><p class="refs small">{refs}</p><details class="sources"><summary>Go deeper</summary><p class="small">{esc(x["deep"])}</p>{cites(x.get("source_ids"), R, (x.get("url"), "0xSero repo, life of Jesus catalogue"))}</details>'))
    phases = []
    for x in sorted(D["life"], key=lambda x: x["n"]):
        if x["phase"] not in phases: phases.append(x["phase"])
    explorer("explore/life/", "Life of Jesus", f"All {len(D['life'])} units of the repo's life catalogue, in order. Framing means the passages exist and tell this unit, not that history has proven it.", items, phases, "the life of Jesus")
    # prophecy
    items = []
    for p in D["prophecy"]:
        items.append(row([p["status"]], f'{p["title"]} {" ".join(p["ot_refs"])} {" ".join(p["nt_refs"])} {p["short"]}', f'{status_tag(p["status"])}<span>{p["n"]}</span><span>· {esc(p.get("repo_rating"))}</span>', esc(p["title"]),
            f'<p class="small muted">{esc(", ".join(p["ot_refs"]))} → {esc(", ".join(p["nt_refs"]))}</p><p class="small">{esc(p["short"])}</p><details class="sources"><summary>Go deeper</summary><p class="small">{esc(p["deep"])}</p>{cites(p.get("source_ids"), R, (p.get("url"), "Passage"))}</details>'))
    explorer("explore/prophecy/", "Prophecies", f"The repo's {len(D['prophecy'])} prophecy entries. Framing: the New Testament itself makes the link. Contested: a later Christian reading or a possible allusion.", items, ["Framing", "Contested"], "prophecies")
    # gospels
    items = []
    cats = []
    for g in D["gospels"]:
        if g["category"] not in cats: cats.append(g["category"])
        items.append(row([g["category"], g["status"]], f'{g["name"]} {g["composed_text"]} {g["short"]} {g.get("witnesses","")}', f'{status_tag(g["status"])}<span>{esc(g["category"])}</span><span>· {esc(g["composed_text"])}</span>{"<span>· not a gospel</span>" if g.get("not_a_gospel") else ""}', esc(g["name"]),
            f'<p class="small">{esc(g["short"])}</p><details class="sources"><summary>Go deeper</summary><p class="small">{esc(g["deep"])}</p><p class="small muted">Today: {esc(g.get("status_today"))}. Ancient verdict: {esc(g.get("ancient_verdict"))}.</p>{cites(g.get("source_ids"), R, (g.get("url"), "0xSero repo, gospel registry"))}</details>'))
    explorer("explore/gospels/", "Gospels registry", f"{len(D['gospels'])} gospels and gospel-like texts from the repo registry, canonical and not, with their dates and ancient reception.", items, cats, "gospels")
    # dating + chart
    dat = sorted(D["dating"], key=lambda d: ((d.get("earliest") or 9999) - (d.get("event_anchor") or 30)))
    rows_svg, yy = [], 30
    W2 = 360; X0 = 120; span = 400
    sx = lambda yrs: X0 + max(0, min(yrs, span)) / span * (W2 - X0 - 10)
    for d in dat:
        if d.get("earliest") is None: continue
        a = d.get("event_anchor") or 30; e0, e1 = d["earliest"] - a, (d.get("latest") or d["earliest"]) - a
        cls = {"Contested": "is-contested", "Framing": "is-framing"}.get(d["status"], "")
        rows_svg.append(f'<g class="dchart__row {cls}"><text x="{X0 - 6}" y="{yy + 4}" text-anchor="end">{esc(d["text"][:22] + ("…" if len(d["text"]) > 22 else ""))}</text><line x1="{sx(e0):.1f}" x2="{max(sx(e1), sx(e0) + 3):.1f}" y1="{yy}" y2="{yy}"/><title>{esc(d["text"])}: {esc(d["date_text"])} ({d["status"]})</title></g>'); yy += 14
    ticks = "".join(f'<g class="dchart__tick"><line x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="18" y2="{yy}"/><text x="{sx(t):.1f}" y="12" text-anchor="middle">{t}</text></g>' for t in (0, 50, 100, 200, 300, 400))
    chart = f'<figure class="dchart"><svg viewBox="0 0 {W2} {yy + 10}" role="img" aria-labelledby="dchart-t"><title id="dchart-t">Chart of {len(rows_svg)} texts by years after the events they describe</title>{ticks}{"".join(rows_svg)}</svg><figcaption class="small muted">Years after the events (0 = the event the text describes, usually AD 30). Bars show the scholarly range; lighter bars are Contested. Ranges from the repo registry; full list below.</figcaption></figure>'
    items = []
    kinds = []
    for d in dat:
        if d["kind"] not in kinds: kinds.append(d["kind"])
        items.append(row([d["kind"], d["status"]], f'{d["text"]} {d["date_text"]} {d["short"]}', f'{status_tag(d["status"])}<span>{esc(d["kind"])}</span><span>· {esc(d["date_text"])}</span>', esc(d["text"]),
            f'<p class="small">{esc(d["short"])}</p><details class="sources"><summary>Go deeper</summary><p class="small">{esc(d["deep"])}</p>{cites(d.get("source_ids"), R, (d.get("url"), "Source"))}</details>'))
    explorer("explore/dating/", "Dating chart", "How far each text sits from the events it describes.", items, kinds, "texts", extra_top=chart)
    # explore index + credits
    tiles = [("explore/sources/", "Sources", f"{len(srcs)} repo references, opened and credited"), ("explore/life/", "Life of Jesus", f"{len(D['life'])} units"), ("explore/prophecy/", "Prophecies", f"{len(D['prophecy'])} entries"),
             ("explore/gospels/", "Gospels registry", f"{len(D['gospels'])} texts"), ("explore/dating/", "Dating chart", f"{len(D['dating'])} texts by distance from the events"), ("explore/credits/", "Attribution", "Every source we used")]
    t = "".join(f'<a class="tile reveal" href="../{r}"><div><span class="tile__n">{i:02d}</span><h3>{esc(l)}</h3><p>{esc(n)}</p></div><span class="tile__go">Explore {ARROW}</span></a>' for i, (r, l, n) in enumerate(tiles, 1))
    page("explore/", "Explore More", B.page_head("Explore More", "Everything in 0xSero's research report, sorted, searchable and credited. We link to it; we don't copy it.", [("Explore", "/explore/")], "../") + f'<div class="wrap section"><div class="grid grid--3 tiles">{t}</div></div>')
    allsrc = []
    for grp, lst in (("Resurrection data (Luke)", D["sources_A"]), ("Repo references (0xSero)", D["sources_B"]), ("Voices (Mark)", D["sources_C"])):
        li = []
        for s in lst:
            rr = S.resolve(s["id"]) if S.resolve(s["id"]).get("_origin") == "B" or s["id"] in S.rec and S.rec[s["id"]].get("_origin") == "B" else s
            rr = S.rec.get(s["id"], s) if s["id"] in S.rec and S.rec[s["id"]].get("_origin") == "B" else s
            u = S.link(rr); bk = S.backup(rr)
            li.append(f'<li>{B.link(S.label(s), u, R) if u else esc(S.label(s))}{f" · {B.link(chr(32).strip() + 'Backup copy', bk, R)}" if bk else ""} <span class="muted small">{esc(s["id"])}</span></li>')
        allsrc.append(f'<section class="block"><h2>{esc(grp)} ({len(lst)})</h2><ul class="source-list credits-list">{"".join(li)}</ul></section>')
    page("explore/credits/", "Attribution", B.page_head("Attribution", "", [("Explore", "/explore/"), ("Attribution", "/explore/credits/")], R) + f'''<div class="wrap section measure-wide"><div class="prose">
<p>Much of this site rests on the research of <strong>0xSero</strong>, whose report <a href="https://github.com/0xSero/all-historical-evidence-of-jesus-christ" rel="noopener" target="_blank">All Historical Evidence of Jesus Christ</a> gathered the references, the life catalogue, the prophecy catalogue, the gospel registry and the dating ranges used in the explorers. The repo carries no licence, so we link to it and write everything in our own words. Thank you.</p>
<p>The "Why this matters" reflections on the resurrection fact cards were drafted by <strong>Gospel Bot</strong>, with every verse checked against the Berean Standard Bible. They are reflection, not evidence, and the theory tester never counts them.</p>
<p>Below is every source our team opened and confirmed. Sources we could not open are not listed and nothing rests on them.</p></div>{"".join(allsrc)}</div>''')
    for r, l, n in tiles: index("Explore", l, r, n, snippet=n)
    return STATS
