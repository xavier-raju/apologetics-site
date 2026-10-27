# Style guide & build guide

Site name: **Certainty** (Luke 1:4; home verse Luke 1:3–4), subtitle **A Toolkit for Christians and Apologists** (shown under the wordmark, in the home `<title>`, og tags and footer; `site.config.json` → `subtitle`). Secondary home line (`tagline`): “The case for Jesus, honestly examined.” Both live in one place: `site.config.json` → `"name"`, (`name`, `tagline`), then rebuild. Repo/URL stays `apologetics-site` (`base_path`).

A static site: plain HTML, CSS and vanilla JavaScript (ES modules). **No PHP, no server code, no frameworks, no trackers (except cookie-free GoatCounter visit counts), no paid services, no API keys.** Built by `build.py` (Python 3.9+, standard library only) into `_site/`, which is what we publish on GitHub Pages.

```
python3 build.py                 # builds _site/, checks every internal link, exits 1 on a broken link
python3 -m http.server -d _site  # preview at http://localhost:8000/
```

## 1. Feel (inspired by D. E. Shaw, not copied)
What we took from deshaw.com: lots of white space, one confident accent blue on white, quiet grey type for secondary text, thin hairline rules instead of boxes, geometric line art that draws itself, a calm sticky header, generous type. Nothing from their site (code, images, logo, fonts) is used. Our mark is an original circle crossed by two lines (`MARK` in build.py, `assets/favicon.svg`).

Rules of thumb: one idea per section; at most one solid (dark) button per view; hairlines (`--line`) before borders; motion only to explain or delight, never to block reading.

## 2. Color (all text pairs pass WCAG AA on their background)
| Token | Hex | Use | Contrast |
|---|---|---|---|
| `--ink` | #14161a | body text, solid buttons | 18.1:1 on white |
| `--ink-2` | #3a3f48 | secondary text | 10.6:1 |
| `--muted` | #5b6270 | meta, captions | 6.1:1 on white, 5.7:1 on mist |
| `--accent` | #1f4fd8 | links, eyebrows, focus | 6.6:1 |
| `--accent-ink` | #173da8 | link hover | 9.3:1 |
| `--paper` / `--mist` / `--mist-2` | #fff / #f5f6f8 / #eef1f5 | backgrounds | |
| `--line` / `--line-2` | #e3e6eb / #cfd4dc | hairlines, control borders | |
| `--ok` on `--ok-soft` | #1d6b3a / #e6f3eb | **Confirmed** | 5.7:1 |
| `--warn` on `--warn-soft` | #8a5300 / #fdf1dc | **Contested** | 5.7:1 |
| `--bad` on `--bad-soft` | #a42323 / #fbe9e9 | **Disputed** | 6.3:1 |
| #5a4a00 on #f6f0d0 | | **Unverified** | 7.6:1 |
Footer: white/#d7dbe2 on `--ink`.

## 3. Type
- **Newsreader** (serif, headings, quotes, Scripture) and **Inter** (sans, UI and body). Both SIL OFL 1.1, self-hosted in `assets/fonts/` (latin subsets, variable weight). No Google requests at runtime.
- Greek/Hebrew: `--font-orig` (system SBL / Noto Serif fallbacks). Hebrew always gets `lang="he" dir="rtl"`.
- Scale (fluid with `clamp`): xs 13px · sm 15px · base 17px · md 20px · lg 22→28px · xl 28→40px · 2xl 36→64px. Body line-height 1.6, headings 1.15, measure ≈ 40rem.
- Eyebrow: 13px, 600, uppercase, letter-spacing .14em, accent color.

## 4. Space, layout, breakpoints
Spacing tokens on a 4px base: `--s1` 4 · `--s2` 8 · `--s3` 12 · `--s4` 16 · `--s5` 24 · `--s6` 32 · `--s7` 48 · `--s8` 72 · `--s9` 112. Sections use `--s8` vertical padding.
Mobile first. Breakpoints (min-width): **600px** (2-column grids), **900px** (3 columns, side-by-side layouts), **1100px** (desktop nav bar replaces the Menu button). Container `.wrap` max 72rem with 24px (32px ≥900) side padding. Tested at 360, 375, 412 and 1280px: zero horizontal scroll. Grid children get `min-width:0` and long words wrap (`overflow-wrap:anywhere`) so nothing pushes the page wider.

