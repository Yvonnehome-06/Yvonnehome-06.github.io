# -*- coding: utf-8 -*-
"""缺料清单 Excel 生成：账本明细(带案例) + 按材料去重补货表。"""
import re
from pathlib import Path

try:
    import openpyxl
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "openpyxl>=3.1.0"])
    import openpyxl

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

BASE = Path(r"D:\软件\workbuddy-1\2026-11-03-19-53-06\homegoods-b2b-site\tools")
LEDGER = BASE / "missing-materials.md"
SUMMARY = BASE / "missing-summary.md"
OUT = BASE / "缺失材料清单_SKU与案例.xlsx"

def xl_color(css_hex: str) -> str:
    value = css_hex.removeprefix("#").upper()
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB, got: {css_hex}")
    return "FF" + value

XL_HEAD = xl_color("#2F5597")
XL_HEAD_FONT = xl_color("#FFFFFF")
XL_ZEBRA = xl_color("#F4F6FB")
XL_BORDER = xl_color("#D9DFEA")
XL_RED_BG, XL_RED_FG = xl_color("#FCE4E4"), xl_color("#9C0006")
XL_YEL_BG, XL_YEL_FG = xl_color("#FFF2CC"), xl_color("#9C6500")
XL_BLU_BG, XL_BLU_FG = xl_color("#DDEBF7"), xl_color("#1F4E79")
XL_GRN_BG, XL_GRN_FG = xl_color("#E2EFDA"), xl_color("#375623")
thin = Side(style="thin", color=XL_BORDER)
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

# ---------- 解析账本 ----------
ledger_rows = []
bank_case_map = {}
for raw in LEDGER.read_text(encoding="utf-8").splitlines():
    s = raw.strip()
    if not s.startswith("|"):
        continue
    cells = [c.strip() for c in s.strip("|").split("|")]
    if len(cells) < 6 or not re.fullmatch(r"\d+", cells[0]):
        continue
    no = int(cells[0])
    cases = [c for c in re.findall(r"case-\d+", cells[2])]
    cases = sorted(set(cases), key=lambda x: int(x.split("-")[1]))
    bank_case_map[no] = cases
    ledger_rows.append({
        "no": no, "date": cells[1], "src": cells[2], "mat": cells[3],
        "feature": cells[4], "status": cells[5], "cases": "、".join(cases) if cases else cells[2],
    })

# ---------- 类别判定 ----------
FLOWER_KEYS = ["蕨","苔藓","翠珠","阿米芹","洋牡丹","大丽花","非洲菊","康乃馨","马蹄莲","朱顶红",
    "风信子","宫灯百合","玉兰","洋桔梗","乒乓菊","柠檬","玫瑰","虞美人","蓝星花","狐尾","毛地黄",
    "鼠尾草","翠菊","黄金球","落新妇","蓝盆花","波斯菊","千屈菜","黄金鱼草","粉小菊","茴香",
    "松果菊","松虫草","小花","紫藤","绿菊","团花","干花配花","罂粟","飞燕","绣球","铃兰","芍药",
    "雏菊","满天星","蝴蝶兰","跳舞兰","文心兰","蕙兰","海芋花","葱球","绒球","刺球","葡萄"]
LEAF_KEYS = ["叶","枫","龟背","春羽","银叶菊","银灰","变叶木","银杏","绿萝","熊掌木","千年木",
    "仙人掌","剑叶","海芋","箭叶芋","红掌","彩叶","尤加利","栀子","常春藤","文竹","天门冬","空气蕨"]
BRANCH_KEYS = ["枯藤","枯枝","龙须草","蒲苇","钢草","芒草","麦穗","麦秆菊","香蒲","银苞菊","八角花",
    "果枝","浆果","雾中情人","填充草","填充绿枝","松枝","南洋杉","柳","芦苇","雪柳","银柳","马尾草",
    "喷泉草","柔丝草","情人泪","芦苇草"]
FABRIC_KEYS = ["纱","布幔","网纱","丝带","蝴蝶结","流苏","雪纺","褶皱","绸","布艺"]
PROP_KEYS = ["灯","椅","凳","桶","镜","板","架","底座","地毯","烛杯","餐巾","KT","衣架","喷泉",
    "花瓣","砾石","摆件","吊灯","霓虹","串灯","纸艺","花篮","置物","背景","方凳","沙发","桌布"]

def classify(mat: str) -> str:
    for k in FABRIC_KEYS:
        if k in mat: return "纱幔/布艺"
    for k in PROP_KEYS:
        if k in mat: return "场地道具"
    for k in LEAF_KEYS:
        if k in mat: return "叶材"
    for k in BRANCH_KEYS:
        if k in mat: return "枝条/草/干花"
    for k in FLOWER_KEYS:
        if k in mat: return "花材"
    return "花材"

# ---------- 从材料名 + 特征抽取当前替代/候选 SKU ----------
NOISE = ("拼版核对过实物", "波比确认后为准", "拼版核对", "实物", "拼版")

