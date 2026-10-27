// Library: filtering is handled by filters.js; this keeps the URL shareable.
export function init() {
  const input = document.querySelector("[data-filter-search]");
  const scope = document.querySelector("[data-library]");
  if (!input || !scope) return;
  let t;
  const sync = (q, topic) => {
    const p = new URLSearchParams();
    if (q) p.set("q", q); if (topic && topic !== "*") p.set("topic", topic);
    history.replaceState(null, "", p.toString() ? `?${p}` : location.pathname);
  };
  let topic = new URLSearchParams(location.search).get("topic") || "*";
  scope.addEventListener("filterchange", (e) => { topic = e.detail.tag; clearTimeout(t); t = setTimeout(() => sync(input.value.trim(), topic), 300); });
}
