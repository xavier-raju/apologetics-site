#!/usr/bin/env python3
"""Static site builder. No dependencies (Python 3.9+).

    python3 build.py          -> writes the whole site into ./_site/

Reads content/ (owned by section writers), data/bible/bsb.json (John), site.config.json,
and writes real folders with index.html per route, so GitHub Pages needs no rewrites.
Every internal URL is written relative to the current page, so the site works from a
project subpath (username.github.io/<repo>/).
"""
import json, re, html, shutil, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
C = ROOT / "content"
OUT = ROOT / "_site"
CFG = json.loads((ROOT / "site.config.json").read_text())
WARN = []

def jload(p, default=None):
    p = C / p
    if not p.exists():
        WARN.append(f"missing content file {p.relative_to(ROOT)}"); return default
    return json.loads(p.read_text())

def esc(s): return html.escape("" if s is None else str(s), quote=True)

# ---------------------------------------------------------------- navigation
NAV = [  # (route, label, note, show in desktop bar)
    ("start-here/", "Start here", "How to use this site", True),
    ("timeline/", "Timeline", "Life of Jesus", False),
    ("map/", "Evidence map", "Places & finds", True),
    ("witnesses/", "Outside witnesses", "Josephus, Tacitus, Pliny…", False),
    ("manuscripts/", "Manuscripts", "Was the text changed?", False),
    ("prophecy/", "Prophecy", "Old & New Testament", True),
    ("resurrection/", "Resurrection", "The core case", True),
    ("answers/", "Answer an objection", "Common questions", True),
    ("learn/", "Learn", "Lessons & quiz", False),
    ("what-others-say/", "What others say", "And how to respond", False),
    ("library/", "Library", "Every document", True),
    ("ask/", "Ask a question", "Search our answers", False),
]

CREDITS = [
    ("0xSero, All Historical Evidence of Jesus Christ (research report, linked not copied)", CFG["credit_repo"], "No license, link only"),
    ("Berean Standard Bible", "https://berean.bible/terms.htm", "Public domain"),
    ("SBL Greek New Testament", "https://sblgnt.com/license/", "CC BY 4.0"),
    ("MorphGNT", "https://github.com/morphgnt/sblgnt", "CC BY-SA 3.0"),
    ("Open Scriptures Hebrew Bible (morphhb)", "https://github.com/openscriptures/morphhb", "Text public domain; tagging CC BY 4.0"),
    ("STEPBible lexicon data", "https://github.com/STEPBible/STEPBible-Data", "CC BY 4.0"),
    ("OpenBible.info geocoding & cross-references", "https://www.openbible.info/geo/", "CC BY 4.0 / CC BY"),
    ("Pleiades gazetteer", "https://pleiades.stoa.org/", "CC BY 3.0"),
    ("BradyStephenson/bible-data", "https://github.com/BradyStephenson/bible-data", "CC BY 4.0"),
    ("Ancient texts: Whiston, Melmoth, Loeb (pre-1964 PD), ANF", "{root}library/?topic=ancient", "Public domain"),
    ("Inter & Newsreader typefaces", "https://openfontlicense.org/", "SIL OFL 1.1"),
]

# ---------------------------------------------------------------- links
def href(u, root):
    """Rewrite site routes ('/answers/x', 'answers/x/') to page-relative URLs. External links untouched."""
    if not u: return "#"
    u = str(u).strip()
    if re.match(r"^(https?:|mailto:|#)", u): return u
    if re.match(r"^[a-z]+:", u, re.I): return "#"  # block javascript: etc.
    path, _, frag = u.partition("#")
    path = path.lstrip("/")
    if path.startswith("content/") and path.endswith(".md"):
        # Content cites hosted texts by source path; map to their Library page.
        st = Path(path).stem
        if slug(st) not in HOSTED_TEXTS:
            raise SystemExit(f"BUILD FAILED: source path '{u}' does not match a hosted text in content/witnesses/texts/")
        path = f"library/{slug(st)}/"
    if path and not path.endswith("/") and "." not in path.split("/")[-1] and "?" not in path:
        path += "/"
    return root + path + (("#" + frag) if frag else "")

def ext_attrs(u):
    return ' rel="noopener" target="_blank"' if re.match(r"^https?:", str(u or "")) else ""

def link(label, u, root):
    return f'<a href="{esc(href(u, root))}"{ext_attrs(u)}>{esc(label)}</a>'

# ---------------------------------------------------------------- markdown
def front_matter(text):
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1); meta[k.strip()] = v.strip().strip('"').strip("'")
            text = text[end + 4:]
    return meta, text

def md_inline(t, root):
    t = esc(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)\*(?!\w)", r"<em>\1</em>", t)
    def lk(m):
        lab, u = m.group(1), html.unescape(m.group(2))
        return f'<a href="{esc(href(u, root))}"{ext_attrs(u)}>{lab}</a>'
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lk, t)
    def bare(m):
        u = html.unescape(m.group(1)); trail = ""
        while u and u[-1] in ".,;:)": trail = u[-1] + trail; u = u[:-1]
        return f'<a href="{esc(u)}" rel="noopener" target="_blank">{esc(short_url(u))}</a>{esc(trail)}'
    t = re.sub(r'(?<!href=")(?<![">])(https?://[^\s<]+)', bare, t)
    return t

def short_url(u):
    s = re.sub(r"^https?://(www\.)?", "", u)
    return s if len(s) < 48 else s[:45] + "…"

def md(text, root, shift=1):
    _, text = front_matter(text)
    out, para, lst, lst_t, tbl = [], [], [], None, []
    def flush():
        nonlocal para, lst, lst_t, tbl
        if para: out.append(f"<p>{md_inline(' '.join(para), root)}</p>"); para = []
        if lst: out.append(f"<{lst_t}>" + "".join(f"<li>{md_inline(i, root)}</li>" for i in lst) + f"</{lst_t}>"); lst = []
        if tbl:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl if not re.match(r"^\s*\|?\s*:?-{2,}", r)]
            if rows:
                h, *b = rows
                out.append('<div class="table-wrap"><table><thead><tr>' + "".join(f"<th scope=\"col\">{md_inline(c, root)}</th>" for c in h) + "</tr></thead><tbody>" +
                           "".join("<tr>" + "".join(f"<td>{md_inline(c, root)}</td>" for c in r) + "</tr>" for r in b) + "</tbody></table></div>")
            tbl = []
    for line in text.splitlines():
        if m := re.match(r"^(#{1,4})\s+(.*)", line):
            flush(); n = min(len(m.group(1)) + shift, 6); out.append(f"<h{n}>{md_inline(m.group(2), root)}</h{n}>"); continue
        if line.strip().startswith("|"):
            if para or lst: f = tbl; tbl = []; flush(); tbl = f
            tbl.append(line); continue
        elif tbl: flush()
        if m := re.match(r"^\s*([-*]|\d+[.)])\s+(.*)", line):
            t = "ol" if m.group(1)[0].isdigit() else "ul"
            if para or (lst and lst_t != t): flush()
            lst_t = t; lst.append(m.group(2)); continue
        if m := re.match(r"^>\s?(.*)", line):
            flush(); out.append(f'<blockquote class="pull">{md_inline(m.group(1), root)}</blockquote>'); continue
        if not line.strip(): flush(); continue
        if lst and line.startswith("  "): lst[-1] += " " + line.strip(); continue
        if lst: flush()
        para.append(line.strip())
    flush()
    return "\n".join(out).replace("</blockquote>\n<blockquote class=\"pull\">", "<br>")

# ---------------------------------------------------------------- bible
BSB = {}
def load_bible():
    p = ROOT / "data/bible/bsb.json"
    if p.exists(): BSB.update(json.loads(p.read_text()))
    else: WARN.append("data/bible/bsb.json missing: verse pop-ups disabled")
BOOK_ALIAS = {"Psalms": "Psalm", "Song of Songs": "Song of Solomon", "Matt": "Matthew", "Mk": "Mark"}
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def verses_for(ref, limit=6):
    """'Luke 2:1-7' / 'Isaiah 52:13-53:12' / 'John 9:7' -> [(ref, text)]; first segment only."""
    m = re.match(r"^\s*((?:[1-3] )?[A-Za-z ]+?)\s+(\d+):(\d+)(?:\s*[-–]\s*(?:(\d+):)?(\d+))?", ref or "")
    if not m or not BSB: return []
    book = BOOK_ALIAS.get(m.group(1).strip(), m.group(1).strip())
    c, v = int(m.group(2)), int(m.group(3))
    c2 = int(m.group(4)) if m.group(4) else c
    v2 = int(m.group(5)) if m.group(5) else v
    res = []
    while len(res) < limit:
        k = f"{book} {c}:{v}"
        if k in BSB: res.append((k, BSB[k]))
        elif f"{book} {c + 1}:1" in BSB and c < c2: c, v = c + 1, 1; continue
        else: break
        if (c, v) >= (c2, v2): break
        v += 1
    return res

