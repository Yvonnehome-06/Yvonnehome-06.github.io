# -*- coding: utf-8 -*-
"""
一键：中文材料清单 -> 站点数据 -> 校验 -> 提交 -> 推送 -> 线上核验

用法：
    python tools/run_case.py <spec.json> [--commit "msg"] [--push]

步骤：
  1. apply_case  匹配 SKU、写 onsite-data.js / onsite-products.js
  2. validate    校验：所有引用键可解析、图片文件真实存在、JS 语法正确
  3. commit/push 可选
  4. verify      线上核验（可选，需先 push）
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply_case  # noqa: E402
from material_matcher import Matcher, BASE  # noqa: E402

SITE = BASE

LIVE = 'https://yvonnehome-06.github.io'


def validate():
    """站点数据自检：引用键、图片路径、JS 语法。"""
    errs = []
    m = Matcher()
    # 1. 所有 case 的 products / materials 引用键必须存在于 LOOK_PRODUCTS
    pre, cases = apply_case.load_cases()
    for c in cases:
        for k in c.get('products', []):
            if k not in m.look:
                errs.append('case %s products 引用不存在的键: %s' % (c['id'], k))
        for g, v in (c.get('materials') or {}).items():
            for it in v.get('items', []):
                if it['k'] not in m.look:
                    errs.append('case %s materials.%s 引用不存在的键: %s' % (c['id'], g, it['k']))
    # 2. LOOK_PRODUCTS 每条的图片必须真实存在
    for k, v in m.look.items():
        for fld in ('t', 'f'):
            p = v.get(fld)
            if not p:
                errs.append('LOOK_PRODUCTS.%s 缺少 %s 字段' % (k, fld))
                continue
            if not os.path.exists(os.path.join(SITE, p)):
                errs.append('LOOK_PRODUCTS.%s 图片不存在: %s' % (k, p))
    # 3. JS 语法
    for f in ('assets/js/onsite-data.js', 'assets/js/onsite-products.js', 'assets/js/onsite.js'):
        r = subprocess.run(['node', '-e',
            'new Function(require("fs").readFileSync(%r,"utf8"))' % os.path.join(SITE, f)],
            capture_output=True, text=True)
        if r.returncode != 0:
            errs.append('%s 语法错误: %s' % (f, (r.stderr or '').strip()[:200]))
    return errs


def sh(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    spec = args[0]
    do_commit = '--commit' in args
    do_push = '--push' in args
    msg = ''
    if do_commit:
        msg = args[args.index('--commit') + 1]

    print('[1/4] 应用拆解 ...')
    rc = apply_case.main(spec)
    if rc:
        return rc

    print('[2/4] 校验 ...')
    errs = validate()
    if errs:
        print('  校验未通过：')
        for e in errs[:30]:
            print('    X %s' % e)
        return 2
    print('  校验通过（引用键 / 图片路径 / JS 语法）')

    if do_commit:
        print('[3/4] 提交 ...')
        spec_rel = os.path.relpath(os.path.abspath(spec), SITE).replace('\\', '/')
        files = ['assets/js/onsite-data.js', 'assets/js/onsite-products.js',
                 spec_rel, 'tools/material_alias.json', 'tools/material_matcher.py',
                 'tools/missing-materials.md']
        r = sh('git add %s' % ' '.join(files), cwd=SITE)
        r = sh('git commit -m %s' % json.dumps(msg), cwd=SITE)
        print('  ' + (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr).strip() else '  committed')
    else:
        print('[3/4] 跳过提交（加 --commit "msg" 启用）')

    if do_push:
        print('[4/4] 推送并核验线上 ...')
        for i in range(1, 7):
            r = sh('git push origin main', cwd=SITE)
            ls = sh('git ls-remote origin main', cwd=SITE)
            head = sh('git rev-parse HEAD', cwd=SITE).stdout.strip()
            if head and head in (ls.stdout or ''):
                print('  推送成功（第 %d 次尝试）' % i)
                break
            print('  第 %d 次推送失败，重试 ...' % i)
            time.sleep(5)
        time.sleep(40)
        ok = False
        for i in range(1, 7):
            r = sh('curl -s %s/assets/js/onsite-data.js' % LIVE)
            if r.returncode == 0 and 'window.ONSITE_CASES' in (r.stdout or ''):
                ok = True
                print('  线上数据已生效（第 %d 次尝试）' % i)
                break
            time.sleep(25)
        if not ok:
            print('  !! 线上未确认生效，请稍后手动核验')
    else:
        print('[4/4] 跳过推送（加 --push 启用）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
