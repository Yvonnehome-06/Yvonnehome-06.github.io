# -*- coding: utf-8 -*-
"""NC-match a query screenshot against onsite gallery cases (PIL+numpy, no cv2)."""
import sys, glob, os
import numpy as np
from PIL import Image

def gray(img, size):
    im = img.convert('L').resize(size, Image.LANCZOS)
    return np.asarray(im, dtype=np.float64) / 255.0

def nc(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a*a).sum() * (b*b).sum())
    return float((a*b).sum() / d) if d > 0 else 0.0

def center_crop(img, frac=0.10):
    w, h = img.size
    dx, dy = int(w*frac), int(h*frac)
    return img.crop((dx, dy, w-dx, h-dy))

def main(query_path, gallery_dir):
    q = center_crop(Image.open(query_path))
    scores = []
    for p in sorted(glob.glob(os.path.join(gallery_dir, 'case-*.jpg'))):
        g = center_crop(Image.open(p))
        best = 0.0
        # multi-scale: resize gallery to query aspect variants
        for qw, qh in [(112, 112), (96, 128), (128, 96)]:
            qa = gray(q, (qw, qh))
            for scale in (0.85, 1.0, 1.15):
                gw, gh = int(qw*scale), int(qh*scale)
                ga_img = g.convert('L').resize((gw, gh), Image.LANCZOS)
                # center-crop back to query shape then compare
                dx, dy = (gw-qw)//2, (gh-qh)//2
                dx, dy = max(dx, 0), max(dy, 0)
                cropped = ga_img.crop((dx, dy, min(dx+qw, gw), min(dy+qh, gh))) \
                    .resize((qw, qh), Image.LANCZOS)
                ga = np.asarray(cropped, dtype=np.float64) / 255.0
                best = max(best, nc(qa, ga))
        scores.append((best, os.path.basename(p)))
    scores.sort(reverse=True)
    for s, name in scores[:6]:
        print(f'{s:.4f}  {name}')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
