---
permalink: side-projects/personal-projects/bac-score/official-source-check-2026-11-25-1
---

# Bac Score — official-source check (2026-11-25)

Agent: OpenCode · Build folder only: `D:\side_projects\personal_projects\bac_score`.
Public sources and the local official PDF were read only. No GPU, Ollama, login, GitHub push or change to bonus logic. The public repo `_github\bac-score-tunisie` was not touched.

## 1. The 12 disputed codes

"Guide town" below is the town inferred by the local lexicon from the **2024-guide institution name**: for university-run institutes it resolved the **university headquarters**, not the institute's own town. The site value came from the hand-corrected 2026 data. **All 12 site values are confirmed by the establishments' own official pages; no value changes.**

| Code | Institution | Guide town (lexicon/HQ) | Site governorate | Official source | Verdict |
|---|---|---|---|---|---|
| 22103 | المعهد العالي للغات بنابل (جامعة قرطاج) | Tunis | **Nabeul** | [Université de Carthage — ISL Nabeul](https://pmo.ucar.rnu.tn/web/content/3192?download=true&unique=017eacc282d8208a555a8f16a029bdcb3592724c) | keep site value — institute is in Nabeul |
| 36311 | كلية العلوم الاقتصادية والتصرف بالمهدية (جامعة المنستير) | Monastir | **Mahdia** | [FSEG Mahdia — contact](https://fsegma.rnu.tn/fr/contact) | keep — FSEG is in Mahdia |
| 36312 | كلية العلوم الاقتصادية والتصرف بالمهدية (جامعة المنستير) | Monastir | **Mahdia** | [FSEG Mahdia — presentation](https://fsegma.rnu.tn/fr/article/708/presentation) | keep — FSEG is in Mahdia |
| 36318 | كلية العلوم الاقتصادية والتصرف بالمهدية (جامعة المنستير) | Monastir | **Mahdia** | [FSEG Mahdia — contact](https://fsegma.rnu.tn/fr/contact) | keep — FSEG is in Mahdia |
| 37311 | المعهد العالي للإعلامية بالمهدية (جامعة المنستير) | Monastir | **Mahdia** | [FSEG Mahdia — presentation](https://fsegma.rnu.tn/fr/article/708/presentation) · [ISI Mahdia](https://isima.rnu.tn/fr/contact) | keep — institute is in Mahdia |
| 36523 | المعهد العالي للإعلامية بالمهدية (جامعة المنستير) | Monastir | **Mahdia** | [ISI Mahdia — contact](https://isima.rnu.tn/fr/contact) | keep — institute is in Mahdia |
| 36524 | المعهد العالي للإعلامية بالمهدية (جامعة المنستير) | Monastir | **Mahdia** | [Université de Monastir — ISI Mahdia](https://um.rnu.tn/fr/etablissements/instituts/institut-sup%C3%A9rieur-dinformatique-de-mahdia/) | keep — institute is in Mahdia |
| 82797 | المعهد العالي لعلوم التمريض بالكاف (جامعة جندوبة) | Jendouba | **Le Kef** | [ISSI Le Kef](https://issikf.rnu.tn/fr/contact) · [UJ establishment page](https://uj.rnu.tn/fr/university-establishments/14?name=institut-superieur-des-sciences-infirmieres-du-kef) | keep — institute is in Le Kef |
| 84509 | المعهد العالي للبيوتكنولوجيا بباجة (جامعة جندوبة) | Jendouba | **Béja** | [UJ establishment page](https://uj.rnu.tn/fr/university-establishments/1?name=institut-superieur-de-biotechnologie-de-beja) · [ISBB contact](https://isbb.rnu.tn/fr/contact) | keep — institute is in Béja |
| 84841 | المعهد العالي للبيوتكنولوجيا بباجة (جامعة جندوبة) | Jendouba | **Béja** | [ISBB — contact](https://isbb.rnu.tn/fr/contact) | keep — institute is in Béja |
| 86202 | المعهد العالي للفنون والحرف بسليانة (جامعة جندوبة) | Jendouba | **Siliana** | [UJ establishment page](https://uj.rnu.tn/fr/university-establishments/8?name=institut-superieur-des-arts-et-metiers-de-siliana) | keep — institute is in Siliana |
| 86207 | المعهد العالي للفنون والحرف بسليانة (جامعة جندوبة) | Jendouba | **Siliana** | [ISAM Siliana — contact](https://isamsl.rnu.tn/fr/contact-intek) | keep — institute is in Siliana |

Cross-check: the [Université de Jendouba presentation page](https://uj.rnu.tn/fr/l-universite/presentation) lists its establishments by town — Béja → ISB, Le Kef → ISSI, Siliana → ISAM — which covers 82797, 84509, 84841, 86202 and 86207 in one official source.

**Applied through `pipeline/normalise.py`, not by hand:** `GOV_SOURCE_CONFIRMATIONS` now locks these 12 codes (and 10 sampled overrides below) to the official value and records the source URL in `governorate_mapping_2026-11-25.csv` (`official_source` column). All other rules are unchanged. Rebuild output is byte-identical for the data values; only provenance metadata for these codes records `official-site-confirmed`.

## 2. All 32 non-blank overrides

Raw OCR governorate → canonical site governorate (full detail, including the official source for 10 sampled codes, is in `governorate_mapping_2026-11-25.csv`):

| Raw → site | Count | Codes |
|---|---:|---|
| Béja → Tunis | 2 | 10452, 18318 |
| Tunis → Ben Arous | 4 | 10603, 11573, 12524, 12629 |
| Manouba → Ariana | 1 | 12511 |
| Tunis → Bizerte | 2 | 20508, 20509 |
| Mahdia → Sousse | 2 | 30202, 30209 |
| Monastir → Mahdia | 5 | 36322, 36512, 36573, 36603, 36629 |
| Gabès → Sfax | 7 | 40102, 40162, 40209, 40518, 40573, 41512, 41518 |
| Nabeul → Gabès | 1 | 50615 |
| Sousse → Gafsa | 1 | 60201 |
| Kairouan → Kasserine | 4 | 73202, 73524, 73570, 73573 |
| Kairouan → Sidi Bouzid | 1 | 75209 |
| Jendouba → Béja | 1 | 80512 |
| Jendouba → Le Kef | 1 | 82844 |
| **Total** | **32** | |

### Sample of 10 checked against official sources

| Code | Raw → site | Official source (what it says) | Result |
|---|---|---|---|
| 10603 | Tunis → **Ben Arous** | [ISTIC contact](http://www.istic.rnu.tn/en/contact-en.html): "Ben Arous, Tunisie" | site correct |
| 12511 | Manouba → **Ariana** | [ISBST](https://isbst.rnu.tn/eng/home): "Sidi Thabet, Ariana-Tunis" | site correct |
| 20508 | Tunis → **Bizerte** | [FSB descriptive card](http://www.fsb.rnu.tn/fiche-descriptive): "7021 Zarzouna Bizerte" | site correct |
| 30202 | Mahdia → **Sousse** | [ISBAS Sousse](https://isbas.rnu.tn/pages/presentation): "centre-ville de Sousse" | site correct |
| 36322 | Monastir → **Mahdia** | [ISSAT Mahdia](https://issatmh.rnu.tn/): "Route Rejiche 5121 Mahdia" | site correct |
| 40102 | Gabès → **Sfax** | [FLSHS contact](https://flshs.rnu.tn/fra/contact): "Route de l'aéroport … Sfax" | site correct |
| 50615 | Nabeul → **Gabès** | [ISSAT Gabès](http://www.issatgb.rnu.tn/): "Rue Omar ibn el Khattab 6029 – Gabès" | site correct |
| 60201 | Sousse → **Gafsa** | [UGAF — ISAM Gafsa](https://ugaf.rnu.tn/fra/pages/961/Institut-Sup%C3%A9rieur-des-Arts-et-M%C3%A9tiers-de-Gafsa): "Route de Tozeur – 2112 Gafsa" | site correct |
| 73202 | Kairouan → **Kasserine** | [ISSAT Kasserine](https://issatkas.rnu.tn/fra/pages/157/Presentation): "Campus Universitaire de Kasserine BP 471" | site correct |
| 82844 | Jendouba → **Le Kef** | [MESRS establishment directory](https://fsegs.rnu.tn/useruploads/files/annuaire-mes.pdf): "Ecole Supérieure d'Agriculture du Kef … 7119 Le Kef" | site correct |

**Error rate:** raw OCR value was wrong in **10/10** sampled overrides (100% of this sample); the current site value was wrong in **0/10** (0% observed error rate). This is a judgment sample chosen from codes with a clear official address page, not a random sample — so it supports "no errors found" rather than a statistical bound for all 32. No change was needed.

## 3. Foreign rows and the +7 % rule

**Official rule text** — local official guide `guide2026.pdf` (vault `_vault\8_personal\bac_orientation_friend\`), PDF page 20 / printed page 18, §3.3 التنفيل الجغرافي. The PDF text layer reads (with its OCR typos) `نسبة 7 % تضاف هو لمجموع نقاط إذا رغبت في االلتحاق ببعض االختصاحات الموجودة في واليت`; with those obvious typos corrected:

> نسبة 7 % تضاف لمجموع نقاط إذا رغبت في الالتحاق ببعض الاختصاصات الموجودة في ولايتك

(≤15 words: a 7 % share is added to the point total if you wish to join certain specialities located in your governorate.)

**Worked example** — same guide, PDF page 21 / printed page 19: `T = 115,115` for the same file in another governorate, and `T = 1,07 x 115,115 = 123,1731` for the home governorate. This confirms the bonus multiplies **T**, not FG. No direct official 2026 PDF URL was found online; the local official PDF is the source used. No explanatory blog was relied on.

**Decision for Alaa:** the 8 foreign programmes (codes `99201, 99202, 99214, 99215, 99217, 99218, 99310, 99311`) keep `gov: null` and therefore stay outside the 24 Tunisian governorates. In `pipeline/template.html` the bonus condition is `gov && p.gov === gov && !p.prep`; with `p.gov === null` these rows can never receive the +7 %, and the dropdown has no selectable null value. **No bonus logic was changed.** Please confirm this is the intended behaviour; if you want these rows treated as Tunisian, that is a separate, explicit decision with a governorate value per row.

## 4. Files and tests

- Changed by the pipeline: `data.json`, `programmes.json`, `index.html`, both mapping CSVs (the `official_source` column is new).
- New: `pipeline/validate_publish.py`, this report, `PUBLISH_FOR_CODEX.md`.
- Unchanged: `pipeline/template.html`, all OCR stages, `sources/*.json`, `verified_cells.json`, `README.md` until the task close.
- `python pipeline/normalise.py` run twice: identical SHA-256 for all five outputs (idempotent).
- `python pipeline/validate_publish.py` → `PUBLISH CHECKS PASSED` (711 codes / 3,249 rows / 8 foreign nulls / 22 confirmations / embedded DATA = data.json).
- Before/after validator → `ALL CHECKS PASSED` (row multisets preserved, official 24 governorates only, no unresolved blanks, one canonical name pair per code).
- `data.json` SHA-256: `73321763299772a3b169fc3bd5469acb001f01f81cc5d1e70a473bd9287bb16a`.
- Next: Alaa confirms the 12 verdicts, the 8 foreign-row decision and the bonus quote; Codex publishes per `PUBLISH_FOR_CODEX.md`.