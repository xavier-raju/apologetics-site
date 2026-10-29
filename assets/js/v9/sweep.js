// v9 heading sweep (owner: Mark, checker: John). The home title sweeps once on load:
// a band of accent light passes across the word, then a thin rule draws in under it. Never loops.
// Reduced motion or no JS: plain title, no sweep.
export function initSweep() {
  const h = document.querySelector(".hero__title");
  if (!h || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  h.classList.add("v9-sweep");
  requestAnimationFrame(() => requestAnimationFrame(() => h.classList.add("is-swept")));
  h.addEventListener("animationend", (e) => { if (e.animationName === "v9-sweep") h.classList.add("is-done"); }, { once: false });
}
