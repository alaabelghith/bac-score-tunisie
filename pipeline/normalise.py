"""Rebuild the bac-score site data with canonical names and governorates.

Inputs (read only):
  data.json            current site data (hand-corrected, 711 codes)
  programmes.json      raw clean.py output (701 codes, 71 blank governorates)
  sources/names2024.json   Arabic institution names from the 2024 guide
  sources/licences2024.json / licence_dict.json  supporting licence vocabulary
  pipeline/template.html   site template with the /*DATA*/ marker
  verified_cells.json      unchanged; kept for the OCR audit trail

Outputs:
  data.json, programmes.json, index.html
  name_mapping_2026-11-25.csv
  governorate_mapping_2026-11-25.csv

Run from anywhere: python pipeline/normalise.py
No model, GPU, network or OCR is used.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "pipeline"

GOVS = [
    "Tunis", "Ariana", "Ben Arous", "Manouba", "Nabeul", "Zaghouan",
    "Bizerte", "Béja", "Jendouba", "Le Kef", "Siliana", "Sousse",
    "Monastir", "Mahdia", "Sfax", "Kairouan", "Kasserine", "Sidi Bouzid",
    "Gabès", "Médenine", "Tataouine", "Gafsa", "Tozeur", "Kébili",
]
GOV_VARIANTS = {}
for g in GOVS:
    key = "".join(c for c in unicodedata.normalize("NFKD", g.lower())
                  if not unicodedata.combining(c)).replace(" ", "")
    GOV_VARIANTS[key] = g
GOV_VARIANTS.update({
    "medenine": "Médenine", "kebili": "Kébili", "gabes": "Gabès",
    "beja": "Béja", "lekef": "Le Kef", "benarous": "Ben Arous",
    "sidi bouzid": "Sidi Bouzid", "sidi_bouzid": "Sidi Bouzid",
})

# One raw OCR code was corrected by hand in the site data. The six rows are
# identical; keep the site code so nothing is lost or doubled.
CODE_CORRECTIONS = {"41120": "11120"}

# Per-code UI flags present in the reviewed published data.json but dropped by
# the first cleanup pass. A field-by-field comparison on 2026-11-25 found
# `special` as the only published field missing from the rebuilt data (row
# shapes and every other field match). Keep the authoritative list here so a
# rebuild cannot silently lose the flag again; a truthy value still present on
# the site input is preserved as-is. Only truthy values are emitted, matching
# the published shape: 10 codes carry "special": true, the other 701 have no
# such key.
PUBLISHED_FLAG_FIELDS = ("special",)
SPECIAL_CODES = frozenset({
    "99101", "99102", "99201", "99202", "99214", "99215",
    "99217", "99218", "99310", "99311",
})

# Ordered, conservative text rules. Arabic diacritics/tatweel are dropped so
# the same name does not appear in decorated and undecorated forms.
TEXT_FIXES = [
    (r"ـ", "", "drop tatweel"),
    (r"[\u064B-\u065F\u0670]", "", "drop Arabic diacritics"),
    (r"[”“\"_]", "", "drop OCR quote marks"),
    (r"\)\s*([^()]{1,120}?)\s*\(", r"(\1)", "unflip reversed OCR brackets"),
    (r"\s+و\s+", " و", "attach Arabic conjunction to the next word"),
    (r"واال", "وال", "fix doubled alef after و"),
    (r"اال", "ال", "fix doubled alef"),
    (r"إنقليزية", "إنجليزية", "standard Arabic spelling: English"),
    (r"الإقتصاد", "الاقتصاد", "standard Arabic spelling: economics"),
    (r"إلقتصاد", "لاقتصاد", "standard Arabic spelling after ل"),
    (r"الأتصال", "الاتصال", "standard Arabic spelling: communication"),
    (r"الأتصالات", "الاتصالات", "standard Arabic spelling: communications"),
    (r"العالى", "العالي", "standard Arabic spelling: higher"),
    (r"المعهدالعالي", "المعهد العالي", "missing space"),
    (r"المعهد ائعاني", "المعهد العالي", "OCR damage"),
    (r"بقتفسة", "بقفصة", "OCR damage: Gafsa"),
    (r"شقصسة", "قفصة", "OCR damage: Gafsa"),
    (r"(?<= )غي(?= )", "في", "OCR damage: in"),
    (r"حلم الاجتماع", "علم الاجتماع", "OCR damage: sociology"),
    (r"الإعالمية", "الإعلامية", "OCR damage: informatics"),
    (r"Genie", "Génie", "French accent"),
    (r"GENIE", "Génie", "French accent"),
    (r"Bachelor Master", "Bachelor-Master", "French hyphenation"),
    (r"IPest", "IPEST", "French acronym"),
    (r"\s*—\s*", " — ", "normalise em dash spacing"),
    (r"\s+", " ", "collapse whitespace"),
]

# Exact fixes where a generic rule would be unsafe. Keys are the text after
# TEXT_FIXES; values are the canonical display name.
NAME_OVERRIDES = {
    "institution": {
        "المعهد العالي إلطاارت الطفولة بقرطاج درمش (جامعة قرطاج)":
            "المعهد العالي للطفولة بقرطاج (جامعة قرطاج)",
        "المعهد العالي الدارة الأعمال بصفاقس (جامعة صفاقس)":
            "المعهد العالي لإدارة الأعمال بصفاقس (جامعة صفاقس)",
        "المعهد العالي للدراسات التكنولوجية قصر هلال (الإدارة العامة للدراسات التكنولوجية)":
            "المعهد العالي للدراسات التكنولوجية بقصر هلال (الإدارة العامة للدراسات التكنولوجية)",
        "المعهد العالي للإعلامية وتكنولوجيات الاتصال بسوسة (جامعة سوسة)":
            "المعهد العالي للإعلامية وتكنولوجيات الاتصال بسوسة (جامعة سوسة)",
    },
    "licence": {
        "الإجازة في تحليلات الأعمال والاقتصاد (تدرس بالإنجليزية)":
            "الإجازة في تحليلات الأعمال والاقتصاد (تدرس بالإنجليزية)",
        "الإجازة في علوم الإعلامية: البيانات الضخمة وتحليل البيانات (تدرس بالإنجليزية)":
            "الإجازة في علوم الإعلامية: البيانات الضخمة وتحليل البيانات (تدرس بالإنجليزية)",
    },
}

FOREIGN_MARKERS = ("فرنسا", "ألمانيا", "Sorbonne", "Hanovre", "Heidelberg")
PREP_MARKERS = ("مرحلة تحضيرية", "المعهد التحضيري", "التحضيرية")

# Official-source confirmations gathered 2026-11-25 from the establishments'
# own .rnu.tn / MESRS pages (full table in official_source_check_2026-11-25.md).
# Two groups:
#   * the 12 codes where the 2024-guide lexicon resolved the *university HQ*
#     town (Tunis / Monastir / Jendouba) instead of the *institute* town;
#   * 10 sampled non-blank OCR overrides, checked against official pages.
# These rules lock the already-correct site value: they are confirmations, not
# new values. The URL is written to governorate_mapping_2026-11-25.csv so a
# future rebuild can re-check each decision without redoing the research.
GOV_SOURCE_CONFIRMATIONS = {
    # 12 disputed codes: lexicon town -> official institute town
    "22103": ("Nabeul", "https://pmo.ucar.rnu.tn/web/content/3192?download=true&unique=017eacc282d8208a555a8f16a029bdcb3592724c"),
    "36311": ("Mahdia", "https://fsegma.rnu.tn/fr/contact"),
    "36312": ("Mahdia", "https://fsegma.rnu.tn/fr/article/708/presentation"),
    "36318": ("Mahdia", "https://fsegma.rnu.tn/fr/contact"),
    "36523": ("Mahdia", "https://isima.rnu.tn/fr/contact"),
    "36524": ("Mahdia", "https://um.rnu.tn/fr/etablissements/instituts/institut-sup%C3%A9rieur-dinformatique-de-mahdia/"),
    "37311": ("Mahdia", "https://fsegma.rnu.tn/fr/article/708/presentation"),
    "82797": ("Le Kef", "https://uj.rnu.tn/fr/university-establishments/14?name=institut-superieur-des-sciences-infirmieres-du-kef"),
    "84509": ("Béja", "https://uj.rnu.tn/fr/university-establishments/1?name=institut-superieur-de-biotechnologie-de-beja"),
    "84841": ("Béja", "https://isbb.rnu.tn/fr/contact"),
    "86202": ("Siliana", "https://uj.rnu.tn/fr/university-establishments/8?name=institut-superieur-des-arts-et-metiers-de-siliana"),
    "86207": ("Siliana", "https://isamsl.rnu.tn/fr/contact-intek"),
    # 10-code sample of the 32 non-blank overrides
    "10603": ("Ben Arous", "http://www.istic.rnu.tn/en/contact-en.html"),
    "12511": ("Ariana", "https://isbst.rnu.tn/eng/home"),
    "20508": ("Bizerte", "http://www.fsb.rnu.tn/fiche-descriptive"),
    "30202": ("Sousse", "https://isbas.rnu.tn/pages/presentation"),
    "36322": ("Mahdia", "https://issatmh.rnu.tn/"),
    "40102": ("Sfax", "https://flshs.rnu.tn/fra/contact"),
    "50615": ("Gabès", "http://www.issatgb.rnu.tn/"),
    "60201": ("Gafsa", "https://ugaf.rnu.tn/fra/pages/961/Institut-Sup%C3%A9rieur-des-Arts-et-M%C3%A9tiers-de-Gafsa"),
    "73202": ("Kasserine", "https://issatkas.rnu.tn/fra/pages/157/Presentation"),
    "82844": ("Le Kef", "https://fsegs.rnu.tn/useruploads/files/annuaire-mes.pdf"),
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canon_gov(value):
    if not value:
        return None
    if value in GOVS:
        return value
    key = "".join(c for c in unicodedata.normalize("NFKD", str(value).lower())
                  if not unicodedata.combining(c)).replace(" ", "")
    return GOV_VARIANTS.get(key, GOV_VARIANTS.get(str(value).lower()))


def canon_name(value, field: str):
    s = str(value or "").strip()
    for pattern, replacement, _ in TEXT_FIXES:
        s = re.sub(pattern, replacement, s)
    s = NAME_OVERRIDES.get(field, {}).get(s, s)
    s = re.sub(r"\s+([,.:;])", r"\1", s)
    return s.strip()


def is_prep(licence: str) -> bool:
    return any(m in licence for m in PREP_MARKERS)


def convert_rows(rows, source: str):
    """Normalise to the site's list rows; the raw dict shape is kept separately."""
    out = []
    for r in rows:
        if isinstance(r, dict):
            row = [r.get("bac"), r.get("formula"),
                   r.get("cutoff2025")]
        else:
            row = list(r)
        out.append(row)
    return out


