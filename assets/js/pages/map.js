// Evidence map: tap a pin to filter the finds list to that place.
export function init() {
  const scope = document.querySelector("[data-filter-scope]");
  const pins = [...document.querySelectorAll(".map__pin")];
  if (!scope || !pins.length) return;
  const empty = scope.querySelector("[data-map-empty]");
  const setEmpty = (pin) => {
    if (!empty) return;
    const name = pin?.getAttribute("aria-label")?.split(",")[0] || "this place";
    empty.textContent = `No finds catalogued here yet for ${name}. Tap another pin, or show all finds.`;
  };
  const pick = (pin, force) => {
    const id = pin.dataset.place;
    const on = force || pin.getAttribute("aria-pressed") !== "true";
    if (typeof scope.filterTo !== "function") return;
    setEmpty(pin);
    pins.forEach((p) => p.setAttribute("aria-pressed", String(on && p === pin)));
    scope.filterTo(on ? id : "*");
    const has = Number(pin.dataset.count || 0) > 0;
    if (on && has && matchMedia("(max-width: 899px)").matches) scope.querySelector(".finds")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  pins.forEach((p) => {
    p.addEventListener("click", () => pick(p));
    p.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(p); } });
  });
  scope.addEventListener("filterchange", (e) => { if (e.detail.tag === "*") pins.forEach((p) => p.setAttribute("aria-pressed", "false")); });
  const fromHash = () => {
    const m = decodeURIComponent(location.hash).match(/^#place-(.+)/);
    const pin = m && pins.find((p) => p.dataset.place === m[1]);
    if (pin) pick(pin, true);
  };
  fromHash();
  addEventListener("hashchange", fromHash);
}
