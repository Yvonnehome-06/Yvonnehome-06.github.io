# -*- coding: utf-8 -*-
"""把 flowers-data.js 的 SKU 聚合成商品：一商品一代表图 + variants[]。
   规则：中文名剥最后一个『-颜色/规格』后缀作为商品键；全部变体保留，绝不丢 SKU。
   产出 assets/js/products-aggregated.js（window.PRODUCT_AGG / PRODUCT_CATS）。"""
import json
import re
from pathlib import Path

BASE = Path(r"D:\软件\workbuddy-1\2026-11-03-19-53-06\homegoods-b2b-site")
SRC = BASE / "assets/js/flowers-data.js"
OUT = BASE / "assets/js/products-aggregated.js"

raw = SRC.read_text(encoding="utf-8")

def grab(var):
    m = re.search(r"window\." + var + r"\s*=\s*(\[.*?\]);", raw, re.S)
    return json.loads(m.group(1))

DATA = grab("FLOWER_DATA")
CATS = grab("FLOWER_CATS")

# 颜色/规格词表：这些作为后缀剥掉后可作为同一商品；剥不掉就整名当商品
COLOR_WORDS = set("""白 粉 红 黄 蓝 紫 绿 咖色 酒红 香槟 奶白 浅粉 深粉 玫红 浅紫 深紫 宝蓝 浅蓝 深蓝
浅绿 深绿 果绿 桔 浅咖 深咖 灰色 银色 金色 杏色 米白 象牙 渐变 混色 多色 拼色
60cm 80cm 100cm 120cm 1米 2米 大号 中号 小号 单只 3头 5头""".split())

def strip_prefix(cn):
    """剥供应商前缀：开头 ≥2 个大写字母(可带数字尾)紧跟中文，如 DM/JN/XH/DD/DT/XGM3/HY/DDYZ。
    数字开头(3D尤加利)或纯中文(12头芦苇)不剥。"""
    cn = (cn or "").strip()
    m = re.match(r"^([A-Z]{2,}\d*)(?=[\u4e00-\u9fa5])", cn)
    return cn[len(m.group(1)):].strip() if m else cn


def cn_base(cn):
    cn = strip_prefix((cn or "").strip())
    # 剥最后一个 -后缀（颜色或规格）
    if "-" in cn or "－" in cn:
        head, tail = re.split(r"[-－]", cn, 1)
        # tail 里若还有 -，取最后一段；只剥颜色/规格词
        last = re.split(r"[-－]", cn)[-1].strip()
        if last in COLOR_WORDS or len(last) <= 4:
            return head.strip() or cn
        return cn
    return cn

EN_COLOR_RE = re.compile(
    r"\s*-\s*(White|Pink|Red|Yellow|Blue|Purple|Green|Cream|Ivory|Champagne|Burgundy|Black|"
    r"Orange|Lilac|Coffee|Milky White|Light \w+|Dark \w+|Fruit Green|Royal Blue|Fuchsia|"
    r"Assorted|Mix|Yellow\b|Golden|Silver|Pink(?:\s*\w+)?)[^)]*$", re.I)

def en_base(name, cn):
    name = (name or "").strip()
    # 有颜色的（cn 带 -后缀）才剥英文尾色；单品整名保留
    stripped = EN_COLOR_RE.sub("", name).strip()
    if not stripped or len(stripped) < 4:
        return name
    return stripped

groups = {}
for it in DATA:
    cn = it.get("cn") or it.get("sku") or it.get("name")
    key_cn = cn_base(cn)
    # 用 cat + cn_base 做键，避免跨类误并
    key = (it.get("cat", ""), key_cn)
    if key not in groups:
        groups[key] = []
    groups[key].append(it)

# 选代表图：优先名字里不带颜色/规格歧义、白底图（文件名序号小），取第一条
# 封面人工指定（波比 2026-11-25：玫红掌杆子太假，换粉款，石纹背景更经得起细看）；键=cat|cn_base
COVER_OVERRIDES = {
    "others|3D掌": "assets/img/flowers/others/others-003.jpg",  # 3D掌-粉
}