## 5. Components (class names in `assets/css/site.css`)
- **Header**: sticky, translucent, hairline appears on scroll. Desktop shows 7 primary links; phones show only brand, search icon and **Menu**. The menu is a full-screen dialog listing all 12 sections with a one-line note each; it traps focus, closes on Esc, and returns focus.
- **Buttons**: `.btn` (solid, one per view), `.btn--ghost` (outline), `.btn--link`, `.btn--sm`. All ≥44px tall. Arrow nudges right on hover.
- **Chips**: `.chip[aria-pressed]` for filters.
- **Tags**: `.tag--confirmed|contested|disputed|unverified|neutral|example|hosted|link`. Made by `status_tag()` from any `status`/`confidence` string.
- **Cards**: `.card` (hairline box), `.card--link` (whole card clickable via stretched title link), `.card__meta`, `.card__title`.
- **Quote card**: `figure.quote > blockquote + figcaption` (author, work, date, status). Large faint opening quote mark.
- **Answer card**: `article.answer` accordion. Head = rank + question; body = **30-second answer** (`.answer__short`, accent rule), **Evidence** list, optional primary text quote, **Still debated**, **Go deeper** links, link to its own page. Same component on `/answers/` (collapsed) and `/answers/<id>/` (open).
- **“What it shows / What it doesn't prove”**: `dl.shows` (second label in amber). Used on finds, witnesses and manuscripts.
- **Sources**: `details.sources` (collapsed, + / −) containing `.source-list`.
- **Tabs**: `[role=tablist]` with arrow-key, Home/End support (`tabs()` in build.py). Used for Christian / Jewish readings, NT passages, others-say.
- **Word pop-up** (Greek/Hebrew): `button.word-chip[data-word]` → popover with original, dictionary form, transliteration, gloss, morphology, Strong's. Closes on Esc, outside tap, or ×; focus returns.
- **Verse pop-up**: `button.verse[data-verse]` (any Scripture reference). BSB text is inlined at build time, so no download is needed.
- **Stat**: `.stat` big serif number + label. **Timeline**: `ol.timeline`. **Map**: schematic SVG with keyboard-focusable pins. **Quiz**: `[data-quiz]`.

## 6. Motion
- Hero: original line geometry that draws itself once (2.4s), one slow orbiting dot (90s/turn).
- `.reveal`: fade + 14px rise when scrolled into view (IntersectionObserver, `rootMargin:"0px 0px -5% 0px"`: only px/% units are legal; a 2.5s safety net reveals everything regardless).
- Hover: 2px card lift, arrow nudge, underline grow. Durations 0.2–0.7s, easing `cubic-bezier(.2,.7,.2,1)`.
- `prefers-reduced-motion: reduce` turns all of it off: content is shown immediately, no drawing, no orbit.

## 7. Accessibility checklist (every page)
WCAG AA contrast (table above) · tap targets ≥44px (inline text links excepted per WCAG 2.5.8) · skip link · landmarks `header`, `nav` (labelled), `main#main`, `footer` · one `h1` per page · visible 3px focus ring on everything · full keyboard use (menu, tabs, accordions, pop-ups, map pins, quiz) · `aria-expanded`/`aria-controls`/`aria-pressed`/`aria-live` on widgets · Hebrew marked `rtl` · works without JavaScript (all content is in the HTML; JS only adds filtering, pop-ups, search and the quiz).

## 8. Routes (real folders, no server rewrites, GitHub Pages friendly)
Every route is a folder with `index.html`; all internal links are written **relative to the page**, so the site works at `username.github.io/<repo>/` (tested at `/apologetics-site/`) and on a custom domain unchanged.