def _clean_sku(v: str) -> str:
    v = re.sub(r"[（(].*?[)）]", "", v)
    for w in NOISE:
        v = v.replace(w, "")
    return v.strip(" *「」【】 ，,;；。、:")

def extract_sku(mat: str, feature: str) -> str:
    text = (mat or "") + " " + (feature or "")
    # 形态匹配：材料→SKU（箭头可能在材料列；排除 51→52 这类数字）
    if "→" in text:
        arr = re.findall(r"→\s*([^（(，,;；、]+)", text)
        arr = [_clean_sku(a) for a in arr]
        arr = [a for a in arr if a and not a.isdigit() and 1 < len(a) < 30
               and a not in ("SKU", "此为", "形态一致", "呈现")]
        if arr:
            return "；".join(dict.fromkeys(arr))
    # 暂用 / 以…呈现 / 候选
    for p in (r"暂用(.+?)呈现", r"用(.+?)呈现", r"以(.+?)呈现", r"候选[:：]\s*([^（，,;；]+)"):
        m = re.search(p, text)
        if m:
            v = _clean_sku(m.group(1))
            v = re.sub(r"^(页面|本案例|实物|真|款|新品|形态一致的|形态一致|此为)", "", v).strip()
            if v and len(v) < 40 and v not in ("SKU", "此为", "形态一致", "呈现"):
                return v
    return "—（纯缺，无现成SKU）"

wb = Workbook()
wb.properties.title = "缺失材料清单·SKU与案例"

# ================= Sheet1 缺料明细 =================
ws = wb.active
ws.title = "缺料明细(按案例)"
headers = ["账本#", "日期", "来源案例", "缺的材料", "类别", "当前SKU/暂代", "状态", "特征/说明"]
ws.append(headers)
for r in ledger_rows:
    sku = extract_sku(r["mat"], r["feature"])
    status = r["status"]
    if "纯缺" in sku and any(k in status for k in ("匹配", "解决", "别名", "替代", "修复")):
        sku = "见说明列（形态匹配）"
    ws.append([r["no"], r["date"], r["cases"], r["mat"], classify(r["mat"]),
               sku, status, r["feature"]])

nrow = ws.max_row
for c in range(1, len(headers) + 1):
    cell = ws.cell(1, c)
    cell.fill = PatternFill("solid", fgColor=XL_HEAD)
    cell.font = Font(bold=True, color=XL_HEAD_FONT, size=11)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER
widths = [7, 12, 42, 34, 14, 30, 20, 64]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
for rr in range(2, nrow + 1):
    for cc in range(1, len(headers) + 1):
        cell = ws.cell(rr, cc)
        cell.border = BORDER
        cell.alignment = Alignment(vertical="top", wrap_text=(cc in (3,4,6,8)),
                                   horizontal="center" if cc in (1,2,5,7) else "left")
        if rr % 2 == 0:
            cell.fill = PatternFill("solid", fgColor=XL_ZEBRA)
ws.freeze_panes = "C2"
ws.auto_filter.ref = f"A1:H{nrow}"
ws.row_dimensions[1].height = 30

def status_cf(ws, col_letter, start, end):
    rng = f"{col_letter}{start}:{col_letter}{end}"
    rules = [
        ("待补充", XL_RED_BG, XL_RED_FG), ("已撤下错误替代", XL_RED_BG, XL_RED_FG),
        ("定夺", XL_YEL_BG, XL_YEL_FG), ("确认", XL_YEL_BG, XL_YEL_FG),
        ("暂用", XL_BLU_BG, XL_BLU_FG), ("形态匹配", XL_BLU_BG, XL_BLU_FG),
        ("已解决", XL_GRN_BG, XL_GRN_FG), ("已修复", XL_GRN_BG, XL_GRN_FG),
    ]
    for word, bg, fg in rules:
        ws.conditional_formatting.add(rng, FormulaRule(
            formula=[f'ISNUMBER(SEARCH("{word}",${col_letter}{start}))'],
            fill=PatternFill("solid", fgColor=bg), font=Font(color=fg)))
status_cf(ws, "G", 2, nrow)

# ================= Sheet2 补货去重 =================
ws2 = wb.create_sheet("补货去重(按材料)")
h2 = ["大类", "分组", "材料/颜色", "频次/状态", "涉及账本#", "涉及案例", "当前SKU/候选", "说明"]
ws2.append(h2)

def cases_from_nums(nums):
    cs = []
    for n in nums:
        for c in bank_case_map.get(n, []):
            if c not in cs:
                cs.append(c)
    cs.sort(key=lambda x: int(x.split("-")[1]))
    return cs

