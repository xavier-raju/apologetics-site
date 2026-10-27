# Certainty: A Toolkit for Christians and Apologists
*The case for Jesus, honestly examined.* A free, static apologetics site (HTML/CSS/vanilla JS, no server code).

- Build: `python3 build.py` → `_site/` (fails on broken internal links or unknown hosted-text paths)
- Preview: `python3 -m http.server -d _site`
- QA: `python3 qa.py <url>` and `bash ../john/qa/run.sh <url>`
- Publish `_site/` to GitHub Pages at `<user>.github.io/apologetics-site/`.
- Design system, routes and content schemas: see `STYLE-GUIDE.md`.

Credits: research pointers from 0xSero's report (https://github.com/0xSero/all-historical-evidence-of-jesus-christ, linked, not copied). Scripture: Berean Standard Bible, public domain. Data licenses listed in the site footer.
