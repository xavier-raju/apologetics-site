// "Ask a question": client-side only. No AI, no network calls beyond our own static JSON.
import { buildIndex, search, tokens } from "../search.js";
import { ROOT } from "../app.js";
const esc = (s = "") => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const hl = (s, words) => { let h = esc(s); for (const w of words) if (w.length > 2) h = h.replace(new RegExp(`\\b(${w.replace(/[^a-z0-9]/g, "")}\\w*)`, "gi"), "<mark>$1</mark>"); return h; };

export async function init() {
  const form = document.querySelector("[data-ask-form]"), input = form?.querySelector("input"), out = document.querySelector("[data-ask-results]");
  if (!form) return;
  let ix;
  try { ix = buildIndex(await (await fetch(new URL("data/search-index.json", ROOT))).json()); }
  catch (e) { out.innerHTML = '<p class="empty">Search is unavailable right now. Try <a href="../answers/">browsing the answers</a>.</p>'; return; }
  const render = (q) => {
    if (!q.trim()) { out.innerHTML = ""; return; }
    const r = search(ix, q), words = tokens(q);
    if (!r.length) { out.innerHTML = `<div class="empty"><p>We haven't written an answer for that yet.</p><p><a href="../answers/">Browse all answers</a> or <a href="../library/?q=${encodeURIComponent(q)}">search the Library</a>.</p></div>`; return; }
    const [best, ...rest] = r;
    const url = (u) => new URL(u, ROOT).href;
    out.innerHTML = `
      <article class="card ask-best"><p class="eyebrow">Best match · ${esc(best.d.k)}</p>
        <h2 class="card__title"><a href="${url(best.d.u)}">${hl(best.d.t, words)}</a></h2>
        <p>${hl(best.d.s || best.d.x.slice(0, 240), words)}</p><p><a class="btn btn--sm" href="${url(best.d.u)}">Read the full answer <span aria-hidden="true">→</span></a></p></article>
      ${rest.length ? `<h2 class="h-sm">Also related</h2><ul class="ask-list">${rest.map(({ d }) => `<li><a href="${url(d.u)}"><span class="tag tag--neutral">${esc(d.k)}</span> <span>${hl(d.t, words)}</span></a></li>`).join("")}</ul>` : ""}
      <p class="muted small">Results come only from material on this site that our team has written and checked.</p>`;
  };
  let t;
  input.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => render(input.value), 120); });
  form.addEventListener("submit", (e) => { e.preventDefault(); render(input.value); history.replaceState(null, "", `?q=${encodeURIComponent(input.value)}`); });
  document.querySelectorAll("[data-ask-try]").forEach((b) => b.addEventListener("click", () => { input.value = b.textContent; render(input.value); input.focus(); }));
  const q = new URLSearchParams(location.search).get("q");
  if (q) { input.value = q; render(q); }
}