def dict_rows(rows):
    out = []
    for r in rows:
        if isinstance(r, dict):
            out.append({"bac": r.get("bac"), "formula": r.get("formula"),
                        "cutoff2025": r.get("cutoff2025")})
        else:
            r = list(r)
            out.append({"bac": r[0], "formula": r[1],
                        "cutoff2025": r[2] if len(r) > 2 else None})
    return out


def main() -> int:
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(PIPELINE))
    from clean import governorate as gov_from_name  # local lexicon, no OCR

    site = {x["code"]: dict(x) for x in load(ROOT / "data.json")}
    raw = {}
    for x in load(ROOT / "programmes.json"):
        code = CODE_CORRECTIONS.get(x["code"], x["code"])
        item = dict(x)
        item["raw_origin"] = item.get("raw_origin", "guide2026")
        for key, source_key in (("ocr_institution_original", "institution"),
                                ("ocr_licence_original", "licence"),
                                ("ocr_governorate_original", "governorate")):
            item[key] = item.get(key, item.get(source_key, ""))
        raw[code] = item
    names24 = load(ROOT / "sources" / "names2024.json")
    licences24 = load(ROOT / "sources" / "licences2024.json")
    licence_dict = load(ROOT / "sources" / "licence_dict.json")

    site_order = list(site)
    codes = sorted(set(site) | set(raw))
    raw_blank_codes = {
        code for code, x in raw.items()
        if x.get("raw_origin") == "guide2026"
        and (x.get("ocr_governorate_original", x.get("governorate", "")) or "") == ""
        and not any(m in str(x.get("ocr_institution_original", x.get("institution", "")))
                    for m in FOREIGN_MARKERS)
    }
    new_site, new_progs = [], []
    name_rows, gov_rows = [], []
    stats = {
        "codes": len(codes),
        "site_codes_before": len(site),
        "raw_codes_before": sum(1 for x in raw.values()
                                if x.get("raw_origin") == "guide2026"),
        "raw_blank_gov": len(raw_blank_codes),
        "raw_blank_resolved_2024": 0,
        "raw_blank_resolved_site": 0,
        "raw_blank_unresolved": 0,
        "foreign_without_gov": 0,
        "names_changed": 0,
        "gov_changed_from_raw": 0,
        "rows_site": 0,
        "rows_raw": 0,
        "published_flags_restored": 0,
    }

    for code in codes:
        s = site.get(code)
        r = raw.get(code)
        base = s or r
        src = "site2026" if s else "guide2026"

        old_inst = (s or {}).get("inst_original",
                    (s or {}).get("inst", (r or {}).get("institution_original",
                    (r or {}).get("institution", ""))))
        old_lic = (s or {}).get("licence_original",
                   (s or {}).get("licence", (r or {}).get("licence_original",
                   (r or {}).get("licence", ""))))
        if r:
            old_gov = r.get("ocr_governorate_original",
                            r.get("governorate", "")) or ""
        else:
            old_gov = s.get("gov_original", s.get("gov", "")) or ""

        new_inst = canon_name(old_inst, "institution")
        new_lic = canon_name(old_lic, "licence")

        # Governorate: the hand-corrected site value wins; raw OCR is next;
        # the 2024 guide institution name is the audit fallback.
        gov = canon_gov((s or {}).get("gov")) or canon_gov((r or {}).get("governorate"))
        gov_source = "site2026" if (s or {}).get("gov") else ("guide2026" if gov else "")
        if not gov:
            n24 = names24.get(code, {}).get("inst", "")
            hit = gov_from_name(n24) if n24 else None
            if hit:
                gov, gov_source = hit[0], "guide2024"
        if not gov and old_gov:
            gov, gov_source = canon_gov(old_gov), "guide2026-original"
        if not gov and any(m in old_inst for m in FOREIGN_MARKERS):
            gov_source = "foreign-hors-Tunisie"

        # Official-source-backed verdicts win over both the local lexicon and
        # the raw OCR. All 22 entries confirm the current site value.
        confirm = GOV_SOURCE_CONFIRMATIONS.get(code)
        if confirm:
            gov, gov_source = confirm[0], "official-site-confirmed"
        gov_source_url = confirm[1] if confirm else ""

        verified24 = ""
        if code in raw_blank_codes:
            n24 = names24.get(code, {}).get("inst", "")
            hit = gov_from_name(n24) if n24 else None
            if hit:
                verified24 = hit[0]
                stats["raw_blank_resolved_2024"] += 1
            if gov and gov in GOVS:
                stats["raw_blank_resolved_site"] += 1
            if not gov:
                stats["raw_blank_unresolved"] += 1
        if gov is None:
            stats["foreign_without_gov"] += 1

        if canon_gov(old_gov) != gov:
            stats["gov_changed_from_raw"] += 1
        if old_inst != new_inst or old_lic != new_lic:
            stats["names_changed"] += 1

        rows_site = convert_rows((s or {}).get("rows", (r or {}).get("rows", [])), src)
        rows_prog = dict_rows((r or {}).get("rows", (s or {}).get("rows", [])))
        stats["rows_site"] += len(rows_site)
        stats["rows_raw"] += len(rows_prog)
        page = (s or {}).get("page", (r or {}).get("page", 0))
        prep = (s or {}).get("prep", is_prep(new_lic))
        town = (r or {}).get("town", "")

        common = {
            "inst_original": old_inst,
            "licence_original": old_lic,
            "gov_original": old_gov or "",
            "gov_source": gov_source,
            "name_source": src,
        }
        flags = {}
        for key in PUBLISHED_FLAG_FIELDS:
            val = (s or {}).get(key)
            if not val and key == "special":
                val = True if code in SPECIAL_CODES else None
            if val:
                flags[key] = val
        stats["published_flags_restored"] += len(flags)
        new_site.append({
            "code": code, "licence": new_lic, "inst": new_inst,
            "gov": gov, "page": page, "prep": bool(prep), "rows": rows_site,
            **common, **flags,
        })
        new_progs.append({
            "code": code, "institution": new_inst, "governorate": gov,
            "town": town, "licence": new_lic, "page": page,
            "rows": rows_prog,
            "institution_original": old_inst,
            "licence_original": old_lic,
            "governorate_original": old_gov or "",
            "ocr_institution_original": (r or {}).get("ocr_institution_original", ""),
            "ocr_licence_original": (r or {}).get("ocr_licence_original", ""),
            "ocr_governorate_original": (r or {}).get("ocr_governorate_original", ""),
            "gov_source": gov_source,
            "raw_origin": (r or {}).get("raw_origin", "site2026"),
        })

        code_note = ""
        if code in CODE_CORRECTIONS.values():
            old_code = next(k for k, v in CODE_CORRECTIONS.items() if v == code)
            code_note = "raw code {} corrected to {} (same 6 rows)".format(old_code, code)
        ocr_inst = ((r or {}).get("ocr_institution_original",
                    (r or {}).get("institution", "")) or "")
        ocr_lic = ((r or {}).get("ocr_licence_original",
                   (r or {}).get("licence", "")) or "")
        name_rows.append({
            "code": code, "source": src,
            "old_institution": old_inst, "canonical_institution": new_inst,
            "old_filiere": old_lic, "canonical_filiere": new_lic,
            "ocr_institution": ocr_inst, "ocr_filiere": ocr_lic,
            "institution_changed": "yes" if old_inst != new_inst else "no",
            "filiere_changed": "yes" if old_lic != new_lic else "no",
            "code_note": code_note,
        })
        gov_rows.append({
            "code": code, "source": src,
            "original_governorate": old_gov or "",
            "canonical_governorate": gov or "",
            "governorate_source": gov_source,
            "official_source": gov_source_url,
            "verifiable_from_2024_guide": verified24,
            "note": ("hors Tunisie — no 7% bonus" if gov is None else code_note),
        })

    # Keep the existing order: site order first, then codes that only existed
    # in the raw clean output.
    order = {code: i for i, code in enumerate(site_order)}
    new_site.sort(key=lambda x: (order.get(x["code"], 10**6), x["code"]))
    new_progs.sort(key=lambda x: (order.get(x["code"], 10**6), x["code"]))

    def dump_json(path, obj):
        path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")),
                        encoding="utf-8")

    def dump_csv(path, rows, fields):
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    dump_json(ROOT / "data.json", new_site)
    dump_json(ROOT / "programmes.json", new_progs)
    dump_csv(ROOT / "name_mapping_2026-11-25.csv", name_rows,
             ["code", "source", "old_institution", "canonical_institution",
              "old_filiere", "canonical_filiere", "ocr_institution",
              "ocr_filiere", "institution_changed", "filiere_changed",
              "code_note"])
    dump_csv(ROOT / "governorate_mapping_2026-11-25.csv", gov_rows,
             ["code", "source", "original_governorate", "canonical_governorate",
              "governorate_source", "official_source",
              "verifiable_from_2024_guide", "note"])

    template = (PIPELINE / "template.html").read_text(encoding="utf-8")
    marker = "const DATA = /*DATA*/[];"
    if marker not in template:
        raise SystemExit("template marker missing: " + marker)
    html = template.replace(marker, "const DATA = /*DATA*/" +
                            json.dumps(new_site, ensure_ascii=False,
                                       separators=(",", ":")) + ";")
    (ROOT / "index.html").write_text(html, encoding="utf-8")

    print("codes {} (site before {}, raw before {})".format(
        stats["codes"], stats["site_codes_before"], stats["raw_codes_before"]))
    print("rows: site {} / programmes {} (no row dropped)".format(
        stats["rows_site"], stats["rows_raw"]))
    print("distinct institutions: {} / filières: {}".format(
        len({x["inst"] for x in new_site}), len({x["licence"] for x in new_site})))
    print("raw blank governorates: {} — 2024-verifiable {}, site-corrected {}, unresolved {}".format(
        stats["raw_blank_gov"], stats["raw_blank_resolved_2024"],
        stats["raw_blank_resolved_site"], stats["raw_blank_unresolved"]))
    print("foreign rows without Tunisian governorate: {}".format(
        stats["foreign_without_gov"]))
    print("published-only UI flags restored: {}".format(
        stats["published_flags_restored"]))
    print("names changed: {} rows; governorate changed from raw: {}".format(
        stats["names_changed"], stats["gov_changed_from_raw"]))
    print("source vocabulary: names2024 {}, licences2024 {}, licence_dict {}".format(
        len(names24), len(licences24), len(licence_dict)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
