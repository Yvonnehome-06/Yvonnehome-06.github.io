# -*- coding: utf-8 -*-
"""
材质匹配引擎 —— 把中文花材/叶材清单自动对到图库 SKU。

用法（作为模块）：
    from material_matcher import Matcher
    m = Matcher()
    res = m.match_group([{"cn":"白绣球","role":"主花"}, ...])
    # res -> {"items":[{"k":"hyd-white","role":"...","n":"126-Petal Hydrangea - White","f":"..."}], "missing":[...]}

设计目标：**不需要人工看图确认形态**。
- 优先查别名词表 tools/material_alias.json（人工核实过的映射）
- 未命中则回落到 flowers-data.js / decor-data.js 的中文名文本匹配
- 命中新 SKU 时自动补进 window.LOOK_PRODUCTS（含英文名，取自图库记录本身）
"""
import json, os, re, sys, unicodedata

def _resolve_base():
    """定位站点根目录。

    兼容两种放置位置：
      A) 仓库内  <repo>/tools/material_matcher.py      -> SITE = <repo>
      B) 仓库外  <workspace>/tools/material_matcher.py   -> SITE = <workspace>/homegoods-b2b-site
    """
    here = os.path.dirname(os.path.abspath(__file__))
    # A) 上一级就是站点根（含 assets/js）
    parent = os.path.dirname(here)
    if os.path.isdir(os.path.join(parent, 'assets', 'js')):
        return parent, here
    # B) 上一级是工作区，再下一级是站点
    cand = os.path.join(parent, 'homegoods-b2b-site')
    if os.path.isdir(os.path.join(cand, 'assets', 'js')):
        return cand, here
    return parent, here


BASE, TOOLS = _resolve_base()
SITE = BASE

# ---------------- 颜色词（用于从材料名里剥离颜色 + 二次筛选） ----------------
COLORS = [
    ('香槟', 'champagne'), ('酒红', 'burgundy'), ('深绿', 'dg'), ('浅绿', 'lg'),
    ('浅紫', 'lp'), ('深紫', 'dp'), ('宝蓝', 'blue'), ('雾蓝', 'blue'),
    ('灰', 'grey'), ('白', 'white'), ('粉', 'pink'), ('紫', 'purple'),
    ('黄', 'yellow'), ('绿', 'green'), ('红', 'red'), ('蓝', 'blue'),
    ('桔', 'orange'), ('橙', 'orange'), ('米', 'beige'), ('裸', 'beige'),
]

# 常见材质词 -> 英文词根（用于生成字典键 & 英文名兜底）
STEM_EN = {
    '绣球': 'Hydrangea', '玫瑰': 'Rose', '洋牡丹': 'Ranunculus', '花毛茛': 'Ranunculus',
    '牡丹': 'Peony', '芍药': 'Peony', '百合': 'Lily', '兰花': 'Orchid', '蝴蝶兰': 'Phalaenopsis',
    '薰衣草': 'Lavender', '樱花': 'Cherry Blossom', '满天星': "Baby's Breath",
    '尤加利': 'Eucalyptus', '四叶梅': 'Four-Leaf Plum', '老人须': 'Spanish Moss',
    '芦苇': 'Reed', '藤': 'Garland', '乒乓菊': 'Pompon Mum', '球菊': 'Ball Chrysanthemum',
    '向日葵': 'Sunflower', '玉兰': 'Magnolia', '掌': 'Anthurium', '石竹': 'Carnation',
    '空气草': 'Air Grass', '雪柳': 'Snow Willow', '吊米': 'Hanging Rice Grass',
    '情人泪': 'Valentine Tears', '天门冬': 'Asparagus', '文竹': 'Asparagus Fern',
    '马尾松': 'Horsetail Pine', '松针': 'Pine Needle', '蓬莱松': 'Pine Spray',
    '千层金': 'Layered Gold', '散尾': 'Areca Palm', '米兰果': 'Milane Berry',
    '小雏菊': 'Mini Daisy', '勿忘我': 'Forget-Me-Not', '霞草': 'Statice',
    '情人草': 'Statice', '云朵': 'Cloud', '雪融花': 'Snowmelt', '千丝万缕': 'Silk Thread',
    '小圆尤加利': 'Mini Round Eucalyptus', '苹果叶': 'Apple Leaf', '叮叮果': 'Berry Branch',
    '芦荀草': 'Asparagus Fern', '空气草': 'Air Grass', '双星草': 'Twin-Star Grass',
    '富贵竹': 'Lucky Bamboo', '龟背竹': 'Monstera', '常春藤': 'Ivy', '苔藓': 'Moss',
    '铃兰': 'Lily of the Valley', '栀子': 'Gardenia', '丁香': 'Lilac', '绣线菊': 'Spiraea',
    '喷泉草': 'Fountain Grass', '观赏草': 'Ornamental Grass', '橄榄枝': 'Olive Branch',
    '洋桔梗': 'Lisianthus', '康乃馨': 'Carnation', '扶郎': 'Gerbera',
}

