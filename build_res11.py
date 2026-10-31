"""v11 Resurrection additions (31 Oct 2026): the deeper-evidence chapter, the Orbit hero,
the global 30-second / deep switch, the courtroom verdict and the sixth chapter link.
Reads content/resurrection/v11.json. Runs after build_evidence.run() and edits its pages in place."""
import json, re

def run(B):
    esc, ARROW, page, index, verse_btn, status_tag = B.esc, B.ARROW, B.page, B.index, B.verse_btn, B.status_tag
    V = json.loads((B.ROOT / "content/resurrection/v11.json").read_text())
    SRC = V["sources"]
    used = set()
    def cites(ids, root):
        li = []
        for i in ids:
            s = SRC[i]; used.add(i)  # KeyError = unknown id = build fails, by design
            li.append(f'<li>{B.link(s["label"], s["url"], root)}</li>')
        return f'<ul class="source-list">{"".join(li)}</ul>' if li else ""
    def card(x, root, title=None, meta="", extra=""):
        fid = x["id"]; d = fid + "-deep"
        return f'''<article class="fact-card reveal" id="{esc(fid)}" data-fact>
  <div class="fact-card__front"><div class="card__meta">{status_tag(x["status"])}{meta}</div>
    <h3 class="fact-card__title">{esc(title or x.get("title") or x.get("name"))}</h3>
    <p class="answer__label">30-second version</p><p>{esc(x["short"])}</p>{extra}
    <button class="btn btn--ghost btn--sm fact-card__toggle" type="button" data-fact-toggle aria-expanded="false" aria-controls="{esc(d)}">Go deeper {ARROW}</button></div>
  <div class="fact-card__deep" id="{esc(d)}"><p class="answer__label">Go deeper</p><p>{esc(x["deep"])}</p>
    <div class="fact-card__sec"><p class="answer__label">Sources</p>{cites(x.get("sources") or [x["source"]], root)}</div>
    <button class="btn btn--link btn--sm fact-card__toggle" type="button" data-fact-toggle aria-expanded="true" aria-controls="{esc(d)}">Back to the 30-second version</button></div>
</article>'''
    rt = "../../"
    toggle = '<div class="sd" role="group" aria-label="How much to show"><button type="button" class="sd__b" data-sd="short" aria-pressed="true">30 seconds</button><button type="button" class="sd__b" data-sd="deep" aria-pressed="false">Deep</button></div>'
    CH = [("resurrection/", "The five facts"), ("resurrection/tester/", "Theory tester"), ("resurrection/timeline/", "Easter to Pentecost"),
          ("resurrection/courtroom/", "The courtroom"), ("resurrection/voices/", "Voices"), ("resurrection/evidence/", "Deeper evidence")]
    def chapters(root, cur):
        return '<nav class="chapters" aria-label="Resurrection chapters"><ol>' + "".join(
            f'<li><a href="{root}{r}"{" aria-current=page" if r == cur else ""}><span class="chapters__n">{i}</span>{esc(l)}</a></li>' for i, (r, l) in enumerate(CH, 1)) + "</ol></nav>" + toggle

    # ------------------------------------------------ deeper evidence chapter
    hs = "".join(card(x, rt) for x in V["habermas"])
    c4 = "".join(card(x, rt, extra=f'<p class="refs small">{" ".join(verse_btn(r) for r in x["refs"])}</p><p class="small"><a class="q-link" href="../#{esc(x["hub"])}"><span>The matching fact on the hub</span>{ARROW}</a></p>') for x in V["craig4"])
    C = V["compare"]; FE = C["features"]
    chips = "".join(f'<button class="chip" type="button" data-cmp="{esc(r["id"])}" aria-pressed="{"true" if i == 0 else "false"}">{esc(r["name"].split(" ")[0] if not r["name"][0].isdigit() else "1 Cor 15")}</button>' for i, r in enumerate(C["rows"]))
    cmp_cards = "".join(f'''<article class="cmp-card" id="{esc(r["id"])}"><div class="card__meta">{status_tag("Framing")}<span>{esc(r["date"])}</span></div>
  <h3 class="fact-card__title">{esc(r["name"])}</h3><p class="refs small">{verse_btn(r["ref"])}</p>
  <p><span class="answer__label">What it gives</span><br>{esc(r["gives"])}</p><p><span class="answer__label">Its limit</span><br>{esc(r["limit"])}</p>
  <ul class="cmp-feat" aria-label="What this account includes">{"".join(f'<li class="{"is-has" if k in r["has"] else "is-not"}"><span aria-hidden="true">{"●" if k in r["has"] else "○"}</span> {esc(v)}<span class="sr"> {"included" if k in r["has"] else "not told"}</span></li>' for k, v in FE.items())}</ul></article>''' for r in C["rows"])
    arch = "".join(card(x, rt, meta='<span>Archaeology</span>') for x in V["archaeology"])
    fa = "".join(card(x, rt, meta=f'<span>{esc(x["date"])}</span>') for x in V["fathers"])
    sc = "".join(card(x, rt, meta=f'<span>{esc(x["who"])}</span>') for x in V["scholars"])
    S = V["strobel"]
    rooms = "".join(f'''<li class="room reveal"><p class="card__meta"><span>Chapter {r["ch"]}</span><span>· {esc(r["expert"])}</span></p><h3 class="fact-card__title">{esc(r["title"])}</h3>
  <p class="room__q">Strobel asks: {esc(r["q"])}</p><p class="small">{esc(r["ties"])}</p>
  <p class="small"><a class="q-link" href="{esc(r["link_fact"])}"><span>{esc(r["link_label"])}</span>{ARROW}</a></p>{f'<p class="small muted">Free work by the same expert or on the same question:</p>{cites(r["free"], rt)}' if r["free"] else '<p class="small muted">No free work by this expert that we could check; cited from the table of contents only.</p>'}</li>''' for r in S["rooms"])
    toc = '<nav class="toc" aria-label="On this page"><ol>' + "".join(f'<li><a class="q-link" href="#{a}"><span>{l}</span>{ARROW}</a></li>' for a, l in (("compare", "The five accounts side by side"), ("craig4", "Craig's four facts"), ("habermas", "Habermas's count of scholars"), ("tomb-arch", "A crucified man's tomb"), ("fathers", "The first writers after the apostles"), ("scholars", "Wright and Allison"), ("strobel", "Strobel's interview room"))) + "</ol></nav>"
    body = B.page_head("Deeper evidence", "The five resurrection accounts side by side, Craig's four facts, Habermas's count of scholars, a crucified man's tomb, the first Christian writers after the apostles, two leading scholars and Strobel's interviews. Tap any card for the 30-second version, then go deeper.", [("Resurrection", "/resurrection/"), ("Deeper evidence", "/resurrection/evidence/")], rt, eyebrow="Resurrection") + f'''
<div class="wrap section">{chapters(rt, "resurrection/evidence/")}{toc}
  <section class="block" id="compare" aria-labelledby="cmp-h"><h2 id="cmp-h">The five accounts side by side</h2><p class="muted measure">{esc(C["intro"])}</p>
    <div class="cmp" data-cmp-root><div class="chips" role="group" aria-label="Pick an account">{chips}</div><div class="cmp__cards" aria-live="polite">{cmp_cards}</div></div>
    <p class="small muted measure">{esc(C["note"])}</p>{cites(C["sources"], rt)}</section>
  <section class="block" id="craig4"><h2>William Lane Craig's four facts</h2><p class="muted measure">Craig sums up the case in four facts he says most scholars who write on the subject accept, and asks what best explains them. Each links back to the matching fact on the hub.</p><div class="stack facts">{c4}</div></section>
  <section class="block" id="habermas"><h2>Habermas's count of scholars</h2><p class="muted measure">Where "most scholars agree" comes from, and what it does and does not mean.</p><div class="stack facts">{hs}</div></section>
  <section class="block" id="tomb-arch"><h2>A crucified man's tomb</h2><div class="stack facts">{arch}</div></section>
  <section class="block" id="fathers"><h2>The first writers after the apostles</h2><p class="muted measure">Public-domain translations, linked so you can read every chapter yourself.</p><div class="stack facts">{fa}</div></section>
  <section class="block" id="scholars"><h2>Wright and Allison</h2><p class="muted measure">Two of the most detailed recent studies, from scholars who reach different levels of confidence.</p><div class="stack facts">{sc}</div></section>
  <section class="block" id="strobel"><h2>Strobel's interview room</h2><p class="muted measure">{esc(S["intro"])}</p><ol class="rooms">{rooms}</ol>{cites(S["sources"], rt)}</section>
  <p class="small muted mt">With thanks to 0xSero, whose research report <a href="https://github.com/0xSero/all-historical-evidence-of-jesus-christ" rel="noopener" target="_blank">All Historical Evidence of Jesus Christ</a> pointed us to many of these sources.</p>
  <p class="btn-row mt"><a class="btn" href="../courtroom/">Take the case to court {ARROW}</a><a class="btn btn--ghost" href="../">Back to the facts</a></p>
</div>'''
    page("resurrection/evidence/", "Deeper evidence", body, page_js="res")
    for grp in ("habermas", "craig4", "archaeology", "fathers", "scholars"):
        for x in V[grp]: index("Resurrection", x.get("title") or x.get("name"), f"resurrection/evidence/#{x['id']}", x["short"] + " " + x["deep"], snippet=x["short"], status=x["status"])
    index("Resurrection", "The five resurrection accounts side by side", "resurrection/evidence/#compare", " ".join(r["name"] + " " + r["gives"] + " " + r["limit"] for r in C["rows"]), snippet=C["intro"])
    index("Resurrection", "Strobel's interview room", "resurrection/evidence/#strobel", S["intro"], snippet=S["intro"])

    # ------------------------------------------------ rewrite chapter nav + toggle on every chapter page
    nav_re = re.compile(r'<nav class="chapters" aria-label="Resurrection chapters">.*?</nav>', re.S)
    for route, _ in CH[:5]:
        t, b, kw = B.PAGES[route]
        depth = route.count("/"); root = "../" * depth
        b, n = nav_re.subn(lambda m: chapters(root, route), b, count=1)
        if n != 1: raise SystemExit(f"BUILD FAILED: chapter nav not found on {route}")
        kw = dict(kw); kw["page_js"] = "res"
        B.PAGES[route] = (t, b, kw)

    # ------------------------------------------------ hub: Orbit hero + 30-second case
    t, b, kw = B.PAGES["resurrection/"]
    c30 = V["case30"]
    orbit = f'''<div class="res-hero"><figure class="res-orbit" aria-hidden="true"><svg class="res-orbit__svg" viewBox="0 0 640 640" focusable="false"><g fill="none" stroke="currentColor" stroke-width="1">
  <circle cx="320" cy="320" r="90" opacity=".5"/><ellipse cx="320" cy="320" rx="250" ry="105" opacity=".35" transform="rotate(-18 320 320)"/><ellipse cx="320" cy="320" rx="205" ry="80" opacity=".35" transform="rotate(24 320 320)"/><ellipse cx="320" cy="320" rx="160" ry="120" opacity=".3"/>
  <path d="M320 40V600M180 250H460" stroke-width="1.5"/></g><circle cx="438" cy="250" r="8" fill="currentColor"/></svg></figure>
  <aside class="card case30 reveal" aria-labelledby="case30-h"><p class="eyebrow">Short on time?</p><h2 id="case30-h" class="card__title">{esc(c30["title"])}</h2><p>{esc(c30["text"])}</p>{cites(c30["sources"], "../")}<p class="small muted">Tap the drawing above: it answers. Scroll and the rings turn.</p></aside></div>'''
    b, n = re.subn(r'(<div class="wrap section">)', lambda m: m.group(1) + orbit, b, count=1)
    if n != 1: raise SystemExit("BUILD FAILED: hub section not found")
    B.PAGES["resurrection/"] = (t, b, kw)

    # ------------------------------------------------ courtroom: your verdict
    t, b, kw = B.PAGES["resurrection/courtroom/"]
    vd = V["verdict"]
    vhtml = f'''<section class="verdict-box block" id="verdict" aria-labelledby="verdict-h"><p class="eyebrow">The jury</p><h2 id="verdict-h">Your verdict</h2>
  <p class="measure">Sir Lionel Luckhoo judged the case the way a lawyer would, by the standard of proof. Having seen the steps, where do you land? Your answer stays on this phone; nothing is sent anywhere.</p>
  <div class="verdict-box__opts" role="group" aria-label="Your verdict">{"".join(f'<button class="btn btn--ghost" type="button" data-verdict="{k}" aria-pressed="false">{esc(l)}</button>' for k, l in vd["options"])}</div>
  <p class="verdict-box__reply" aria-live="polite" data-verdict-reply></p>
  <div class="verdict-box__replies" hidden>{"".join(f'<p data-reply="{k}">{esc(v)}</p>' for k, v in vd["replies"].items())}</div>
  <p class="small muted">The Luckhoo card above carries his background, labelled Contested; this page is our dramatisation, not a transcript of any trial.</p></section>'''
    b, n = re.subn(r'(<p class="btn-row mt"><a class="btn" href="\.\./tester/">)', lambda m: vhtml + m.group(1), b, count=1)
    if n != 1: raise SystemExit("BUILD FAILED: courtroom anchor not found")
    B.PAGES["resurrection/courtroom/"] = (t, b, kw)

    unused = set(SRC) - used
    if unused: raise SystemExit(f"BUILD FAILED: v11 sources declared but never cited: {sorted(unused)}")
    return {"v11_sources": len(used)}
