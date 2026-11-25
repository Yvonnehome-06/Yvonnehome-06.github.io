# -*- coding: utf-8 -*-
"""今天(2026-11-25)23个新品品类按同色去重入库。
   源: 19目录商品图；目标: 03独立站 assets/img/newitems/ + flowers-data.js。
   每个多色商品聚合为1个商品(多SKU)，不同品种独立。绝不近似顶替，图片文件真实存在才写。"""
import json
import re
import shutil
from pathlib import Path
from PIL import Image

SRC = Path(r"D:\软件\workbuddy-1\2026-11-19-17-52-02")
BASE = Path(r"D:\软件\workbuddy-1\2026-11-03-19-53-06\homegoods-b2b-site")
IMGDIR = BASE / "assets/img/newitems"
DATAJS = BASE / "assets/js/flowers-data.js"
IMGDIR.mkdir(parents=True, exist_ok=True)

# 颜色中英对照
COL = {
 "白色":"White","白":"White","乳白色":"Milky White","奶白":"Cream","米白":"Ivory","香槟":"Champagne","香槟色":"Champagne",
 "粉色":"Pink","粉":"Pink","浅粉":"Light Pink","淡粉":"Light Pink","深粉":"Dark Pink","粉红":"Pink","桔粉":"Coral Pink","秋粉":"Autumn Pink","边粉":"Pink Edge","粉心香槟":"Pink-centre Champagne","黄心香槟":"Yellow-centre Champagne",
 "红色":"Red","红":"Red","大红":"Bright Red","粉边":"Pink Edge","深槟":"Dark Champagne",
 "黄色":"Yellow","黄":"Yellow","桔色":"Orange","橘色":"Orange","深橘色":"Deep Orange","浅紫红":"Light Mauve",
 "紫色":"Purple","紫":"Purple","浅紫":"Light Purple","深紫":"Dark Purple","暗紫":"Deep Purple","玫红":"Fuchsia","炫彩紫":"Iridescent Purple","边深紫":"Dark Purple Edge","边玫红":"Fuchsia Edge","紫心":"Purple Centre",
 "蓝色":"Blue","蓝":"Blue","宝蓝":"Royal Blue","天蓝":"Sky Blue","深蓝":"Navy Blue","浅蓝":"Light Blue","深蓝":"Dark Blue",
 "浅绿":"Light Green","绿色":"Green","绿":"Green","深绿":"Deep Green","黄绿":"Yellow Green","浅绿色":"Light Green","边绿":"Green Edge","秋绿":"Autumn Green",
 "灰色":"Grey","咖色":"Coffee","深咖":"Dark Coffee","黑色":"Black","黑":"Black","紫边":"Purple Edge","雪色":"Snow","艳夕":"Sunset",
 "玫红色":"Fuchsia","浅紫":"Light Purple","紫心绿":"Purple-centre Green","红心绿":"Red-centre Green","红斑绿":"Red-spot Green","红点白":"Red-dot White","黄心绿":"Yellow-centre Green","白绿":"White Green","白点绿":"White-spot Green","骨节白":"Bone White","渐变绿":"Gradient Green","斑点白":"Spotted White","红边绿":"Red-edge Green","白网纹":"White Vein",
}

