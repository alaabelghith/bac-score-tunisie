"""Publish-time checks for the bac-score site, with no before/after snapshot.

Run from anywhere: python pipeline/validate_publish.py [root]
Default root is the parent of this script's folder. Checks the site data, the
embedded DATA in index.html and every official-source-confirmed governorate.
Prints the SHA-256 of data.json and index.html for the handoff.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import sys
from pathlib import Path

GOVS = {
    "Tunis", "Ariana", "Ben Arous", "Manouba", "Nabeul", "Zaghouan",
    "Bizerte", "Béja", "Jendouba", "Le Kef", "Siliana", "Sousse",
    "Monastir", "Mahdia", "Sfax", "Kairouan", "Kasserine", "Sidi Bouzid",
    "Gabès", "Médenine", "Tataouine", "Gafsa", "Tozeur", "Kébili",
}
FOREIGN = {"99217", "99218", "99201", "99214", "99202", "99215", "99310", "99311"}
HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from normalise import GOV_SOURCE_CONFIRMATIONS, SPECIAL_CODES  # noqa: E402  (same pipeline)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent
    data_path = root / "data.json"
    html_path = root / "index.html"
    site = json.loads(data_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")

    by_code = {x["code"]: x for x in site}
    assert len(by_code) == len(site) == 711, "expected 711 unique codes"
    nrows = sum(len(x["rows"]) for x in site)
    assert nrows == 3249, "expected 3,249 rows, got {}".format(nrows)

    bad = [(x["code"], x.get("gov")) for x in site
           if x.get("gov") is not None and x["gov"] not in GOVS]
    assert not bad, "non-official governorate: {}".format(bad)
    none_codes = {x["code"] for x in site if x.get("gov") is None}
    assert none_codes == FOREIGN, "foreign null set changed: {}".format(sorted(none_codes))

    m = re.search(r"const DATA = /\*DATA\*/(\[.*\]);", html)
    assert m, "DATA marker missing from index.html"
    embedded = json.loads(m.group(1))
    assert embedded == site, "index.html DATA != data.json"

    pairs = collections.defaultdict(set)
    for x in site:
        pairs[x["code"]].add((x["inst"], x["licence"]))
    assert all(len(v) == 1 for v in pairs.values()), "more than one name pair per code"

    wrong = [(c, by_code[c]["gov"], g) for c, (g, _url)
             in GOV_SOURCE_CONFIRMATIONS.items()
             if by_code[c]["gov"] != g]
    assert not wrong, "official-source confirmation broken: {}".format(wrong)

    flagged = {x["code"] for x in site if x.get("special")}
    assert flagged == SPECIAL_CODES, "special flag set changed: {}".format(
        sorted(flagged ^ SPECIAL_CODES))
    assert all(x.get("special") is True for x in site if x["code"] in SPECIAL_CODES)

    print("codes {} / rows {} / foreign nulls {}".format(len(site), nrows, len(none_codes)))
    print("official-source confirmations checked: {}".format(len(GOV_SOURCE_CONFIRMATIONS)))
    print("special flags checked: {}".format(len(flagged)))
    print("sha256 data.json  {}".format(sha256(data_path)))
    print("sha256 index.html {}".format(sha256(html_path)))
    print("PUBLISH CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
