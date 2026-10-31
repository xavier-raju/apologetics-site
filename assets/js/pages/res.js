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

// v11: one switch for every card on the page, remembered on this device only.
function initSwitch() {
  const bs = [...document.querySelectorAll("[data-sd]")];
  if (!bs.length) return;
  const set = (mode, save) => {
    bs.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.sd === mode)));
    const deep = mode === "deep";
    document.querySelectorAll("[data-fact]").forEach((c) => { c.classList.toggle("is-open", deep); c.querySelectorAll("[data-fact-toggle]").forEach((x) => x.setAttribute("aria-expanded", String(deep))); });
    document.querySelectorAll("main details.sources").forEach((d) => { d.open = deep; });
    if (save) try { localStorage.setItem("res-sd", mode); } catch (e) {}
  };
  bs.forEach((b) => b.addEventListener("click", () => set(b.dataset.sd, true)));
  let m = null; try { m = localStorage.getItem("res-sd"); } catch (e) {}
  if (m === "deep") set("deep", false);
}

function initCompare() {
  const root = document.querySelector("[data-cmp-root]");
  if (!root) return;
  root.classList.add("is-live");
  const chips = [...root.querySelectorAll("[data-cmp]")];
  const show = (id) => { chips.forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.cmp === id))); root.querySelectorAll(".cmp-card").forEach((k) => k.toggleAttribute("data-active", k.id === id)); };
  chips.forEach((c) => c.addEventListener("click", () => show(c.dataset.cmp)));
  show(chips[0].dataset.cmp);
}

function initVerdict() {
  const box = document.querySelector(".verdict-box");
  if (!box) return;
  const bs = [...box.querySelectorAll("[data-verdict]")], out = box.querySelector("[data-verdict-reply]");
  const set = (k, save) => {
    bs.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.verdict === k)));
    out.textContent = box.querySelector(`[data-reply="${k}"]`)?.textContent || "";
    if (save) try { localStorage.setItem("res-verdict", k); } catch (e) {}
  };
  bs.forEach((b) => b.addEventListener("click", () => set(b.dataset.verdict, true)));
  let k = null; try { k = localStorage.getItem("res-verdict"); } catch (e) {}
  if (k && bs.some((b) => b.dataset.verdict === k)) set(k, false);
}

export function init() {
  initFacts(); initTester(); initSwitch(); initCompare(); initVerdict();
  if (document.querySelector(".res-orbit")) import("./orbit.js").then((m) => m.initOrbit()).catch(() => {});
}