def verse_btn(ref):
    vs = verses_for(ref)
    if not vs: return f'<span class="ref">{esc(ref)}</span>'
    data = json.dumps({"ref": ref, "verses": vs, "more": len(vs) == 6}, ensure_ascii=False)
    return f'<button type="button" class="verse" aria-haspopup="dialog" aria-expanded="false" data-verse="{esc(data)}">{esc(ref)}</button>'

def split_bible():
    if not BSB: return
    books = {}
    for k, t in BSB.items():
        b, cv = k.rsplit(" ", 1); books.setdefault(b, {})[cv] = t
    d = OUT / "data/bible/books"; d.mkdir(parents=True, exist_ok=True)
    for b, vs in books.items():
        (d / f"{slug(b)}.json").write_text(json.dumps(vs, ensure_ascii=False, separators=(",", ":")))
    (d / "index.json").write_text(json.dumps({b: slug(b) for b in books}, ensure_ascii=False))

# ---------------------------------------------------------------- components
def status_tag(s):
    if not s: return ""
    k = str(s).strip().lower().split()[0]
    cls = {"confirmed": "confirmed", "contested": "contested", "disputed": "disputed", "unverified": "unverified"}.get(k, "neutral")
    return f'<span class="tag tag--{cls}">{esc(str(s).strip().capitalize())}</span>'

def example_tag(o): return '<span class="tag tag--example">EXAMPLE</span>' if isinstance(o, dict) and o.get("example") else ""

def src_list(sources, root):
    items = []
    for s in sources or []:
        if isinstance(s, str):
            items.append(f"<li>{link(short_url(s), s, root) if s.startswith('http') else esc(s)}</li>")
        else:
            lab = s.get("label") or s.get("title") or s.get("name") or s.get("url")
            note = s.get("use") or s.get("note") or ""
            items.append(f"<li>{link(lab, s.get('url'), root) if s.get('url') else esc(lab)}{f'<span class=muted> · {esc(note)}</span>' if note else ''}</li>")
    return f'<ul class="source-list">{"".join(items)}</ul>' if items else ""

CHEV = '<svg class="answer__chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'
ARROW = '<span class="arrow" aria-hidden="true">→</span>'
_uid = [0]
def uid(p): _uid[0] += 1; return f"{p}-{_uid[0]}"

def tabs(items, label):
    ids = [uid("tab") for _ in items]
    head = "".join(f'<button class="tab" role="tab" type="button" id="{i}" aria-controls="{i}-p" aria-selected="{"true" if n == 0 else "false"}" tabindex="{0 if n == 0 else -1}">{esc(t)}</button>' for n, ((t, _), i) in enumerate(zip(items, ids)))
    panes = "".join(f'<div class="tabpanel" role="tabpanel" id="{i}-p" aria-labelledby="{i}" tabindex="0"{" hidden" if n else ""}>{h}</div>' for n, ((_, h), i) in enumerate(zip(items, ids)))
    return f'<div class="tabs"><div class="tabs__list" role="tablist" aria-label="{esc(label)}">{head}</div>{panes}</div>'

def page_head(title, intro, crumbs, root, eyebrow=""):
    cr = " / ".join([f'<a href="{root}">Home</a>'] + [link(l, u, root) for l, u in crumbs])
    return f'''<div class="page-head"><div class="wrap"><nav class="crumbs" aria-label="Breadcrumb">{cr}</nav>
    {f'<p class="eyebrow">{esc(eyebrow)}</p>' if eyebrow else ''}<h1>{esc(title)}</h1>{f'<p class="lede measure">{intro}</p>' if intro else ''}</div></div>'''

def answer_card(c, root, open_=False):
    bid = uid("ans")
    pt = c.get("primary_text") or {}
    body = f'''
      <div><p class="answer__label">30-second answer</p><p class="answer__short">{esc(c.get("short_answer"))}</p></div>
      <div><p class="answer__label">Evidence</p><ul class="evidence-list">{"".join(f"<li>{esc(e)}</li>" for e in c.get("evidence", []))}</ul></div>
      {f'<figure class="quote quote--inline"><blockquote>{esc(pt.get("quote"))}</blockquote><figcaption>{verse_btn(pt.get("ref",""))} · {esc(pt.get("translation",""))}</figcaption></figure>' if pt.get("quote") else ""}
      {f'<div><p class="answer__label">Still debated</p><p class="muted">{esc(c["still_debated"])}</p></div>' if c.get("still_debated") else ""}
      {f'<p class="points-to-jesus"><span class="points-to-jesus__label">Where this points</span>{md_inline(c["points_to_jesus"], root)}</p>' if c.get("points_to_jesus") else ""}
      <div><p class="answer__label">Go deeper</p><ul class="source-list">
        {f"<li>{link(c['scholarly_link'].get('name'), c['scholarly_link'].get('url'), root)}</li>" if c.get("scholarly_link") else ""}
        {"".join(f"<li>{link(s.get('name'), s.get('url'), root)}</li>" for s in c.get("see_also", []))}
        <li><a href="{root}answers/{esc(c["id"])}/">Open this answer on its own page {ARROW}</a></li></ul></div>'''
    return f'''<article class="answer reveal" id="{esc(c["id"])}" data-tags="{esc(" ".join(c.get("keywords", [])))}">
      <h2 class="answer__h"><button class="answer__head" type="button" data-toggle aria-expanded="{"true" if open_ else "false"}" aria-controls="{bid}">
        <span class="answer__rank">{esc(c.get("order", ""))}</span><span class="answer__q">{esc(c.get("objection"))}</span>{CHEV}</button></h2>
      <div class="answer__body" id="{bid}"{"" if open_ else " hidden"}>{body}</div></article>'''

# ---------------------------------------------------------------- layout
MARK = '<svg class="brand__mark" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="16" cy="16" r="13"/><path d="M16 5v22M9 13h14" stroke="#1f4fd8"/></svg>'
ICON_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/></svg>'
ICON_X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>'
ICON_S = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg>'

def layout(route, title, body, page_js=None, desc=None):
    depth = route.count("/") if route else 0
    root = "../" * depth
    cur = route.split("/")[0] + "/" if route else ""
    def a(r, inner, cls=""):
        return f'<a href="{root}{r}"{" aria-current=page" if r == cur else ""}{f" class={cls}" if cls else ""}>{inner}</a>'
    bar = "".join(f"<li>{a(r, esc(l))}</li>" for r, l, _, p in NAV if p)
    menu = "".join(f"<li>{a(r, f'<span>{esc(l)}</span><small>{esc(n)}</small>')}</li>" for r, l, n, _ in NAV)
    foot_nav = "".join(f"<li>{a(r, esc(l))}</li>" for r, l, _, _ in NAV)
    creds = "".join(f'<li>{link(n, u.replace("{root}", root), "")} <span>— {esc(l)}</span></li>' for n, u, l in CREDITS)
    full = f"{title} · {CFG['name']}" if title else f"{CFG['name']}: {CFG['subtitle']}"
    js = f'<script type="module" src="{root}assets/js/app.js"></script>'
    return f'''<!doctype html>
<html lang="en" class="no-js" data-root="{root}"{f' data-page="{page_js}"' if page_js else ""}>
<head>
<meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; font-src 'self'; connect-src 'self'; base-uri 'self'; form-action 'self'"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc or CFG['description'])}">
<meta name="theme-color" content="#ffffff">
<meta property="og:title" content="{esc(full)}"><meta property="og:description" content="{esc(desc or CFG['description'])}"><meta property="og:type" content="website"><meta property="og:site_name" content="{esc(CFG['name'])}: {esc(CFG['subtitle'])}">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{root}assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{root}assets/fonts/newsreader-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}assets/css/site.css">
<script src="{root}assets/js/nojs.js"></script>
{js}
</head>
<body{' class="is-home"' if route == "" else ""}>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap site-header__bar">
  <a class="brand" href="{root}">{MARK}<span class="brand__text"><span class="brand__name">{esc(CFG['name'])}</span><span class="brand__sub">{esc(CFG['subtitle'])}</span></span></a>
  <nav class="nav-primary" aria-label="Main"><ul>{bar}</ul></nav>
  <div class="header-actions">
    <a class="icon-btn" href="{root}ask/" aria-label="Ask a question">{ICON_S}</a>
    <button class="icon-btn menu-toggle" type="button" aria-expanded="false" aria-controls="site-menu">{ICON_MENU}<span>Menu</span></button>
  </div></div></header>
<div class="menu" id="site-menu" role="dialog" aria-modal="true" aria-label="Site menu" hidden>
  <div class="wrap menu__top"><a class="brand" href="{root}">{MARK}<span class="brand__text"><span class="brand__name">{esc(CFG['name'])}</span><span class="brand__sub">{esc(CFG['subtitle'])}</span></span></a>
  <button class="icon-btn menu-close" type="button" aria-label="Close menu">{ICON_X}</button></div>
  <div class="wrap menu__body"><nav aria-label="All sections"><ul class="menu__list">{menu}</ul></nav></div>
</div>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="site-footer"><div class="wrap"><div class="footer-grid">
  <div><p class="footer-name">{esc(CFG['name'])}</p><p class="footer-sub">{esc(CFG['subtitle'])}</p><p>{esc(CFG['tagline'])} Free to use, written in our own words, with sources you can check.</p>
  <p><strong>With thanks to 0xSero</strong>, whose research report <a href="{CFG['credit_repo']}" rel="noopener" target="_blank">All Historical Evidence of Jesus Christ</a> pointed us to many of these sources. We link to it; we don't copy it.</p></div>
  <nav aria-label="Footer"><h2>Explore</h2><ul class="footer-links">{foot_nav}</ul></nav>
  <div><h2>Sources &amp; licenses</h2><ul class="credits">{creds}</ul></div>
</div>
<p class="fine">Scripture from the Berean Standard Bible (BSB), public domain. Copyrighted books, articles and images are linked, never reproduced. A static site: no tracking, no accounts, no cookies.</p>
</div></footer>
</body></html>'''

