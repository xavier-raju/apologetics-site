// Home hero: an "armillary" cross. Three thin rings orbit the cross on tilted planes,
// each carrying a bead; light pulses travel along the beams; the whole figure leans
// gently toward the pointer (or device tilt). Decorative only. The static SVG stays
// as the no-JS and reduced-motion fallback.
export function initHero() {
  const svg = document.querySelector(".hero__art");
  if (!svg || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const cv = document.createElement("canvas");
  cv.className = "hero__art hero__canvas";
  cv.setAttribute("aria-hidden", "true");
  svg.after(cv);
  const ctx = cv.getContext("2d");
  if (!ctx) { cv.remove(); return; }
  const accent = getComputedStyle(svg).color || "#1f4fd8";
  const gray = "#8a93a3";
  let W = 0, S = 1, dpr = 1, running = false, visible = true, raf = 0, t0 = performance.now();
  let tx = 0, ty = 0, px = 0, py = 0;
  const rings = [
    { r: 250, tilt: 1.15, yaw: 0.0, speed: 0.10, bead: 5 },
    { r: 205, tilt: 1.25, yaw: 2.1, speed: -0.14, bead: 4 },
    { r: 160, tilt: 0.95, yaw: 4.2, speed: 0.19, bead: 3.5 },
  ];
  function size() {
    const b = cv.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = b.width; S = W / 640;
    cv.width = Math.round(W * dpr); cv.height = Math.round(W * dpr);
  }
  const ease = (x) => 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 3);
  // project a point on a ring (3D) to 2D with a small view tilt from pointer
  function proj(rg, a, rot) {
    let x = rg.r * Math.cos(a), y = rg.r * Math.sin(a), z = 0;
    const ct = Math.cos(rg.tilt), st = Math.sin(rg.tilt);   // tilt ring plane about x
    let y2 = y * ct, z2 = y * st;
    const yw = rg.yaw + rot, cy = Math.cos(yw), sy = Math.sin(yw); // spin plane about z
    let x3 = x * cy - y2 * sy, y3 = x * sy + y2 * cy; z = z2;
    // view tilt
    const ax = py * 0.25, ay = px * 0.25;
    let y4 = y3 * Math.cos(ax) - z * Math.sin(ax), z4 = y3 * Math.sin(ax) + z * Math.cos(ax);
    let x5 = x3 * Math.cos(ay) + z4 * Math.sin(ay), z5 = -x3 * Math.sin(ay) + z4 * Math.cos(ay);
    return [320 + x5, 320 + y4, z5];
  }
  function frame(now) {
    raf = 0;
    const t = (now - t0) / 1000;
    px += (tx - px) * 0.05; py += (ty - py) * 0.05;
    const c = ctx; c.setTransform(dpr * S, 0, 0, dpr * S, 0, 0); c.clearRect(0, 0, 640, 640);
    c.lineWidth = 1 / S; c.lineCap = "round";
    const ox = px * 14, oy = py * 14; // parallax for cross layer
    // faint rays
    const rIn = ease(t / 2.4);
    c.strokeStyle = accent; c.globalAlpha = 0.12; c.beginPath();
    for (let i = 0; i < 24; i++) { const a = i * Math.PI / 12; c.moveTo(320, 320); c.lineTo(320 + 300 * rIn * Math.cos(a), 320 + 300 * rIn * Math.sin(a)); }
    c.stroke();
    // rings + beads (back half dimmer)
    rings.forEach((rg, k) => {
      const p = ease((t - 0.3 * k) / 2.2); if (p <= 0) return;
      const rot = t * 0.04 * (k % 2 ? -1 : 1);
      const N = 120, end = Math.floor(N * p);
      for (let i = 0; i < end; i++) {
        const a1 = i / N * Math.PI * 2, a2 = (i + 1) / N * Math.PI * 2;
        const [x1, y1, z1] = proj(rg, a1, rot), [x2, y2] = proj(rg, a2, rot);
        c.globalAlpha = z1 > 0 ? 0.28 : 0.7; c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke();
      }
      if (p >= 1 || t > 2) {
        const ba = t * rg.speed * Math.PI * 2 + k;
        for (let j = 0; j < 6; j++) { // short trail
          const [bx, by, bz] = proj(rg, ba - j * 0.035 * Math.sign(rg.speed), rot);
          c.globalAlpha = (bz > 0 ? 0.35 : 1) * (1 - j / 6) * Math.min(1, (t - 2) * 2 + 1);
          c.fillStyle = accent; c.beginPath(); c.arc(bx, by, rg.bead * (1 - j / 8) / 1, 0, 7); c.fill();
        }
      }
    });
    // inner circle
    c.globalAlpha = 0.5; c.beginPath(); c.arc(320 + ox * .5, 320 + oy * .5, 90, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * ease((t - 0.6) / 2)); c.stroke();
    // cross
    const cp = ease((t - 0.9) / 1.8);
    c.globalAlpha = 1; c.lineWidth = 1.5 / S; c.strokeStyle = accent; c.beginPath();
    c.moveTo(320 + ox, 40 + oy); c.lineTo(320 + ox, 40 + oy + 560 * cp);
    c.moveTo(180 + ox, 250 + oy); c.lineTo(180 + ox + 280 * cp, 250 + oy); c.stroke();
    // light pulses along the beams
    if (cp >= 1) {
      const pulse = (x1, y1, x2, y2, ph) => {
        const u = ((t * 0.18 + ph) % 1); const x = x1 + (x2 - x1) * u, y = y1 + (y2 - y1) * u;
        const g = c.createRadialGradient(x, y, 0, x, y, 22); g.addColorStop(0, accent); g.addColorStop(1, "rgba(255,255,255,0)");
        c.globalAlpha = 0.55 * Math.sin(u * Math.PI); c.fillStyle = g; c.beginPath(); c.arc(x, y, 22, 0, 7); c.fill();
      };
      pulse(320 + ox, 40 + oy, 320 + ox, 600 + oy, 0);
      pulse(180 + ox, 250 + oy, 460 + ox, 250 + oy, 0.5);
      // node at the crossing breathes
      c.globalAlpha = 0.6 + 0.4 * Math.sin(t * 1.4); c.fillStyle = accent; c.beginPath(); c.arc(320 + ox, 250 + oy, 3, 0, 7); c.fill();
    }
    c.globalAlpha = 1;
    if (running) raf = requestAnimationFrame(frame);
  }
  const start = () => { if (!running && visible && !document.hidden) { running = true; raf = requestAnimationFrame(frame); } };
  const stop = () => { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; };
  size(); svg.classList.add("is-live"); start();
  addEventListener("resize", () => { size(); if (!running) requestAnimationFrame(frame); }, { passive: true });
  addEventListener("pointermove", (e) => { tx = e.clientX / innerWidth * 2 - 1; ty = e.clientY / innerHeight * 2 - 1; }, { passive: true });
  addEventListener("deviceorientation", (e) => { if (e.gamma == null) return; tx = Math.max(-1, Math.min(1, e.gamma / 30)); ty = Math.max(-1, Math.min(1, (e.beta - 45) / 30)); }, { passive: true });
  document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
  if ("IntersectionObserver" in window) new IntersectionObserver(([en]) => { visible = en.isIntersecting; visible ? start() : stop(); }).observe(cv);
}