# 装饰品类中文 -> 英文（decor-data.js 无中文名，只有 cat/title）
DECOR_CAT_CN = {
    'candelabra': ['烛台', '烛架', '烛灯架'], 'candles': ['蜡烛', '烛'],
    'runners': ['桌旗', '餐垫', '桌饰带'], 'tablecloths': ['桌布'],
    'chair': ['椅背花', '椅饰'], 'confetti': ['礼花', '彩带礼炮'],
    'dessert': ['甜品台', '蛋糕台'], 'frames': ['花架', '框架', '支架'],
    'pots': ['花盆', '花器', '柱盆'], 'vases': ['花瓶', '花器', '瓶'],
    'accents': ['装饰', '配饰'], 'holiday': ['圣诞', '节日'],
    'drapery': ['布幔', '幔布', '垂幔', '帷幕'], 'sheers': ['纱帘', '纱幔'],
    'jute': ['麻绳', '黄麻'],
}

# 词根匹配时剥离的通用后缀
TAIL_WORDS = ['叶', '枝', '条', '花', '草', '球', '串', '球菊', '蕨']

# 同物异名：材料名 -> 图库中文名（当字面检索不到时按此改写再检索）
SYNONYM_CN = {
    '桉叶': ['桉树叶'],
    '桉树叶': ['桉树叶'],
    '龟背竹': ['镂空龟背叶', '超大型龟背'],
    '龟背叶': ['镂空龟背叶', '超大型龟背'],
    '绿萝': ['常春藤', '龟背'],
    '常春藤': ['常春藤'],
    '绿毛球': ['石竹'],
    '霞草': ['情人草'],
    '喷泉草': ['空气草'],
    '观赏草': ['空气草'],
    '绣线菊': ['雪柳'],
    '小手球': ['雪柳'],
    '情人泪': ['情人泪'],
    '柔丽丝': ['吊米'],
    '橄榄枝': ['米兰果'],
    '绿灵草': ['狐尾'],
    '垂吊柔丝': ['狐尾'],
    '长垂松': ['狐尾'],
    '大羽叶': ['散尾'],
    '白小菊': ['小雏菊'],
}


def _read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def _load_js_object(path):
    """解析 `window.X = {...}` 或 `window.X = [...]` 形式的 JS 赋值。"""
    s = _read(path)
    i = min(x for x in (s.find('{'), s.find('[')) if x >= 0)
    return json.JSONDecoder().raw_decode(s[i:])[0]


def _norm(s):
    """归一化中文/英文串：小写、去空格、去括号内容、去修饰后缀。"""
    s = (s or '').strip().lower()
    s = re.sub(r'[（(].*?[)）]', '', s)
    s = re.sub(r'[\s\-_/·、,，]', '', s)
    return s


