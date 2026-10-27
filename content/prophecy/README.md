# Prophecy explorer content (owner: Mark, checker: John)

These are content files only, with no page code. Routes are placeholders until TARS posts the style guide. Built 2026-10-26 by script (`/workspace/data/build/spec.py` holds the content, and `build.py` holds the extraction and checks).

## Files
- `prophecies.json`: 29 entries.
- `words.json`: 55 Hebrew/Greek pop-up entries.
- `crossrefs.json`: OpenBible top 10 for each of the 29 passages.
- `CREDITS.md`: attribution lines.

## Schema
**prophecies.json** has `{meta, prophecies[]}`. Each entry has:
`id` (stable slug, e.g. `isaiah-53`), `title`, `category`, `strength` (`direct prediction` | `typological` | `pattern`, defined in `meta.strength_labels`), `contested` (bool), `ot` and `nt[]` passages, `why_christians_read_it_this_way`, `traditional_jewish_reading` (our own paraphrase, never quoted), `note` (string or null), `word_ids[]` (keys into words.json), and `sources[]`.
- A passage is `{ref, translation:"BSB", text_source, verses[{ref, text}]}`. Every verse is taken from `site/data/bible/bsb.json` and was checked by script for an exact match against an independent download of bereanbible.com/bsb.txt. BSB uses English verse numbering.
- A source is `{title, url, use, link_check}`. `use` is `public domain`, `link only…` and so on.

**words.json** has `{meta, words{id: …}}`. Each word has `lang`, `strongs`, `stepbible_id`, `lemma`, `transliteration` and `gloss` (STEPBible), `definition` (STEPBible, shortened), `occurrence{ref, versification, surface, segmented, morph_code, morphology}`, `sources[]`, and an optional `editor_note`. Hebrew refs use **Hebrew** verse numbering (e.g. Isa.9.5 = English 9:6; Ps.22.17 = English 22:16).

**crossrefs.json** has `{meta, crossrefs{prophecy_id: {ot_ref, refs[{from, to, votes}]}}}` in OSIS refs. It holds references only, so the page should pull verse text from bsb.json.
- **Filter rule:** an OpenBible link is kept only if its target is a New Testament verse that overlaps one of the entry's listed NT fulfilment passages, meaning passages that quote, allude to, or claim fulfilment of the OT text. Thematic links (e.g. Isa 7:14 → John 1:1) and OT-to-OT links are dropped. Up to 10 are kept, sorted by votes. That leaves 80 links in total, from 1 to 10 per entry.

**Hand-written word card:** `ps22-16-textual-question` (`kind: "textual question"`, `hand_written: true`) has `title`, `readings[{witness, form, transliteration, meaning}]`, `explanation`, `status_note` and `references[]`. It replaces the OSHB-generated ka'ari card.

Each prophecy also has `traditional_jewish_reading_status`, which reads "Paraphrased… Pending John's check. Jewish sources are link only."

## Rules followed
- There is no date-setting for Daniel 9, no probability math, and no Bible codes.
- Jewish readings are stated respectfully.
- Copyrighted works are links only.

## Open items
1. **Sefaria links (13) and isaiah53.com return HTTP 403 to curl**, so they're marked UNVERIFIED in `link_check`. They need a browser check, and Sefaria stays link only.
2. **Ps 22:16:** the generated 'to dig' card was replaced with a hand-written textual-question card (TARS's call). The Nahal Hever plate is marked unconfirmed.
3. **Nahal Hever plate**: still unconfirmed as showing Ps 22, so it stays Contested.
4. The Jewish-reading summaries come from my general knowledge of the standard commentators. The specific attributions (Sanhedrin 98a/98b, Sukkah 52a, the Targums on Gen 3:15, Gen 49:10 and Isa 42:1, and Maimonides) should be spot-checked in a browser.
5. Cross-references are now filtered to fulfilment links (see the filter rule).

## Update 2026-10-26, 11:20 PM ET (after John's check)
- Applied John's fixes: Sanhedrin 98a for clouds/donkey; Gen 3:15 names Targum Pseudo-Jonathan and the Jerusalem (Fragment) Targum; added Targum Jonathan on Isa 52:13 (exaltation only); Sukkah 52a "slaying" wording; new Matt 27:9 note; Ps 22:16 card labeled Contested, "a few Hebrew manuscripts", "Ps 21:17 LXX (= Ps 22:16)".
- `traditional_jewish_reading_status` reads "Checked by John" for isaiah-53, zech-9-9, ps-2-7, gen-3-15, gen-49-10 and isa-42-1. All other entries are still pending. That includes zech-12-10, which wasn't on the list even though its wording fix has been applied.
- Maimonides (Deut 18): the link is to Yesodei HaTorah 7:6, which is link only and Unverified (403).
- Word glosses: when STEPBible lists both a proper-name sense and a common sense of a word, we now pick the common sense. This changed corner (Ps 118:22), fish (Jonah 2:1) and pit: grave (Ps 16:10). Hand overrides: qedem = "ancient times, of old"; Shiloh = meaning debated.
