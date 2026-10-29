// Resurrection pages: fact cards (30-second / go deeper) and the theory tester.
// Server-rendered HTML works without this file; it only adds the toggles.
const reduce = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

function initFacts() {
  document.querySelectorAll("[data-fact]").forEach((card) => {
    const toggles = card.querySelectorAll("[data-fact-toggle]");
    toggles.forEach((b) => b.addEventListener("click", () => {
      const open = !card.classList.contains("is-open");
      card.classList.toggle("is-open", open);
      toggles.forEach((x) => x.setAttribute("aria-expanded", String(x.closest(".fact-card__deep") ? open : open)));
      if (!reduce() && card.animate) card.animate([{ transform: "scale(.985)", opacity: .6 }, { transform: "none", opacity: 1 }], { duration: 380, easing: "cubic-bezier(.2,.7,.2,1)" });
      const target = open ? card.querySelector(".fact-card__deep [data-fact-toggle]") : card.querySelector(".fact-card__front [data-fact-toggle]");
      target?.focus({ preventScroll: true });
      if (!open) card.scrollIntoView({ block: "nearest", behavior: reduce() ? "auto" : "smooth" });
    }));
  });
  const id = decodeURIComponent(location.hash.slice(1));
  const c = id && document.getElementById(id);
  if (c && c.matches("[data-fact]")) c.querySelector(".fact-card__front [data-fact-toggle]")?.click();
}

function initTester() {
  const root = document.querySelector("[data-tester]");
  if (!root) return;
  root.classList.add("is-live");
  const chips = [...root.querySelectorAll("[data-theory]")];
  const show = (id) => {
    chips.forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.theory === id)));
    root.querySelectorAll(".theory").forEach((p) => p.toggleAttribute("data-active", p.id === id));
  };
  chips.forEach((c) => c.addEventListener("click", () => { show(c.dataset.theory); history.replaceState(null, "", "#" + c.dataset.theory); }));
  const h = location.hash.slice(1);
  if (h && chips.some((c) => c.dataset.theory === h)) show(h);
}

export function init() { initFacts(); initTester(); }
