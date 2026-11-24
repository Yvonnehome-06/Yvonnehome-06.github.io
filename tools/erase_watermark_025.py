# -*- coding: utf-8 -*-
"""Remove the faint 'AI生成' watermark from case-025 top-left via shifted texture clone + median suppression."""
import os
from PIL import Image, ImageFilter
import numpy as np
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# box + shift in FULL-res (1050x1400) coordinates
BOX = (8, 7, 70, 43)
SHIFT = 46

def erase(im, box, shift):
    x1,y1,x2,y2 = box
    w,h = x2-x1, y2-y1
    patch = im.crop((x1, y1+shift, x2, y2+shift))
    yy,xx = np.mgrid[0:h,0:w]
    d = np.minimum.reduce([xx,w-1-xx,yy,h-1-yy]).astype(float)
    ma = (np.clip((d-2)/8,0,1)*255).astype('uint8')
    mask = Image.fromarray(ma).filter(ImageFilter.GaussianBlur(2))
    out = im.copy(); out.paste(patch,(x1,y1),mask)
    b = np.array(out).astype(float)
    roi = b[y1:y2,x1:x2]
    med = np.array(Image.fromarray(roi.astype('uint8')).filter(ImageFilter.MedianFilter(5))).astype(float)
    lum = roi.mean(axis=2); ml = med.mean(axis=2)
    alpha = np.clip(((lum-ml)-6)/16,0,1)*0.9
    roi2 = roi*(1-alpha[...,None]) + med*alpha[...,None]
    b[y1:y2,x1:x2] = roi2
    return Image.fromarray(np.clip(b,0,255).astype('uint8'))

def main():
    for sub,scale in [('gallery',1.0),('gallery/thumb',390/1050)]:
        p=os.path.join(BASE,'assets/img/onsite/%s/case-025.jpg'%sub)
        im=Image.open(p).convert('RGB')
        box=tuple(int(round(v*scale)) for v in BOX)
        shift=max(1,int(round(SHIFT*scale)))
        out=erase(im,box,shift)
        out.save(p,quality=94)
        print(sub,'processed',im.size,'->',out.size,'box',box,'shift',shift)

if __name__=='__main__': main()