# 手动合并（波比 2026-11-25：情人泪5个SKU实为2个实物，感知哈希 024≈016、023≈017，
# 021 与 017 同色重复；合并为一个商品，只留 黄016 + 奶黄017，重复图不再上墙）
# 键=cat|cn_base（目标商品），merge_bases=并入的组，drop_files=并组后丢弃的重复图，labels=变体显示名覆盖
MERGE_OVERRIDES = {
    "babys-breath|情人泪": {
        "merge_bases": ["DT情人泪", "DT情人泪2", "情人泪2"],
        "drop_files": [
            "assets/img/flowers/babys-breath/babys-breath-021.jpg",
            "assets/img/flowers/babys-breath/babys-breath-023.jpg",
            "assets/img/flowers/babys-breath/babys-breath-024.jpg",
        ],
        "labels": {
            "情人泪2-黄": {"color": "奶黄", "cn": "情人泪-奶黄", "name": "Valentine Tears - Creamy Yellow"},
        },
    },
    # 万圣节藤条-1米 与 1米万圣节藤条：同一张图(d=1)同一规格，仅名字顺序不同
    "garlands|万圣节藤条": {
        "merge_bases": ["1米万圣节藤条"],
        "drop_files": ["assets/img/newitems/garlands-968.jpg"],
        "labels": {},
    },
    # 硬胶/软胶满天星：同一实物不同拍摄照片(d=78哈希抓不到)，波比 2026-11-25 指认合并
    "babys-breath|硬胶满天星": {
        "merge_bases": ["软胶满天星"],
        "drop_files": [],
        "labels": {
            "硬胶满天星-白": {"color": "白（硬胶）"},
            "软胶满天星-白": {"color": "白（软胶）", "cn": "软胶满天星-白", "name": "Baby's Breath - White (Soft-Gel)"},
            "软胶满天星-粉": {"color": "粉（软胶）"},
            "软胶满天星-紫": {"color": "紫（软胶）"},
            "软胶满天星-黄": {"color": "黄（软胶）"},
            "软胶满天星": {"color": "软胶款"},
        },
        "name": "Baby's Breath",
    },
    # ---- 同款同色重复拍摄去重（2026-11-25 波比授权"有重复就需要更正"，拼版人工核对）----
    # 国潮牡丹 红/酒红 实物同色，仅背景不同（白底/灰底），留白底 028
    "peonies|国潮牡丹": {"merge_bases": [], "drop_files": ["assets/img/flowers/peonies/peonies-029.jpg"], "labels": {}},
    # 锦绣 红/酒红 实物同色，留 060
    "peonies|锦绣": {"merge_bases": [], "drop_files": ["assets/img/flowers/peonies/peonies-062.jpg"], "labels": {}},
    # 燕尾兰 BDJN 前缀条目与 083 同款同色重复拍摄，留 083
    "orchids|燕尾兰": {"merge_bases": [], "drop_files": ["assets/img/flowers/orchids/orchids-119.jpg"], "labels": {}},
    # 塑料葱球 HY 前缀条目重复拍摄，留 187
    "others|塑料葱球": {"merge_bases": [], "drop_files": ["assets/img/flowers/others/others-228.jpg"], "labels": {}},
    # 把束花生叶 XGM 前缀条目重复拍摄，留 090
    "greenery|把束花生叶": {"merge_bases": [], "drop_files": ["assets/img/flowers/greenery/greenery-206.jpg"], "labels": {}},
    # 叉圣诞叶：087=XGM3叉(3叉)、088=XGM5叉(5叉) 同色不同规格，标签区分
    "greenery|叉圣诞叶": {
        "merge_bases": [],
        "drop_files": [],
        "labels": {
            "叉圣诞叶-黄": {"color": "黄（3叉）"},
            "叉圣诞叶-黄@greenery-088.jpg": {"color": "黄（5叉）"},
        },
    },
}

