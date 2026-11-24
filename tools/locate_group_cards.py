# -*- coding: utf-8 -*-
"""Locate each card in the 16 group screenshots to a gallery case via grayscale NC.

Cards in the screenshots are the site's thumb images (520x520) with a caption
bar. Column counts fixed per screenshot from bobby's grouping. We compare the
card's photo region against both main images and thumbs, trying several crop
heights, and report the best case + score.
"""
import sys, glob, os
import numpy as np
from PIL import Image

GAL = 'assets/img/onsite/gallery'
THUMB = os.path.join(GAL, 'thumb')

COLS = {
    '305db914': 2, '535fb1e5': 2, 'e15b4818': 3, '3c4406a5': 2,
    '441f6b8b': 2, '2b291e94': 3, '8ce81176': 3, '2bff83b4': 1,
    'f3fefac2': 2, '005638ab': 1, '5ab35e23': 1, '5b86510f': 2,
    '65bb1d26': 1, '58a2abca': 2, '93bec03d': 1, '40543d57': 2,
}

def gray(img, size):
    return np.asarray(img.convert('L').resize(size, Image.LANCZOS), dtype=np.float64) / 255.0

def nc(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a*a).sum() * (b*b).sum())
    return float((a*b).sum() / d) if d > 0 else 0.0

SIZES = [(96, 96), (80, 112), (112, 80)]
CACHE = {}
for d, tag in [(GAL, 'm'), (THUMB, 't')]:
    for p in sorted(glob.glob(os.path.join(d, 'case-*.jpg'))):
        name = os.path.basename(p)
        CACHE[(tag, name)] = {sz: gray(Image.open(p), sz) for sz in SIZES}

def match(query):
    best = (0.0, None, None)
    for qw, qh in SIZES:
        qa = gray(query, (qw, qh))
        for (tag, name), cache in CACHE.items():
            s = nc(qa, cache[(qw, qh)])
            if s > best[0]:
                best = (s, name, tag)
    return best

def token(path):
    b = os.path.basename(path)
    return next((t for t in COLS if t in b), None)

if __name__ == '__main__':
    for path in sys.argv[1:]:
        tk = token(path)
        ncol = COLS[tk] if tk else 1
        img = Image.open(path)
        w, h = img.size
        print('\n=== %s (%dx%d, %d卡) ===' % (tk or os.path.basename(path), w, h, ncol))
        for k in range(ncol):
            x0 = int(k*w/ncol); x1 = int((k+1)*w/ncol)
            card_best = (0.0, None, None, 0.0)
            for frac in (0.55, 0.62, 0.70, 0.78, 0.86, 0.94, 1.0):
                card = img.crop((x0, 0, x1, int(h*frac)))
                s, name, tag = match(card)
                if s > card_best[0]:
                    card_best = (s, name, tag, frac)
            print('  卡%d -> %s  %.4f  [%s, 裁%.2f]' % (
                k+1, card_best[1] or '?', card_best[0], card_best[2] or '?', card_best[3]))
