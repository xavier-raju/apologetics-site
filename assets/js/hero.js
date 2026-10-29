// Home hero motion: Orbit (prototype A, picked by Xavier 29 Oct). The v8 armillary cross, but the ball now travels a richer
// orbit (a slow rosette around the cross). A tap sends a faint ring outward from
// the touch point and kicks the ball forward; scrolling turns the rings like a dial.
export function initHero() {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const svg = document.querySelector(".hero__art");
  if (!svg || reduce) return;
  const cv = document.createElement("canvas");
  cv.className = "hero__art hero__canvas"; cv.setAttribute("aria-hidden", "true"); cv.setAttribute("role", "presentation"); svg.after(cv);
  const ctx = cv.getContext("2d"); if (!ctx) { cv.remove(); return; }
  const accent = getComputedStyle(svg).color || "#1f4fd8";
  const hero = document.querySelector(".hero");
  let W = 0, S = 1, dpr = 1, running = false, visible = true, raf = 0, t0 = performance.now(), last = t0;
  let tx = 0, ty = 0, px = 0, py = 0, scrollT = 0, scrollV = 0, phase = 0, kick = 0;
  const ripples = [];
  const rings = [
    { r: 250, tilt: 1.15, yaw: 0.0, speed: 0.10, bead: 5 },
    { r: 205, tilt: 1.25, yaw: 2.1, speed: -0.14, bead: 4 },
    { r: 160, tilt: 0.95, yaw: 4.2, speed: 0.19, bead: 3.5 },
  ];
  function size() { const b = cv.getBoundingClientRect(); dpr = Math.min(devicePixelRatio || 1, 2); W = b.width; S = W / 640; cv.width = Math.round(W * dpr); cv.height = Math.round(W * dpr); }
  const ease = (x) => 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 3);
  function proj(rg, a, rot, tiltAdd) {
    const x = rg.r * Math.cos(a), y = rg.r * Math.sin(a);
    const tl = rg.tilt + tiltAdd, y2 = y * Math.cos(tl), z = y * Math.sin(tl);
    const yw = rg.yaw + rot, cy = Math.cos(yw), sy = Math.sin(yw);
    const x3 = x * cy - y2 * sy, y3 = x * sy + y2 * cy;
    const ax = py * 0.25, ay = px * 0.25;
    const y4 = y3 * Math.cos(ax) - z * Math.sin(ax), z4 = y3 * Math.sin(ax) + z * Math.cos(ax);
    const x5 = x3 * Math.cos(ay) + z4 * Math.sin(ay), z5 = -x3 * Math.sin(ay) + z4 * Math.cos(ay);
    return [320 + x5, 320 + y4, z5];
  }
  function frame(now) {
    raf = 0; const t = (now - t0) / 1000, dt = Math.min(0.05, (now - last) / 1000); last = now;
    px += (tx - px) * 0.05; py += (ty - py) * 0.05;
    scrollV *= 0.92; kick *= 0.94; phase += dt * (1 + kick * 6) + scrollV * 0.002;
    const c = ctx; c.setTransform(dpr * S, 0, 0, dpr * S, 0, 0); c.clearRect(0, 0, 640, 640);
    c.lineWidth = 1 / S; c.lineCap = "round"; c.strokeStyle = accent; c.fillStyle = accent;
    const ox = px * 14, oy = py * 14, tiltAdd = Math.sin(scrollT * 0.004) * 0.35;
    // faint concentric guide rings that breathe and react to ripples
    for (let k = 1; k <= 4; k++) {
      let r = 70 * k + 6 * Math.sin(t * 0.6 + k);
      ripples.forEach((rp) => { const d = Math.abs(rp.r - r); if (d < 40) r += (1 - d / 40) * 8 * rp.a; });
      c.globalAlpha = 0.07 + 0.03 * k % 2; c.beginPath(); c.arc(320, 320, r, 0, 7); c.stroke();
    }
    // tap ripples
    for (let i = ripples.length - 1; i >= 0; i--) { const rp = ripples[i]; rp.r += dt * 260; rp.a -= dt * 0.7; if (rp.a <= 0) { ripples.splice(i, 1); continue; }
      c.globalAlpha = 0.35 * rp.a; c.beginPath(); c.arc(rp.x, rp.y, rp.r, 0, 7); c.stroke(); }
    rings.forEach((rg, k) => {
      const p = ease((t - 0.3 * k) / 2.2); if (p <= 0) return;
      const rot = phase * 0.05 * (k % 2 ? -1 : 1) + scrollT * 0.0015 * (k + 1);
      const N = 120, end = Math.floor(N * p);
      for (let i = 0; i < end; i++) { const [x1, y1, z1] = proj(rg, i / N * 6.2832, rot, tiltAdd), [x2, y2] = proj(rg, (i + 1) / N * 6.2832, rot, tiltAdd);
        c.globalAlpha = z1 > 0 ? 0.25 : 0.65; c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke(); }
      if (t > 2) {
        const ba = phase * rg.speed * 6.2832 + k;
        for (let j = 0; j < 10; j++) { const [bx, by, bz] = proj(rg, ba - j * 0.03 * Math.sign(rg.speed) * (1 + kick * 3), rot, tiltAdd);
          c.globalAlpha = (bz > 0 ? 0.35 : 1) * (1 - j / 10) * Math.min(1, t - 2); c.beginPath(); c.arc(bx, by, rg.bead * (1 - j / 12), 0, 7); c.fill(); }
      }
    });
    // the main ball: rosette orbit around the crossing
    if (t > 1.5) {
      const a = phase * 0.55, rr = 118 + 34 * Math.sin(phase * 1.65);
      const bx = 320 + ox + rr * Math.cos(a), by = 250 + oy + rr * 0.62 * Math.sin(a);
      c.globalAlpha = 0.18 * Math.min(1, t - 1.5); c.beginPath();
      for (let j = 0; j <= 60; j++) { const aa = a - j * 0.03, r2 = 118 + 34 * Math.sin((phase - j * 0.03 / 0.55) * 1.65); const x = 320 + ox + r2 * Math.cos(aa), y = 250 + oy + r2 * 0.62 * Math.sin(aa); j ? c.lineTo(x, y) : c.moveTo(x, y); }
      c.stroke();
      const g = c.createRadialGradient(bx - 3, by - 3, 1, bx, by, 11); g.addColorStop(0, "#fff"); g.addColorStop(0.35, accent); g.addColorStop(1, accent);
      c.globalAlpha = Math.min(1, t - 1.5); c.fillStyle = g; c.beginPath(); c.arc(bx, by, 9, 0, 7); c.fill(); c.fillStyle = accent;
    }
    c.globalAlpha = 0.5; c.beginPath(); c.arc(320 + ox * .5, 320 + oy * .5, 90, -1.5708, -1.5708 + 6.2832 * ease((t - 0.6) / 2)); c.stroke();
    const cp = ease((t - 0.9) / 1.8);
    c.globalAlpha = 1; c.lineWidth = 1.5 / S; c.beginPath();
    c.moveTo(320 + ox, 40 + oy); c.lineTo(320 + ox, 40 + oy + 560 * cp); c.moveTo(180 + ox, 250 + oy); c.lineTo(180 + ox + 280 * cp, 250 + oy); c.stroke();
    if (cp >= 1) { c.globalAlpha = 0.6 + 0.4 * Math.sin(t * 1.4); c.beginPath(); c.arc(320 + ox, 250 + oy, 3 + kick * 4, 0, 7); c.fill(); }
    c.globalAlpha = 1;
    if (running) raf = requestAnimationFrame(frame);
  }
  const start = () => { if (!running && visible && !document.hidden) { running = true; last = performance.now(); raf = requestAnimationFrame(frame); } };
  const stop = () => { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; };
  size(); svg.classList.add("is-live"); start();
  addEventListener("resize", size, { passive: true });
  addEventListener("pointermove", (e) => { tx = e.clientX / innerWidth * 2 - 1; ty = e.clientY / innerHeight * 2 - 1; }, { passive: true });
  let lastY = scrollY; addEventListener("scroll", () => { scrollV += scrollY - lastY; lastY = scrollY; scrollT = scrollY; }, { passive: true });
  hero && hero.addEventListener("pointerdown", (e) => { const b = cv.getBoundingClientRect(); ripples.push({ x: (e.clientX - b.left) / S, y: (e.clientY - b.top) / S, r: 4, a: 1 }); kick = 1; tx = (e.clientX / innerWidth) * 2 - 1; }, { passive: true });
  document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
  if ("IntersectionObserver" in window) new IntersectionObserver(([en]) => { visible = en.isIntersecting; visible ? start() : stop(); }).observe(cv);
}
