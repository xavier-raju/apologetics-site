// Tiny self-written search engine (BM25 with field weights, light stemming, synonyms, prefix match).
// Index built by build.py -> data/search-index.json: [{k:kind, t:title, u:url, x:text, w:keywords, s:snippet, st:status}]
const STOP = new Set("a an and are as at be but by did do does for from had has have he her his how i if in into is it its me my no not of on or our she so that the their them then there these they this to was we were what when where which who why will with would you your about can could just than really even ever".split(" "));
const SYN = {
  real: ["exist", "historical"], exist: ["real", "historical", "myth"], myth: ["legend", "exist", "fairy", "copied"],
  changed: ["corrupted", "altered", "manuscripts", "copies"], corrupt: ["changed", "altered"], bible: ["scripture", "text", "gospels"],
  nicaea: ["constantine", "council", "canon", "nicene"], nicea: ["nicaea", "constantine", "council", "nicene"], nicene: ["nicaea", "council", "creed"], nicaean: ["nicaea"], constantine: ["nicaea", "council"], rise: ["resurrection", "risen", "raised"],
  resurrection: ["risen", "rise", "tomb"], tomb: ["resurrection", "body"], hallucinate: ["hallucination", "visions"],
  contradict: ["contradictions", "disagree"], evil: ["suffering", "pain"], suffering: ["evil"], prophecy: ["prophecies", "fulfilled", "messiah"],
  israel: ["servant", "jewish"], archaeology: ["find", "excavation", "dig"], pagan: ["copied", "myths", "horus", "mithras"],
};
export const stem = (w) => w.length > 4 ? w.replace(/(ations?|ings?|edly|ies|ied|es|ed|ly|s)$/, (m) => (m === "ies" || m === "ied" ? "y" : "")) : w;
export const tokens = (s) => (String(s).toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").match(/[a-z0-9]+/g) || []).filter((w) => !STOP.has(w));

const FIELDS = { t: 3, w: 2.5, s: 1.2, x: 1 };
const KIND = { Answer: 1.35, Resurrection: 1.15, Prophecy: 1.05, Witness: 1.05 };

export function buildIndex(docs) {
  const post = new Map(); const len = []; let total = 0;
  docs.forEach((d, i) => {
    let n = 0;
    for (const [f, wt] of Object.entries(FIELDS)) for (const w of tokens(d[f] || "")) {
      const s = stem(w); n++;
      let m = post.get(s); if (!m) post.set(s, (m = new Map()));
      m.set(i, (m.get(i) || 0) + wt);
    }
    len[i] = n; total += n;
  });
  return { docs, post, len, avg: total / Math.max(1, docs.length), terms: [...post.keys()] };
}

export function search(ix, q, limit = 8) {
  const qt = tokens(q);
  if (!qt.length) return [];
  const N = ix.docs.length, k1 = 1.2, b = 0.75, score = new Map(), hits = new Map(), core = new Set();
  const add = (term, weight, orig) => {
    const m = ix.post.get(term); if (!m) return;
    if (weight >= 0.85) core.add(term); // the query's own words (or their typo corrections)
    const idf = Math.log(1 + (N - m.size + 0.5) / (m.size + 0.5));
    for (const [i, tf] of m) {
      const s = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * ix.len[i] / ix.avg));
      score.set(i, (score.get(i) || 0) + s * weight);
      (hits.get(i) || hits.set(i, new Set()).get(i)).add(orig);
    }
  };
  qt.forEach((w, n) => {
    const s = stem(w);
    add(s, 1, w);
    if (!ix.post.has(s) && !SYN[s] && !SYN[w] && w.length >= 5) { // typo tolerance
      const max = w.length >= 9 ? 2 : 1, cands = [];
      for (const t of ix.terms) {
        if (Math.abs(t.length - s.length) > max && Math.abs(t.length - w.length) > max) continue;
        const d = Math.min(dl(s, t, max), dl(w, t, max));
        if (d <= max) cands.push([d, t]);
      }
      const best = Math.min(...cands.map((c) => c[0]));
      for (const [d, t] of cands) if (d === best) add(t, 0.85, w);
    }
    for (const y of SYN[s] || SYN[w] || []) add(stem(y), 0.45, w);
    if (n === qt.length - 1 && w.length >= 3) for (const t of ix.terms) if (t !== s && t.startsWith(s)) add(t, 0.5, w); // type-ahead
  });
  return [...score].map(([i, s]) => {
    const d = ix.docs[i], cover = hits.get(i).size / qt.length;
    // Prefer whole pages whose title or route is exactly what was asked (e.g. "resurrection" -> /resurrection/).
    const tt = tokens(d.t).map(stem), path = (d.u || "").split(/[#?]/)[0], page = !/[#?]/.test(d.u || "");
    const rt = tokens(path.split("/").filter(Boolean).pop() || "").map(stem);
    const exactTitle = tt.length > 0 && tt.length <= core.size + 1 && tt.every((t) => core.has(t));
    const exactRoute = page && rt.length > 0 && rt.every((t) => core.has(t));
    const boost = (exactTitle ? 1.8 : 1) * (exactRoute ? 1.5 : 1) * (page ? 1.1 : 1);
    return { d, score: s * (KIND[d.k] || 1) * (0.5 + cover) * boost };
  }).sort((a, z) => z.score - a.score).slice(0, limit);
}

// Optimal-string-alignment (Damerau-Levenshtein) distance with early exit above max.
export function dl(a, b, max = 2) {
  if (a === b) return 0;
  if (Math.abs(a.length - b.length) > max) return max + 1;
  const m = a.length, n = b.length; let p2 = null, p = Array.from({ length: n + 1 }, (_, j) => j);
  for (let i = 1; i <= m; i++) {
    const c = [i]; let low = i;
    for (let j = 1; j <= n; j++) {
      let v = Math.min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (p2 && i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, p2[j - 2] + 1);
      c[j] = v; if (v < low) low = v;
    }
    if (low > max) return max + 1;
    p2 = p; p = c;
  }
  return p[n];
}
