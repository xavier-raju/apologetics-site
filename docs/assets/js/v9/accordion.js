// v9 sliding accordion (owner: Mark, checker: John; merge by TARS).
// grid-template-rows 0fr -> 1fr slide, no JS measuring. ui.js / "Expand all" still flip aria-expanded and hidden on
// the body; we mirror that onto a class. Closed content gets hidden="until-found" (not inert), so find-in-page can
// reveal it; "beforematch" opens the card and syncs aria-expanded. Browsers without until-found: answers stay open.
// Reduced motion: --dur is 0, so it opens instantly. No JS: plain hidden attribute, unchanged.
const UF = "onbeforematch" in document.documentElement;
export function initAccordion() {
  const bodies = [...document.querySelectorAll(".answer > .answer__body")];
  if (!bodies.length) return;
  const sync = (p, t, inner) => {
    if (!UF) { // no until-found support: keep everything readable
      if (p.hidden) p.hidden = false;
      if (t.getAttribute("aria-expanded") !== "true") t.setAttribute("aria-expanded", "true");
      p.classList.remove("is-closed"); inner.hidden = false; return;
    }
    const open = t.getAttribute("aria-expanded") === "true";
    if (p.hidden) p.hidden = false;
    clearTimeout(inner._t);
    if (open) { inner.hidden = false; requestAnimationFrame(() => p.classList.remove("is-closed")); }
    else {
      p.classList.add("is-closed");
      const ms = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--dur")) * 1000 || 0;
      const hide = () => { if (t.getAttribute("aria-expanded") !== "true") inner.setAttribute("hidden", "until-found"); };
      if (ms && document.documentElement.classList.contains("v9-acc-ready")) inner._t = setTimeout(hide, ms); else hide();
    }
  };
  for (const p of bodies) {
    const t = document.querySelector(`[aria-controls="${CSS.escape(p.id)}"]`);
    if (!t) continue;
    const inner = document.createElement("div"); inner.className = "answer__inner";
    while (p.firstChild) inner.append(p.firstChild);
    p.append(inner); p.classList.add("v9-acc");
    inner.addEventListener("beforematch", () => t.setAttribute("aria-expanded", "true"));
    sync(p, t, inner);
    new MutationObserver(() => sync(p, t, inner)).observe(p, { attributes: true, attributeFilter: ["hidden"] });
    new MutationObserver(() => sync(p, t, inner)).observe(t, { attributes: true, attributeFilter: ["aria-expanded"] });
  }
  requestAnimationFrame(() => requestAnimationFrame(() => document.documentElement.classList.add("v9-acc-ready")));
}
