---
permalink: side-projects/personal-projects/bac-score/cleanup-report-2026-11-25-1
---

# Bac Score — names + governorates cleanup (2026-11-25)

Agent: OpenCode · Build folder only: `D:\side_projects\personal_projects\bac_score`.
No GPU, Ollama, OCR model, network, login or GitHub push. The public repo `_github\bac-score-tunisie` was not touched.

## 1. Source data used

| File | Role |
|---|---|
| `data.json` | Current site data: **711 codes / 3,249 rows**, already hand-corrected. Authoritative for display names and final governorates. |
| `programmes.json` | Raw `clean.py` output: **701 codes / 3,233 rows**, **71 blank governorates**, raw OCR names. Kept as the audit original. |
| `verified_cells.json` | 106 hand-verified formula cell images. Unchanged. |
| `pipeline/clean.py` | Arabic dot-insensitive lexicon + `governorate()` town→governorate resolver. Imported by the new build step. |
| `pipeline/ocr_v2.py`, `ocr_fast.py`, `vote.py`, `crops.py` | OCR / vote stages that produced `programmes.json`. Not rerun: page images and `rows.json` are not in the build folder, and no GPU/Ollama was allowed. |
| `pipeline/template.html` | Site template: official 24-governorate list and `const DATA = /*DATA*/[];` marker. |
| `sources/names2024.json` | 644 institution names extracted from the 2024 guide; used to verify 61 of the 71 blanks. |
| `sources/licences2024.json`, `sources/licence_dict.json` | 317 / 143 licence fragments and frequency vocabulary; support only, not authoritative. |
| `_vault/8_personal/bac_orientation_friend/guide2026.pdf`, `guide2026_p126-137.pdf` | Official source PDFs, read-only, outside the build folder. Not modified. `guide2024.pdf` is not present locally; only its extracted JSON is available. |

New pipeline step: **`pipeline/normalise.py`** — rebuilds `data.json`, `programmes.json` and `index.html` from the saved sources plus the mapping rules. Outputs were never hand-edited.

## 2. What "71 governorates" meant

It was **not 71 governorates or 71 spelling variants**. It was **71 programme rows in raw `programmes.json` whose `governorate` field was blank** because the OCR institution name had lost its town (`بمنوبة`, `ب صفاقس`, `بقابس`, etc.). The non-blank values were already exactly the 24 official French labels from the template (`Béja`, `Gabès`, `Médenine`, `Kébili` accented correctly).

Of the 71 blanks:

- **61** are independently verifiable from a 2024-guide institution name via `clean.governorate()`.
- **10** were only resolvable from the existing hand-corrected site data: `10166, 12518, 13524, 41597, 51318, 54604, 56570, 56597, 60740, 60741` → `Manouba, Manouba, Manouba, Sfax, Gabès, Médenine, Kébili, Kébili, Gafsa, Gafsa`.
- **0** remain unresolved.

Final output: **all 703 domestic programme codes have one of the 24 official governorates**. The only 8 blank values are foreign programmes from guide p.29/31 (France ×6, Germany ×2); they are intentionally outside the Tunisian governorate system so the +7% bonus cannot apply. Original blank/foreign values are preserved in `gov_original` / `governorate_original` and in `governorate_mapping_2026-11-25.csv`.

## 3. Names

`name_mapping_2026-11-25.csv` has one row per code (711) with:
`code · source · old_institution · canonical_institution · old_filiere · canonical_filiere · ocr_institution · ocr_filiere · institution_changed · filiere_changed · code_note`.

Applied rules (in `pipeline/normalise.py`):
- Standard Arabic spelling: `إنقليزية → إنجليزية` (English), `الإقتصاد/إلقتصاد → الاقتصاد`, `الأتصال → الاتصال`, `العالى → العالي`.
- Join Arabic conjunctions: `و الملتيميديا → والملتيميديا`, `الفنون و الحرف → الفنون والحرف`.
- Fix doubled alef and missing spaces: `اال → ال`, `واال → وال`, `المعهدالعالي → المعهد العالي`.
- Drop Arabic diacritics/tatweel so `تدرّس` and `تدرس` do not split a name; keep French accents (`Génie`), acronym case (`IPEST`, `Bachelor-Master`) and em-dash spacing.
- Exact overrides for OCR damage: `إلطاارت الطفولة بقرطاج درمش → للطفولة بقرطاج`, `الدارة الأعمال → لإدارة الأعمال`, `قصر هلال → بقصر هلال`, `بقتفسة/شقصسة → بقفصة`, `حلم الاجتماع → علم الاجتماع`, `غي → في`.
- Reversed OCR brackets `)جامعة تونس(` → `(جامعة تونس)`.