| Route | Source |
|---|---|
| `/` | home (build_home) |
| `/start-here/` | content/start-here/start-here.md |
| `/timeline/` (`#<event-id>`) | content/timeline/events.json |
| `/map/` (`#find-<id>`, `#place-<id>` pre-selects a pin) | content/evidence-map/places.json + finds.json |
| `/witnesses/` (`#<card-id>`) | content/witnesses/witnesses.json + intro.md |
| `/manuscripts/` | content/manuscripts/*.json + *.md |
| `/prophecy/` and `/prophecy/<passage-id>/` (e.g. `/prophecy/isaiah-53/`) | content/prophecy/prophecies.json, words.json, crossrefs.json |
| `/resurrection/` | content/resurrection/resurrection.md |
| `/answers/` (`#<card-id>` opens that card) and `/answers/<card-id>/` | content/answer-cards/cards.json |
| `/learn/` (`#<lesson-slug>`, `#quiz`) | content/learn/lessons/*.md + quiz.json |
| `/what-others-say/` | content/what-others-say/perspectives.json |
| `/library/` (`?q=`, `?topic=`) and `/library/<text-slug>/` | content/library/index.json + every content/witnesses/texts/*.md |
| `/ask/` (`?q=`) | data/search-index.json (generated) |
| `/<slug>/` | content/pages/<slug>.md (generic page template) |
| `/404.html` | uses `<base href>` from `site.config.json` → `base_path` (set to `/<repo>/` when published) |

**Writing links in content:** use site routes starting with `/` (e.g. `/answers/hallucination`, `/prophecy/isaiah-53`); the build rewrites them to correct relative URLs. Source paths to hosted texts (e.g. `/content/witnesses/texts/pliny-letters-10-96-97.md`) are mapped to `/library/pliny-letters-10-96-97/`; **the build fails** if such a path does not match a hosted file. External links open in a new tab with `rel=noopener`.

## 9. How section owners plug content in
Content lives in `content/<section>/`. Owners edit only their folder, then run `python3 build.py`. The schemas below are the ones the build reads today; they match each section's own README.

- **start-here/start-here.md** — front matter `title`. `# H1` becomes the page title; text before the first `##` is the lede; each `##` becomes a panel. Quoted section names (“Ask a question”, “Answer an objection”, …) are auto-linked.
- **timeline/events.json** — `[{id, title, date_display, date_start, date_end, approximate, category, summary, scripture_refs[], sources[{label,url}], status, related_places[]}]`. Category chips are generated from `category`. Refs become BSB verse pop-ups; places link to the map.
- **evidence-map/places.json** — `[{id, name, lat, lon, coord_note, source_dataset, source_id, source_url, license}]` (null lat/lon = not drawn). **finds.json** — `[{id, name, place_id, date_found, era, category, summary, shows, does_not_prove, sources[{label,url}], status, image_license}]`. Images are not shown until `image_license` is set (future field: `image` path).
- **witnesses/witnesses.json** — `{assumption, cards:[{id, name, stance, work, date_written, years_after_cross, quote|null, quote_note, paraphrase, translator, source_url, shows, does_not_prove, scholarly_status, framing, confidence, confidence_note, full_text: path|[paths]|null}]}`. **texts/*.md** front matter `title, source_url, translation, license, retrieved`; each becomes a hosted Library page with a download link.
- **manuscripts/** — `key-facts.json {facts:[{id, number, wording, detail, source, url, confidence}]}`, `showcase.json {manuscripts:[{id, name, date_range, contents, holding, image_link, image_note, shows, caution, sources[], confidence}]}`, `myths.json {myths:[{claim, why, use_instead}]}`, `intro.md`, `what-changed.md`.
- **prophecy/prophecies.json** — `{meta:{strength_labels}, prophecies:[{id, title, category, strength, contested, ot:{ref, verses[{ref,text}]}, nt:[{ref, verses[]}], why_christians_read_it_this_way, traditional_jewish_reading, note, word_ids[], sources[{title,url,use}]}]}`; **words.json** `{words:{<id>:{lang, strongs, lemma, transliteration, gloss, definition, occurrence:{ref, surface, morphology}}}}`; **crossrefs.json** `{crossrefs:{<prophecy-id>:{refs:[{from,to,votes}]}}}`. If `verses` is missing the build fills them from the BSB.
- **resurrection/resurrection.md** — front matter `title, summary`; Markdown incl. ordered lists, blockquotes, GFM tables, bare URLs.
- **answer-cards/cards.json** (“objections”, 11 cards) — `{cards:[{order, id, objection, short_answer, evidence[], primary_text{ref, translation, quote}, scholarly_link{name,url}, still_debated, keywords[], related[], see_also[{name,url}]}]}`. `keywords` feed the Ask box.
- **learn/** — `lessons/NN-slug.md` (front matter `title, minutes`; order by filename) and `quiz.json {pass_mark, questions:[{id, question, choices[4], answer (0-based), explanation, source (site route)}]}`. The page asks 10 random questions per round and shuffles choices.
- **what-others-say/perspectives.json** (“others-say”) — `{principles[], perspectives:[{id, group, title, their_view, how_to_respond, common_ground[], links[{name,url}]}]}`. Chips by `group`; each card has tabs What they say / How to respond / Common ground.
- **library/index.json** (TARS) — `{intro, topics:[{id,label}], items:[{id, title, author, date, topic, kind, access:"hosted"|"link", license, url, description, keywords[], example?}]}`. Witness texts are added automatically as hosted items. Rule: `hosted` only for public-domain or openly licensed files; copyrighted works (0xSero's report and PDF, scholars' books, articles, images) are `link` entries.
- **pages/<slug>.md** — generic page (copy `pages/_TEMPLATE.md`).
- Any item may carry `"example": true` to show a purple **EXAMPLE** tag.

**Field notes / requested changes (not edited; for owners to decide):**
1. answer-cards & quiz `source`/`url` values like `/answers/{id}` and `/prophecy/isaiah-53` are fine as written; the build rewrites them.
2. timeline/finds use `sources[{label,url}]`, prophecy uses `{title,url,use}`, others-say `{name,url}`: all accepted; new content should prefer `{label, url, note}`.
3. Status words: use exactly `Confirmed`, `Contested`, `Disputed` or `Unverified` (in `status` or `confidence`).

## 10. Bible data (`data/bible/`, John)
- `bsb.txt` (original) and `bsb.json` (`{"Book C:V": text}`) are John's and are never edited.
- The page never loads `bsb.json` (4.5 MB). At build time: (a) every Scripture reference gets its verse text inlined into the page (max 6 verses per pop-up); (b) the BSB is split into `_site/data/bible/books/<book-slug>.json` (`{"C:V": text}`) plus `books/index.json` (book name → slug) for any future lazy-loaded reader.
- Book names follow the BSB file (`Psalm`, `Song of Solomon`); `Psalms` and `Song of Songs` are aliased.
- Credit line (footer): “Scripture from the Berean Standard Bible (BSB), public domain.”

## 11. Ask a question (search)
`assets/js/search.js` is a self-written BM25 search (~70 lines): field weights (title 3, keywords 2.5, snippet 1.2, text 1), light stemming, a small synonym list (e.g. *real → exist*, *Nicaea → Constantine, canon*), prefix matching on the last word, and a boost for answer cards. The index (`data/search-index.json`, ~150 entries) is generated from answer cards, timeline, map finds, witnesses, manuscripts, prophecy, resurrection, lessons, others-say and the Library. It shows the best match (with snippet and link) and up to 7 related results. No AI, no network calls to anyone else.

## 12. JavaScript files
`app.js` (menu, header, reveal, accordions-from-hash, page loader) · `ui.js` (accordions, tabs, pop-ups) · `filters.js` (chip + text filtering via `data-filter-scope`, `data-filter`, `data-tags`, `data-filter-search`) · `search.js` · `pages/ask.js`, `pages/library.js`, `pages/map.js`, `pages/quiz.js`. A page opts into a page script via `page_js="name"` in build.py.

## 13. Adding a new section page
1. Put content in `content/<section>/` with a README of fields.
2. In `build.py`, copy a builder such as `build_others()` (filter chips + cards) or `build_resurrection()` (Markdown), point it at your files, add it to the list at the bottom, and add the route to `NAV`.
3. `python3 build.py` (must print no BROKEN LINK) → `python3 qa.py http://127.0.0.1:8000/` (console errors, overflow, tap targets, screenshots) → John's harness `bash john/qa/run.sh <url>`.

## 14. Publishing (when Xavier connects GitHub)
Publish `_site/` with GitHub Pages (Actions: `actions/upload-pages-artifact` with `path: site/_site`, then `actions/deploy-pages`), or commit `_site/` contents to a `gh-pages` branch. Set `base_path` in `site.config.json` to `/<repo>/` first (only the 404 page uses it). `.nojekyll` is included.
