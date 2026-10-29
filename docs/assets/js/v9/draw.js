// v9 self-drawing lines (owner: Mark, checker: John).
// 1) Home: a thin "instrument rule" (line, ticks, one node) draws in at the top of each section.
// 2) Timeline: an accent spine fills down the timeline as you scroll; each dot lights as the spine reaches it.
// Decorative only (aria-hidden). Animates stroke-dashoffset and transform only. Reduced motion: drawn at once, no listeners.
const RM = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const NS = "http://www.w3.org/2000/svg";

function rule() {
  const s = document.createElementNS(NS, "svg");
  s.setAttribute("class", "v9-rule"); s.setAttribute("viewBox", "0 0 600 16");
  s.setAttribute("preserveAspectRatio", "none"); s.setAttribute("aria-hidden", "true"); s.setAttribute("focusable", "false");
  const mk = (tag, attrs) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); s.append(e); return e; };
  mk("path", { d: "M0 8H600", class: "v9-rule__line", pathLength: "1" });
  let ticks = ""; for (let x = 0; x <= 600; x += 50) ticks += `M${x} ${x % 150 ? 6 : 3}V${x % 150 ? 10 : 13}`;
  mk("path", { d: ticks, class: "v9-rule__ticks" });
  mk("circle", { cx: "150", cy: "8", r: "3", class: "v9-rule__node" });
  return s;
}

function initRules() {
  if (!document.querySelector(".hero")) return; // home page only
  const secs = [...document.querySelectorAll(".hero ~ .section")].filter((s) => !s.classList.contains("hero"));
  if (!secs.length) return;
  const rules = secs.map((sec) => { const w = sec.querySelector(".wrap") || sec; const r = rule(); w.prepend(r); return r; });
  if (RM() || !("IntersectionObserver" in window)) { rules.forEach((r) => r.classList.add("is-drawn")); return; }
  const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("is-drawn"); io.unobserve(e.target); } }), { rootMargin: "0px 0px -10% 0px" });
  rules.forEach((r) => io.observe(r));
  setTimeout(() => rules.forEach((r) => r.classList.add("is-drawn")), 4000); // never leave a rule undrawn
}

function initSpine() {
  const tl = document.querySelector("ol.timeline");
  if (!tl) return;
  const spine = document.createElement("span"); spine.className = "v9-spine"; spine.setAttribute("aria-hidden", "true");
  tl.prepend(spine); tl.classList.add("has-spine");
  const items = [...tl.querySelectorAll(".timeline__item")];
  if (RM()) { spine.classList.add("is-full"); items.forEach((i) => i.classList.add("is-lit")); return; }
  let raf = 0, live = false;
  const update = () => {
    raf = 0;
    const r = tl.getBoundingClientRect(), mark = innerHeight * 0.6;
    const p = Math.max(0, Math.min(1, (mark - r.top) / r.height));
    spine.style.transform = `scaleY(${p.toFixed(4)})`; // CSSOM, allowed by the CSP
    const y = r.top + p * r.height;
    for (const it of items) it.classList.toggle("is-lit", it.getBoundingClientRect().top + 10 <= y);
  };
  const onScroll = () => { if (live && !raf) raf = requestAnimationFrame(update); };
  // Only listen while the timeline is on screen.
  new IntersectionObserver(([e]) => { live = e.isIntersecting; if (live) onScroll(); }).observe(tl);
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll, { passive: true });
  update();
}

export function initDraw() { try { initRules(); } catch (e) { console.warn("v9 rules:", e); } try { initSpine(); } catch (e) { console.warn("v9 spine:", e); } }
