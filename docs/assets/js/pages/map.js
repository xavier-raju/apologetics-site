// Evidence map: tap a pin to filter the finds list to that place.
export function init() {
  const scope = document.querySelector("[data-filter-scope]");
  const pins = [...document.querySelectorAll(".map__pin")];
  if (!scope || !pins.length) return;
  const pick = (pin) => {
    const id = pin.dataset.place;
    const on = pin.getAttribute("aria-pressed") !== "true";
    pins.forEach((p) => p.setAttribute("aria-pressed", String(on && p === pin)));
    scope.filterTo(on ? id : "*");
    if (on && matchMedia("(max-width: 899px)").matches) scope.querySelector(".finds")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  pins.forEach((p) => {
    p.addEventListener("click", () => pick(p));
    p.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(p); } });
  });
  scope.addEventListener("filterchange", (e) => { if (e.detail.tag === "*") pins.forEach((p) => p.setAttribute("aria-pressed", "false")); });
  const m = location.hash.match(/^#place-(.+)/);
  const pin = m && pins.find((p) => p.dataset.place === m[1]);
  if (pin) pick(pin);
}
