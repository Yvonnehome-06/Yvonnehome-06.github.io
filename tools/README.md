# 案例拆解自动化流水线

把「中文花材清单 → 站点 SKU 匹配 → 改数据 → 校验 → 上线」做成一条命令，**不需要人工看图确认形态**。

## 用法

```bash
# 1. 写一份 spec（JSON），case_id 指向要改的案例
# 2. 一键跑
python tools/run_case.py tools/specs/case-003.json

# 3. 需要上线时
python tools/run_case.py tools/specs/case-003.json --commit "说明" --push
```

## spec 格式

```json
{
  "case_id": 3,
  "title": "Castle Wedding Arch",
  "scene": "wedding",
  "colors": ["white", "green"],
  "groups": [
    {
      "key": "blooms",
      "label": "Blooms & accents",
      "blurb": "The main flowers and the small accents that fill the gaps between them.",
      "items": [
        {"cn": "白绣球", "role": "Large white clusters along the top — the visual main flower."}
      ]
    }
  ]
}
```

- `key`：分组标识，随便起（blooms / accents / foliage …），**组数不限**
- `cn`：**图库里的中文材料名**，脚本靠它匹配 SKU
- `role`：这一项在造景里起什么作用（英文，站点上展示）

## 匹配规则（按优先级）

1. `tools/material_alias.json` 的 `terms` 精确命中 —— 人工核实过的，最可靠
2. 别名词表按「剥离颜色后的词根」命中
3. `flowers-data.js` 中文名精确命中
4. 图库词根命中（剥离颜色 + 剥离数字头数 + 剥离「叶/枝/草/球」等通用后缀）
5. 中文名包含关系模糊匹配
6. 同物异名改写（`SYNONYM_CN`：龟背竹→镂空龟背叶、桉叶→桉树叶…）
7. 装饰品类中文别名（`DECOR_CAT_CN`：烛台/桌布/花瓶/布幔/纱帘/麻绳…）

命中图库里还没有的 SKU 时，**自动补进 `window.LOOK_PRODUCTS`**（英文名直接取图库记录本身，无需人工起名）。

## 校验（`run_case.py` 自动执行）

- 所有 `materials` / `products` 引用的键都能在 `LOOK_PRODUCTS` 里解析
- `LOOK_PRODUCTS` 每条的 `t` / `f` 图片文件**真实存在**
- 三个 JS 文件语法正确

任何一项不过就中止，不会写出坏数据。

## 已知缺口（库里没有，需补货）

| 材料 | 状态 |
|---|---|
| 喷泉草（观赏草） | 用空气草顶替 |
| 绣线菊 / 小手球 | 用雪柳顶替 |
| 高山羊齿（真蕨） | 用芦荀草顶替 |
| 落新妇 Astilbe | 用霞草顶替 |
| 橄榄枝 | 用三叉米兰果顶替 |
| 灰紫绣球 | 用勿忘我绣球-紫顶替 |
| 苔藓 / 蒲苇 / 干花 / 桉叶 / 绿萝 / 龟背竹 / 灯串 / 珠帘 / 气球 / 椅套 / 拱门骨架 / 玻璃花瓶 | 真缺口 |

补到货后，把新 SKU 加进 `flowers-data.js` 或 `decor-data.js`，再跑一次流水线即可自动接上。

## 文件

| 文件 | 作用 |
|---|---|
| `tools/material_matcher.py` | 匹配引擎（中文名 → SKU） |
| `tools/material_alias.json` | 别名表（terms 精确映射 / by_key 反查） |
| `tools/apply_case.py` | 写数据 + 输出缺口 |
| `tools/run_case.py` | 一键：应用 → 校验 → 提交 → 推送 → 线上核验 |
| `tools/specs/case-XXX.json` | 各案例的拆解 spec |

## 同实景多图合并 / 删除 / 详情页（2026-11-24）

- 分组定义在 `tools/groups.json`：`groups[]`（keep + absorb）+ `hidden[]`（用户要求删除的案例 id，数据保留仅前端隐藏）
- 改完配置后跑 `python tools/apply_groups.py`（幂等，可反复重跑）
- **注意**：`git checkout -- assets/` 会把合并字段一起还原——回归测试重跑拆解后若需恢复数据，用 `python tools/apply_groups.py` 重建，不要用 checkout 还原整个 assets 目录
- 材料清单**不在页面下方平铺展示**（用户明确否决），只在点开案例后的灯箱详情界面里显示：左大图 + 右侧浅色面板（分组编号/说明 + 材料缩略图卡片 + 询价按钮）
- 左上角水印去除：PIL 纹理克隆（取水印框正下方同尺寸树叶块 + 羽化蒙版），主图与 thumb 都要处理；box 需留足余量（WELLNEED logo + 文字约 190×130px，取 200×150px 框）
