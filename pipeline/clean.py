import json, re, collections
# Arabic letters that differ only by dots -> same class (OCR mostly gets dots wrong)
SK = str.maketrans({"ب":"ٮ","ت":"ٮ","ث":"ٮ","ن":"ٮ","ي":"ٮ","ى":"ٮ","ئ":"ٮ","ج":"ح","خ":"ح","ذ":"د","ز":"ر","ش":"س","ض":"ص","ظ":"ط","غ":"ع","ف":"ٯ","ق":"ٯ","ة":"ه","أ":"ا","إ":"ا","آ":"ا","ؤ":"و","ـ":None})
def sk(w): return w.translate(SK)
TOWNS = {  # town spelling -> governorate (fr)
 "تونس":"Tunis","قرطاج":"Tunis","باردو":"Tunis","المرسى":"Tunis","الكرم":"Tunis","الشرقية":"Tunis","المنار":"Tunis","رادس":"Ben Arous","بن عروس":"Ben Arous","المروج":"Ben Arous","حمام الأنف":"Ben Arous","الزهراء":"Ben Arous","مقرين":"Ben Arous","برج السدرية":"Ben Arous",
 "أريانة":"Ariana","سكرة":"Ariana","الغزالة":"Ariana","سيدي ثابت":"Ariana","منوبة":"Manouba","الدندان":"Manouba","قصر السعيد":"Manouba",
 "نابل":"Nabeul","الحمامات":"Nabeul","قليبية":"Nabeul","قربة":"Nabeul","منزل تميم":"Nabeul","المعمورة":"Nabeul","بني خيار":"Nabeul",
 "بنزرت":"Bizerte","ماطر":"Bizerte","زغوان":"Zaghouan","باجة":"Béja","مجاز الباب":"Béja","جندوبة":"Jendouba","طبرقة":"Jendouba","الكاف":"Le Kef","سليانة":"Siliana",
 "سوسة":"Sousse","حمام سوسة":"Sousse","المنستير":"Monastir","المكنين":"Monastir","المهدية":"Mahdia","صفاقس":"Sfax","القيروان":"Kairouan","القصرين":"Kasserine","سبيطلة":"Kasserine",
 "سيدي بوزيد":"Sidi Bouzid","قفصة":"Gafsa","المتلوي":"Gafsa","توزر":"Tozeur","نفطة":"Tozeur","قبلي":"Kébili","دوز":"Kébili","قابس":"Gabès","مدنين":"Médenine","جربة":"Médenine","جرجيس":"Médenine","تطاوين":"Tataouine","بوعرادة":"Siliana","الجم":"Mahdia","سيدي بوسعيد":"Tunis","شط مريم":"Sousse","مساكن":"Sousse","قصر هلال":"Monastir","المحرس":"Sfax"}
WORDS = """المعهد العالي العليا المدرسة الوطنية كلية العلوم الآداب الإنسانية الاجتماعية الإجتماعية الاقتصادية الإقتصادية والتصرف التصرف الحقوق والعلوم السياسية جامعة للدراسات التكنولوجية التكنولوجيا التطبيقية للمهندسين للتجارة الإعلامية الاعلامية للإعلامية والرياضيات الرياضيات للفنون والحرف الفنون الحرف للموسيقى الموسيقى للرياضة والتربية البدنية للتمريض الصحة لعلوم وتقنيات تقنيات للغات اللغات الطب الصيدلة طب الأسنان الهندسة البيطري للفلاحة الفلاحية الزراعية للعلوم والتكنولوجيا والتقنيات للتصرف للمحاسبة وإدارة المؤسسات للشغل والدراسات للدراسات التجارية العليا للنقل واللوجستية للحضارة الإسلامية لأصول الدين الزيتونة الشريعة القانونية للعلوم الإنسانية الإنسانيات للتكنولوجيا الطبية البيولوجية للإعلامية والملتيميديا لفنون الملتيميديا الملتميديا التحضيري التحضيرية للدراسات الهندسية والحرف والعلوم والآداب للصحافة وعلوم الإخبار للتوثيق للتراث للسياحة للتنشيط الشبابي والثقافي للمسرح للفنون الجميلة للبيئة للمياه للغابات للعلوم البيولوجية للعلوم التطبيقية والتكنولوجيا للإعلامية والتصرف للإعلامية والاتصالات للاتصالات والإلكترونيك الإلكترونيك للإحصاء والتحليل وتحليل المعلومات للإدارة العامة الإدارة العامة للدراسات التكنولوجية بالشرقية الافتراضية الأساسية للتربية وبالمكفوفين المكفوفين معاهد شعبة مخصصة للناجحين من ذات اختبار وغير معنية بالتنفيل الجغرافي
الإجازة في علوم تصميم الفضاء الصورة العربية الفرنسية الإنجليزية الإنقليزية الألمانية الإيطالية الإسبانية سنوات أمد الاقتصادية هندسة نظم المنتوج الشعبة الإجازة الوطنية الأساسية الموضة البصرية والسمعية الفيزياء الكيمياء الحياة والأرض البيولوجيا الجغرافيا التاريخ الفلسفة علم الاجتماع النفس الإعلامية التصرف المالية التسويق المحاسبة إدارة الأعمال الموارد البشرية مرحلة تحضيرية دراسات هندسية الكهربائية الميكانيكية الإلكترونيك والكهروتقنية والآلية تكنولوجيات المعلومات والاتصال الإخبار المدنية الصناعية الكيميائية البيوتكنولوجيا الطاقة الفنون التشكيلية السينما المسرح التصميم الداخلي الموضة الجرافيك المرئية الهندسة المعمارية التهيئة الحضرية التعمير التمريض القبالة البصريات الأشعة التخدير الإنعاش التغذية التأهيل العلاج الطبيعي المخبر الصيدلي الحاسوب البرمجيات الشبكات المنظومات الإعلامية المضمنة الأنظمة البيانات المالية والمصرفية التأمين المحاسبة التدقيق القانون العام الخاص الإدارة التجارة الدولية اللوجستية السياحة الفندقة الترجمة الحضارة""".split()
LEX = {}
def add(w, canon=None):
    for p in ("", "ب", "ل", "و", "وال", "بال", "لل"):
        LEX.setdefault(sk(p + w), p + (canon or w))
