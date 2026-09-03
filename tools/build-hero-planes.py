"""Hero depth planes for index.html (v6).

Cuts three planes from the 4272px original and grades them into a real
aerial-perspective ladder. Two rules govern this file:

  1. Sharpness is non-negotiable on MID and NEAR. All softening lives on FAR,
     which is sky and distant haze, where softness is what the eye expects.
  2. No runtime CSS filters. Everything here is baked, so the browser only
     ever composites translate3d. See feedback_no_runtime_css_filters...

v6 changes over v5, both aimed at making the STILL image read as layered:
  - NEAR's seam moved up from 0.70 to the waterfront strip (0.545-0.605).
    Measured detail energy: waterfront 11.56 vs open water 2.67. v5's near
    plane was featureless water, so its motion was literally untrackable.
  - Added the grade ladder + horizon glow + base shadow below. v5 graded all
    three planes identically, which is why it was sharp but flat.
"""
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np, os

SRC, MASK = 'assets/a58-255e1ed2a1.jpg', 'assets/hero-skyline-cutout.webp'
base = Image.open(SRC).convert('RGB')
W, H = base.size
WATER = 0.632                      # buildings meet water
NEAR_FEATHER, NEAR_SOLID = 0.545, 0.605   # seam sits in the textured waterfront

# ---------- grading helpers (all operate on float 0..1 RGB) ----------------
def arr(im):  return np.asarray(im).astype(np.float32) / 255.0
def img(a):   return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

def contrast(a, k, pivot=0.5):   return (a - pivot) * k + pivot
def lift(a, amt):                return a + amt * (1.0 - a)      # haze lifts blacks
def warm(a, amt):
    a = a.copy(); a[..., 0] *= 1 + amt; a[..., 2] *= 1 - amt; return a
def clarity(im, amt):
    return im.filter(ImageFilter.UnsharpMask(radius=2.0, percent=amt, threshold=3))

def save(im, name, width, q, alpha=None):
    h = round(im.size[1] * width / im.size[0])
    out = im.resize((width, h), Image.LANCZOS)
    if alpha is not None:
        out = out.convert('RGB'); out.putalpha(alpha.resize((width, h), Image.LANCZOS))
    out.save(f'assets/{name}', 'WEBP', quality=q, method=6)
    print(f'  {name:22s} {width}x{h}  {os.path.getsize("assets/"+name)/1024:>5.0f} KB')

# ---------- silhouette alpha, refined to full resolution -------------------
m = Image.open(MASK).convert('RGBA').split()[3].resize((W, H), Image.LANCZOS)
a = np.clip((np.asarray(m).astype(np.float32) / 255.0 - 0.30) / 0.40, 0, 1)
a[int(WATER * H):, :] = 1.0        # extend down so no gap opens under the skyline
mid_alpha = img(a[..., None].repeat(3, 2))[:, :].convert('L') if False else \
            Image.fromarray((a * 255).astype(np.uint8))

y = np.arange(H, dtype=np.float32)[:, None] / H

# ---------- FAR: sky + distant haze. The only soft plane. -----------------
far = arr(base)
far = lift(far, 0.24)                       # aerial perspective: distance washes out
far = contrast(far, 0.74)
# horizon glow - haze is brightest where it stacks up behind the skyline, and
# this is what lifts a dark silhouette off the sky in a STILL frame
glow = np.exp(-((y - 0.50) ** 2) / (2 * 0.16 ** 2)) * 0.20
far = far * (1 + glow[..., None])
far = arr(ImageEnhance.Color(img(far)).enhance(0.60))
far = img(far * 1.02)
far = far.resize((2400, round(2400 * H / W)), Image.LANCZOS)
save(far.filter(ImageFilter.GaussianBlur(3.4)), 'hero-far.webp', 2400, 80)

# ---------- MID: the skyline, with depth graded ACROSS it -----------------
# The tower mass is one plane, so grading it uniformly makes it read as a flat
# cutout no matter how the planes move. Real depth inside a skyline comes from
# aerial perspective: distant clusters are lighter, flatter and less saturated.
#
# A per-pixel haze map is far too noisy to cut planes from (tested - it speckles
# badly in shadowed building cores). But collapsed to ONE VALUE PER COLUMN and
# smoothed hard, the same signal is stable, and applied as a continuous grade it
# needs no mask and can produce no seam. Distance in a broadside skyline varies
# with x - which part of the city you are looking at - not within one tower.
import cv2
sm = cv2.resize(np.asarray(base), (W // 4, H // 4))
g  = cv2.cvtColor(sm, cv2.COLOR_RGB2GRAY).astype(np.float32)
lab = cv2.cvtColor(sm, cv2.COLOR_RGB2LAB).astype(np.float32)
sat = cv2.cvtColor(sm, cv2.COLOR_RGB2HSV).astype(np.float32)[:, :, 1]
detail = cv2.GaussianBlur(np.abs(g - cv2.GaussianBlur(g, (0, 0), 9)), (0, 0), 15)

def nrm(v):
    lo, hi = np.percentile(v, 2), np.percentile(v, 98)
    return np.clip((v - lo) / (hi - lo + 1e-6), 0, 1)

band = np.asarray(m.resize((W // 4, H // 4))) > 140
band[int(WATER * H / 4):, :] = False                     # buildings only
haze = 0.40 * nrm(lab[:, :, 0]) + 0.25 * (1 - nrm(sat)) + 0.35 * (1 - nrm(detail))

col = np.array([haze[band[:, x], x].mean() if band[:, x].any() else np.nan
                for x in range(W // 4)])
idx = np.arange(len(col))
col = np.interp(idx, idx[~np.isnan(col)], col[~np.isnan(col)])   # fill sky gaps
col = cv2.GaussianBlur(col.reshape(1, -1), (0, 0), 26).ravel()   # kill all speckle
col = nrm(col)
depth = np.interp(np.linspace(0, len(col) - 1, W), idx, col)[None, :]  # 0 near .. 1 far
print(f'  skyline depth ramp: near={depth.min():.2f} far={depth.max():.2f}')

mid = arr(clarity(base, 46))
mid = contrast(mid, 1.10 - 0.26 * depth[..., None])      # distance flattens contrast
mid = lift(mid, 0.03 + 0.20 * depth[..., None])          # and washes it toward haze
mid = mid * (1 + 0.06 * depth[..., None])                # and lifts it
sat_mix = 1.0 - 0.42 * depth[..., None]                  # and drains colour
grey = mid.mean(axis=2, keepdims=True)
mid = grey + (mid - grey) * sat_mix
# base shadow: towers sink into shade at the waterline so the near plane reads
# as standing in front of them rather than pasted onto them
shade = np.clip((y - 0.40) / (WATER - 0.40), 0, 1) ** 1.6 * 0.20
mid = mid * (1 - shade[..., None])
save(img(mid), 'hero-mid.webp', 3200, 86, alpha=mid_alpha)

# ---------- NEAR: waterfront + harbour. Deepest contrast = closest ---------
near = arr(clarity(base, 40))
near = contrast(near, 1.20)
near = near * 0.90
near = warm(near, 0.012)
near = arr(ImageEnhance.Color(img(near)).enhance(1.10))
na = np.clip((y - NEAR_FEATHER) / (NEAR_SOLID - NEAR_FEATHER), 0, 1)
na = (na ** 1.4).repeat(W, axis=1)          # long, soft handover into the strip
save(img(near), 'hero-near.webp', 3200, 86,
     alpha=Image.fromarray((na * 255).astype(np.uint8)))