for mkey, cfg in MERGE_OVERRIDES.items():
    mcat, mbase = mkey.split("|", 1)
    tgt = groups.get((mcat, mbase))
    if tgt is None:
        continue
    for b in cfg.get("merge_bases", []):
        src = groups.pop((mcat, b), [])
        tgt.extend(src)
    drops = set(cfg.get("drop_files", []))
    if drops:
        groups[(mcat, mbase)] = [x for x in tgt if x.get("file") not in drops]

# ---- 通用近重复合并（波比规则：同商品同色同规格只保留一个展示图）----
# 判据：感知哈希 d<=8（同一张图）+ 颜色后缀兼容（相等或均为纯数字）+ 规格词（X头/X叉/X米/cm）一致
# 仅同类目内并；决策全部打印供人工复核
import collections as _collections
from PIL import Image as _PILImage

def _phash(path):
    im = _PILImage.open(path).convert("L").resize((16, 16))
    px = list(im.getdata())
    avg = sum(px) / len(px)
    bits = 0
    for i, v in enumerate(px):
        if v > avg:
            bits |= 1 << i
    return bits

# 彩色距离：同构图不同色相（如宝蓝/玫红绣球）灰度哈希相同但彩距大(>10)；真同图 <7
def _csmall(path, sz=12):
    return list(_PILImage.open(path).convert("RGB").resize((sz, sz)).getdata())

def _cdist(a, b):
    return sum(abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2]) for x, y in zip(a, b)) / max(len(a), 1)

_SPEC_RE = re.compile(r"\d+(?:\.\d+)?(?:头|叉|米|cm)")

def _spec_tokens(cn):
    return sorted(_SPEC_RE.findall(strip_prefix(cn or "")))

def _csuf(cn):
    cn = strip_prefix(cn or "")
    return cn.rsplit("-", 1)[-1] if "-" in cn else ""

def _same_display(cna, cnb, ha, hb, ca=None, cb=None):
    """同一张照片 = 灰度 d<=8 且彩距<=8（同构图不同色相不算同图）"""
    if bin(ha ^ hb).count("1") > 8:
        return False
    if ca is not None and cb is not None and _cdist(ca, cb) > 8:
        return False
    return True

def _compat(cna, cnb):
    """UNION 级兼容：规格词一致 + 颜色后缀兼容"""
    if _spec_tokens(cna) != _spec_tokens(cnb):
        return False
    s1, s2 = _csuf(cna), _csuf(cnb)
    return s1 == s2 or (s1.isdigit() and s2.isdigit())

_fh_cache = {}
_fc_cache = {}
def _fh(f):
    if f not in _fh_cache:
        try:
            _fh_cache[f] = _phash(f)
        except Exception:
            _fh_cache[f] = None
    return _fh_cache[f]

def _fc(f):
    if f not in _fc_cache:
        try:
            _fc_cache[f] = _csmall(f)
        except Exception:
            _fc_cache[f] = None
    return _fc_cache[f]

_parent = {k: k for k in groups}
def _find(x):
    while _parent[x] != x:
        _parent[x] = _parent[_parent[x]]
        x = _parent[x]
    return x

_by_cat = _collections.defaultdict(list)
for k in groups:
    _by_cat[k[0]].append(k)