class Matcher:
    def __init__(self):
        self.alias = json.loads(_read(os.path.join(TOOLS, 'material_alias.json')))
        self.terms = self.alias.get('terms', {})
        self.by_key = self.alias.get('by_key', {})

        # 图库全量条目（花材 + 装饰），统一成 {key, n, cn, c, s, t, f}
        self.look = _load_js_object(os.path.join(SITE, 'assets/js/onsite-products.js'))
        self.flowers = _load_js_object(os.path.join(SITE, 'assets/js/flowers-data.js'))
        self.decor = self._load_decor()

        # 图库中文名 -> 候选花材记录索引
        self.cn_index = {}
        for d in self.flowers:
            cn = (d.get('cn') or '').strip()
            if cn:
                self.cn_index.setdefault(cn, []).append(d)

        # 中文名（去颜色后）-> 候选记录
        self.stem_index = {}
        for d in self.flowers:
            cn = (d.get('cn') or '').strip()
            if not cn:
                continue
            stem = self._strip_color(cn)
            self.stem_index.setdefault(stem, []).append(d)

    def _load_decor(self):
        """decor-data.js 是 JS 字面量（无引号键），需先补引号再解析。"""
        p = os.path.join(SITE, 'assets/js/decor-data.js')
        s = _read(p)
        body = s[s.find('['):]
        body = re.sub(r'([{,]\s*)([a-zA-Z_$][\w$]*)\s*:', r'\1"\2":', body)
        body = re.sub(r',\s*\]', ']', body)
        try:
            return json.JSONDecoder().raw_decode(body)[0]
        except Exception:
            return []

    def _decor_records(self):
        """装饰记录 -> 与花材一致的字段形状。"""
        out = []
        for d in self.decor:
            if not isinstance(d, dict):
                continue
            f = d.get('file') or d.get('img') or ''
            if not f:
                continue
            out.append({
                'cat': d.get('cat') or 'decor',
                'name': d.get('title') or '',
                'cn': '',
                'sku': '',
                'file': f,
                'thumb': f,
                'desc': d.get('desc') or '',
                '_decor': True,
            })
        return out

    # ---------- 工具 ----------
    @staticmethod
    def _strip_color(cn):
        """从中文名剥离颜色词，得到材质词根。"""
        s = cn
        for zh, _ in sorted(COLORS, key=lambda x: -len(x[0])):
            s = s.replace(zh, '')
        return s.strip('-_ ')

    @staticmethod
    def _split_color(cn):
        """从中文名抽出色泽键（用于在同名多色中挑对）。"""
        for zh, en in COLORS:
            if zh in cn:
                return en
        return ''

    @staticmethod
    def _slug(cn, en=''):
        """中文名 -> 字典键（ASCII slug）。优先用图库英文名，退回 STEM_EN 词表。"""
        base = None
        if en:
            base = en
        else:
            for zh, e in STEM_EN.items():
                if zh in cn:
                    base = e
                    break
        if base is None:
            base = re.sub(r'[^A-Za-z0-9]+', '', cn) or 'item'
        key = base.lower().replace(' ', '-').replace("'", '')
        key = re.sub(r'-+', '-', key).strip('-')
        return key

    def _color_suffix(self, color_en):
        if not color_en:
            return ''
        return '-' + color_en

    # ---------- 匹配 ----------
    def match_one(self, cn, role=''):
        """返回 (dict|None, reason)。dict 含 k/n/cn/f/t 或新增 SKU 信息。"""
        cn = (cn or '').strip()
        if not cn:
            return None, 'empty'

        # 1) 别名词表精确命中（人工核实过的，最可靠）
        if cn in self.terms:
            keys = self.terms[cn]
            got = [k for k in keys if k in self.look]
            if got:
                out = []
                for k in got:
                    p = dict(self.look[k])
                    p['k'] = k
                    p['role'] = role
                    out.append(p)
                return (out if len(out) == 1 else out), None

        # 2) 图库中文名精确命中（spec cn 本就是图库真实名时最权威，
        #    必须先于别名剥色词根，否则无色别名会抢走有色精确名）
        if cn in self.cn_index:
            rec = self.cn_index[cn][0]
            return [self._rec_to_item(rec, role)], None

        # 3) 别名词表按"剥离颜色后的词根"命中
        stem = self._strip_color(cn)
        color = self._split_color(cn)
        for term, keys in self.terms.items():
            if _norm(self._strip_color(term)) == _norm(stem) and _norm(term) != _norm(cn):
                tcolor = self._split_color(term)
                if tcolor and color and tcolor != color:
                    continue
                got = [k for k in keys if k in self.look]
                if got:
                    out = []
                    for k in got:
                        p = dict(self.look[k])
                        p['k'] = k
                        p['role'] = role
                        out.append(p)
                    return out, None

        # 3b) 装饰品类命中（按类别中文别名）
        if '花环' in cn or 'wreath' in cn.lower():
            for d in self._decor_records():
                if d['cat'] in ('wreaths', 'frames'):
                    return [self._rec_to_item(d, role)], None

        # 4) 图库词根命中（按颜色挑）
        cands = self.stem_index.get(stem, [])
        if not cands:
            # 4b) 去掉尾部修饰词后再试（如 "126瓣绣球" -> "绣球"）
            m = re.match(r'^(\d+)(瓣|头|枝|朵)', stem)
            if m:
                cands = self.stem_index.get(stem[m.end():], [])
        if not cands:
            # 4c) 剥离通用后缀（"尤加利叶" -> "尤加利"）
            for t in TAIL_WORDS:
                if stem.endswith(t) and len(stem) > len(t):
                    cands = self.stem_index.get(stem[:-len(t)], [])
                    if cands:
                        break
        if cands:
            pick = None
            if color:
                for d in cands:
                    if self._split_color(d.get('cn') or '') == color:
                        pick = d
                        break
            if pick is None:
                pick = cands[0]
            return [self._rec_to_item(pick, role)], None

        # 5) 模糊：图库任一中文名包含该词根（花材 + 装饰）
        hit = None
        allrec = list(self.flowers) + self._decor_records()
        for d in allrec:
            dcn = (d.get('cn') or '')
            if stem and stem in dcn:
                if color and self._split_color(dcn) != color:
                    continue
                hit = d
                break
        if hit:
            return [self._rec_to_item(hit, role)], None

        # 5b) 双向前缀容错：材料名是图库名的前缀或反之
        #      "龟背竹" vs "镂空龟背叶" / "桉叶" vs "桉树叶"
        #      dcn 至少 3 字，防短名假命中（"波斯" ≠ "波斯顿蕨"）
        for d in allrec:
            dcn = (d.get('cn') or '').strip()
            if not dcn or not stem:
                continue
            if (stem in dcn and len(stem) >= 3) or (dcn in stem and len(dcn) >= 3):
                if color and self._split_color(dcn) != color:
                    continue
                hit = d
                break
        if hit:
            return [self._rec_to_item(hit, role)], None

        # 5c) 同物异名改写后再检索（龟背竹 -> 镂空龟背叶 / 桉叶 -> 桉树叶）
        for alt in SYNONYM_CN.get(cn, []):
            for d in allrec:
                dcn = (d.get('cn') or '').strip()
                if alt and alt in dcn:
                    dc = self._split_color(dcn)
                    if color and dc and dc != color:
                        continue
                    return [self._rec_to_item(d, role)], None

        # 6) 装饰类别中文别名命中（烛台/桌布/花瓶/布幔/纱帘/麻绳...）
        for cat, aliases in DECOR_CAT_CN.items():
            if cn in aliases:
                for d in self._decor_records():
                    if d['cat'] == cat:
                        return [self._rec_to_item(d, role)], None

        return None, 'not-found'

    def _rec_to_item(self, rec, role):
        """图库记录 -> 字典条目（英文名直接取图库记录本身）"""
        cn = rec.get('cn') or ''
        en = rec.get('name') or ''
        f = rec.get('file') or ''
        # 0) 已有同款（cn 或图片路径相同）-> 直接复用现有关键，不重复建键
        for k, v in self.look.items():
            if (cn and v.get('cn') == cn) or (f and v.get('f') == f):
                return {
                    'k': k, 'role': role,
                    'n': v.get('n') or en, 'cn': v.get('cn') or cn,
                    'c': v.get('c') or '', 's': v.get('s') or '',
                    't': v.get('t') or f, 'f': v.get('f') or f,
                    '_new': False, '_rec': rec,
                }
        key = self._slug(cn, en)
        # 避免键名退化（以标点结尾）
        if not key or key.endswith('-'):
            key = (key or 'item').rstrip('-') or 'item'
        if key in self.look and self.look[key].get('cn') != cn:
            suf = re.sub(r'[^a-z0-9]+', '', _norm(cn))[:6]
            if not suf:
                # 中文名归一化后无 ASCII 可用（如"彩玉叶"）——退回图片文件名做区分后缀，
                # 防止同英文名不同变体（彩玉叶/彩玉叶绿黄）退化成同一个键互相覆盖
                stem = os.path.splitext(os.path.basename(f or rec.get('thumb') or ''))[0]
                suf = re.sub(r'[^a-z0-9]+', '', stem.lower())[:10] or 'var'
            key = key + '-' + suf
            while key in self.look and self.look[key].get('cn') != cn:
                key += 'x'
        return {
            'k': key,
            'role': role,
            'n': en or cn,
            'cn': cn,
            'c': rec.get('cat') or rec.get('catCn') or '',
            's': rec.get('sku') or '',
            't': rec.get('thumb') or rec.get('file') or '',
            'f': rec.get('file') or '',
            '_new': key not in self.look,
            '_rec': rec,
        }

    def match_group(self, items):
        """items: [{cn, role}] -> (matched_items, missing_cn_list)"""
        matched, missing = [], []
        for it in items:
            cn = it.get('cn') or it.get('name') or ''
            role = it.get('role') or ''
            res, reason = self.match_one(cn, role)
            if res is None:
                missing.append({'cn': cn, 'reason': reason})
            else:
                matched.extend(res if isinstance(res, list) else [res])
        return matched, missing

    def ensure_in_dict(self, items):
        """把匹配到的新 SKU 补进 self.look，返回新增列表。"""
        added = []
        for it in items:
            if it.get('_new') and it['k'] not in self.look:
                rec = it['_rec']
                self.look[it['k']] = {
                    'n': rec.get('name') or it['cn'],
                    'cn': rec.get('cn') or '',
                    'c': rec.get('cat') or '',
                    's': rec.get('sku') or '',
                    't': rec.get('thumb') or rec.get('file') or '',
                    'f': rec.get('file') or '',
                }
                added.append(it['k'])
        return added

    def lookup_key(self, k):
        return self.look.get(k)


if __name__ == '__main__':
    # CLI: python tools/material_matcher.py 白绣球 洋牡丹 "高山羊齿"
    m = Matcher()
    if len(sys.argv) > 1:
        for term in sys.argv[1:]:
            r, why = m.match_one(term)
            if r is None:
                print('MISS  %-12s (%s)' % (term, why))
            else:
                for x in (r if isinstance(r, list) else [r]):
                    print('HIT   %-12s -> %-18s %s%s' % (
                        term, x['k'], x['n'],
                        '   [NEW]' if x.get('_new') else ''))
