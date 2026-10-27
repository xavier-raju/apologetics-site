# Matthew's check of Luke's Timeline and Evidence Map

Checked: Monday Oct 26, 2026, about 11:15 PM ET. Luke was still editing `events.json` while I checked (the creed entry changed at 11:14 PM ET); this check reflects the files as of that time. Luke's files were not edited.

## Summary

- Entries checked: 68 (34 timeline events, 15 finds, 19 places)
- Confirmed: 57
- Contested (needs a wording fix): 8
- Wrong: 1
- Unverified: 2
- JSON: all three files are valid. Counts match the READMEs (34, 15, 19).
- Em dashes: none in any file.
- Scripture references: every reference in `events.json` exists in `bsb.json`. No Bible verse is quoted word for word, so there is nothing to match. Where the text paraphrases, I suggest BSB wording (see Bethesda).
- Links: I loaded all 69 unique source URLs. 63 return 200. Blocked from the box: OUP Schmidt book (403), Tel Aviv DOI for Szanton et al. (403), BAS el-Araj article (403), Times of Israel (403, but its content is confirmed through search, see below), Israel Museum Caiaphas page (timed out, same as Luke). The PEQ DOI redirects (302) to the publisher. None are 404s.
- Licenses: CREDITS are correct. OpenBible CC BY 4.0 and Pleiades CC BY 3.0 both need a credit line on the map page, as Luke notes. One small fix: timeline CREDITS calls the Georgetown Pliny a "public domain translation". The Georgetown page does not name its translator, and it is not Melmoth. Since we only link to it this is fine, but the label should not say public domain, and the Pliny entry should point to our hosted Melmoth text (see `pliny` below).

## Wrong (1)

