from PIL import Image, ImageFilter, ImageEnhance, ImageChops
import numpy as np

SRC   = 'assets/a58-255e1ed2a1.jpg'
MASK  = 'assets/hero-skyline-cutout.webp'
base  = Image.open(SRC).convert('RGB')
W, H  = base.size                       # 4272 x 2856
print('base', W, H)

# ---- refined, full-res alpha for the skyline silhouette -------------------
m  = Image.open(MASK).convert('RGBA').split()[3].resize((W, H), Image.LANCZOS)
a  = np.asarray(m).astype(np.float32) / 255.0
# firm up the edge: remap 0.30..0.70 -> 0..1 (keeps ~1.5px feather, kills the
# 14%-of-frame semi-transparent haze that was ghosting over the backdrop)
a  = np.clip((a - 0.30) / 0.40, 0.0, 1.0)
WATER = int(0.632 * H)                  # buildings meet water here
a[WATER:, :] = 1.0                      # extend silhouette to the bottom so no
                                        # gap can open under it when planes split
alpha = Image.fromarray((a * 255).astype(np.uint8))

def clarity(img, amt=42):
    return img.filter(ImageFilter.UnsharpMask(radius=2.0, percent=amt, threshold=3))

def out(img, name, width, q, alpha_ch=None):
    h = round(img.size[1] * width / img.size[0])
    im = img.resize((width, h), Image.LANCZOS)
    if alpha_ch is not None:
        al = alpha_ch.resize((width, h), Image.LANCZOS)
        im = im.convert('RGB'); im.putalpha(al)
    im.save(f'assets/{name}', 'WEBP', quality=q, method=6)
    import os; print(f'  {name:26s} {width}x{h}  {os.path.getsize("assets/"+name)/1024:.0f} KB')

# ---- FAR: sky / atmosphere. Blur BAKED IN -> zero runtime CSS filter ------
far = base.resize((2400, round(2400 * H / W)), Image.LANCZOS)
far = far.filter(ImageFilter.GaussianBlur(3.4))
far = ImageEnhance.Color(far).enhance(0.86)
far = ImageEnhance.Brightness(far).enhance(0.90)
out(far, 'hero-far.webp', 2400, 80)

# ---- MID: the skyline itself. Full-res, sharp, clarity-boosted -----------
out(clarity(base, 46), 'hero-mid.webp', 3200, 86, alpha_ch=alpha)

# ---- NEAR: harbour foreground. Seam sits in smooth open water ------------
seam, feather = int(0.70 * H), int(0.045 * H)
y  = np.arange(H, dtype=np.float32)[:, None]
na = np.clip((y - (seam - feather)) / feather, 0.0, 1.0)
na = np.repeat(na, W, axis=1)
out(clarity(base, 34), 'hero-near.webp', 3200, 86,
    alpha_ch=Image.fromarray((na * 255).astype(np.uint8)))