PAGES = {}
def page(route, title, body, **kw): PAGES[route] = (title, body, kw)

# ---------------------------------------------------------------- data
SEARCH = []
def index(kind, title, url, text, kw=(), snippet="", status=""):
    SEARCH.append({"k": kind, "t": title, "u": url, "x": re.sub(r"\s+", " ", text)[:4000], "w": " ".join(kw), "s": snippet[:260], "st": status})

def build_home():
    cards = (jload("answer-cards/cards.json", {"cards": []}) or {}).get("cards", [])
    facts = (jload("manuscripts/key-facts.json", {}) or {}).get("facts", [])
    wit = (jload("witnesses/witnesses.json", {}) or {}).get("cards", [])
    root = ""
    tiles = "".join(f'''<a class="tile reveal" href="{r}"><div><span class="tile__n">{n:02d}</span><h3>{esc(l)}</h3><p>{esc(no)}</p></div><span class="tile__go">Explore {ARROW}</span></a>'''
                    for n, (r, l, no, _) in enumerate(NAV, 1))
    top = "".join(f'<li><a class="q-link" href="answers/{esc(c["id"])}/"><span>{esc(c["objection"])}</span>{ARROW}</a></li>' for c in sorted(cards, key=lambda c: c.get("order", 99))[:5])
    stats = "".join(f'<div class="stat reveal"><div class="stat__n">{esc(f.get("number"))}</div><div class="stat__l">{esc(f.get("wording"))}</div></div>' for f in facts[:3])
    q = next((w for w in wit if w.get("id") == "tacitus" and w.get("quote")), next((w for w in wit if w.get("quote")), None))
    quote = f'''<figure class="quote quote--hero reveal"><blockquote>{esc(q["quote"])}</blockquote><figcaption><strong>{esc(q["name"])}</strong>, {esc(q["work"])} · {esc(q["date_written"])}<br>{status_tag(q.get("confidence"))}</figcaption></figure>
      <p><a class="btn btn--ghost" href="witnesses/">All outside witnesses {ARROW}</a></p>''' if q else ""
    art = hero_art()
    body = f'''
<section class="hero"><div class="wrap">
  <div class="hero__inner">
    <h1 class="hero__title">{esc(CFG['name'])}</h1>
    <figure class="hero__verse"><blockquote>{re.sub(r"\b(certainty)\b", r'<strong class="hl">\1</strong>', esc(BSB.get("Luke 1:4", "")), count=1, flags=re.I)}</blockquote><figcaption>Luke 1:4 · BSB</figcaption></figure>
    <p class="lede hero__desc">{esc(CFG['hero_line'])}</p>
    <form class="ask-form" action="ask/" method="get" role="search">
      <label class="sr-only" for="hero-q">Ask a question</label>
      <div class="field">{ICON_S}<input id="hero-q" name="q" type="search" placeholder="Ask: “Didn’t Nicaea change the Bible?”" autocomplete="off" enterkeyhint="search"><button class="btn" type="submit">Ask</button></div>
    </form>
    <div class="btn-row hero__cta"><a class="btn" href="start-here/">Start here {ARROW}</a><a class="btn btn--link" href="start-here/doubting/">Have doubts? Read this first</a></div>
  </div>{art}</div></section>
<section class="section section--mist"><div class="wrap split">
  <div><p class="eyebrow">Questions people ask</p><h2>Ready answers, honest sources</h2><p class="muted">Each answer gives you something to say in thirty seconds, then the evidence behind it.</p><a class="btn btn--ghost" href="answers/">See all answers {ARROW}</a></div>
  <ol class="q-list">{top}</ol></div></section>
<section class="section"><div class="wrap"><p class="eyebrow">Explore</p><h2>Twelve ways in</h2><div class="grid grid--3 tiles">{tiles}</div></div></section>
<section class="section section--mist"><div class="wrap"><p class="eyebrow">The text we have</p><h2>Numbers that hold up</h2><div class="grid grid--3">{stats}</div><p><a href="manuscripts/">How we know the text wasn't changed {ARROW}</a></p></div></section>
<section class="section"><div class="wrap measure-wide"><p class="eyebrow">Outside the Bible</p><h2>What a Roman historian wrote</h2>{quote}</div></section>'''
    page("", "", body)

def hero_art():
    lines = "".join(f'<line pathLength="1" x1="320" y1="320" x2="{320 + 300 * __import__("math").cos(a * 3.14159 / 12):.1f}" y2="{320 + 300 * __import__("math").sin(a * 3.14159 / 12):.1f}" class="draw d{a}"/>' for a in range(24))
    return f'''<svg class="hero__art" viewBox="0 0 640 640" fill="none" stroke="currentColor" stroke-width="1" aria-hidden="true" focusable="false">
  <g opacity=".18">{lines}</g>
  <g class="orbit"><circle class="draw" pathLength="1" cx="320" cy="320" r="250"/><circle cx="570" cy="320" r="5" fill="currentColor" stroke="none"/></g>
  <circle class="draw dl3" pathLength="1" cx="320" cy="320" r="170"/>
  <circle class="draw dl6" pathLength="1" cx="320" cy="320" r="90"/>
  <path class="draw dl9" pathLength="1" d="M320 40V600M180 250H460" stroke-width="1.5"/></svg>'''

def build_start():
    p = C / "start-here/start-here.md"
    if not p.exists(): WARN.append("start-here/start-here.md missing"); return
    meta, text = front_matter(p.read_text())
    root = "../"
    # Split into H2 panels; first block (H1 + welcome) becomes the lede.
    parts = re.split(r"^## ", text, flags=re.M)
    lead = re.sub(r"^# .*$", "", parts[0], flags=re.M)
    lead = re.sub(r"^#\s.*\n", "", parts[0].strip())
    h1 = (re.search(r"^# (.*)$", parts[0], re.M) or [None, meta.get("title", "Start here")])[1]
    panels = "".join(f'<section class="panel reveal"><h2>{esc(s.splitlines()[0])}</h2>{autolink_sections(md(chr(10).join(s.splitlines()[1:]), root), root)}</section>' for s in parts[1:])
    body = page_head(h1, "", [("Start here", "/start-here/")], root) + f'<div class="wrap section"><a class="doubt-banner reveal" href="doubting/"><span><strong>Doubting?</strong> Start here instead: honest questions, no pressure.</span>{ARROW}</a><div class="prose lede-block">{md(lead, root)}</div><div class="panels">{panels}</div></div>'
    index("Guide", "Start here", "start-here/", text)
    dp = C / "start-here/doubting.md"
    if dp.exists():
        dm, dt = front_matter(dp.read_text()); rt = "../../"
        dt = re.sub(r"^# .*\n", "", dt.strip() + "\n", count=1)
        page("start-here/doubting/", dm.get("title", "Doubting? Start here"), page_head(dm.get("title", "Doubting? Start here"), esc(dm.get("summary", "")), [("Start here", "/start-here/"), ("Doubting?", "/start-here/doubting/")], rt) + f'<div class="wrap section"><div class="prose">{md(dt, rt, shift=0)}</div></div>')
        index("Guide", dm.get("title", "Doubting? Start here"), "start-here/doubting/", dt, kw=["doubt", "doubting", "faith", "struggling"], snippet=dm.get("summary", ""))
    page("start-here/", "Start here", body)