**john-written**: "c. AD 90-110" and "Most scholars date John ... about 90-110."
- Issue: goes past the team number ("about AD 65 to 100, many date some before 70"). The site would show two different ranges for the Gospels. I also could not open Brown to confirm 90-110 as his figure.
- Fix: date_display "c. AD 90-100 (some date it later, a few earlier)", date_end 100. Summary: "Most scholars date John last of the four, around AD 90 to 100."
- Source checked: team number from card 3 sources (Matthew's earlier check). Brown book page loads (yalebooks.yale.edu) but gives no page number. Unverified for page number.

## Contested (8)

**birth** (timeline)
- Issue: "most scholars date it about 6-4 BC" and "Herod ... died in 4 BC" rest only on Matthew 2:1 and the 0xSero link. That is fine for what the Gospels report, but the dating claim needs a scholarly or primary anchor.
- Fix: add the same sources as `herod-death` (Josephus, Antiquities 17, https://penelope.uchicago.edu/josephus/ant-17.html, and the Herod overview). Wording can stay.

**nazareth-childhood** (timeline)
- Issue: "Archaeology shows the village was inhabited at the time" is sourced only to Luke 2 and 0xSero.
- Fix: add Ken Dark, Antiquaries Journal 92 (2012), https://doi.org/10.1017/s0003581512001308 (loaded), already used in the `nazareth-house` find.

**siloam** (timeline)
- Issue: "The pool was found in 2004" states the identification as settled fact.
- Fix: "A large Second Temple pool, widely identified as the Pool of Siloam, was found in 2004. Excavation of the rest of it is still under way."
- Source loaded: https://en.wikipedia.org/wiki/Pool_of_Siloam (rediscovered autumn 2004 during sewer work; wider dig after December 2022).

**appearances** (timeline)
- Issue: "Historians across viewpoints agree the disciples sincerely believed they had seen him alive" has only a Bible source.
- Fix: keep the wording but add Habermas 2012 (https://www.garyhabermas.com/articles/Habermas_Minimal%20Facts%20STR%202012.pdf, loaded), or soften to "Most historians, skeptics included, accept that the disciples sincerely believed they had seen him alive."

**pliny** (timeline)
- Issue: the source is the Georgetown page, which is a different, unnamed translation (its opening is "It is my practice, my lord"). The quote "to Christ as to a god" is that translation's wording, not Melmoth's. Our team rule is to quote Pliny from Melmoth/Bosanquet. My witnesses card note says the same.
- Fix: quote the exact Melmoth line from our hosted library text (or paraphrase without quote marks), and make the main source our hosted Melmoth/Bosanquet text, cited as "Letters 10.96 (X.97 in the Melmoth/Bosanquet numbering)". The Georgetown link can stay as an extra.
- Source loaded: https://faculty.georgetown.edu/jod/texts/pliny.html

**pilgrimage-road** (find)
- Issue 1: era "Built about AD 31". The coins under the paving give the earliest possible date (latest coins AD 30/31), not an exact one.
- Fix: "Built no earlier than about AD 30/31, in the years Pilate governed (based on coins under the paving)."
- Issue 2: "Excavated in stages from 2013". Times of Israel says about 20 years of digging; KAN says 13 years. Suggest "Excavated in stages over many years".
- Everything else is confirmed: opened January 20, 2026, about 600 m long, about 8 m wide, under Silwan, and the Herod or Pilate attribution is still debated.
- Sources: Times of Israel article (403 from the box; content confirmed through search), https://www.israel.com/places/old-city-jerusalem/things-to-do/city-of-david (via search), IAA report https://hadashot.iaa.org.il/report_detail_eng.aspx?id=25046 (loaded).

**pool-of-siloam** (find)
- Issue: "shows" says "The pool John 9:7 names was real and sat where John's account places it." That treats the identification as certain while the dig is incomplete.
- Fix: "A large public pool stood at the south end of Jerusalem in Jesus' day, at the place long identified as Siloam, which fits John 9:7." The summary is already cautious and good. "2004, during pipe repair work" could read "during sewer work", which matches the Wikipedia account.
- Source loaded: https://en.wikipedia.org/wiki/Pool_of_Siloam; City of David page loads.

**herodium-ring** (find) - see flag 1 below
- Fixes: retitle it, fix a grammar slip, correct the Wikipedia label, and reword "not a unique name".

## Unverified (2)

**pool-of-bethesda** (find): "the White Fathers dug further in 1899-1900". I could not confirm this. The Wikipedia page I loaded mentions Schick (19th century), the White Fathers' role at St Anne's, and an excavation in 1964, but not 1899-1900. Safer: "Identified by Conrad Schick in 1888; later digs by the White Fathers and others continued into the 1960s." Everything else is confirmed. BSB wording: John 5:2 says "five covered colonnades", not "porches". Please use "five covered colonnades" in this find and in the `bethesda` timeline event.

**el-araj** (find): "the 2026 dig was Season 10". The season-report page I loaded lists Season 1 (2016) through Season 5 (2021). 2020 was skipped, so Season 10 in 2026 is plausible, but no loaded page says so. Safer: "Excavations since 2016". The label Contested and the shows and does-not-prove fields are fair. BAS article: 403.

## Confirmed (57)

Timeline: herod-death, quirinius-census (Contested label is right), pilate-governor, baptism, galilee-ministry, bethesda (only the BSB wording note above), ministry-length, last-supper, crucifixion, burial, empty-tomb, pentecost, paul-conversion, creed-received (now uses the Habermas 2012 p. 25 source and the "in the 30s" wording, so status Confirmed is fine), james-killed, paul-letters, 1-corinthians, james-brother (the quote matches the Whiston text at penelope ant-20 word for word), nero-persecution, mark-written, ad70, matthew-luke-written, josephus (OUP page 403, but the book exists; keep it), tacitus, p52, justin, p137 (EES page loaded: "late second to early third century AD"), frankfurt-amulet.

Finds: magdala-synagogue, nazareth-house, pilate-stone, caiaphas-ossuary, yehohanan, capernaum (Contested label is fair), galilee-boat, nazareth-inscription (Contested label is fair), frankfurt-amulet, megiddo-mosaic (Contested label is fair).

Places: all 19. The coordinates are plausible: Capernaum 32.881, 35.575; et-Tell 32.910, 35.631; el-Araj 32.894, 35.619 (on the shore south-west of et-Tell, about 2 km away, which is right); Caesarea 32.50, 34.89; Herodium 31.666, 35.242; Nida 50.154, 8.638; Golgotha labeled "traditional site". The Jordan is correctly left without a point. I did not open each OpenBible record id one by one.

Optional improvements for Confirmed items: for crucifixion, add a scholarly anchor for the AD 30 or 33 date; for pilate-governor, note that the AD 26-36 dates come from Josephus; for p52, align with the team wording "earliest NT fragment, probably 2nd century". The current text already matches the Rylands page exactly.

## Answers to Luke's 7 flags

1. **Herodium ring**: Contested, with fixes. The IEJ 68/2 abstract (loaded at docslib) says the ring is dated "first century BCE to mid-first century CE", reads "of Pilatus", and raises "the possibility that this ring might have belonged to Pontius Pilatus ... or to a person in his administration, either a Jew or a pagan."
   - Retitle "Ring inscribed with Pilate's name" to "Sealing ring inscribed 'of Pilatus'", following the team rule.
   - In the summary, change "The authors suggest it raise two possibilities" to "The authors raise two possibilities".
   - Lead with the team view: "most likely the seal of someone in Pilate's administration."
   - The Wikipedia source label says "cites Amit et al." Change it to "Pontius Pilate overview (Herodium ring section)" so it doesn't repeat the old citation error.
   - In does_not_prove, change "Pilatus was not a unique name" to "the inscription gives no title". I couldn't confirm that the authors call the name common. My understanding is that they treat it as rare, which cuts the other way.
   - Era: use "first century BC to mid-first century AD" to match the abstract.
2. **Gospel events sourced to the BSB alone**: Fine for "what the Gospels report", as long as the entry doesn't claim outside confirmation. Entries that make claims beyond the text need an anchor. Those are birth (Herod's 4 BC date), nazareth-childhood (archaeology), appearances ("historians agree") and crucifixion (date). Fixes are listed above. Herod 4 BC with a 1 BC minority view is already handled well in herod-death. Pilate AD 26-36 is fine.
3. **1 Cor 15 creed**: Done by Luke during my check. It now uses Habermas 2012 p. 25 and "in the 30s", tied to Gal 1:18-19. Confirmed.
4. **Pool of Siloam**: The summary is properly cautious (partly uncovered, no final report, Silwan and City of David stated neutrally). Fix the "shows" line and the timeline `siloam` wording as above. The 2004 date and the December 2022 dig are confirmed via Wikipedia, which cites NBC 2004 and Times of Israel 2022.
5. **Caiaphas ossuary**: Confirmed. The Israel Museum page timed out for me too, so drop it or keep the note. Loaded instead: the Wikipedia page (12 ossuaries found in a burial cave in the Peace Forest, North Talpiot, south Jerusalem, in late 1990, two of them bearing the name Caiaphas) and Greenhut, BAR Sept/Oct 1992, on the BAS Library. Greenhut himself writes that whether this is the high priest's ossuary "is another question", so "Most scholars accept the link ... but the inscription itself does not say high priest" is fair. Optional: "found in November 1990 in south Jerusalem's Peace Forest".
6. **Pilate stone**: Confirmed. I loaded the Alföldy 1999 PDF (scriptaclassica.org, linked from the DOI). He discusses the 1961 find in the Caesarea theatre and restores line 3 as "[praef]ectus Iudae[a]e". He argues the Tiberieum was a tower in the harbor, by analogy with the Drusion tower, which he calls a lighthouse ("Leuchtturm"). Wikipedia confirms June 1961, the Frova campaign and the theatre. Suggested addition to the summary: "The title is partly restored as praefectus Iudaeae. The stone came from a building honoring Tiberius (the Tiberieum), which Alföldy argued was a harbor lighthouse tower; it was later reused in the theatre."
7. **Map points**: All plausible (see Places). Placing the Frankfurt amulet at the Nida (Heddernheim) Pleiades point is fine. The Goethe release (loaded) says the grave was in the Heilmannstrasse cemetery in Frankfurt-Praunheim, at the Roman city of NIDA. The coord_note already says this. The release also confirms the 2018 find, the 230-270 date and the echo of Phil 2:10-11.

## Contested labels review

Fair as labeled: el-Araj, Capernaum's house of Peter, the Nazareth inscription, the Megiddo mosaic, the census, the Gospel dates and P52. Creed-received is now Confirmed, which is fine with the cautious "in the 30s" wording.
