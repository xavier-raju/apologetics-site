// Evidence map: tap a place (map label or list button) to filter the finds list to it.
export function init() {
  const scope = document.querySelector("[data-filter-scope]");
  const ctrls = [...document.querySelectorAll(".map__pin[data-place], .place-btn[data-place]")];
  if (!scope || !ctrls.length) return;
  const empty = scope.querySelector("[data-map-empty]");
  const nameOf = (id) => scope.querySelector(`.place-btn[data-place="${CSS.escape(id)}"] .place-btn__name`)?.textContent || "this place";
  let current = null;
  const mark = (id) => ctrls.forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.place === id)));
  const pick = (id, { force = false, fromHash = false } = {}) => {
    if (typeof scope.filterTo !== "function") return;
    const on = force || current !== id;
    current = on ? id : null;
    if (empty) empty.textContent = `No finds catalogued here yet for ${nameOf(id)}. Pick another place, or show all finds.`;
    mark(current);
    scope.filterTo(on ? id : "*");
    if (!fromHash) history.replaceState(null, "", on ? `#place-${id}` : location.pathname + location.search);
    const has = Number(ctrls.find((c) => c.dataset.place === id)?.dataset.count || 0) > 0;
    if (on && has && !fromHash && matchMedia("(max-width: 899px)").matches) scope.querySelector(".finds")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  ctrls.forEach((c) => c.addEventListener("click", () => pick(c.dataset.place)));
  scope.addEventListener("filterchange", (e) => {
    if (e.detail.tag === "*") { current = null; mark(null); if (location.hash.startsWith("#place-")) history.replaceState(null, "", location.pathname + location.search); }
  });
  const fromHash = () => {
    const m = decodeURIComponent(location.hash).match(/^#place-(.+)/);
    if (m && ctrls.some((c) => c.dataset.place === m[1])) pick(m[1], { force: true, fromHash: true });
  };
  fromHash();
  addEventListener("hashchange", fromHash);
}
