# Credits: Prophecy explorer and word pop-ups

All explanations, "why Christians read it this way" notes and "traditional Jewish reading" summaries are Team Gideon's own words. Nothing is copied from the 0xSero dossier (no license) or from any copyrighted book or website.

## Scripture text
- **Berean Standard Bible (BSB)**: "Scripture from the Berean Standard Bible (BSB), public domain." Source: https://bereanbible.com/bsb.txt (team copy: `site/data/bible/bsb.json`). Dedicated to the public domain as of April 30, 2023 (https://berean.bible/terms.htm). No changes made.

## Hebrew data (words.json)
- **Open Scriptures Hebrew Bible (OSHB / morphhb)**: "Hebrew text and morphology from the Open Scriptures Hebrew Bible (https://github.com/openscriptures/morphhb). WLC text public domain; lemma and morphology tagging licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)."
  - Changes: we extracted single words, removed the segmentation slashes for the `surface` field, and expanded the morphology codes into English.
- **STEPBible TBESH**: "Hebrew lexicon data from STEPBible.org, Tyndale House Cambridge: TBESH (Translators Brief lexicon of Extended Strongs for Hebrew), licensed CC BY 4.0 (https://github.com/STEPBible/STEPBible-Data)."
  - Changes: we removed HTML from the definitions and shortened them to about 220 characters.

## Greek data (words.json)
- **SBLGNT**: "Greek text from the SBL Greek New Testament (SBLGNT), copyright 2010 Society of Biblical Literature and Logos Bible Software, licensed CC BY 4.0 (https://sblgnt.com/license/)."
- **MorphGNT**: "Morphological parsing and lemmatization by MorphGNT (https://github.com/morphgnt/sblgnt), licensed CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/)."
  - Changes: we extracted single words and expanded the parsing codes into English. Share-alike applies: the Greek `occurrence` fields in words.json, which are adapted from MorphGNT, are shared under CC BY-SA 3.0.
- **STEPBible TBESG**: "Greek lexicon data from STEPBible.org, Tyndale House Cambridge: TBESG, licensed CC BY 4.0." Changes: we removed HTML and shortened the definitions.

## Cross-references (crossrefs.json)
- **OpenBible.info**: "Cross-reference data from OpenBible.info (https://www.openbible.info/labs/cross-references/), licensed CC BY." Data file: https://a.openbible.info/data/cross-references.zip (downloaded 2026-10-26).
  - Changes: we filtered the data to our passages, removed references inside each passage, and kept the top 10 by votes. We store the references only, not OpenBible's ESV verse text.

## Linked only (not copied)
Brown, *Answering Jewish Objections to Jesus*, Vols. 2 and 3; Kaiser, *The Messiah in the Old Testament*; the NET Bible notes; isaiah53.com; Sefaria (Rashi, Ibn Ezra, Talmud and Maimonides translations); Jewish Virtual Library; Outreach Judaism; IAA Dead Sea Scrolls library; Qumran Digital.
