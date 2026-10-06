#!/usr/bin/env python3
"""Smaller pupils for Frank's frames (75% reads calmer and more grown-up than the traced art's): paint each pupil white, then draw a smaller oval that keeps the
original's outer edge (so the gaze is unchanged), clipped to the open eye (never over a lid or the ring)."""
import io, re, numpy as np, cv2, cairosvg
from PIL import Image
from scipy.ndimage import binary_fill_holes, gaussian_filter1d
UP=3
k=lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
def clean(s): return re.sub(r'<metadata>.*?</metadata>','',s,flags=re.S)
def resample(p, step):
    q=np.vstack([p,p[:1]]); d=np.r_[0,np.cumsum(np.hypot(*np.diff(q,axis=0).T))]
    t=np.arange(0,d[-1],step); return np.c_[np.interp(t,d,q[:,0]),np.interp(t,d,q[:,1])]
def path(mask, sigma=1.2):
    cs,_=cv2.findContours(mask.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); d=""
    for c in cs:
        if cv2.contourArea(c)<30: continue
        p=resample(c[:,0,:].astype(float)+0.5,1.0)
        p=np.c_[gaussian_filter1d(p[:,0],sigma,mode='wrap'),gaussian_filter1d(p[:,1],sigma,mode='wrap')]/UP
        p=resample(p,0.8); d+="M"+" L".join(f"{x:.2f} {y:.2f}" for x,y in p)+"Z"
    return d
def eyes_of(svg_text, size):
    im=np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=clean(svg_text).encode(), output_width=size*UP, output_height=size*UP))).convert("RGBA")).astype(int)
    a=im[...,3]>128; black=a&(im[...,:3].max(-1)<90); white=a&(im[...,:3].min(-1)>200)
    H=im.shape[0]; out=[]
    n,l,s,_=cv2.connectedComponentsWithStats(white.astype(np.uint8))
    for i in range(1,n):
        x,y,w,h,ar=s[i]
        if ar<1500*UP*UP/9 or y+h/2>H*0.5: continue          # eye whites only (upper half, big enough)
        W=(l==i)
        closed=binary_fill_holes(cv2.morphologyEx(W.astype(np.uint8),cv2.MORPH_CLOSE,k(10*UP)))
        cand=black&cv2.dilate(closed.astype(np.uint8),k(2*UP)).astype(bool)
        core=cv2.morphologyEx(cand.astype(np.uint8),cv2.MORPH_OPEN,k(6*UP)).astype(bool)     # solid blobs only: not lid lines, not the ring
        P=cand&cv2.dilate(core.astype(np.uint8),k(6*UP)).astype(bool)
        if P.sum()<200: continue
        V=closed|P                                            # the open eye: white plus pupil
        out.append((V,P,closed))
    return out
def smaller(svg_text, size, s, uid="pp"):
    """svg_text: a frame SVG (viewBox 0 0 size size). Returns it with pupils scaled by s."""
    add=""; defs=""
    for e,(V,P,closed) in enumerate(eyes_of(svg_text,size)):
        cs,_=cv2.findContours(P.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=max(cs,key=cv2.contourArea)
        (pcx,pcy),(A,B),ang=cv2.fitEllipse(c)
        ys,xs=np.nonzero(V); E=np.array([xs.mean(),ys.mean()]); pc=np.array([pcx,pcy])
        off=pc-E; dist=np.hypot(*off)
        py,px=np.nonzero(P); pts=np.c_[px,py]
        if dist>4*UP:                                          # a glance: keep the outer edge where it was
            d=off/dist; ext=((pts-pc)@d).max()
            far=pc+d*ext; nc=far-d*ext*s
        else:                                                  # looking ahead: shrink around the centre
            nc=pc
        cid=f"{uid}-eye{e}"
        vpath=path(V)
        defs+=f'<clipPath id="{cid}"><path d="{vpath}"/></clipPath>'
        # paint the old pupil out, soft grey edge included, but only inside the eye's white (the ring stays as traced)
        patch=cv2.dilate(P.astype(np.uint8),k(3*UP)).astype(bool)&cv2.dilate(closed.astype(np.uint8),k(1)).astype(bool)
        add+=(f'<path d="{path(patch)}" fill="#FDFDFC"/>'
              f'<g clip-path="url(#{cid})"><ellipse cx="{nc[0]/UP:.2f}" cy="{nc[1]/UP:.2f}" rx="{A/2*s/UP:.2f}" ry="{B/2*s/UP:.2f}" '
              f'transform="rotate({ang:.1f} {nc[0]/UP:.2f} {nc[1]/UP:.2f})" fill="#121311"/></g>')
    t=clean(svg_text)
    return t.replace("</svg>", f"<defs>{defs}</defs>{add}</svg>",1)


SCALE = 0.75   # not in use: Frank ships with his pupils as traced (frogs/src = frogs/src-traced)

if __name__ == "__main__":
    # frogs/src-traced/ holds the frames exactly as traced; frogs/src/ gets them with smaller pupils.
    # Then run build_frank_sprite.py (and the other builders) as usual.
    import glob, os
    root = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(glob.glob(os.path.join(root, "frogs", "src-traced", "frank-*.svg"))):
        name = os.path.basename(f)
        svg = open(f).read()
        size = float(re.search(r'viewBox="0 0 ([\d.]+)', svg).group(1))
        open(os.path.join(root, "frogs", "src", name), "w").write(smaller(svg, size, SCALE, uid="p" + name[6:8]))
        print(f"  {name}: pupils at {int(SCALE * 100)}%")
