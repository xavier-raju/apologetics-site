// v9 (Luke): soft pointer spotlight on answer cards, home tiles and Start here panels.
// Updates --x/--y via rAF; a tap places the light on touch. Off for reduced motion.
const SEL = ".answer, .tile, .panel";
export function initSpotlight(root = document) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const cards = [...root.querySelectorAll(SEL)];
  if (!cards.length) return;
  let raf = 0, pending = null;
  const apply = () => {
    raf = 0; if (!pending) return;
    const { el, x, y } = pending; pending = null;
    const r = el.getBoundingClientRect();
    el.style.setProperty("--x", `${x - r.left}px`);
    el.style.setProperty("--y", `${y - r.top}px`);
    el.classList.add("is-lit");
  };
  const move = (e) => {
    if (document.hidden) return;
    pending = { el: e.currentTarget, x: e.clientX, y: e.clientY };
    if (!raf) raf = requestAnimationFrame(apply);
  };
  cards.forEach((el) => {
    el.classList.add("spot");
    el.addEventListener("pointermove", (e) => { if (e.pointerType === "mouse" || e.pointerType === "pen") move(e); }, { passive: true });
    el.addEventListener("pointerdown", move, { passive: true });
    el.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") el.classList.remove("is-lit"); });
  });
  // Touch: a tap elsewhere clears the light.
  document.addEventListener("pointerdown", (e) => {
    cards.forEach((c) => { if (!c.contains(e.target)) c.classList.remove("is-lit"); });
  }, { passive: true });
}
