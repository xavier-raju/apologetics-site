// Generic chip filters + text search. Markup contract (see STYLE-GUIDE.md):
//   [data-filter-scope]  container
//   button[data-filter="tag"|"*"]           toggles one tag (single select)
//   button[data-access-filter="hosted"|"link"|"*"]  optional second filter (library)
//   input[data-filter-search]               optional text filter (matches data-text or textContent)
//   [data-tags="a b"]                       filterable items
//   [data-filter-count], [data-filter-empty] optional status outputs
export function initFilters(doc) {
  doc.querySelectorAll("[data-filter-scope]").forEach((scope) => {
    const items = [...scope.querySelectorAll("[data-tags]")];
    const search = scope.querySelector("[data-filter-search]");
    const count = scope.querySelector("[data-filter-count]");
    const empty = scope.querySelector("[data-filter-empty]");
    const state = { tag: "*", access: "*", q: "" };
    const params = new URLSearchParams(location.search);
    if (params.get("topic")) state.tag = params.get("topic");
    if (params.get("q") && search) { state.q = params.get("q").toLowerCase(); search.value = params.get("q"); }

    const press = (attr, val) => scope.querySelectorAll(`[${attr}]`).forEach((b) => b.setAttribute("aria-pressed", String(b.getAttribute(attr) === val)));
    const apply = () => {
      const words = state.q.split(/\s+/).filter(Boolean);
      let n = 0;
      for (const it of items) {
        const tags = (it.dataset.tags || "").split(/\s+/);
        const text = it.dataset.text || it.textContent.toLowerCase();
        const ok = (state.tag === "*" || tags.includes(state.tag)) &&
          (state.access === "*" || it.dataset.access === state.access) &&
          words.every((w) => text.includes(w));
        it.hidden = !ok; if (ok) n++;
      }
      if (count) count.textContent = `${n} of ${items.length} shown`;
      if (empty) empty.hidden = n > 0;
      press("data-filter", state.tag); press("data-access-filter", state.access);
      scope.dispatchEvent(new CustomEvent("filterchange", { detail: { ...state } }));
    };
    scope.addEventListener("click", (e) => {
      const b = e.target.closest("[data-filter],[data-access-filter]");
      if (!b) return;
      if (b.hasAttribute("data-filter")) state.tag = b.dataset.filter === state.tag && b.dataset.filter !== "*" ? "*" : b.dataset.filter;
      else state.access = b.dataset.accessFilter;
      apply();
    });
    search?.addEventListener("input", () => { state.q = search.value.trim().toLowerCase(); apply(); });
    scope.filterTo = (tag) => { state.tag = tag; apply(); };
    apply();
  });
}
