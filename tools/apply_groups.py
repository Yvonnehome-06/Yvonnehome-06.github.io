# -*- coding: utf-8 -*-
"""Apply same-scene photo groups to onsite-data.js.

For each group in tools/groups.json:
  - keep case gets `images` = [keep.img, absorb imgs...] and `imageCount`
  - absorb cases get `mergedInto` = keep id
Re-running is idempotent: fields are recomputed from the base img, not appended.
"""
import json, re, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'assets/js/onsite-data.js')
GROUPS = os.path.join(BASE, 'tools/groups.json')

def load_cases(src):
    m = re.search(r'(window\.ONSITE_CASES\s*=\s*)(\[.*\])(\s*;)', src, re.S)
    if not m:
        raise SystemExit('!! 找不到 ONSITE_CASES 数组')
    return m, json.loads(m.group(2))

def main():
    src = open(DATA, encoding='utf-8').read()
    m, cases = load_cases(src)
    by_id = {c['id']: c for c in cases}
    spec = json.load(open(GROUPS, encoding='utf-8'))
    groups = spec['groups']

    # idempotency: clear prior merge fields
    for c in cases:
        c.pop('images', None); c.pop('imageCount', None); c.pop('mergedInto', None)

    covered = set()
    for g in groups:
        keep_id = g['keep']
        if keep_id not in by_id:
            raise SystemExit('!! keep id 不存在: %s' % keep_id)
        ids = [keep_id] + list(g['absorb'])
        for i in ids:
            if i not in by_id:
                raise SystemExit('!! 案例 id 不存在: %s' % i)
            if i in covered:
                raise SystemExit('!! 案例 id 重复出现在多组: %s' % i)
            covered.add(i)
        keep = by_id[keep_id]
        imgs = [by_id[i]['img'] for i in ids]
        keep['images'] = imgs
        keep['imageCount'] = len(imgs)
        for a in g['absorb']:
            by_id[a]['mergedInto'] = keep_id
        print('组 keep=%d 吸收=%s -> %d 张图' % (keep_id, g['absorb'], len(imgs)))

    out = src[:m.start(2)] + json.dumps(cases, ensure_ascii=False) + src[m.end(2):]
    open(DATA, 'w', encoding='utf-8').write(out)
    print('\n写入完成：%d 组，%d 个案例被并入，展示案例 %d' %
          (len(groups), len(covered)-len(groups), len(cases)-len([c for c in cases if c.get('mergedInto')])))

if __name__ == '__main__':
    main()