def autolink_sections(h, root):
    for r, l, _, _ in NAV:
        h = re.sub(rf'([“"]){re.escape(l)}([”"])', rf'\1<a href="{root}{r}">{esc(l)}</a>\2', h, count=1)
    return h

def build_timeline():
    ev = jload("timeline/events.json", []) or []
    places = {p["id"]: p for p in jload("evidence-map/places.json", []) or []}
    root = "../"
    cats = []
    for e in ev:
        if e.get("category") not in cats: cats.append(e.get("category"))
    chips = '<button class="chip" type="button" data-filter="*" aria-pressed="true">All</button>' + "".join(f'<button class="chip" type="button" data-filter="{esc(c)}" aria-pressed="false">{esc(str(c).capitalize())}</button>' for c in cats)
    items = []
    for e in sorted(ev, key=lambda e: (e.get("date_start", 0), e.get("date_end", 0))):
        refs = " ".join(verse_btn(r) for r in e.get("scripture_refs", []))
        pl = ", ".join(link(places[p]["name"], f"/map/#place-{p}", root) for p in e.get("related_places", []) if p in places)
        items.append(f'''<li class="timeline__item reveal" id="{esc(e["id"])}" data-tags="{esc(e.get("category"))}">
          <p class="timeline__date">{esc(e.get("date_display"))}{' <span class="timeline__approx">(approx.)</span>' if e.get("approximate") else ""} <span class="tag tag--neutral">{esc(e.get("category"))}</span> {status_tag(e.get("status"))}</p>
          <h2 class="timeline__title">{esc(e.get("title"))}</h2><p>{esc(e.get("summary"))}</p>
          {f'<p class="refs"><span class="muted">Read:</span> {refs}</p>' if refs else ""}
          {f'<p class="muted small">Places: {pl}</p>' if pl else ""}
          <details class="sources"><summary>Sources</summary>{src_list(e.get("sources"), root)}</details></li>''')
        index("Timeline", e.get("title"), f"timeline/#{e['id']}", f"{e.get('summary')} {' '.join(e.get('scripture_refs', []))}", snippet=e.get("summary", ""), status=e.get("status", ""))
    body = page_head("Life of Jesus timeline", "From his birth to the earliest witnesses and manuscripts. Dates marked approx. are scholarly estimates.", [("Timeline", "/timeline/")], root) + f'''
    <div class="wrap section"><div class="filterable" data-filter-scope>
      <div class="chips" role="group" aria-label="Filter by category">{chips}</div><p class="muted small" data-filter-count aria-live="polite"></p>
      <ol class="timeline">{"".join(items)}</ol></div></div>'''
    page("timeline/", "Timeline", body)

