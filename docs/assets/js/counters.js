// v9 (Luke): stat numbers count up once when scrolled into view.
// The real text stays in the HTML; the counting copy is aria-hidden and the final
// text is restored exactly. Stats without a clean number (e.g. "4th century") stay static.
const NUM = /\d[\d,]*(?![\d,]*(?:st|nd|rd|th)\b)/g;
export function initCounters(root = document) {
  const els = [...root.querySelectorAll(".stat__n")].filter((el) => {
    const t = el.textContent;
    return /\d/.test(t) && !/century/i.test(t) && !/\d(?:st|nd|rd|th)\b/i.test(t) && (t.match(NUM) || []).length;
  });
  if (!els.length || !("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const dur = () => {
    const v = getComputedStyle(document.documentElement).getPropertyValue("--dur-draw").trim();
    const ms = v.endsWith("ms") ? parseFloat(v) : v.endsWith("s") ? parseFloat(v) * 1000 : 1200;
    return isNaN(ms) ? 1200 : ms;
  };
  els.forEach((el) => el.classList.add("num"));
  const run = (el, i) => {
    const final = el.textContent;
    const parts = []; let last = 0;
    final.replace(NUM, (m, off) => { parts.push(final.slice(last, off), { n: +m.replace(/,/g, ""), comma: m.includes(",") }); last = off + m.length; return m; });
    parts.push(final.slice(last));
    const vis = document.createElement("span"); vis.setAttribute("aria-hidden", "true"); vis.className = "count__vis";
    const sr = document.createElement("span"); sr.className = "sr-only"; sr.textContent = final;
    el.textContent = ""; el.append(sr, vis);
    const D = dur(), delay = i * 80; let t0 = 0, raf = 0;
    const fmt = (p, k) => { const v = Math.round(p.n * k); return p.comma ? v.toLocaleString("en-US") : String(v); };
    const done = () => { cancelAnimationFrame(raf); el.textContent = final; };
    if (D <= 0) return done();
    const step = (now) => {
      if (!t0) t0 = now + delay;
      const x = Math.min(Math.max((now - t0) / D, 0), 1), k = 1 - Math.pow(1 - x, 3);
      vis.textContent = parts.map((p) => typeof p === "string" ? p : fmt(p, k)).join("");
      if (x < 1 && !document.hidden) raf = requestAnimationFrame(step); else done();
    };
    raf = requestAnimationFrame(step);
  };
  let n = 0;
  const io = new IntersectionObserver((ens) => {
    for (const en of ens) if (en.isIntersecting) { io.unobserve(en.target); run(en.target, n++ % 3); }
  }, { rootMargin: "0px 0px -10% 0px", threshold: 0 });
  els.forEach((e) => io.observe(e));
}
