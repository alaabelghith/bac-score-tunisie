import cv2, numpy as np, subprocess, sys, json, re, os, hashlib
from multiprocessing import Pool
from ocr_fast import lines, runs, tsv, assign

def grid(img):
    hor, ver = lines(img)
    h, w = hor.shape
    xs = runs(ver.sum(0) / 255, h * 0.5)
    if xs and xs[-1] < w - 15: xs.append(w - 1)       # missing right border (p.117)
    if xs and xs[0] > 15: xs.insert(0, 0)
    xs = [x for i, x in enumerate(xs) if i == 0 or x - xs[i - 1] > 25]   # drop doubled divider lines
    return hor, xs

def ink(crop):
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    m = g < 160
    if m.sum() < 8: return None
    ys, xs = np.where(m)
    return crop[max(ys.min()-3,0):ys.max()+4, max(xs.min()-3,0):xs.max()+4]

def key(c):
    g = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (max(8, c.shape[1] // 2), max(4, c.shape[0] // 2)))
    return hashlib.md5((g > 140).tobytes() + bytes(g.shape)).hexdigest()

def page(path):
    img = cv2.imread(path)
    hor, xs = grid(img)
    cols = list(zip(xs[:-1], xs[1:]))
    name = os.path.basename(path)
    if len(cols) != 7: return {"file": name, "error": f"{len(cols)} columns"}
    def ys(c):
        x0, x1 = cols[c]; return runs(hor[:, x0 + 2:x1 - 2].sum(1) / 255, (x1 - x0) * 0.6)
    sub, blk = ys(0), ys(3)
    if len(sub) < 2: return {"file": name, "error": "no rows"}
    top, bot = sub[0], sub[-1]
    subs = [(a, b) for a, b in zip(sub[:-1], sub[1:]) if b - a >= 12]
    blks = [(a, b) for a, b in zip(blk[:-1], blk[1:]) if b - a >= 12]
    def col(c, lang):
        x0, x1 = cols[c]; return tsv(img[top:bot, x0 + 2:x1 - 1], lang, 4)
    code = assign(col(3, "eng"), blks, top); spec = assign(col(4, "ara"), blks, top)
    inst = assign(col(5, "ara"), blks, top); lic = " ".join(t for _, t in col(6, "ara"))
    rows, crops = [], {}
    for a, b in subs:
        j = next((k for k, (c0, c1) in enumerate(blks) if c0 - 3 <= a and b <= c1 + 3), None)
        r = {"code": re.sub(r"\D", "", code[j]) if j is not None else "",
             "institution": inst[j] if j is not None else "", "specialities": spec[j] if j is not None else "", "y": a}
        for c, f in ((0, "score"), (1, "formula"), (2, "bac")):
            x0, x1 = cols[c]
            cr = ink(img[a + 2:b - 1, x0 + 3:x1 - 2])
            if cr is None: r[f] = None; continue
            k = key(cr); r[f] = k; crops[k] = (f, cr)
        rows.append(r)
    return {"file": name, "licence": lic, "rows": rows, "crops": crops}

CFG = {"score": ("eng", "-c tessedit_char_whitelist=0123456789.,-"), "formula": ("eng", ""), "bac": ("ara", "")}
def ocr_cell(item):
    k, (f, cr) = item
    lang, extra = CFG[f]
    big = cv2.copyMakeBorder(cv2.resize(cr, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC), 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    ok, buf = cv2.imencode(".png", big)
    r = subprocess.run(["tesseract", "stdin", "stdout", "-l", lang, "--psm", "7"] + extra.split(), input=buf.tobytes(), capture_output=True)
    return k, re.sub(r"\s+", " ", r.stdout.decode("utf-8", "ignore")).strip()

if __name__ == "__main__":
    files = [l.strip() for l in open("tables.txt") if l.strip()]
    with Pool(2) as p:
        pages = p.map(page, files)
    crops = {}
    for pg in pages:
        crops.update(pg.pop("crops", {}))
    print("unique cells:", {f: sum(1 for v in crops.values() if v[0] == f) for f in CFG}, file=sys.stderr)
    VER = json.load(open("verified_cells.json"))
    todo = {k: v for k, v in crops.items() if v[0] == "score"}
    missing = [k for k, v in crops.items() if v[0] != "score" and k not in VER]
    print("unverified bac/formula cells:", missing, file=sys.stderr)
    with Pool(2) as p:
        txt = dict(p.map(ocr_cell, todo.items()))
    txt.update({k: VER[k] for k in crops if k in VER})
    for pg in pages:
        for r in pg.get("rows", []):
            for f in CFG:
                r[f] = txt.get(r[f]) if r[f] else None
    json.dump(pages, open("all_v2.json", "w"), ensure_ascii=False)
    print("ok", sum(len(p.get("rows", [])) for p in pages), "rows; errors:", [p["file"] for p in pages if "error" in p], file=sys.stderr)