Mapping stats:
- **31 site rows** changed institution name; **21 site rows** changed filière name.
- Raw OCR names: **382 institution variants → 193 canonical targets**, **101 raw licence strings → 156 clean filière names**. Seven raw institution strings and 65 raw licence strings map to more than one canonical target because OCR collapsed distinct programmes; the hand-corrected site data resolves them per code.
- Distinct institutions: **208 → 201** (7 merges, all listed in the mapping CSV). Distinct filières: **165 → 165** (spelling fixed, no programme lost).
- One canonical `(institution, licence)` pair per code: verified.

## 4. Before / after counts

| Dataset | Before | After | Reason |
|---|---:|---:|---|
| Site codes | 711 | 711 | No code added or removed. |
| Site rows | 3,249 | 3,249 | Multiset of `(bac, formula, cutoff)` identical. |
| Site institutions | 208 | 201 | 7 OCR/spacing variants merged into canonical names. |
| Site filières | 165 | 165 | Spelling normalised; no merge/loss. |
| Site governorate nulls | 8 | 8 | Same 8 foreign rows. |
| Raw `programmes.json` codes | 701 | 711 | +10 special codes already present in the site (IPEST + foreign); raw code `41120` corrected to `11120` with the same 6 rows. |
| Raw rows | 3,233 | 3,249 | +16 rows from those 10 site-only codes; all 3,233 original rows preserved. |
| Raw blank governorates | 71 | 8 | 71 domestic blanks filled; 8 remaining are the foreign rows. |

Nothing disappeared: raw code `41120` → site code `11120` was checked row-for-row (6/6 identical); all original row tuples are present in both rebuilt files.

## 5. Tests / evidence

- `python pipeline/normalise.py` run twice from the same input: identical SHA-256 for `data.json`, `programmes.json`, `index.html`, and both mapping CSVs (idempotent).
- Validator run: all rows preserved as multisets; site code set unchanged; official governorate set enforced; all 71 blanks resolved; embedded `index.html` DATA equals `data.json`; one canonical name pair per code → **ALL CHECKS PASSED**.
- No file in `2026_VFX_disciplines\*`, `autonomous_company\production_hub`, `_github`, `_gpu` or `to_delete` was touched.

## 6. Open doubts for Alaa

1. **12 codes where the 2024 guide town and the current site governorate disagree** — site value kept, please confirm against `guide2026.pdf`: `22103 Tunis→Nabeul`; `36311/36312/36318/36523/36524/37311 Monastir→Mahdia`; `82797 Jendouba→Le Kef`; `84509/84841 Jendouba→Béja`; `86202/86207 Jendouba→Siliana`.
2. **32 raw non-blank governorate values were overridden** by the site data: `Gabès→Sfax ×7`, `Monastir→Mahdia ×5`, `Tunis→Ben Arous ×4`, `Kairouan→Kasserine ×4`, plus 9 smaller pairs (full original→canonical in `governorate_mapping_2026-11-25.csv`).
3. **Foreign rows**: confirm the 8 France/Germany programmes should stay without a Tunisian governorate and without the +7% bonus.
4. **Institution wording inferred from OCR damage**: `10470` is now `المعهد العالي للطفولة بقرطاج (جامعة قرطاج)`; the exact official wording ("لعلوم الطفولة"?) needs a PDF check.
5. **Diacritics removed** from `تدرّس` in two English-taught filières; confirm plain `تدرس` is acceptable for the site.
6. The 2024 guide PDF itself is not in the build folder; only `names2024.json` was available for cross-checks. A full fresh OCR rerun would need the page images / `rows.json` and a separate decision.

## 7. Files changed / created

- Updated: `data.json`, `programmes.json`, `index.html`.
- New: `pipeline/normalise.py`, `name_mapping_2026-11-25.csv`, `governorate_mapping_2026-11-25.csv`, this report.
- Unchanged: `verified_cells.json`, all `pipeline/ocr*.py`, `vote.py`, `crops.py`, `template.html`, `sources/*.json`, `reel/`.
- Next: Alaa confirms the open doubts; no push — Codex handles GitHub pushes.