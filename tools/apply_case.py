# -*- coding: utf-8 -*-
"""
一键写入案例拆解 —— 中文材料清单 -> 站点数据，零看图。

用法：
    python tools/apply_case.py <spec.json>

spec.json 格式：
{
  "case_id": 3,
  "title": "Castle Wedding Arch",              # 可选，默认沿用原标题
  "scene": "wedding",                          # 可选
  "colors": ["white", "green"],                # 可选
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

流程：
1. 读 tools/material_alias.json + 图库（flowers-data.js / decor-data.js）自动匹配 SKU
2. 命中的新 SKU 自动补进 window.LOOK_PRODUCTS（英文名取自图库记录本身）
3. 写回 assets/js/onsite-data.js 的 materials 分组 + products 聚合数组
4. 输出缺口清单（自动追加到 案例展示_缺口产品清单.md）
"""
import json, os, re, sys, collections, io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from material_matcher import Matcher, _read, BASE, TOOLS  # noqa: E402

SITE = BASE
DATA_P = os.path.join(SITE, 'assets/js/onsite-data.js')
PROD_P = os.path.join(SITE, 'assets/js/onsite-products.js')
GAP_P = os.path.join(os.path.dirname(BASE), '案例展示_缺口产品清单.md')


def load_cases():
    s = _read(DATA_P)
    k = s.find('window.ONSITE_CASES = ')
    pre = s[:k]
    cases = json.JSONDecoder().raw_decode(s[s.find('[', k):])[0]
    return pre, cases


def save_cases(pre, cases):
    with open(DATA_P, 'w', encoding='utf-8', newline='\n') as f:
        f.write(pre + 'window.ONSITE_CASES = ' + json.dumps(cases, ensure_ascii=False) + ';\n')


def save_look(look):
    """写回产品字典。保持紧凑单行格式，避免无谓的大 diff。"""
    body = ',\n  '.join(
        '%s: %s' % (json.dumps(k), json.dumps(v, ensure_ascii=False))
        for k, v in look.items())
    with open(PROD_P, 'w', encoding='utf-8', newline='\n') as f:
        f.write('// 精选 SKU 字典：案例拆解 / shop-the-look 引用\n')
        f.write('// 键名 = 案例 materials 里引用的 k；字段 n/cn/c/s/t/f 对应图库记录\n')
        f.write('window.LOOK_PRODUCTS = {\n  ' + body + '\n};\n')


def main(spec_path):
    with open(spec_path, encoding='utf-8') as f:
        spec = json.load(f)

    m = Matcher()
    pre, cases = load_cases()
    case = next((c for c in cases if c['id'] == spec['case_id']), None)
    if case is None:
        print('!! 找不到 case id=%s' % spec['case_id'])
        return 1

    all_items, missing = [], []
    for g in spec['groups']:
        items, miss = m.match_group(g['items'])
        if miss:
            missing.extend(miss)
        # 只保留已存在的键，避免写入无法解析的引用；同组内同 SKU 去重
        real, seen_in_group = [], set()
        for it in items:
            if it['k'] not in m.look:
                m.ensure_in_dict([it])
            if it['k'] in seen_in_group:
                continue
            seen_in_group.add(it['k'])
            real.append({'k': it['k'], 'role': it.get('role', '')})
        g['_items'] = real
        all_items.extend(real)

    # 新 SKU 补进字典
    added = m.ensure_in_dict(all_items)

    # 组装 materials
    materials = collections.OrderedDict()
    for g in spec['groups']:
        if not g['_items']:
            continue
        materials[g['key']] = {
            'label': g['label'],
            'blurb': g.get('blurb', ''),
            'items': g['_items'],
        }

    case['materials'] = materials
    case['products'] = [it['k'] for it in all_items]

    if spec.get('title'):
        case['title'] = spec['title']
    if spec.get('scene'):
        case['scene'] = spec['scene']
    if spec.get('colors'):
        case['colors'] = spec['colors']

    save_cases(pre, cases)
    save_look(m.look)

    print('case %s 已更新：%d 组 / %d 项材料' % (
        spec['case_id'], len(materials), len(all_items)))
    if added:
        print('  新增 SKU 到产品字典：%s' % ', '.join(added))
    if missing:
        print('  库里没有（需补货）：')
        for x in missing:
            print('    - %s' % x['cn'])
    else:
        print('  全部命中，零缺口')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