def build_map():
    places = jload("evidence-map/places.json", []) or []
    finds = jload("evidence-map/finds.json", []) or []
    root = "../"
    pts = [p for p in places if isinstance(p.get("lat"), (int, float)) and isinstance(p.get("lon"), (int, float))]
    by_place = {}
    for f in finds: by_place.setdefault(f.get("place_id"), []).append(f)
    short = lambda n: re.sub(r",\s*Jerusalem$", "", re.split(r"\s+\(", n)[0]).strip()
    cnt = lambda pid: len(by_place.get(pid, []))
    ftxt = lambda n: f"{n} find" + ("" if n == 1 else "s") if n else "no finds catalogued yet"
    REG = {"Jerusalem": "judea", "Judea": "judea", "Galilee": "galilee", "Coast": "galilee", "Wider world": "world"}
    NODOT = {"siloam", "bethesda", "golgotha"}  # sites inside Jerusalem: label rows only, no dot
    AREA = {"bithynia"}                          # regions, drawn as a soft dashed area
    def region(p): return REG.get(p.get("region"), "world")
    W, ROW = 400, 62
    def cross(a, b, c, d):
        o = lambda p, q, r: (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0
    def km(a, b):
        import math
        x = math.radians(b["lon"] - a["lon"]) * math.cos(math.radians((a["lat"] + b["lat"]) / 2)); y = math.radians(b["lat"] - a["lat"])
        return 6371 * math.hypot(x, y)
    def panel(key, title, ps, extra=None, note=""):
        # Dots sit in a central band; labels sit in two side columns joined by hairline leader lines.
        # Only the label rows are tap targets, and rows never overlap. Rows are then reordered so no leader lines cross.
        if not ps: return ""
        geo = [p for p in ps if p["id"] not in NODOT] or ps
        la0, la1 = min(p["lat"] for p in geo), max(p["lat"] for p in geo); lo0, lo1 = min(p["lon"] for p in geo), max(p["lon"] for p in geo)
        if extra: la0, la1, lo0, lo1 = min(la0, extra[0]), max(la1, extra[0]), min(lo0, extra[1]), max(lo1, extra[1])
        dl, dlo = (la1 - la0) or 1, (lo1 - lo0) or 1
        order = sorted(ps, key=lambda p: (p["id"] in NODOT, p["lon"]))
        bp_ = {p["id"]: p for p in ps}; xy_ = lambda p: 166 + (p["lon"] - lo0) / dlo * 68
        dotted = [p for p in order if p["id"] not in NODOT]; half = (len(dotted) + 1) // 2
        side = {p["id"]: ("L" if i < half else "R") for i, p in enumerate(dotted)}
        if "jerusalem" in side and any(p["id"] in NODOT for p in ps):
            side["jerusalem"] = "R" if xy_(bp_[ "jerusalem"]) > 200 else "L"  # put Jerusalem (and its sites) on the side nearest its dot
        for p in order:  # label-only rows sit with Jerusalem, so they never land beside another place's dot
            if p["id"] in NODOT: side[p["id"]] = side.get("jerusalem") or ("L" if sum(v == "L" for v in side.values()) <= sum(v == "R" for v in side.values()) else "R")
        nrows = max(sum(1 for v in side.values() if v == "L"), sum(1 for v in side.values() if v == "R"))
        H = max(220, nrows * ROW + 60)
        xy = lambda lat, lon: (166 + (lon - lo0) / dlo * 68, 40 + (la1 - lat) / dl * (H - 80))
        pos = {p["id"]: list(xy(p["lat"], p["lon"])) for p in ps}
        mk = xy(*extra) if extra else None
        if mk:  # keep dots clear of the region marker
            for k, v in pos.items():
                dx, dy = v[0] - mk[0], v[1] - mk[1]; dd = (dx * dx + dy * dy) ** .5
                if dd < 34: f = 34 / (dd or 1); v[0], v[1] = mk[0] + (dx or 1) * f, mk[1] + (dy or -1) * f
        out = []
        for sd in "LR":
            # dotted rows ordered by dot y; label-only rows go next to Jerusalem's row
            col = sorted([p for p in ps if side[p["id"]] == sd and p["id"] not in NODOT], key=lambda p: pos[p["id"]][1])
            for p in sorted([p for p in ps if side[p["id"]] == sd and p["id"] in NODOT], key=lambda p: -p["lat"]):
                j = next((i for i, q in enumerate(col) if q["id"] == "jerusalem"), None)
                col.insert(j + 1 if j is not None else len(col), p)
            ys, prev = [], 4 - ROW
            for p in col:
                y = max(pos[p["id"]][1] - ROW / 2, prev + ROW); ys.append(y); prev = y
            over = (ys[-1] + ROW) - (H - 4) if ys else 0
            if over > 0: ys = [y - over for y in ys]
            for i in range(1, len(ys)): ys[i] = max(ys[i], ys[i - 1] + ROW)
            ex = 150 if sd == "L" else 250
            rowy = {p["id"]: y for p, y in zip(col, ys)}
            dots = [p["id"] for p in col if p["id"] not in NODOT]
            for _ in range(50):  # swap rows of crossing leaders until none cross
                done = True
                for i in range(len(dots)):
                    for j in range(i + 1, len(dots)):
                        a, b = dots[i], dots[j]
                        if cross((ex, rowy[a] + ROW / 2), pos[a], (ex, rowy[b] + ROW / 2), pos[b]): rowy[a], rowy[b] = rowy[b], rowy[a]; done = False
                if done: break
            for p in col:
                y = rowy[p["id"]]; x, py = pos[p["id"]]; n = cnt(p["id"]); cy = y + ROW / 2
                lx0, lx1 = (4, 150) if sd == "L" else (250, 396)
                tx, anc = (12, "start") if sd == "L" else (388, "end")
                nd, ar = p["id"] in NODOT, p["id"] in AREA
                sub = (ftxt(n) if n else "no finds yet") + (" · in Jerusalem" if nd else "") + (" · region" if ar else "")
                mark = "" if nd else (f'<line class="lead" x1="{ex}" y1="{cy:.1f}" x2="{x - (14 if ar and sd == "R" else -14 if ar else 0):.1f}" y2="{py:.1f}"/><ellipse class="area" cx="{x:.1f}" cy="{py:.1f}" rx="14" ry="9"/>' if ar else
                    f'<line class="lead" x1="{ex}" y1="{cy:.1f}" x2="{x:.1f}" y2="{py:.1f}"/><circle class="halo" cx="{x:.1f}" cy="{py:.1f}" r="{7 if n else 6}"/><circle class="dot" cx="{x:.1f}" cy="{py:.1f}" r="{3.5 if n else 2.8}"/>')
                out.append(f'''<g class="map__pin{" is-empty" if not n else ""}{" is-area" if ar else ""}" data-place="{esc(p["id"])}" data-count="{n}">{mark}
          <rect class="hit" x="{lx0}" y="{y + 1:.1f}" width="{lx1 - lx0}" height="{ROW - 2}" rx="6"/>
          <text class="map__label" x="{tx}" y="{cy - 3:.1f}" text-anchor="{anc}">{esc(short(p["name"]))}</text><text class="map__count" x="{tx}" y="{cy + 15:.1f}" text-anchor="{anc}">{esc(sub)}</text></g>''')
        if mk:
            out.append(f'<g class="map__region"><circle cx="{mk[0]:.1f}" cy="{mk[1]:.1f}" r="12"/><text x="{mk[0]:.1f}" y="{mk[1] + 28:.1f}" text-anchor="middle">Judea &amp; Galilee</text></g>')
        return f'<figure class="map__panel"><figcaption class="map__title">{esc(title)}</figcaption><svg viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false">{"".join(out)}</svg>{f'<p class="map__aside">{esc(note)}</p>' if note else ""}</figure>'
    groups = {k: [p for p in pts if region(p) == k] for k in ("galilee", "judea", "world")}
    bp = {p["id"]: p for p in pts}; gnote = ""
    if all(k in bp for k in ("capernaum", "el-araj", "et-tell")):
        far = max(km(bp[a], bp[b]) for a, b in (("capernaum", "el-araj"), ("capernaum", "et-tell"), ("el-araj", "et-tell")))
        gnote = f"These dots really are close: Capernaum, el-Araj and et-Tell lie within about {round(far)} km of each other, and el-Araj and et-Tell are about {round(km(bp['el-araj'], bp['et-tell']))} km apart."
    svg = panel("galilee", "Galilee and the coast", groups["galilee"], note=gnote) + panel("judea", "Jerusalem and Judea", groups["judea"]) + panel("world", "The wider Roman world", groups["world"], extra=(32.2, 35.2))
    RORDER = ["Jerusalem", "Judea", "Galilee", "Coast", "Wider world"]
    def pbtn(p):
        n = cnt(p["id"]); extra_ = " · river, not pinned" if p["id"] not in {q["id"] for q in pts} else ""
        return f'<li><button class="place-btn" type="button" data-place="{esc(p["id"])}" data-count="{n}" aria-pressed="false"><span class="place-btn__name">{esc(short(p["name"]))}</span><span class="place-btn__n">{esc(ftxt(n))}{esc(extra_)}</span></button></li>'
    plist = ""
    for r in RORDER + sorted({p.get("region") or "Other" for p in places} - set(RORDER)):
        ps_ = [p for p in places if (p.get("region") or "Other") == r]
        if not ps_: continue
        hid = "places-" + slug(r)
        plist += f'<section class="place-group" aria-labelledby="{hid}"><h3 class="place-group__h" id="{hid}">{esc(r)}</h3><ul class="place-list">{"".join(pbtn(p) for p in ps_)}</ul></section>'
    svg += f'<div class="places"><h2 class="h-sm">Places</h2>{plist}</div>'
    cards = []
    pname = {p["id"]: p["name"] for p in places}
    for f in finds:
        cards.append(f'''<article class="card find reveal" id="find-{esc(f["id"])}" data-tags="{esc(f.get("place_id") or "none")}">
          <div class="card__meta">{status_tag(f.get("status"))}<span>{esc(pname.get(f.get("place_id"), "Location not mapped"))}</span><span>· {esc(f.get("era"))}</span></div>
          <h2 class="card__title">{esc(f.get("name"))}</h2><p>{esc(f.get("summary"))}</p>
          <dl class="shows"><div><dt>What it shows</dt><dd>{esc(f.get("shows"))}</dd></div><div><dt>What it doesn't prove</dt><dd>{esc(f.get("does_not_prove"))}</dd></div></dl>
          <details class="sources"><summary>Sources</summary>{src_list(f.get("sources"), root)}</details></article>''')
        index("Evidence map", f.get("name"), f"map/#find-{f['id']}", f"{f.get('summary')} {f.get('shows')} {f.get('does_not_prove')}", snippet=f.get("shows", ""), status=f.get("status", ""))
    anchors = "".join(f'<span id="place-{esc(p["id"])}"></span>' for p in places)
    body = page_head("Evidence map", "Places and finds from the world of the Gospels. Each find says what it shows and what it doesn't prove.", [("Evidence map", "/map/")], root) + f'''
    <div class="wrap section" data-filter-scope>{anchors}<div class="map-layout">
      <div class="map" data-map>{svg}<p class="map__note">Schematic, in three panels. Positions from OpenBible.info and Pleiades; not to survey scale.</p></div>
      <div><div class="map-status"><p class="muted small" data-filter-count aria-live="polite"></p><button class="btn btn--ghost btn--sm" type="button" data-filter="*" aria-pressed="true">Show all finds</button></div>
      <p class="empty" data-filter-empty data-map-empty hidden>No finds catalogued here yet.</p><div class="stack finds">{"".join(cards)}</div></div></div></div>'''
    page("map/", "Evidence map", body, page_js="map")

def build_witnesses():
    d = jload("witnesses/witnesses.json", {}) or {}
    root = "../"
    intro = (C / "witnesses/intro.md").read_text() if (C / "witnesses/intro.md").exists() else ""
    cards = []
    for w in d.get("cards", []):
        ft = w.get("full_text"); ft = [ft] if isinstance(ft, str) else (ft or [])
        q = f'<blockquote>{esc(w["quote"])}</blockquote>' if w.get("quote") else f'<p class="paraphrase"><span class="tag tag--neutral">Our paraphrase</span> {esc(w.get("paraphrase"))}</p>'
        cards.append(f'''<figure class="quote witness reveal" id="{esc(w["id"])}">
          <div class="card__meta">{status_tag(w.get("confidence"))}<span>{esc(w.get("date_written"))}</span>{f"<span>· {esc(w['years_after_cross'])} years after the cross</span>" if w.get("years_after_cross") else ""}</div>
          {q}<figcaption><strong>{esc(w.get("name"))}</strong> · {esc(w.get("work"))}<br><span>{esc(w.get("stance"))}</span>{f" · tr. {esc(w['translator'])}" if w.get("translator") else ""}</figcaption>
          {f'<p class="muted small">{esc(w["framing"])}</p>' if w.get("framing") else ""}
          <dl class="shows"><div><dt>What it shows</dt><dd>{esc(w.get("shows"))}</dd></div><div><dt>What it doesn't prove</dt><dd>{esc(w.get("does_not_prove"))}</dd></div></dl>
          <details class="sources"><summary>Scholarly status</summary><p>{esc(w.get("scholarly_status"))}</p>{f"<p class=muted>{esc(w['confidence_note'])}</p>" if w.get("confidence_note") else ""}</details>
          <div class="btn-row">{"".join(f'<a class="btn btn--ghost btn--sm" href="../library/{slug(Path(t).stem)}/">Read the full text {ARROW}</a>' for t in ft)}{f'<a class="btn btn--link btn--sm" href="{esc(w["source_url"])}" rel="noopener" target="_blank">Online source</a>' if w.get("source_url") else ""}</div></figure>''')
        index("Witness", w.get("name"), f"witnesses/#{w['id']}", f"{w.get('work')} {w.get('quote') or w.get('paraphrase')} {w.get('shows')}", snippet=w.get("shows", ""), status=w.get("confidence", ""))
    body = page_head("Outside witnesses", "", [("Outside witnesses", "/witnesses/")], root) + f'''
    <div class="wrap section"><div class="prose">{md(intro, root)}</div>{f'<p class="muted small">{esc(d.get("assumption"))}</p>' if d.get("assumption") else ""}
    <div class="grid grid--2 witnesses">{"".join(cards)}</div></div>'''
    page("witnesses/", "Outside witnesses", body)
    # Full-text pages for each hosted public-domain text.
    for p in sorted((C / "witnesses/texts").glob("*.md")):
        meta, text = front_matter(p.read_text())
        r = f"library/{slug(p.stem)}/"; rt = "../../"
        info = f'''<dl class="meta-list"><div><dt>Translation</dt><dd>{esc(meta.get("translation"))}</dd></div><div><dt>License</dt><dd>{esc(meta.get("license"))}</dd></div>
          <div><dt>Online source</dt><dd>{link(short_url(meta.get("source_url", "")), meta.get("source_url"), rt)}</dd></div><div><dt>Retrieved</dt><dd>{esc(meta.get("retrieved"))}</dd></div></dl>'''
        body = page_head(meta.get("title", p.stem), "Full text, public domain.", [("Library", "/library/"), (meta.get("title", p.stem), "/" + r)], rt) + f'<div class="wrap section"><div class="prose reading">{info}{md(text, rt)}</div><p class="btn-row"><a class="btn btn--ghost btn--sm" href="{rt}{r}{p.name}" download>Download (.md)</a><a class="btn btn--ghost btn--sm" href="{rt}witnesses/">Back to outside witnesses</a></p></div>'
        page(r, meta.get("title", p.stem), body, copy=(p, p.name))
        LIB_HOSTED.append({"id": "text-" + slug(p.stem), "title": meta.get("title", p.stem), "author": meta.get("translation", ""), "topic": "ancient", "kind": "Ancient text", "access": "hosted", "license": "Public domain", "url": "/" + r, "description": f"Full text. {meta.get('translation','')}"})
        index("Library", meta.get("title", p.stem), r, text[:3000], snippet="Full public-domain text")
LIB_HOSTED = []
HOSTED_TEXTS = {slug(p.stem) for p in (C / "witnesses/texts").glob("*.md")}

def build_manuscripts():
    root = "../"
    facts = (jload("manuscripts/key-facts.json", {}) or {}).get("facts", [])
    show = (jload("manuscripts/showcase.json", {}) or {}).get("manuscripts", [])
    myths = (jload("manuscripts/myths.json", {}) or {}).get("myths", [])
    rd = lambda n: (C / f"manuscripts/{n}").read_text() if (C / f"manuscripts/{n}").exists() else ""
    st = "".join(f'''<div class="stat reveal"><div class="stat__n">{esc(f.get("number"))}</div><div class="stat__l">{esc(f.get("wording"))}</div>
        <div class="card__meta">{status_tag(f.get("confidence"))}{link("Source", f.get("url"), root) if f.get("url") else esc(f.get("source"))}</div>
        {f'<details class="sources"><summary>Detail</summary><p>{esc(f["detail"])}</p></details>' if f.get("detail") else ""}</div>''' for f in facts)
    sh = "".join(f'''<article class="card reveal" id="{esc(m["id"])}"><div class="card__meta">{status_tag(m.get("confidence"))}<span>{esc(m.get("date_range"))}</span></div>
        <h3 class="card__title">{esc(m.get("name"))}</h3><p>{esc(m.get("contents"))}</p><p class="muted small">{esc(m.get("holding"))}</p>
        <dl class="shows"><div><dt>What it shows</dt><dd>{esc(m.get("shows"))}</dd></div><div><dt>Careful</dt><dd>{esc(m.get("caution"))}</dd></div></dl>
        {f'<p>{link("View images (owner site)", m["image_link"], root)}</p>' if m.get("image_link") else ""}
        <details class="sources"><summary>Sources</summary>{src_list(m.get("sources"), root)}</details></article>''' for m in show)
    my = "".join(f'<li class="myth reveal"><p class="myth__claim"><span class="tag tag--disputed">We don\'t use</span> {esc(m.get("claim"))}</p><p>{esc(m.get("why"))}</p><p><strong>Say instead:</strong> {esc(m.get("use_instead"))}</p></li>' for m in myths)
    for f in facts: index("Manuscripts", f.get("number"), f"manuscripts/#{f['id']}", f.get("wording", ""), snippet=f.get("wording", ""), status=f.get("confidence", ""))
    for m in show: index("Manuscripts", m.get("name"), f"manuscripts/#{m['id']}", f"{m.get('contents')} {m.get('shows')}", snippet=m.get("shows", ""))
    body = page_head("Manuscripts", "How we know the text wasn't changed, using numbers that hold up.", [("Manuscripts", "/manuscripts/")], root) + f'''
    <div class="wrap section"><div class="prose">{md(rd("intro.md"), root)}</div><h2>Key facts</h2><div class="grid grid--3">{st}</div></div>
    <section class="section section--mist"><div class="wrap"><h2>Manuscripts to know</h2><div class="grid grid--2">{sh}</div></div></section>
    <div class="wrap section"><div class="prose">{md(rd("what-changed.md"), root)}</div></div>
    {f'<section class="section section--mist"><div class="wrap"><h2>Numbers you may hear that we don’t use</h2><ul class="myths">{my}</ul></div></section>' if my else ""}'''
    page("manuscripts/", "Manuscripts", body)

def word_btn(w):
    lang = "he" if str(w.get("lang", "")).startswith("heb") else "grc"
    occ = w.get("occurrence") or {}
    data = {"orig": occ.get("surface") or w.get("lemma"), "lemma": w.get("lemma"), "lang": lang, "translit": w.get("transliteration"), "gloss": w.get("gloss"),
            "strongs": w.get("strongs"), "note": (w.get("definition") or "")[:220], "morph": occ.get("morphology"), "where": occ.get("ref")}
    if not data["orig"]:
        data["orig"] = w.get("transliteration") or w.get("gloss") or w.get("id"); data["lang"] = lang = "en"
        WARN.append(f"prophecy word {w.get('id')} has no Hebrew/Greek form; showing transliteration")
    lab = f"{data['orig']}: {w.get('gloss') or ''}. Show word details"
    return f'''<button type="button" class="word-chip" aria-label="{esc(lab)}" aria-haspopup="dialog" aria-expanded="false" data-word="{esc(json.dumps(data, ensure_ascii=False))}">
      <span class="word-chip__orig" lang="{lang}" dir="{"rtl" if lang == "he" else "ltr"}">{esc(data["orig"])}</span><span class="word-chip__gloss">{esc(w.get("gloss"))}</span></button>'''

def verses_html(block):
    vs = block.get("verses") or [{"ref": r, "text": t} for r, t in verses_for(block.get("ref", ""), 30)]
    return "".join(f'<p class="verse-line"><sup>{esc(v["ref"].rsplit(":", 1)[-1])}</sup> {esc(v["text"])}</p>' for v in vs)

def build_prophecy():
    root = "../"
    P = jload("prophecy/prophecies.json", {}) or {}
    words = (jload("prophecy/words.json", {}) or {}).get("words", {})
    xr = (jload("prophecy/crossrefs.json", {}) or {}).get("crossrefs", {})
    labels = (P.get("meta") or {}).get("strength_labels", {})
    items = P.get("prophecies", [])
    cats = []
    for p in items:
        if p.get("category") not in cats: cats.append(p.get("category"))
    chips = '<button class="chip" type="button" data-filter="*" aria-pressed="true">All</button>' + "".join(f'<button class="chip" type="button" data-filter="{slug(c or "")}" aria-pressed="false">{esc(c)}</button>' for c in cats)
    cards = "".join(f'''<article class="card card--link reveal" data-tags="{slug(p.get("category") or "")}"><div class="card__meta"><span class="tag tag--neutral">{esc(p.get("strength"))}</span>{status_tag("Contested") if p.get("contested") else ""}</div>
      <h2 class="card__title"><a href="{esc(p["id"])}/">{esc(p.get("title"))}</a></h2><p class="muted">{esc((p.get("ot") or {}).get("ref"))} → {esc(", ".join(n.get("ref", "") for n in p.get("nt", [])[:2]))}</p></article>''' for p in items)
    legend = "".join(f"<div><dt>{esc(k.capitalize())}</dt><dd>{esc(v)}</dd></div>" for k, v in labels.items())
    body = page_head("Prophecy explorer", "Each passage: the Old Testament text, its New Testament fulfillment, the original words, and the traditional Jewish reading shown fairly beside the Christian one.", [("Prophecy", "/prophecy/")], root) + f'''
    <div class="wrap section" data-filter-scope><details class="sources legend"><summary>What the labels mean</summary><dl class="shows">{legend}</dl></details>
    <div class="chips" role="group" aria-label="Filter by theme">{chips}</div><p class="muted small" data-filter-count aria-live="polite"></p><div class="grid grid--3">{cards}</div></div>'''
    page("prophecy/", "Prophecy explorer", body)
    for p in items:
        rt = "../../"; ot = p.get("ot") or {}
        nt_tabs = [(n.get("ref", "NT"), verses_html(n)) for n in p.get("nt", [])]
        ws = "".join(word_btn(words[i]) for i in p.get("word_ids", []) if i in words)
        x = xr.get(p["id"], {}).get("refs", [])
        xh = "".join(f'<li><span>{esc(r.get("to"))}</span> <span class="muted small">{esc(r.get("votes"))} votes</span></li>' for r in x[:10])
        read = tabs([("Christian reading", f"<p>{esc(p.get('why_christians_read_it_this_way'))}</p>"), ("Traditional Jewish reading", f"<p>{esc(p.get('traditional_jewish_reading'))}</p>")], "Readings")
        body = page_head(p.get("title"), "", [("Prophecy", "/prophecy/"), (p.get("title"), f"/prophecy/{p['id']}/")], rt, eyebrow=p.get("category", "")) + f'''
        <div class="wrap section"><div class="card__meta"><span class="tag tag--neutral">{esc(p.get("strength"))}</span>{status_tag("Contested") if p.get("contested") else ""}</div>
        <div class="prophecy-pair">
          <section class="card"><p class="eyebrow">Old Testament · {esc(ot.get("ref"))}</p><div class="scripture">{verses_html(ot)}</div></section>
          <section class="card"><p class="eyebrow">New Testament</p>{tabs(nt_tabs, "Fulfillment passages") if nt_tabs else ""}</section></div>
        {f'<section class="block"><h2>The original words</h2><p class="muted">Tap a word to see its meaning.</p><div class="word-chips">{ws}</div></section>' if ws else ""}
        <section class="block"><h2>Two readings, fairly stated</h2>{read}{f'<p class="note"><strong>Note.</strong> {esc(p["note"])}</p>' if p.get("note") else ""}</section>
        {f'<section class="block"><h2>Cross-references</h2><p class="muted small">From OpenBible.info (CC BY): verses readers most link to this passage.</p><ul class="xrefs">{xh}</ul></section>' if xh else ""}
        <section class="block"><h2>Sources</h2>{src_list(p.get("sources"), rt)}<p class="muted small">Scripture: Berean Standard Bible (public domain).</p></section>
        <p><a class="btn btn--ghost" href="../">All prophecies {ARROW}</a></p></div>'''
        page(f"prophecy/{p['id']}/", p.get("title"), body)
        index("Prophecy", p.get("title"), f"prophecy/{p['id']}/", f"{ot.get('ref')} {p.get('why_christians_read_it_this_way')} {p.get('traditional_jewish_reading')} {p.get('category')}", snippet=p.get("why_christians_read_it_this_way", ""))

def build_resurrection():
    p = C / "resurrection/resurrection.md"
    root = "../"
    if not p.exists(): WARN.append("resurrection.md missing"); return
    meta, text = front_matter(p.read_text())
    text = re.sub(r"^# .*\n", "", text.strip() + "\n", count=1)
    body = page_head(meta.get("title", "The resurrection"), esc(meta.get("summary", "")), [("Resurrection", "/resurrection/")], root) + f'<div class="wrap section"><div class="prose">{md(text, root, shift=0)}</div></div>'
    index("Resurrection", meta.get("title", "The resurrection"), "resurrection/", text, kw=["rise", "risen", "empty tomb", "easter"], snippet=meta.get("summary", ""))
    page("resurrection/", "The resurrection", body)

def build_answers():
    d = jload("answer-cards/cards.json", {"cards": []}) or {"cards": []}
    cards = sorted(d.get("cards", []), key=lambda c: c.get("order", 99))
    root = "../"
    body = page_head("Answer an objection", "The questions people ask most. Each card gives a 30-second answer, the evidence, and where to go deeper.", [("Answer an objection", "/answers/")], root) + f'''
    <div class="wrap section"><div class="answers-tools"><a class="btn btn--ghost btn--sm" href="../ask/">Search instead {ARROW}</a><button class="btn btn--link" type="button" data-expand-all aria-pressed="false">Expand all</button></div>
    <div class="stack answers">{"".join(answer_card(c, root) for c in cards)}</div></div>'''
    page("answers/", "Answer an objection", body)
    byid = {c["id"]: c for c in cards}
    for c in cards:
        rt = "../../"
        rel = "".join(f'<li><a href="../{esc(r)}/">{esc(byid[r]["objection"])}</a></li>' for r in c.get("related", []) if r in byid)
        body = page_head(c.get("objection"), "", [("Answer an objection", "/answers/"), (f"Question {c.get('order')}", f"/answers/{c['id']}/")], rt, eyebrow="Answer an objection") + f'''
        <div class="wrap section measure-wide">{answer_card(c, rt, open_=True)}{f'<section class="block"><h2>Related questions</h2><ul class="source-list">{rel}</ul></section>' if rel else ""}
        <p><a class="btn btn--ghost" href="../">All answers {ARROW}</a></p></div>'''
        page(f"answers/{c['id']}/", c.get("objection", "")[:60], body, desc=c.get("short_answer"))
        index("Answer", c.get("objection"), f"answers/{c['id']}/", f"{c.get('short_answer')} {' '.join(c.get('evidence', []))}", kw=c.get("keywords", []), snippet=c.get("short_answer", ""))

def build_learn():
    root = "../"
    les = []
    for n, p in enumerate(sorted((C / "learn/lessons").glob("*.md")), 1):
        meta, text = front_matter(p.read_text())
        bid = uid("les")
        les.append(f'''<article class="answer lesson reveal" id="{slug(p.stem)}"><h2 class="answer__h"><button class="answer__head" type="button" data-toggle aria-expanded="false" aria-controls="{bid}">
          <span class="answer__rank">{n}</span><span class="answer__q">{esc(meta.get("title", p.stem))}<span class="muted small lesson__min"> · {esc(meta.get("minutes", "?"))} min</span></span>{CHEV}</button></h2>
          <div class="answer__body prose" id="{bid}" hidden>{md(text, root)}</div></article>''')
        index("Lesson", meta.get("title", p.stem), f"learn/#{slug(p.stem)}", text, snippet=text.strip()[:200])
    quiz = jload("learn/quiz.json", {}) or {}
    for q in quiz.get("questions", []):
        if q.get("source"): q["source"] = href(q["source"], root)
    qjson = json.dumps(quiz, ensure_ascii=False).replace("</", "<\\/")
    body = page_head("Learn", "Short lessons, then a quick quiz to see what stuck.", [("Learn", "/learn/")], root) + f'''
    <div class="wrap section"><h2>Lessons</h2><div class="stack">{"".join(les)}</div></div>
    <section class="section section--mist" id="quiz"><div class="wrap measure-wide"><p class="eyebrow">Quiz</p><h2>Check yourself</h2>
      <div class="quiz card" data-quiz><p class="muted">Loading quiz…</p></div><script type="application/json" id="quiz-data">{qjson}</script></div></section>'''
    page("learn/", "Learn", body, page_js="quiz")

def build_others():
    d = jload("what-others-say/perspectives.json", {}) or {}
    root = "../"
    groups = []
    for p in d.get("perspectives", []):
        if p.get("group") not in groups: groups.append(p.get("group"))
    chips = '<button class="chip" type="button" data-filter="*" aria-pressed="true">All</button>' + "".join(f'<button class="chip" type="button" data-filter="{slug(g or "")}" aria-pressed="false">{esc(g)}</button>' for g in groups)
    cards = []
    for p in d.get("perspectives", []):
        cards.append(f'''<article class="card reveal" id="{esc(p["id"])}" data-tags="{slug(p.get("group") or "")}"><div class="card__meta"><span class="tag tag--neutral">{esc(p.get("group"))}</span></div>
          <h2 class="card__title">{esc(p.get("title"))}</h2>
          {tabs([("What they say", f"<p>{esc(p.get('their_view'))}</p>"), ("How to respond", f"<p>{esc(p.get('how_to_respond'))}</p>"), ("Common ground", "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in p.get("common_ground", [])) + "</ul>")], p.get("title", ""))}
          {src_list(p.get("links"), root)}</article>''')
        index("Others say", p.get("title"), f"what-others-say/#{p['id']}", f"{p.get('their_view')} {p.get('how_to_respond')}", snippet=p.get("how_to_respond", ""))
    pr = "".join(f"<li>{esc(x)}</li>" for x in d.get("principles", []))
    body = page_head("What others say, and how to respond", "Views from skeptics, other religions and groups outside historic Christianity, described as their own followers would, with a gracious response.", [("What others say", "/what-others-say/")], root) + f'''
    <div class="wrap section" data-filter-scope>{f'<details class="sources legend" open><summary>Our principles</summary><ul>{pr}</ul></details>' if pr else ""}
    <div class="chips" role="group" aria-label="Filter by group">{chips}</div><p class="muted small" data-filter-count aria-live="polite"></p><div class="grid grid--2">{"".join(cards)}</div></div>'''
    page("what-others-say/", "What others say", body)

def build_library():
    d = jload("library/index.json", {}) or {}
    root = "../"
    items = LIB_HOSTED + d.get("items", [])
    topics = d.get("topics", [])
    tl = {t["id"]: t["label"] for t in topics}
    chips = '<button class="chip" type="button" data-filter="*" aria-pressed="true">All topics</button>' + "".join(f'<button class="chip" type="button" data-filter="{esc(t["id"])}" aria-pressed="false">{esc(t["label"])}</button>' for t in topics if any(i.get("topic") == t["id"] for i in items))
    rows = []
    for i in sorted(items, key=lambda i: (i.get("topic", ""), i.get("title", ""))):
        hosted = i.get("access") == "hosted"
        rows.append(f'''<li class="lib-item" data-tags="{esc(i.get("topic"))}" data-access="{"hosted" if hosted else "link"}" data-text="{esc((i.get("title","") + " " + i.get("author","") + " " + i.get("description","") + " " + " ".join(i.get("keywords", []))).lower())}">
          <div><div class="card__meta">{example_tag(i)}<span class="tag tag--{"hosted" if hosted else "link"}">{"Hosted here" if hosted else "Link only"}</span><span>{esc(tl.get(i.get("topic"), i.get("topic")))}</span><span>· {esc(i.get("kind"))}</span><span>· {esc(i.get("license"))}</span></div>
          <h2 class="lib-item__title">{link(i.get("title"), i.get("url"), root)}</h2><p class="muted small">{esc(i.get("author"))}{" · " + esc(i.get("date")) if i.get("date") else ""}</p><p class="small">{esc(i.get("description"))}</p></div>
          <a class="btn {"" if hosted else "btn--ghost"} btn--sm" href="{esc(href(i.get("url"), root))}"{ext_attrs(i.get("url"))}>{"Read" if hosted else "Visit source"} {ARROW}</a></li>''')
        if not str(i.get("id", "")).startswith("text-"):
            index("Library", i.get("title"), "library/?q=" + re.sub(r"\W+", "+", i.get("title", "")[:40]), f"{i.get('author')} {i.get('description')}", kw=i.get("keywords", []), snippet=i.get("description", ""))
    body = page_head("Library", esc(d.get("intro", "")), [("Library", "/library/")], root) + f'''
    <div class="wrap section" data-filter-scope data-library>
      <div class="lib-controls"><label class="sr-only" for="lib-q">Search the library</label><div class="field">{ICON_S}<input id="lib-q" type="search" placeholder="Search titles, authors, topics" data-filter-search autocomplete="off"></div>
        <div class="chips" role="group" aria-label="Filter by topic">{chips}</div>
        <div class="chips" role="group" aria-label="Filter by access"><button class="chip" type="button" data-access-filter="*" aria-pressed="true">Everything</button><button class="chip" type="button" data-access-filter="hosted" aria-pressed="false">Hosted here</button><button class="chip" type="button" data-access-filter="link" aria-pressed="false">Link only</button></div></div>
      <p class="muted small" data-filter-count aria-live="polite"></p>
      <ul class="lib-list">{"".join(rows)}</ul><p class="empty" data-filter-empty hidden>Nothing matches. Try a shorter search or clear the filters.</p>
      <p class="muted small">“Hosted here” items are public domain or openly licensed. Copyrighted works are listed with a link to their owner and are never copied.</p></div>'''
    page("library/", "Library", body, page_js="library")

def build_ask():
    root = "../"
    body = page_head("Ask a question", "Type a question in your own words. We'll find the closest answer we've already written and checked, with its sources. No AI and nothing leaves your phone.", [("Ask a question", "/ask/")], root) + f'''
    <div class="wrap section measure-wide" data-ask><form class="ask-form" role="search" data-ask-form><label class="sr-only" for="ask-q">Your question</label>
      <div class="field">{ICON_S}<input id="ask-q" name="q" type="search" placeholder="e.g. Did Jesus really exist?" autocomplete="off" enterkeyhint="search"><button class="btn" type="submit">Ask</button></div></form>
      <div class="chips ask-suggest" aria-label="Try asking"><button class="chip" type="button" data-ask-try>Did Jesus exist?</button><button class="chip" type="button" data-ask-try>Was the Bible changed?</button><button class="chip" type="button" data-ask-try>Isaiah 53 is about Israel</button><button class="chip" type="button" data-ask-try>Did the disciples hallucinate?</button></div>
      <div class="ask-results" data-ask-results aria-live="polite"></div></div>'''
    page("ask/", "Ask a question", body, page_js="ask")

def build_pages():
    """Generic page template: content/pages/<slug>.md -> /<slug>/ (files starting with _ are skipped)."""
    for p in sorted((C / "pages").glob("*.md")) if (C / "pages").exists() else []:
        if p.name.startswith("_"): continue
        meta, text = front_matter(p.read_text()); r = slug(p.stem) + "/"; root = "../"
        body = page_head(meta.get("title", p.stem), esc(meta.get("summary", "")), [(meta.get("title", p.stem), "/" + r)], root, eyebrow=meta.get("eyebrow", "")) + f'<div class="wrap section"><div class="prose">{md(text, root)}</div></div>'
        page(r, meta.get("title", p.stem), body)
        index("Page", meta.get("title", p.stem), r, text, snippet=meta.get("summary", ""))

def build_404():
    body = page_head("Page not found", "That page may have moved. Try the search, or start from the home page.", [], "")
    PAGES["404.html"] = ("Not found", body, {})

# ---------------------------------------------------------------- write
def write():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    for route, (title, body, kw) in PAGES.items():
        if route == "404.html":
            # 404 is served at arbitrary depths; use absolute-free links by rendering as root page with <base>-less root "".
            html_ = layout("", title, body).replace("<head>", f'<head>\n<base href="{esc(CFG.get("base_path", "/"))}">', 1)
            (OUT / "404.html").write_text(html_); continue
        html_ = layout(route, title, body, page_js=kw.get("page_js"), desc=kw.get("desc"))
        d = OUT / route; d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html_)
        if kw.get("copy"): shutil.copy(kw["copy"][0], d / kw["copy"][1])
    (OUT / "data").mkdir(exist_ok=True)
    (OUT / "data/search-index.json").write_text(json.dumps(SEARCH, ensure_ascii=False, separators=(",", ":")))
    split_bible()
    (OUT / ".nojekyll").write_text("")

def check_links():
    bad = []
    for f in OUT.rglob("*.html"):
        if f.name == "404.html": continue
        for u in re.findall(r'href="([^"]+)"', f.read_text()):
            u = html.unescape(u)
            if re.match(r"^(https?:|mailto:|#)", u): continue
            path = u.split("#")[0].split("?")[0]
            t = (f.parent / path).resolve()
            if t.is_dir(): t = t / "index.html"
            if not t.exists(): bad.append(f"{f.relative_to(OUT)} -> {u}")
    return bad

if __name__ == "__main__":
    load_bible()
    for fn in (build_home, build_start, build_timeline, build_map, build_witnesses, build_manuscripts, build_prophecy,
               build_resurrection, build_answers, build_learn, build_others, build_library, build_ask, build_pages, build_404):
        try: fn()
        except Exception as e:  # one broken content file must not break the whole site
            import traceback; traceback.print_exc(); WARN.append(f"{fn.__name__} failed: {e}")
    write()
    bad = check_links()
    print(f"Built {len(PAGES)} pages, {len(SEARCH)} search entries -> {OUT}")
    for w in WARN: print("WARN", w)
    for b in bad: print("BROKEN LINK", b)
    sys.exit(1 if bad or any("failed" in w for w in WARN) else 0)
