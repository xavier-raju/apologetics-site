// Shared widgets via event delegation:
//  - Accordions: button[data-toggle][aria-controls]
//  - Tabs: [role=tablist] > [role=tab] (click, Arrow keys, Home/End)
//  - Pop-ups: button[data-word] (Greek/Hebrew) and button[data-verse] (BSB verse text, inlined at build time)
const esc = (s = "") => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';

let pop, owner;
function closePop(back = true) {
  if (!pop || pop.hidden) return;
  pop.hidden = true; owner?.setAttribute("aria-expanded", "false");
  if (back) owner?.focus();
  owner = null;
}
function showPop(btn, html, label) {
  if (owner === btn && pop && !pop.hidden) return closePop();
  closePop(false);
  if (!pop) {
    pop = document.createElement("div");
    pop.className = "popover"; pop.id = "popover"; pop.setAttribute("role", "dialog"); pop.hidden = true;
    document.body.append(pop);
  }
  pop.setAttribute("aria-label", label);
  pop.innerHTML = `<button class="icon-btn popover__close" type="button" aria-label="Close">${X}</button>${html}`;
  pop.hidden = false;
  const r = btn.getBoundingClientRect(), vw = document.documentElement.clientWidth;
  const w = pop.offsetWidth, h = pop.offsetHeight;
  const left = Math.max(12, Math.min(r.left, vw - w - 12));
  const below = r.bottom + 8 + h < innerHeight || r.top < h + 8;
  pop.style.left = `${left + scrollX}px`;
  pop.style.top = `${(below ? r.bottom + 8 : r.top - h - 8) + scrollY}px`;
  btn.setAttribute("aria-expanded", "true"); btn.setAttribute("aria-controls", "popover");
  owner = btn;
  pop.querySelector(".popover__close").focus();
}
function wordHTML(d) {
  const rtl = d.lang === "he";
  return `<div class="popover__orig" lang="${esc(d.lang)}" dir="${rtl ? "rtl" : "ltr"}">${esc(d.orig)}</div>
    ${d.lemma && d.lemma !== d.orig ? `<div class="muted small">Dictionary form: <span lang="${esc(d.lang)}" dir="${rtl ? "rtl" : "ltr"}">${esc(d.lemma)}</span></div>` : ""}
    <div class="popover__translit">${esc(d.translit || "")}</div>
    <p class="popover__gloss">${esc(d.gloss || "")}</p>
    ${d.morph ? `<p class="muted small">${esc(d.morph)}</p>` : ""}
    ${d.note ? `<p class="small">${esc(d.note)}</p>` : ""}
    ${d.strongs ? `<p class="muted small">Strong's ${esc(d.strongs)}${d.where ? ` · ${esc(d.where)}` : ""}</p>` : ""}`;
}
function verseHTML(d) {
  return `<p class="eyebrow">${esc(d.ref)} · BSB</p>${d.verses.map(([r, t]) => `<p class="small"><sup>${esc(r.split(":").pop())}</sup> ${esc(t)}</p>`).join("")}${d.more ? '<p class="muted small">…</p>' : ""}`;
}

function selectTab(tab) {
  tab.closest('[role="tablist"]').querySelectorAll('[role="tab"]').forEach((t) => {
    const on = t === tab;
    t.setAttribute("aria-selected", String(on)); t.tabIndex = on ? 0 : -1;
    const p = document.getElementById(t.getAttribute("aria-controls")); if (p) p.hidden = !on;
  });
}

export function initWidgets(root) {
  root.addEventListener("click", (e) => {
    const t = e.target.closest("[data-toggle]");
    if (t) {
      const on = t.getAttribute("aria-expanded") !== "true";
      t.setAttribute("aria-expanded", String(on));
      const p = document.getElementById(t.getAttribute("aria-controls")); if (p) p.hidden = !on;
      return;
    }
    const tab = e.target.closest('[role="tab"]'); if (tab) return selectTab(tab);
    const w = e.target.closest("[data-word]");
    if (w) { try { return showPop(w, wordHTML(JSON.parse(w.dataset.word)), "Word details"); } catch { return; } }
    const v = e.target.closest("[data-verse]");
    if (v) { try { return showPop(v, verseHTML(JSON.parse(v.dataset.verse)), "Bible verse"); } catch { return; } }
    if (e.target.closest(".popover__close")) return closePop();
    if (pop && !pop.hidden && !e.target.closest(".popover")) closePop(false);
  });
  root.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closePop();
    const tab = e.target.closest?.('[role="tab"]');
    if (tab && ["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) {
      const tabs = [...tab.closest('[role="tablist"]').querySelectorAll('[role="tab"]')];
      let i = tabs.indexOf(tab);
      i = e.key === "Home" ? 0 : e.key === "End" ? tabs.length - 1 : (i + (e.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
      e.preventDefault(); tabs[i].focus(); selectTab(tabs[i]);
    }
  });
  addEventListener("resize", () => closePop(false));
}