# 品类映射: (源目录, 中文商品名, 英文商品名, 分类slug, 是否按颜色多SKU, 代表图指定)
# 多品种混合包(蕨类叶/波斯蕨羽毛)按每个文件名=独立商品，单独处理
SINGLE_COLOR = [
 ("商品图_仿真壁挂空气草_1072107595231/壁挂空气草类","仿真壁挂空气草","Artificial Wall-mounted Air Plant","greenery"),
]
MULTI_COLOR = [
 ("商品图_仿真3头桔梗_774807762661/桔梗花类","仿真3头桔梗","Artificial 3-Head Balloon Flower","others"),
 ("商品图_仿真PU大丽花_853002173375/大丽花类","仿真PU大丽花","Artificial PU Dahlia","others"),
 ("商品图_仿真宫灯百合_1005659055144/宫灯百合类","仿真宫灯百合","Artificial Lantern Lily","lilies"),
 ("商品图_仿真小康乃馨_1080120865190/小康乃馨类","仿真小康乃馨","Artificial Mini Carnation","others"),
 ("商品图_仿真小马蹄莲_1006580901581/马蹄莲类","仿真小马蹄莲","Artificial Mini Calla Lily","others"),
 ("商品图_仿真朱顶红君子兰_993392420978/朱顶红君子兰类","仿真朱顶红","Artificial Amaryllis","others"),
 ("商品图_仿真百合花_725463755817/百合花类","仿真百合花","Artificial Lily","lilies"),
 ("商品图_仿真翠珠花_1056999092632/翠珠花类","仿真翠珠花","Artificial Ammi Majus","others"),
 ("商品图_仿真落新妇_1077065509913/落新妇类","仿真落新妇","Artificial Astilbe","others"),
 ("商品图_仿真蓝星花_1068391525996/蓝星花类","仿真蓝星花","Artificial Blue Star Flower","others"),
 ("商品图_仿真蓝盆花_649626652114/蓝盆花类","仿真蓝盆花","Artificial Scabiosa","others"),
 ("商品图_仿真露莲_932169424862/露莲类","仿真3头露莲","Artificial 3-Head Lewisia","others"),
 ("商品图_仿真非洲菊_850177202004/非洲菊类","仿真非洲菊","Artificial African Daisy","others"),
 ("商品图_仿真黄金球_1078508794595/黄金球类","仿真黄金球","Artificial Craspedia","others"),
 ("商品图_寂遥虞美人_1101335626174/虞美人花类","仿真虞美人","Artificial Poppy","others"),
 ("商品图_蕾丝玫瑰_1091631374636/玫瑰花类","仿真蕾丝玫瑰","Artificial Lace Rose","roses"),
]
# 海芋叶19色=多品种(彩芋叶/大海芋/海棠叶/海芋)，每个品种聚合颜色
HAIYU = ("商品图_仿真海芋叶_787233084624/海芋叶类", "greenery",
         [("单只大海芋","Artificial Large Alocasia Leaf","仿真大海芋"),
          ("单只彩芋叶","Artificial Coloured Alocasia Leaf","仿真彩芋叶"),
          ("单只海棠叶","Artificial Begonia Leaf","仿真海棠叶"),
          ("单只海芋","Artificial Elephant Ear Leaf","仿真海芋叶"),
          ("单支大海芋","Artificial Large Alocasia Leaf 2","仿真大海芋2"),
          ("单支彩芋叶","Artificial Coloured Alocasia Leaf 2","仿真彩芋叶2"),
          ("单支海棠叶","Artificial Begonia Leaf 2","仿真海棠叶2")])
# 蕨类波斯叶：按子目录品种，每品种内再按颜色后缀聚合
FERN = ("商品图_仿真蕨类波斯叶_989453327974", "greenery")
FERN_FEATHER = ("商品图_仿真波斯蕨羽毛_973940625681", "greenery")
BIRDNEST = ("商品图_仿真鸟巢蕨巴西木_896672199983", "greenery")
MOSS = ("商品图_仿真苔藓草皮_950371186335/按颜色代表图_3张", "仿真苔藓草皮","Artificial Moss Mat","greenery")
REED = ("商品图_芦苇蒲苇_713887492596/按品种代表图_2张", "仿真蒲苇","Artificial Pampas Grass","greenery")

# 现有数据
raw = DATAJS.read_text(encoding="utf-8")
m = re.search(r"window\.FLOWER_DATA\s*=\s*(\[.*?\]);", raw, re.S)
DATA = json.loads(m.group(1))
m2 = re.search(r"window\.FLOWER_CATS\s*=\s*(\[.*?\]);", raw, re.S)
CATS = json.loads(m2.group(1))
existing_files = {it["file"] for it in DATA}
next_no = {}
def next_idx(cat):
    n = next_no.get(cat, 0)
    pref = "newitems-" + cat + "-"
    while True:
        n += 1
        fn = f"assets/img/newitems/{pref}{n:03d}.jpg"
        if fn not in existing_files and not (IMGDIR / f"{pref}{n:03d}.jpg").exists():
            break
    next_no[cat] = n
    return n, f"{pref}{n:03d}"

added = []
def add_one(cat, cn_full, en_full, src_img, color_cn=""):
    idx, base = next_idx(cat)
    target = IMGDIR / (base + ".jpg")
    shutil.copy2(src_img, target)
    im = Image.open(target)
    if im.mode in ("RGBA","LA","P"):
        b = Image.new("RGB", im.size, (255,255,255)); im = im.convert("RGBA"); b.paste(im, mask=im.split()[-1]); im = b
    else:
        im = im.convert("RGB")
    im.thumbnail((1200,1200), Image.LANCZOS)
    im.save(target, "JPEG", quality=88, optimize=True)
    c = next((x for x in CATS if x["slug"]==cat), {})
    sku = cn_full + ("-" + color_cn if color_cn else "")
    en = en_full + (" - " + COL.get(color_cn, color_cn) if color_cn and COL.get(color_cn, color_cn) else "")
    cn_disp = cn_full + ("-" + color_cn if color_cn else "")
    DATA.append({"cat":cat,"catCn":c.get("cn",cat),"file":f"assets/img/newitems/{base}.jpg",
                 "thumb":f"assets/img/newitems/{base}.jpg","name":en,"cn":cn_disp,"sku":sku})
    existing_files.add(f"assets/img/newitems/{base}.jpg")
    added.append((cat, cn_disp, color_cn))

