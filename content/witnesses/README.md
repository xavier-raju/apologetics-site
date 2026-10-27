# Outside witnesses: content files

Owner: Matthew. Checker: Luke. Content only; no page code.

## Files
- `witnesses.json`: one object `{assumption, cards[]}`. 11 cards.
- `intro.md`: short section intro.
- `texts/*.md`: full public-domain texts (only the relevant chapter or letter) for the site Library. Each file starts with a YAML header: title, source_url, translation, license, retrieved.

## Card schema
- `id`, `name`, `stance` (who they were), `work` (work and passage), `date_written` (approx), `years_after_cross` (from AD 30; see `assumption`)
- `quote`: short exact quote from the PD translation in `texts/` (null where we paraphrase). `quote_note` optional.
- `paraphrase`: our own words, used only where no PD text is available (Talmud).
- `translator`, `source_url`
- `shows`, `does_not_prove`, `scholarly_status`
- `framing`: optional note for hostile material (Celsus, Talmud)
- `confidence`: Confirmed / Contested / Unverified, plus optional `confidence_note`
- `full_text`: path or list of paths in `texts/`, or null
- `note_for_site`, `license_note`: optional

## Sources and licenses (all loaded 26 Oct 2026)
- Josephus, Antiquities, Whiston 1737: Project Gutenberg #2848, https://www.gutenberg.org/ebooks/2848 . Public domain.
- Pliny, Letters, Melmoth rev. Bosanquet: Project Gutenberg #2811, https://www.gutenberg.org/ebooks/2811 . Public domain. Gutenberg numbers 10.96/10.97 as X.97/X.98.
- Tacitus, Annals 15.44, Jackson (Loeb 1937): LacusCurtius, https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/15B*.html . Page states "The text is in the public domain." Thayer's and Loeb notes are not copied.
- Suetonius, Claudius and Nero, Rolfe (Loeb 1914): LacusCurtius, https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Suetonius/12Caesars/Claudius*.html and .../Nero*.html . Public domain per page. Notes not copied.
- Lucian, Death of Peregrine, Fowler 1905: https://sacred-texts.com/cla/luc/wl4/wl420.htm . Public domain by age. Translator confirmed on the volume index, https://sacred-texts.com/cla/luc/wl4/index.htm (vol. IV, Clarendon Press 1905).
- Origen, Against Celsus 1 and 2, Crombie, ANF vol. 4 (1885): https://www.newadvent.org/fathers/04161.htm and 04162.htm . Public domain translation. We host our own copy of the relevant chapters; New Advent is credited as the online source.
- Julius Africanus, Chronography XVIII, ANF vol. 6 (1886): https://www.newadvent.org/fathers/0614.htm . Public domain.
- Mara bar Serapion, Pratten, ANF vol. 8 (1886): https://www.newadvent.org/fathers/0863.htm . Public domain.
- Talmud Sanhedrin 43a: https://www.sefaria.org/Sanhedrin.43a . English (William Davidson Edition) is CC BY-NC. Paraphrased only; link only.
- Scholarship named (link only, not quoted): T. C. Schmidt, Josephus and Jesus: New Evidence for the One Called Christ (Oxford University Press, 2025; open access CC BY-NC-ND, link only); Agapius' Arabic summary of the Testimonium.

## Editing notes
Footnote and page markers from the source pages were removed from texts; wording is otherwise unchanged. Gutenberg license boilerplate is not included; if we redistribute the Gutenberg files as files, strip all Gutenberg trademark references (already done).
