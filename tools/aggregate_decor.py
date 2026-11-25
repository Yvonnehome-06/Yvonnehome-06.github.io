# -*- coding: utf-8 -*-
"""聚合 DECOR_DATA：同系列（同品名不同颜色/尺寸/套装）合并为一个商品 + variants。
封面按波比 2026-11-25 指定规则。variants = 组内除封面外全部条目（保原顺序）。
重跑安全：直接从 decor-data.js 读取重建。"""
import json, re, io, sys

SRC = "assets/js/decor-data.js"
s = io.open(SRC, encoding="utf-8").read()

arr_start = s.index("[", s.index("DECOR_DATA"))
data, end = json.JSONDecoder().raw_decode(s[arr_start:])
tail = s[end + arr_start:]  # DECOR_CATS 之后原样保留

# 组定义：prefix 匹配 title；cover 为封面条目 title；name 为聚合后商品名
GROUPS = [
    ("Cupid Candelabra",       "Cupid Candelabra 3-Piece Set - Black",           "Cupid Candelabra - Black",      lambda t: "Cupid Candelabra" in t and "Black" in t),
    ("European Candelabra",    "European Candelabra 3-Piece Set - Antique Gold", "European Candelabra",           lambda t: t.startswith("European Candelabra") or t.startswith("European Candlestick")),
    ("Pearl Mesh Table Runner","Pearl Mesh Table Runner - White",                "Pearl Mesh Table Runner",       lambda t: t.startswith("Pearl Mesh Table Runner")),
    ("Chair Back Flower",      "Chair Back Flower - Buttercup Yellow",           "Chair Back Flower",             lambda t: t.startswith("Chair Back Flower")),
    ("Floral Support Frame",   "Floral Support Frame - Black 02",                "Floral Support Frame - Black",  lambda t: t.startswith("Floral Support Frame")),
    ("Halloween Bouquet",      "Halloween Pumpkin Stem 01 - Orange & Black",     "Halloween Bouquet",             lambda t: t.startswith("Halloween Pumpkin Stem")),
    ("Trumpet Vase",           "Trumpet Vase 3-Piece Set - Gold",                "Trumpet Vase 3-Piece Set",      lambda t: t.startswith("Trumpet Vase")),
    ("Antique Iron Candelabra","Antique Iron Candelabra 3-Arm - Classic White",  "Antique Iron Candelabra",       lambda t: t.startswith("Antique Iron Candelabra")),
    ("Horn Arch Frame",        "Horn Arch Frame - White 1.4 + 1.8 m",            "Horn Arch Frame",               lambda t: t.startswith("Horn Arch Frame")),
    ("Roman Column Flower Pot","Roman Column Flower Pot - 24.5 cm",              "Roman Column Flower Pot",       lambda t: t.startswith("Roman Column Flower Pot")),
    ("Iridescent Butterfly",   "Iridescent Butterfly - White",                   "Iridescent Butterfly",          lambda t: t.startswith("Iridescent Butterfly")),
    ("White Bullet Candle",    "White Bullet Candle 7.8 x 10 cm",                "White Bullet Candle",           lambda t: "Bullet Candle" in t),
    ("Satin Tablecloth",       "Satin Tablecloth - Cream",                       "Satin Tablecloth",              lambda t: t.startswith("Satin Tablecloth")),
    ("Wedding Chair Back Tulle","Wedding Chair Back Tulle - Champagne",          "Wedding Chair Back Tulle",      lambda t: t.startswith("Wedding Chair Back Tulle")),
    ("Wedding Backdrop Drape", "Wedding Backdrop Drape - Cream",                 "Wedding Backdrop Drape",        lambda t: t.startswith("Wedding Backdrop Drape")),
    ("Coloured Jute Mesh",     "Coloured Jute Mesh - Cream",                     "Coloured Jute Mesh",            lambda t: t.startswith("Coloured Jute Mesh")),
]

used = set()
covers = {}
for name, cover_t, agg_t, match in GROUPS:
    members = [x for x in data if match(x["title"])]
    assert members, "no members for " + name
    cov = [x for x in members if x["title"] == cover_t]
    assert cov, "cover not found for " + name + ": " + cover_t
    for x in members:
        used.add(id(x))
    covers[name] = {"cover": cov[0], "members": members, "agg": agg_t}

out = []
emitted = set()
for x in data:
    owner = None
    for name, cover_t, agg_t, match in GROUPS:
        if match(x["title"]):
            owner = name
            break
    if owner is None:
        out.append(x)
        continue
    if owner in emitted:
        continue
    emitted.add(owner)
    c = covers[owner]
    cov, members, agg_t = c["cover"], c["members"], c["agg"]
    variants = [m for m in members if m is not cov]
    out.append({
        "img": cov["img"], "cat": cov["cat"], "title": agg_t,
        "desc": cov.get("desc", ""),
        "variants": [{"img": m["img"], "title": m["title"], "desc": m.get("desc", "")} for m in variants],
    })

body = json.dumps(out, ensure_ascii=False, indent=2)
new = s[:arr_start] + body + tail
io.open(SRC, "w", encoding="utf-8").write(new)
print("items:", len(data), "->", len(out), "groups:", len(GROUPS))
for name in covers:
    c = covers[name]
    print(" ", name, "cover:", c["cover"]["title"], "| variants:", len(c["members"]) - 1)