for w in WORDS: add(w)
for t in TOWNS:
    for part in t.split(): add(part)
    add(t.replace(" ", ""), t)
SKL = {}
for k, v in list(LEX.items()):
    SKL.setdefault(len(k), []).append((k, v))
def near(w):
    """lexicon word whose skeleton is 1 edit away (substitution/insert/delete), only for words >= 4 letters"""
    t = sk(w)
    if t in LEX: return LEX[t]
    if len(t) < 4: return None
    best = None
    for L in (len(t) - 1, len(t), len(t) + 1):
        for k, v in SKL.get(L, []):
            if L == len(t):
                if sum(a != b for a, b in zip(k, t)) == 1: best = best or v
            else:
                a, b = (k, t) if len(k) > len(t) else (t, k)
                if any(a[:i] + a[i+1:] == b for i in range(len(a))): best = best or v
    return best
def fix_text(s):
    s = re.sub(r"[|”“\"_]", " ", s or ""); s = re.sub(r"\b\d\b", " ", s)
    s = s.replace("(", " ( ").replace(")", " ) ")
    toks = s.split(); out = []; i = 0
    while i < len(toks):
        w = toks[i]
        if i + 1 < len(toks) and sk(w + toks[i + 1]) in LEX and sk(w) not in LEX:      # "يتوت س" -> "بتونس"
            out.append(LEX[sk(w + toks[i + 1])]); i += 2; continue
        m = re.match(r"^([(\[]?)(.*?)([)\].,]?)$", w); pre, core, post = m.groups()
        out.append(pre + (near(core) or core) + post); i += 1
    s = " ".join(out).replace("( ", "(").replace(" )", ")")
    return re.sub(r"\s+", " ", s).strip()
def governorate(s):
    t = sk(s.replace(" ", ""))
    hits = [(t.find(sk(town.replace(" ", ""))), town) for town in TOWNS if sk(town.replace(" ", "")) in t]
    if not hits: return None
    # the town written right after "ب" before the university bracket is the location; prefer the first hit before "("
    pre = sk(s.split("(")[0].replace(" ", ""))
    loc = [town for town in sorted(TOWNS, key=len, reverse=True) if sk(town.replace(" ", "")) in pre]
    town = loc[0] if loc else sorted(hits)[0][1]
    return TOWNS[town], town
if __name__ == "__main__":
    rows = json.load(open("rows.json"))
    by = collections.defaultdict(list)
    for r in rows: by[r["code"]].append(r)
    unknown = collections.Counter(); progs = []
    for code, rs in by.items():
        names = [fix_text(r["institution"]) for r in rs]
        name = max(names, key=lambda n: (("جامعة" in n) + ("(" in n), len(n)))
        g = governorate(name)
        lic = fix_text(rs[0]["licence"])
        for w in name.split():
            c = w.strip("()[].,")
            if sk(c) not in LEX and len(c) > 2: unknown[c] += 1
        progs.append({"code": code, "institution": name, "governorate": g[0] if g else None, "town": g[1] if g else None,
                      "licence": lic, "page": rs[0]["page"],
                      "rows": [{"bac": r["bac"], "formula": r["formula"], "cutoff2025": float(r["score_final"]) if r.get("score_final") not in (None, "", "-") else None} for r in rs]})
    print("programmes", len(progs), "no governorate", sum(1 for p in progs if not p["governorate"]))
    print("unknown words:", unknown.most_common(60))
    json.dump(progs, open("programmes.json", "w"), ensure_ascii=False)
    for p in progs[:8] + progs[300:306]: print(p["code"], p["governorate"], "|", p["institution"][:80], "|", p["licence"][:60])
