# answer-cards
`cards.json` = `{version, updated, cards:[...]}`. Each card:
- `order` (int, display order), `id` (slug, used as URL `/answers/{id}`)
- `objection`, `short_answer` (strings, about 30 seconds aloud)
- `evidence` (string[]), `primary_text` `{ref, translation, quote}` (public domain only)
- `scholarly_link` `{name, url}` (link only, never copy text)
- `still_debated` (string), `keywords` (string[], for the Ask box), `related` (card ids)
- optional `see_also` `[{name,url}]` (Isaiah 53 card links to Rashi and Mark's prophecy explorer; adjust that path to Mark's real route).
No X users are named or linked anywhere.
- `points_to_jesus`: object with `text` (one-line close that points back to Jesus, in our own words, no direct quote), `ref` ("1 Corinthians 15:3-8", BSB) and `link` (placeholder route to the resurrection page). Shown at the end of each card.