def color_of(stem, base=None):
    s = stem
    if base: s = s.replace(base, "", 1)
    s = s.strip(" -－()（）0123456789新款")
    return s

# --- 单色/双色商品 ---
for rel, cn, en, cat in SINGLE_COLOR:
    for f in sorted((SRC/rel).glob("*.jpg")):
        col = color_of(f.stem)
        add_one(cat, cn, en, f, col if col != cn else "")

# --- 多色商品：每个颜色一个 SKU（聚合时同品名会合并成1商品） ---
for rel, cn, en, cat in MULTI_COLOR:
    for f in sorted((SRC/rel).glob("*.jpg")):
        col = color_of(f.stem)
        add_one(cat, cn, en, f, col)

# --- 海芋叶：按品种前缀分组 ---
hy_dir, hy_cat, hy_specs = HAIYU
for prefix, en, cn in hy_specs:
    fs = sorted((SRC/hy_dir).glob(prefix+"*.jpg"))
    for f in fs:
        col = f.stem.replace(prefix, "", 1).strip(" -－")
        add_one(hy_cat, cn, en, f, col)

# --- 蕨类波斯叶：按子目录=品种，每文件一个规格 ---
fern_dir, fern_cat = FERN
for sub in sorted((SRC/fern_dir).iterdir()):
    if not sub.is_dir(): continue
    variety_cn = sub.name.replace("类","")
    variety_en = {"波斯叶蕨类":"Boston Fern","枫叶类":"Maple Leaf","棕榈竹芋类":"Palm Leaf",
                  "葵叶类":"Sunflower Leaf","其他叶类":"Assorted Greenery"}.get(sub.name, sub.name)
    for f in sorted(sub.glob("*.jpg")):
        stem = f.stem
        # 品种名从文件名剥离做颜色/规格
        spec = re.sub(r"^(9头|13片|15片|14片|2叉|5叉|7叉|9片|13片|15片|23片|带须|仿真|带须把束|单只|9叶|15叶)","",stem)
        add_one(fern_cat, variety_cn, variety_en, f, spec.strip())

# --- 波斯蕨羽毛：按子目录品种 ---
ff_dir, ff_cat = FERN_FEATHER
for sub in sorted((SRC/ff_dir).iterdir()):
    if not sub.is_dir(): continue
    variety_cn = sub.name.replace("类","")
    variety_en = {"波斯蕨类":"Boston Fern","羽毛类":"Feather Grass","枫叶类":"Maple Leaf"}.get(sub.name, sub.name)
    for f in sorted(sub.glob("*.jpg")):
        add_one(ff_cat, variety_cn, variety_en, f, f.stem.strip())

# --- 鸟巢蕨巴西木 ---
for sub in sorted((SRC/BIRDNEST[0]).iterdir()):
    if not sub.is_dir(): continue
    variety_cn = sub.name.replace("类","")
    variety_en = {"鸟巢蕨类":"Bird's Nest Fern","巴西木万年青类":"Dracaena"}.get(sub.name, sub.name)
    for f in sorted(sub.glob("*.jpg")):
        add_one("greenery", variety_cn, variety_en, f, "")

# --- 苔藓草皮代表图 ---
mdir, cn, en, cat = MOSS
for f in sorted((SRC/mdir).glob("*.jpg")):
    add_one(cat, cn, en, f, f.stem.split("_")[-1])

# --- 芦苇蒲苇代表图 ---
rdir, cn, en, cat = REED
for f in sorted((SRC/rdir).glob("*.jpg")):
    add_one(cat, cn, en, f, f.stem.split("_")[-1])

# 更新 CATS count
for cc in CATS:
    cc["count"] = sum(1 for it in DATA if it["cat"]==cc["slug"])

# 写回 flowers-data.js（保持原格式）
out = "// AUTO-GENERATED — do not edit by hand.\n"
out += "window.FLOWER_DATA = " + json.dumps(DATA, ensure_ascii=False, separators=(",",":")) + ";\n"
out += "window.FLOWER_CATS = " + json.dumps(CATS, ensure_ascii=False, separators=(",",":")) + ";\n"
DATAJS.write_text(out, encoding="utf-8")

print(f"新增 SKU: {len(added)} | 总 SKU: {len(DATA)}")
from collections import Counter
for cat,n in Counter(a[0] for a in added).most_common():
    print(f"  {cat}: {n}")
print("WROTE", DATAJS)