# 同图但规格/颜色标注冲突的强制去重：同一张照片只有一个实物，保留规格词标注更全的一条
_force_drop = set()
for _cat, _keys in _by_cat.items():
    _flat = [(k, it) for k in _keys for it in groups[k]]
    for _i in range(len(_flat)):
        _ka, _ia = _flat[_i]
        if id(_ia) in {id(x) for _, x in _flat[:_i]}:
            pass
        _ha = _fh(_ia.get("file", ""))
        if _ha is None:
            continue
        for _j in range(_i + 1, len(_flat)):
            _kb, _ib = _flat[_j]
            if _find(_ka) == _find(_kb):
                continue
            if _ia.get("file", "") == _ib.get("file", ""):
                continue
            _hb = _fh(_ib.get("file", ""))
            if _hb is None:
                continue
            _ca, _cb = _fc(_ia.get("file", "")), _fc(_ib.get("file", ""))
            if not _same_display(_ia.get("cn", ""), _ib.get("cn", ""), _ha, _hb, _ca, _cb):
                continue
            if _compat(_ia.get("cn", ""), _ib.get("cn", "")):
                _parent[_find(_kb)] = _find(_ka)
            else:
                # 同图但标注冲突：留规格词多者，同多则留文件序号小者
                sa, sb = len(_spec_tokens(_ia.get("cn", ""))), len(_spec_tokens(_ib.get("cn", "")))
                if sa != sb:
                    winner, loser = (_ia, _ib) if sa > sb else (_ib, _ia)
                else:
                    winner, loser = (_ia, _ib) if _ia.get("file", "") <= _ib.get("file", "") else (_ib, _ia)
                _force_drop.add(id(loser))
                print("FORCE-DROP %-10s 留[%s] %s  弃[%s] %s  (同图标注冲突)" % (
                    _cat, winner.get("cn"), winner.get("file", "").split("/")[-1],
                    loser.get("cn"), loser.get("file", "").split("/")[-1]))

_merged = {}
for k in groups:
    _merged.setdefault(_find(k), []).extend([it for it in groups[k] if id(it) not in _force_drop])
_merged = {k: v for k, v in _merged.items() if v}
_union_log = []
_new_groups = {}
for _root, _items in sorted(_merged.items()):
    _bases = sorted({cn_base(it.get("cn") or "") for it in _items})
    _base = min(_bases, key=lambda b: (len(b), b))
    _new_groups[(_root[0], _base)] = _items
    if len(_bases) > 1:
        _union_log.append((_root[0], _base, _bases, len(_items)))
groups = _new_groups
for _cat, _base, _bases, _n in sorted(_union_log):
    print("UNION %-12s -> %-14s  并入组: %s  (共%d SKU)" % (_cat, _base, " / ".join(_bases), _n))

agg = []
for (cat, base), items in groups.items():
    items = sorted(items, key=lambda x: x.get("file", ""))
    # 组内去重：与已保留项同图（d<=8）且颜色/规格兼容的不重复上墙
    kept = []
    for it in items:
        _h = _fh(it.get("file", ""))
        if _h is None:
            kept.append(it)
            continue
        _dup = False
        for _k in kept:
            _hk = _fh(_k.get("file", ""))
            if _hk is not None and _same_display(it.get("cn", ""), _k.get("cn", ""), _h, _hk, _fc(it.get("file", "")), _fc(_k.get("file", ""))):
                _dup = True
                break
        if not _dup:
            kept.append(it)
    items = kept
    # 代表项：优先 cn_base == base 的条目，否则第一条
    rep = next((x for x in items if cn_base(x.get("cn") or "") == base), items[0])
    ov = COVER_OVERRIDES.get(cat + "|" + base)
    if ov:
        cand = [x for x in items if x.get("file") == ov]
        if cand:
            rep = cand[0]
    variants = []
    seen = set()
    label_cfg = (MERGE_OVERRIDES.get(cat + "|" + base) or {}).get("labels", {})
    for it in items:
        color = (it.get("cn") or it.get("sku") or "").replace(base, "").lstrip("-－").strip()
        # 供应商前缀残留清理（并组后 base 变短，如 JN高枝夏花-黄 剥 高枝夏花 得 JN-黄 → 黄）
        color = re.sub(r"^[A-Za-z0-9]+[-－]?", "", color).strip()
        vkey = (it.get("cn"), it.get("file"))
        if vkey in seen:
            continue
        seen.add(vkey)
        _cn = it.get("cn", "")
        lo = label_cfg.get(_cn + "@" + it.get("file", "").split("/")[-1]) or label_cfg.get(_cn, {}) or label_cfg.get(_cn + "@" + it.get("file", ""), {})
        variants.append({
            "name": lo.get("name", it.get("name", "")),
            "cn": lo.get("cn", it.get("cn", "")),
            "sku": it.get("sku", ""),
            "color": lo.get("color", color),
            "thumb": it.get("thumb", ""),
            "file": it.get("file", ""),
        })
    c = next((x for x in CATS if x["slug"] == cat), {})
    _name_ov = (MERGE_OVERRIDES.get(cat + "|" + base) or {}).get("name")
    agg.append({
        "id": base[:40] + "-" + cat,
        "cat": cat,
        "catCn": c.get("cn", ""),
        "catEn": c.get("en", ""),
        "base": base,
        "name": _name_ov or en_base(rep.get("name", ""), base),
        "thumb": rep.get("thumb", ""),
        "file": rep.get("file", ""),
        "count": len(variants),
        "variants": variants,
    })

