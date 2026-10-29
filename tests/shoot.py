"""Phone screenshots (390x844) + Orbit/John checks + short videos. python3 tests/shoot.py http://127.0.0.1:8811/"""
import sys, json, pathlib, shutil, subprocess
from playwright.sync_api import sync_playwright
B = sys.argv[1].rstrip("/") + "/"; OUT = pathlib.Path(__file__).resolve().parents[1] / "shots"; OUT.mkdir(exist_ok=True)
shots = [("01-home", "", None), ("02-hub", "resurrection/", None), ("03-fact-open", "resurrection/", "open"), ("04-tester", "resurrection/tester/", "tester"),
         ("05-timeline-map", "resurrection/timeline/", None), ("06-courtroom", "resurrection/courtroom/", None), ("07-voices", "resurrection/voices/", None),
         ("08-explorer-sources", "explore/sources/", "search"), ("09-dating-chart", "explore/dating/", None), ("10-explore", "explore/", None), ("11-credits", "explore/credits/", None)]
rep = {}
with sync_playwright() as p:
    try: b = p.chromium.launch()
    except Exception: b = p.chromium.launch(channel="chrome")
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg = ctx.new_page(); errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
    for name, r, act in shots:
        pg.goto(B + r, wait_until="networkidle"); pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-in'))")
        if act == "open": pg.click("#fact-crucifixion .fact-card__front [data-fact-toggle]"); pg.wait_for_timeout(500); pg.locator("#fact-crucifixion").scroll_into_view_if_needed()
        if act == "tester": pg.click('[data-theory="th-hallucination"]'); pg.wait_for_timeout(200)
        if act == "search": pg.fill("[data-filter-search]", "tacitus"); pg.wait_for_timeout(200)
        pg.wait_for_timeout(2600 if r == "" else 400)
        if act == "open": pg.locator("#fact-crucifixion").screenshot(path=str(OUT / f"{name}.png"))
        else: pg.screenshot(path=str(OUT / f"{name}.png"))
        rep[name] = {"overflow_x": pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")}
    # John's Orbit checks at 375
    pg.set_viewport_size({"width": 375, "height": 812}); pg.goto(B, wait_until="networkidle"); pg.wait_for_timeout(1500)
    c = pg.evaluate("""()=>{const c=document.querySelector('canvas.hero__canvas'); if(!c) return null; const s=getComputedStyle(c);
      return {pe:s.pointerEvents, aria:c.getAttribute('aria-hidden'), tabIndex:c.tabIndex, focusable:c.matches(':focus-visible')||c.tabIndex>=0, ow:document.documentElement.scrollWidth-document.documentElement.clientWidth}}""")
    pg.mouse.wheel(0, 900); pg.wait_for_timeout(400); sy = pg.evaluate("scrollY")
    fps = pg.evaluate("""()=>new Promise(r=>{let n=0,t0=performance.now(),worst=0,last=t0;function f(t){n++;worst=Math.max(worst,t-last);last=t;if(t-t0<2000)requestAnimationFrame(f);else r({fps:n/((t-t0)/1000),worst_ms:worst})}window.scrollTo(0,0);requestAnimationFrame(f)})""")
    tap = pg.evaluate("""()=>[...document.querySelectorAll('main a,main button,main input,main summary')].filter(e=>{const r=e.getBoundingClientRect();if(!r.width)return false;
      if(e.closest('[hidden]')||e.matches('main p a,.prose a,dd a,.small a,figcaption a,li.source-list a'))return false;return r.height<44}).length""")
    rep["orbit_375"] = {"canvas": c, "scroll_after_wheel": sy, "frames": fps, "small_tap_targets_home": tap}
    # reduced motion
    rc = b.new_context(viewport={"width": 375, "height": 812}, reduced_motion="reduce"); rp = rc.new_page(); rp.goto(B, wait_until="networkidle"); rp.wait_for_timeout(800)
    rep["reduced"] = rp.evaluate("""()=>({canvas:!!document.querySelector('canvas.hero__canvas'), orbitAnim:getComputedStyle(document.querySelector('.hero__art .orbit')).animationName})""")
    rp.screenshot(path=str(OUT / "01b-home-reduced.png")); rc.close()
    # motion off (no JS)
    nc = b.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False); npg = nc.new_page(); npg.goto(B + "resurrection/"); 
    rep["nojs_hub_deep_visible"] = npg.locator("#fact-crucifixion .fact-card__deep").is_visible(); nc.close()
    rep["console_errors"] = errs[:10]
    ctx.close()
    # videos
    for name, r, act in [("orbit-home", "", None), ("fact-card-open", "resurrection/", "open")]:
        vc = b.new_context(viewport={"width": 390, "height": 844}, record_video_dir=str(OUT / "_v"), record_video_size={"width": 390, "height": 844}, has_touch=True)
        vp = vc.new_page(); vp.goto(B + r, wait_until="networkidle")
        if act:
            vp.wait_for_timeout(800); vp.click("#fact-crucifixion .fact-card__front [data-fact-toggle]"); vp.wait_for_timeout(1500); vp.mouse.wheel(0, 400); vp.wait_for_timeout(1200)
        else:
            vp.wait_for_timeout(3500); vp.mouse.click(300, 300); vp.wait_for_timeout(1500); vp.mouse.wheel(0, 300); vp.wait_for_timeout(1200); vp.mouse.wheel(0, -300); vp.wait_for_timeout(1500)
        path = vp.video.path(); vc.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT / f"{name}.mp4")])
    shutil.rmtree(OUT / "_v", ignore_errors=True)
    b.close()
(OUT / "shoot-report.json").write_text(json.dumps(rep, indent=1)); print(json.dumps(rep, indent=1))
