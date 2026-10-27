# learn
- `lessons/NN-slug.md`: Markdown with front matter `title`, `minutes`. Order by filename prefix.
- `quiz.json` = `{version, pass_mark, questions:[{id, question, choices[4], answer, explanation, source}]}`.
  - `answer` is a **0-based index** into `choices`.
  - `source` is a site route (e.g. `/answers/{card-id}`, `/resurrection`, `/what-others-say`, `/start-here`). Adjust to TARS's final routes.
  - Shuffle choice order client-side if desired (remap `answer`).
