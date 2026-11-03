import cv2, numpy as np, subprocess, sys, json, re, os, glob
from multiprocessing import Pool

def lines(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bw = cv2.adaptiveThreshold(~g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
    h, w = bw.shape
    hor = cv2.morphologyEx(bw, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (max(20, w // 30), 1)))
    ver = cv2.morphologyEx(bw, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(20, h // 30))))
    return hor, ver

def runs(profile, thr, gap=3):
    out = []
    for i in np.where(profile > thr)[0]:
        if out and i - out[-1][1] <= gap: out[-1][1] = i
        else: out.append([i, i])
    return [int((a + b) / 2) for a, b in out]

S = 3
def tsv(crop, lang, psm=4, extra=""):
    """OCR a column once; return list of (y_center_in_crop, text_line)."""
    big = cv2.resize(crop, None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
    ok, buf = cv2.imencode(".png", big)
    r = subprocess.run(["tesseract", "stdin", "stdout", "-l", lang, "--psm", str(psm)] + extra.split() + ["tsv"],
                       input=buf.tobytes(), capture_output=True)
    groups = {}
    for ln in r.stdout.decode("utf-8", "ignore").splitlines()[1:]:
        p = ln.split("\t")
        if len(p) < 12 or not p[11].strip() or p[0] != "5": continue
        key = (p[2], p[3], p[4])
        top, hgt = int(p[7]), int(p[9])
        groups.setdefault(key, []).append((top + hgt / 2, p[11]))
    out = []
    for words in groups.values():
        y = sum(w[0] for w in words) / len(words) / S
        out.append((y, " ".join(w[1] for w in words)))
    return sorted(out)

def assign(items, bounds, y_off):
    cells = ["" for _ in bounds]
    for y, t in items:
        y += y_off
        for i, (a, b) in enumerate(bounds):
            if a - 2 <= y <= b + 2:
                cells[i] = (cells[i] + " " + t).strip(); break
    return cells

def read(path):
    img = cv2.imread(path)
    hor, ver = lines(img)
    h, w = hor.shape
    xs = runs(ver.sum(0) / 255, h * 0.5)
    cols = list(zip(xs[:-1], xs[1:]))
    if len(cols) != 7:
        return {"file": os.path.basename(path), "error": f"{len(cols)} columns"}
    def ys(c):
        x0, x1 = cols[c]
        return runs(hor[:, x0 + 2:x1 - 2].sum(1) / 255, (x1 - x0) * 0.6)
    sub = ys(0); blk = ys(3)
    if len(sub) < 2:
        return {"file": os.path.basename(path), "error": "no rows"}
    top, bot = sub[0], sub[-1]
    subs = [(a, b) for a, b in zip(sub[:-1], sub[1:]) if b - a >= 12]
    blks = [(a, b) for a, b in zip(blk[:-1], blk[1:]) if b - a >= 12]
    def col(c, lang, psm=4, extra=""):
        x0, x1 = cols[c]
        return tsv(img[top:bot, x0 + 2:x1 - 1], lang, psm, extra)
    score = assign(col(0, "eng", 4, "-c tessedit_char_whitelist=0123456789.-"), subs, top)
    form = assign(col(1, "eng", 4, "-c tessedit_char_whitelist=FGMABCDEHIJKLNOPQRSTUVWXYZ()+-/*,.0123456789axm"), subs, top)
    bac = assign(col(2, "ara", 4), subs, top)
    code = assign(col(3, "eng", 4, "-c tessedit_char_whitelist=0123456789"), blks, top)
    spec = assign(col(4, "ara", 4), blks, top)
    inst = assign(col(5, "ara", 4), blks, top)
    lic = " ".join(t for _, t in col(6, "ara", 4))
    rows = []
    for i, (a, b) in enumerate(subs):
        j = next((k for k, (c0, c1) in enumerate(blks) if c0 - 3 <= a and b <= c1 + 3), None)
        rows.append({"bac": bac[i], "formula": form[i], "score2025": score[i],
                     "code": re.sub(r"\D", "", code[j]) if j is not None else "",
                     "institution": inst[j] if j is not None else "",
                     "specialities": spec[j] if j is not None else "", "y": a})
    return {"file": os.path.basename(path), "licence": lic, "rows": rows}

if __name__ == "__main__":
    files = sys.argv[1:]
    with Pool(2) as p:
        res = p.map(read, files)
    print(json.dumps(res, ensure_ascii=False))
