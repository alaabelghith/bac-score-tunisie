import json, cv2, re, subprocess, numpy as np, os, sys
from multiprocessing import Pool
from ocr_v2 import grid, ink, key
from ocr_fast import runs
files=[l.strip() for l in open("tables.txt")]
def cells(path):
    im=cv2.imread(path); hor,xs=grid(im)
    if len(xs)!=8: return {}
    x0,x1=xs[0],xs[1]; sub=runs(hor[:,x0+2:x1-2].sum(1)/255,(x1-x0)*0.6); out={}
    for a,b in zip(sub[:-1],sub[1:]):
        if b-a<12: continue
        cr=ink(im[a+2:b-1,x0+3:x1-2])
        if cr is not None: out[key(cr)]=cr
    return out
def ocr(img,psm):
    ok,buf=cv2.imencode(".png",img)
    r=subprocess.run(["tesseract","stdin","stdout","-l","eng","--psm",str(psm),"-c","tessedit_char_whitelist=0123456789.-"],input=buf.tobytes(),capture_output=True)
    return re.sub(r"\s+","",r.stdout.decode())
def passes(item):
    k,cr=item
    g=cv2.cvtColor(cr,cv2.COLOR_BGR2GRAY)
    a=cv2.resize(g,None,fx=6,fy=6,interpolation=cv2.INTER_LANCZOS4); a=cv2.threshold(a,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    a=cv2.copyMakeBorder(a,30,30,30,30,cv2.BORDER_CONSTANT,value=255)
    b=cv2.resize(g,None,fx=3,fy=3,interpolation=cv2.INTER_LINEAR); b=cv2.copyMakeBorder(b,20,20,20,20,cv2.BORDER_CONSTANT,value=255)
    return k,[ocr(a,7),ocr(b,8)]
if __name__=="__main__":
    with Pool(2) as p: allc={}; [allc.update(d) for d in p.map(cells,files)]
    with Pool(2) as p: res=dict(p.map(passes,allc.items()))
    os.makedirs("scorecells",exist_ok=True)
    for k,cr in allc.items(): cv2.imwrite(f"scorecells/{k}.png",cr)
    json.dump(res,open("score_passes.json","w")); print(len(res))
