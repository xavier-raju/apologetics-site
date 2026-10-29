// v9 (Luke): Resurrection minimal facts as a line of tappable nodes.
// Built from the existing ordered list (same words, cloned). The list stays in the
// HTML for no-JS; once the widget is built the list is hidden.
// Closed facts use hidden="until-found" (find-in-page opens them via beforematch); unsupported: all open.
const UF = "onbeforematch" in document.documentElement;
export function initFacts(root = document) {
  if (!/\/resurrection\/$/.test(location.pathname)) return;
  const h = [...root.querySelectorAll("main h2, main h3")].find((x) => /minimal facts/i.test(x.textContent));
  let ol = h; while (ol && ol.tagName !== "OL") ol = ol.nextElementSibling;
  if (!ol) return;
  const items = [...ol.children].filter((li) => li.tagName === "LI");
  if (items.length < 2) return;
  const wrap = document.createElement("div"); wrap.className = "facts";
  const line = document.createElement("div"); line.className = "facts__line"; line.setAttribute("role", "group"); line.setAttribute("aria-label", "Minimal facts");
  const panels = document.createElement("div"); panels.className = "facts__panels";
  const btns = items.map((li, i) => {
    const b = document.createElement("button"); b.type = "button"; b.className = "facts__node";
    const id = `fact-panel-${i + 1}`;
    b.setAttribute("aria-expanded", "false"); b.setAttribute("aria-controls", id);
    const num = document.createElement("span"); num.className = "facts__num num"; num.textContent = String(i + 1);
    const lab = document.createElement("span"); lab.className = "facts__label label-mono";
    lab.textContent = (li.querySelector("strong") || li).textContent;
    b.append(num, lab);
    // Closed facts: grid 0fr slide, then hidden=until-found.
    const p = document.createElement("div"); p.className = "facts__panel"; p.id = id;
    p.setAttribute("role", "region"); p.setAttribute("aria-label", lab.textContent);
    const inner = document.createElement("div"); inner.className = "facts__inner";
    inner.append(...[...li.childNodes].map((n) => n.cloneNode(true)));
    p.append(inner);
    if (UF) inner.setAttribute("hidden", "until-found"); else { p.classList.add("is-open"); b.setAttribute("aria-expanded", "true"); }
    inner.addEventListener("beforematch", () => { if (b.getAttribute("aria-expanded") !== "true") open(i); });
    panels.append(p); line.append(b);
    return b;
  });
  const open = (i) => btns.forEach((b, k) => {
    const on = k === i && b.getAttribute("aria-expanded") !== "true";
    b.setAttribute("aria-expanded", String(on));
    const p = document.getElementById(b.getAttribute("aria-controls"));
    const inner = p.firstElementChild;
    clearTimeout(inner._t);
    if (!UF) { p.classList.add("is-open"); inner.hidden = false; return; }
    if (on) { inner.hidden = false; requestAnimationFrame(() => p.classList.add("is-open")); }
    else if (p.classList.contains("is-open")) {
      p.classList.remove("is-open");
      const ms = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--dur")) * 1000 || 0;
      inner._t = setTimeout(() => { if (b.getAttribute("aria-expanded") !== "true") inner.setAttribute("hidden", "until-found"); }, ms);
    } else inner.setAttribute("hidden", "until-found");
  });
  btns.forEach((b, i) => {
    b.addEventListener("click", () => open(i));
    b.addEventListener("keydown", (e) => {
      const k = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
      let j = null;
      if (k) j = (i + k + btns.length) % btns.length;
      else if (e.key === "Home") j = 0; else if (e.key === "End") j = btns.length - 1;
      if (j !== null) { e.preventDefault(); btns[j].focus(); }
    });
  });
  wrap.append(line, panels);
  ol.before(wrap); ol.hidden = true;
  return wrap;
}
