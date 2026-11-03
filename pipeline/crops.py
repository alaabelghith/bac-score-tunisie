import cv2, numpy as np, os, json, sys
from ocr_v2 import grid, ink, key
from ocr_fast import runs
from multiprocessing import Pool
def one(path):
    img = cv2.imread(path); hor, xs = grid(img); cols = list(zip(xs[:-1], xs[1:]))
    if len(cols) != 7: return (os.path.basename(path), len(cols), {})
    x0, x1 = cols[0]; sub = runs(hor[:, x0+2:x1-2].sum(1)/255, (x1-x0)*0.6)
    out = {}
    for a, b in zip(sub[:-1], sub[1:]):
        if b - a < 12: continue
        for c, f in ((1, "formula"), (2, "bac")):
            cx0, cx1 = cols[c]; cr = ink(img[a+2:b-1, cx0+3:cx1-2])
            if cr is not None: out[key(cr)] = (f, cr)
    return (os.path.basename(path), len(cols), out)
files = [l.strip() for l in open("tables.txt") if l.strip()]
with Pool(2) as p: res = p.map(one, files)
crops = {}
for n, c, o in res:
    if n.startswith("x-117"): print("117 cols:", c)
    crops.update(o)
os.makedirs("cells", exist_ok=True)
for k, (f, cr) in crops.items(): cv2.imwrite(f"cells/{f}_{k}.png", cr)
print(len(crops))
