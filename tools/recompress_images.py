# -*- coding: utf-8 -*-
"""Recompress oversized JPGs (>300KB) at quality 82 — dimensions unchanged.
Idempotent: already-small files untouched. Run from site root:
  python tools/recompress_images.py [--dry]
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THRESH = 300 * 1024
Q = 82
dry = "--dry" in sys.argv

changed = saved = 0
for dirpath, _, files in os.walk(os.path.join(ROOT, "assets", "img")):
    for f in files:
        if not f.lower().endswith(".jpg"):
            continue
        fp = os.path.join(dirpath, f)
        sz = os.path.getsize(fp)
        if sz <= THRESH:
            continue
        im = Image.open(fp)
        if im.mode != "RGB":
            im = im.convert("RGB")
        tmp = fp + ".tmp"
        im.save(tmp, "JPEG", quality=Q, optimize=True, progressive=True)
        nsz = os.path.getsize(tmp)
        if nsz < sz * 0.9:  # only keep if real saving
            if not dry:
                os.replace(tmp, fp)
            changed += 1
            saved += sz - nsz
            print(f"{sz//1024:5d}KB -> {nsz//1024:5d}KB  {os.path.relpath(fp, ROOT)}")
        else:
            os.remove(tmp)

print(f"\n{'[DRY] ' if dry else ''}recompressed: {changed} files, saved {saved/1024/1024:.1f} MB")
