// Learn-mode quiz. Data: inline <script type="application/json" id="quiz-data"> from content/learn/quiz.json.
const esc = (s = "") => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

export function init() {
  const box = document.querySelector("[data-quiz]");
  let data;
  try { data = JSON.parse(document.getElementById("quiz-data").textContent); } catch { data = null; }
  if (!box) return;
  const all = data?.questions || [];
  if (!all.length) { box.innerHTML = '<p class="muted">The quiz is coming soon.</p>'; return; }
  const ROUND = Math.min(10, all.length), pass = data.pass_mark ?? 0.7;
  let qs, i, score;
  const start = () => { qs = shuffle([...all]).slice(0, ROUND); i = 0; score = 0; show(); };
  function show() {
    const q = qs[i];
    const order = shuffle(q.choices.map((c, k) => k));
    box.innerHTML = `
      <div class="quiz__top"><span class="muted small">Question ${i + 1} of ${qs.length}</span><span class="muted small">Score ${score}</span></div>
      <div class="progress" role="progressbar" aria-label="Quiz progress" aria-valuemin="0" aria-valuemax="${qs.length}" aria-valuenow="${i}"><span style="width:${(i / qs.length) * 100}%"></span></div>
      <h3 class="quiz__q" tabindex="-1">${esc(q.question)}</h3>
      <div class="quiz__opts">${order.map((k) => `<button class="quiz-opt" type="button" data-k="${k}">${esc(q.choices[k])}</button>`).join("")}</div>
      <div class="quiz__fb" aria-live="polite"></div>`;
    box.querySelector(".quiz__q").focus({ preventScroll: true });
    box.querySelectorAll(".quiz-opt").forEach((b) => b.addEventListener("click", () => answer(+b.dataset.k)));
  }
  function answer(k) {
    const q = qs[i], right = k === q.answer;
    if (right) score++;
    box.querySelectorAll(".quiz-opt").forEach((b) => {
      b.disabled = true;
      if (+b.dataset.k === q.answer) b.classList.add("is-right");
      else if (+b.dataset.k === k) b.classList.add("is-wrong");
    });
    const last = i === qs.length - 1;
    box.querySelector(".quiz__fb").innerHTML = `<p class="quiz__verdict ${right ? "ok" : "bad"}">${right ? "Correct." : "Not quite."}</p>
      <p>${esc(q.explanation || "")}</p>${q.source ? `<p><a href="${esc(q.source)}">Read more</a></p>` : ""}
      <button class="btn" type="button" data-next>${last ? "See my score" : "Next question"} <span aria-hidden="true">→</span></button>`;
    const n = box.querySelector("[data-next]"); n.focus();
    n.addEventListener("click", () => { if (last) done(); else { i++; show(); } });
  }
  function done() {
    const ok = score / qs.length >= pass;
    box.innerHTML = `<p class="eyebrow">Your score</p><p class="stat__n">${score} / ${qs.length}</p>
      <p>${ok ? "Well done. You're ready to share this with someone." : "Good start. Read a lesson or two and try again."}</p>
      <div class="btn-row"><button class="btn" type="button" data-again>Try another round</button><a class="btn btn--ghost" href="#main">Back to lessons</a></div>`;
    box.querySelector("[data-again]").addEventListener("click", start);
    box.querySelector("[data-again]").focus();
  }
  start();
}
