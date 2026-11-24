# -*- coding: utf-8 -*-
"""Remove the WELLNEED watermark from case-053/054 (gallery + thumb) via texture cloning."""
import os
from PIL import Image, ImageFilter
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = {53:(50,62,240,212), 54:(50,62,250,212)}

def erase(im, box, shift, feather):
    x1,y1,x2,y2 = box; w,h=x2-x1,y2-y1
    src=im.crop((x1,y1+shift,x2,y2+shift))
    yy,xx=np.mgrid[0:h,0:w]
    d=np.minimum.reduce([xx,w-1-xx,yy,h-1-yy]).astype(float)
    ma=(np.clip(d/feather,0,1)*255).astype('uint8')
    mask=Image.fromarray(ma).filter(ImageFilter.GaussianBlur(3))
    out=im.copy(); out.paste(src,(x1,y1),mask)
    return out

def main():
    for n in (53,54):
        for sub,scale in [('gallery',1.0),('gallery/thumb',520/1400)]:
            p=os.path.join(BASE,'assets/img/onsite/%s/case-%03d.jpg'%(sub,n))
            im=Image.open(p).convert('RGB')
            box=tuple(int(round(v*scale)) for v in BOX[n])
            im2=erase(im,box,shift=max(14,int(180*scale)),feather=max(5,int(16*scale)))
            im2.save(p,quality=92)
            a=np.asarray(im2); h,w,_=a.shape
            white=(a[:int(h*0.22),:int(w*0.36)].min(axis=2)>220)
            print('%s 剩余白像素=%d'%(os.path.basename(p),white.sum()))

if __name__=='__main__': main()
