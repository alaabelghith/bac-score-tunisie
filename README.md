# حساب مجموع النقاط · Bac orientation score — Tunisia

**🌐 https://alaabelghith.github.io/bac-score-tunisie/**

Free, unofficial calculator for Tunisian baccalauréat students: enter your grades, get your **FG** (formule globale), your **T score** for every programme, and see which programmes are *safe / borderline / out of reach* against the **last admitted scores of 2025** — with the **7 % home-governorate bonus**.

أداة مجانية وغير رسمية: احسب الصيغة الإجمالية FG ومجموع النقاط T لكل شعبة، وقارن مع مجموع آخر موجه 2025 (مع التنفيل الجغرافي 7%).

- No login, no tracking — grades stay in your browser.
- Works offline (one HTML file).
- ⚠️ Data read automatically from the official guide *دليل التوجيه الجامعي 2026* — always check the official guide and orientation.tn before filling your choices.

## Data
`data.json` — 701 programme codes, 3,233 rows (bac section · T formula · last admitted 2025), extracted from the image-only tables of the 2026 guide.
- Formulas and bac sections: every distinct cell checked by hand.
- Cut-offs: OCR read twice, disagreements checked by hand.
- Rules (guide p.16, p.19): FG per section; T = programme formula (M = maths grade, MG = bac average); bonus T × 1.07 only for programmes in the home governorate (not prépas); session de contrôle grade = (2 × main + control) / 3.
- Checked against the guide's worked examples (FG 94.405 · FG 104.055 · T 123.17 with bonus).

Known limits: some institution names still have OCR errors; 71 programmes have no governorate detected (bonus not applied); special programmes (IPEST, France, Germany) not included.

## Update each year
`pipeline/`: `pdfimages -png guide.pdf img/x -p` → `ocr_v2.py` (grid detection + Tesseract ara/eng) → `vote.py` (2nd pass on cut-offs) → `clean.py` (names, governorates) → build `index.html` from `template.html` + `data.json`.

## License
Code: MIT. Data: from the public official orientation guide of the Tunisian Ministry of Higher Education — unofficial reproduction for information only.

Made by [Alaa Belghith](https://alaabelghith.github.io).