agg.sort(key=lambda x: (next((c.get("order", 99) for c in CATS if c["slug"] == x["cat"]), 99), x["base"]))

# 每个分类的商品数（用于 chips）
cat_counts = {}
for a in agg:
    cat_counts[a["cat"]] = cat_counts.get(a["cat"], 0) + 1
cats_out = []
for c in sorted(CATS, key=lambda x: x.get("order", 99)):
    n = cat_counts.get(c["slug"], 0)
    if n:
        cats_out.append({"slug": c["slug"], "en": c["en"], "cn": c["cn"], "count": n})

js = "// AUTO-GENERATED by tools/build_aggregated.py — do not edit by hand.\n"
js += "window.PRODUCT_AGG = " + json.dumps(agg, ensure_ascii=False, separators=(",", ":")) + ";\n"
js += "window.PRODUCT_CATS = " + json.dumps(cats_out, ensure_ascii=False, separators=(",", ":")) + ";\n"
OUT.write_text(js, encoding="utf-8")

print("SKU:", len(DATA), "-> 商品:", len(agg))
print("多规格商品:", sum(1 for a in agg if a["count"] > 1))
print("分类:", " | ".join(f'{c["slug"]}:{c["count"]}' for c in cats_out))
print("WROTE", OUT)

# ---- 前缀剥离清单（人工过目防误剥）----
_pref = _collections.Counter()
for it in DATA:
    m = re.match(r"^([A-Z]{2,}\d*)(?=[\u4e00-\u9fa5])", (it.get("cn") or "").strip())
    if m:
        _pref[m.group(1)] += 1
print("剥前缀清单:", dict(_pref) or "（无）")

# ---- 残留同图扫描（合并后同类目内不应再有同图重复；灰度+彩距双判据）----
_left = []
for _cat in {a["cat"] for a in agg}:
    _items = [(a["name"], v) for a in agg if a["cat"] == _cat for v in a["variants"]]
    for _i in range(len(_items)):
        _ha = _fh(_items[_i][1].get("file", ""))
        if _ha is None:
            continue
        for _j in range(_i + 1, len(_items)):
            if _items[_i][1]["file"] == _items[_j][1]["file"]:
                continue
            _hb = _fh(_items[_j][1].get("file", ""))
            if _hb is None or bin(_ha ^ _hb).count("1") > 8:
                continue
            _ca, _cb = _fc(_items[_i][1].get("file", "")), _fc(_items[_j][1].get("file", ""))
            if _ca is None or _cb is None or _cdist(_ca, _cb) > 8:
                continue
            _left.append((_cat, _items[_i][0], _items[_j][0], _items[_i][1]["file"], _items[_j][1]["file"]))
print("残留同图对(d<=8):", len(_left))
for _c, _n1, _n2, _f1, _f2 in _left[:30]:
    print("  [%s] %s <-> %s  (%s | %s)" % (_c, _n1, _n2, _f1.split("/")[-1], _f2.split("/")[-1]))
