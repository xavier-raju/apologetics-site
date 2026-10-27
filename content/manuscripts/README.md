# Manuscripts: content files

Owner: Matthew. Checker: Luke. Content only; no page code. Feeds Alfred's answer card 4.

## Files
- `intro.md`: warm, short section intro.
- `key-facts.json`: `{facts[]}`, 7 facts. Fields: `id`, `number`, `wording` (site text), optional `detail`, `source`, `url`, `confidence` (Confirmed / Contested / Unverified), optional `todo`.
- `showcase.json`: `{manuscripts[]}`, 7 manuscripts (P52, P46, P66, P75, Sinaiticus, Vaticanus, Alexandrinus). Fields: `id`, `name`, `date_range`, `contents`, `holding`, `image_link` (link only, never embed), `image_note`, `shows`, `caution`, `sources[]`, `confidence`.
- `what-changed.md`: what changed and what didn't, the three late passages, and the answer card hook.
- `myths.json`: `{myths[]}`, 7 items "numbers you may hear that we don't use". Fields: `claim`, `why`, `use_instead`.

## Sources (all link only; none of their text or images is reused)
- INTF Kurzgefasste Liste, https://ntvmr.uni-muenster.de/liste (loaded). No open license seen.
- Evangelical Textual Criticism blog, Liste tally, http://evangelicaltextualcriticism.blogspot.com/search/label/Kurzgefasste%20Liste (via search).
- Peter J. Gurry, NTS 62 (2016), https://doi.org/10.1017/s0028688515000314 ; open copy https://www.repository.cam.ac.uk/items/c8072fdb-796c-4660-a232-c487c3b8a36f
- Brent Nongbri, HTR 98 (2005), https://doi.org/10.1017/s0017816005000842
- Brent Nongbri, 'Palaeography, Precision and Publicity: Further Thoughts on P.Ryl. iii.457 (P52)', New Testament Studies (online 2020), https://doi.org/10.1017/s0028688520000089 (author and title per Crossref, from Luke's check; Mazza not cited)
- Oxford Handbook chapter, https://doi.org/10.1093/oxfordhb/9780197581315.013.0027 ; Cambridge chapter, https://doi.org/10.1017/9781108620420.023
- Hixson and Gurry eds., Myths and Mistakes in NT Textual Criticism (IVP 2019). Book, not loaded.
- Peter J. Williams, Can We Trust the Gospels? (Crossway 2018); Richard Bauckham, Jesus and the Eyewitnesses (2nd ed. 2017). Books, not loaded; for further reading.
- CSNTM, https://www.csntm.org/manuscript (loaded). Images restricted: link only.
- Codex Sinaiticus Project, https://codexsinaiticus.org/en/codex/ (loaded). Image terms unknown: link only.
- Vatican Library, Vat. gr. 1209, https://digi.vatlib.it/view/MSS_Vat.gr.1209 (loaded). Image terms unknown: link only.
- SBLGNT (CC BY 4.0), https://sblgnt.com/license/ ; if we show Greek, use SBLGNT or STEPBible TAGNT (CC BY 4.0) with credit.

## Sources added 26 Oct 2026 (follow-up)
- P52: Manchester Digital Collections, https://www.digitalcollections.manchester.ac.uk/view/MS-GREEK-P-00457
- P46: CSNTM record quoting the INTF Liste, http://images.csntm.org/Manuscripts/GA_P46/P46%20(CBL%20BP%20II).pdf ; University of Michigan, https://apps.lib.umich.edu/reading/Paul/discovery.html
- P66: CSNTM, https://manuscripts.csntm.org/manuscript/View/GA_P66_Bodmer ; Pinakes, https://pinakes.irht.cnrs.fr/notices/cote/getPdf/74136/ ; Nongbri on P66, https://researchers.mq.edu.au/en/publications/the-limits-of-palaeographic-dating-of-literary-papyri-some-observ/
- P75: Vatican Library, https://www.vaticanlibrary.va/en/multimedia/papiro-hanna-1.html ; Nongbri, JBL 135 (2016) 405-37, https://brentnongbri.com/wp-content/uploads/2020/01/nongbri-pbodmer-xiv-xv-jbl-2016-offprint.pdf
- P137: Egypt Exploration Society, https://www.ees.ac.uk/news/poxy-lxxxiii-5345/
- Ehrman paraphrase source: transcription with page photos, https://christianapologetics.org/biblical-items/the-elusive-bart-ehrman-quote/ (Misquoting Jesus, 2005 paperback, pp. 252-253)
- Bible quotes: Berean Standard Bible (public domain), from site/data/bible/bsb.json

Note: these items were seen through search-result extracts or WebFetch; the INTF Liste server itself did not respond from the box on 26 Oct 2026.

## Open items
- Codex Alexandrinus: Confirmed "5th century" from the BL archive catalogue (Royal MS 1 D VIII), John, 26 Oct 2026. BL item pages still down; link the catalogue.
- 5,711: Confirmed as a passing tally, Gurry on ETC, 2 Apr 2026. Cambridge open copy of Gurry is CC BY-NC, link only. OUP chapter still blocked by Cloudflare; needs a human click before launch.
- Ehrman line: paraphrased, not quoted (team rule: no word-for-word quote from a secondhand transcription). If someone checks the book itself before launch, the exact quote can go back in.
- Image reuse terms for Manchester, CSNTM, Vatican, Sinaiticus: link only until checked.
