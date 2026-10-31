// Orbit (Xavier's pick, prototype A), scaled down for the Resurrection hub.
// A ball loops around the cross, a tap sends out a ring, scrolling turns the rings.
// Skipped entirely under prefers-reduced-motion: the static SVG stays.
export function initOrbit() {
  const fig = document.querySelector(".res-orbit");
  if (!fig || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const cv = document.createElement("canvas"); cv.className = "res-orbit__cv"; cv.setAttribute("aria-hidden", "true");
  const ctx = cv.getContext("2d"); if (!ctx) return;
  fig.appendChild(cv); fig.classList.add("is-live");
  const accent = getComputedStyle(fig).color || "#1f4fd8";
  let W = 0, S = 1, dpr = 1, run = false, vis = true, raf = 0, t0 = performance.now(), last = t0, scrollT = 0, scrollV = 0, phase = 0, kick = 0;
  const rip = [], rings = [{ r: 250, tilt: 1.15, yaw: 0, sp: .10, b: 5 }, { r: 205, tilt: 1.25, yaw: 2.1, sp: -.14, b: 4 }, { r: 160, tilt: .95, yaw: 4.2, sp: .19, b: 3.5 }];
  const size = () => { const r = cv.getBoundingClientRect(); dpr = Math.min(devicePixelRatio || 1, 2); W = r.width; S = W / 640; cv.width = Math.round(W * dpr); cv.height = Math.round(W * dpr); };
  const ease = (x) => 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 3);
  const proj = (g, a, rot, ta) => { const x = g.r * Math.cos(a), y = g.r * Math.sin(a), tl = g.tilt + ta, y2 = y * Math.cos(tl), z = y * Math.sin(tl), w = g.yaw + rot;
    return [320 + x * Math.cos(w) - y2 * Math.sin(w), 320 + x * Math.sin(w) + y2 * Math.cos(w), z]; };
  function frame(now) {
    raf = 0; const t = (now - t0) / 1000, dt = Math.min(.05, (now - last) / 1000); last = now;
    scrollV *= .92; kick *= .94; phase += dt * (1 + kick * 6) + scrollV * .002;
    const c = ctx; c.setTransform(dpr * S, 0, 0, dpr * S, 0, 0); c.clearRect(0, 0, 640, 640);
    c.lineWidth = 1 / S; c.strokeStyle = accent; c.fillStyle = accent; const ta = Math.sin(scrollT * .004) * .35;
    for (let i = rip.length - 1; i >= 0; i--) { const p = rip[i]; p.r += dt * 260; p.a -= dt * .7; if (p.a <= 0) { rip.splice(i, 1); continue; } c.globalAlpha = .35 * p.a; c.beginPath(); c.arc(p.x, p.y, p.r, 0, 7); c.stroke(); }
    rings.forEach((g, k) => {
      const p = ease((t - .3 * k) / 2.2); if (p <= 0) return;
      const rot = phase * .05 * (k % 2 ? -1 : 1) + scrollT * .0015 * (k + 1), N = 96, end = Math.floor(N * p);
      for (let i = 0; i < end; i++) { const [x1, y1, z1] = proj(g, i / N * 6.2832, rot, ta), [x2, y2] = proj(g, (i + 1) / N * 6.2832, rot, ta); c.globalAlpha = z1 > 0 ? .25 : .6; c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke(); }
      if (t > 2) { const [bx, by, bz] = proj(g, phase * g.sp * 6.2832 + k, rot, ta); c.globalAlpha = (bz > 0 ? .35 : 1) * Math.min(1, t - 2); c.beginPath(); c.arc(bx, by, g.b, 0, 7); c.fill(); }
    });
    if (t > 1.5) { const a = phase * .55, rr = 118 + 34 * Math.sin(phase * 1.65); c.globalAlpha = Math.min(1, t - 1.5); c.beginPath(); c.arc(320 + rr * Math.cos(a), 250 + rr * .62 * Math.sin(a), 9, 0, 7); c.fill(); }
    c.globalAlpha = .5; c.beginPath(); c.arc(320, 320, 90, -1.5708, -1.5708 + 6.2832 * ease((t - .6) / 2)); c.stroke();
    const cp = ease((t - .9) / 1.8); c.globalAlpha = 1; c.lineWidth = 1.5 / S; c.beginPath(); c.moveTo(320, 40); c.lineTo(320, 40 + 560 * cp); c.moveTo(180, 250); c.lineTo(180 + 280 * cp, 250); c.stroke();
    if (run) raf = requestAnimationFrame(frame);
  }
  const start = () => { if (!run && vis && !document.hidden) { run = true; last = performance.now(); raf = requestAnimationFrame(frame); } };
  const stop = () => { run = false; if (raf) cancelAnimationFrame(raf); raf = 0; };
  size(); start();
  addEventListener("resize", size, { passive: true });
  let lastY = scrollY; addEventListener("scroll", () => { scrollV += scrollY - lastY; lastY = scrollY; scrollT = scrollY; }, { passive: true });
  fig.addEventListener("pointerdown", (e) => { const b = cv.getBoundingClientRect(); rip.push({ x: (e.clientX - b.left) / S, y: (e.clientY - b.top) / S, r: 4, a: 1 }); kick = 1; }, { passive: true });
  document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
  if ("IntersectionObserver" in window) new IntersectionObserver(([en]) => { vis = en.isIntersecting; vis ? start() : stop(); }).observe(cv);
}