section, group = "", ""
prop_added = False
for raw in SUMMARY.read_text(encoding="utf-8").splitlines():
    s = raw.strip()
    if s.startswith("## ") or s.startswith("# "):
        section = s.lstrip("# ").strip()
        group = ""
        continue
    if s.startswith("### "):
        group = s.lstrip("# ").strip()
        continue
    if s.startswith("## 五、") or "场地装置" in section:
        if not prop_added and s and not s.startswith("|") and not s.startswith(">"):
            ws2.append([section, "场地道具", "（详见明细表·按案例）", "一般不补", "—", "—", "—", s[:120]])
            prop_added = True
    if not s.startswith("|"):
        continue
    cells = [c.strip() for c in s.strip("|").split("|")]
    if len(cells) < 2:
        continue
    if any(k in cells[0] for k in ("材料", "颜色")) or set(cells[0]) <= set("-: "):
        continue
    if "备注案号" in "|".join(cells):
        continue
    mat = cells[0]
    freq = cells[1] if len(cells) > 1 else ""
    memo = cells[2] if len(cells) > 2 else ""
    nums = [int(x) for x in re.findall(r"#(\d+)", freq + " " + memo)]
    cases = cases_from_nums(nums)
    if len(cases) > 14:
        case_str = "、".join(cases[:14]) + f" 等共{len(cases)}个案例"
    else:
        case_str = "、".join(cases) if cases else "—"
    cand = extract_sku(mat, memo) if memo and ("候选" in memo or "→" in memo) else ("—（纯缺）" if "缺" in freq or "待补" in memo else "")
    sec_short = re.sub(r"^[一二三四五]、", "", section).split("（")[0]
    ws2.append([sec_short, group, mat, freq, " ".join(f"#{n}" for n in nums) if nums else "—",
                case_str, cand, memo])

nrow2 = ws2.max_row
for c in range(1, len(h2) + 1):
    cell = ws2.cell(1, c)
    cell.fill = PatternFill("solid", fgColor=XL_HEAD)
    cell.font = Font(bold=True, color=XL_HEAD_FONT, size=11)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER
widths2 = [16, 22, 30, 12, 26, 46, 24, 40]
for i, w in enumerate(widths2, 1):
    ws2.column_dimensions[get_column_letter(i)].width = w
for rr in range(2, nrow2 + 1):
    for cc in range(1, len(h2) + 1):
        cell = ws2.cell(rr, cc)
        cell.border = BORDER
        cell.alignment = Alignment(vertical="top", wrap_text=(cc in (2,3,5,6,7,8)),
                                   horizontal="center" if cc in (1,4) else "left")
        if rr % 2 == 0:
            cell.fill = PatternFill("solid", fgColor=XL_ZEBRA)
ws2.freeze_panes = "C2"
ws2.auto_filter.ref = f"A1:H{nrow2}"
ws2.row_dimensions[1].height = 30
status_cf(ws2, "D", 2, nrow2)

# ================= Sheet3 填表说明 =================
ws3 = wb.create_sheet("填表说明")
ws3["A1"] = "缺失材料清单 · 填表说明"
ws3["A1"].font = Font(bold=True, size=14, color=XL_HEAD)
notes = [
    ("数据来源", "tools/missing-materials.md（165 行账本）+ tools/missing-summary.md（按材料去重汇总）"),
    ("账本#", "缺失材料账本行号，用于追溯；与 missing-summary.md 里的 #N 一致"),
    ("来源案例 / 涉及案例", "该缺料出现在哪些现场案例（case-XXX）。已合并同实景隐藏案例，仅显示可见案例"),
    ("当前SKU/暂代", "页面当前用于呈现的替代 SKU 或候选款；标为纯缺表示图库确无对应款"),
    ("状态口径", "待补充=图库确无；待定夺=有候选但口径未定；暂用替代/形态匹配=已用近似款呈现待确认；已解决/已修复=已处理"),
    ("补货流程", "①按材料去重表确定优先级（频次越高越先补）→②补入图库→③回填对应 case spec→④重跑流水线自动上线"),
    ("铁律", "名字≠实物：匹配到中文名只证明名字对，颜色/形态必须核对缩略图；禁止用近似品冒充真缺料"),
]
ws3["A2"] = "项目"; ws3["B2"] = "说明"
for c in ("A2", "B2"):
    ws3[c].fill = PatternFill("solid", fgColor=XL_HEAD)
    ws3[c].font = Font(bold=True, color=XL_HEAD_FONT)
    ws3[c].border = BORDER
for i, (k, v) in enumerate(notes, 3):
    ws3.cell(i, 1, k).font = Font(bold=True)
    ws3.cell(i, 2, v).alignment = Alignment(wrap_text=True, vertical="top")
    ws3.cell(i, 1).border = BORDER
    ws3.cell(i, 2).border = BORDER
ws3.column_dimensions["A"].width = 20
ws3.column_dimensions["B"].width = 110

wb.save(OUT)
print(f"SAVED {OUT}")
print(f"Sheet1 明细 {nrow-1} 行 / Sheet2 去重 {nrow2-1} 行")
