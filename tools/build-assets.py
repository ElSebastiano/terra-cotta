"""
Asset-Build fuer die Website TERRA COTTA - das Keramikatelier von Ursula Rhensius.

Erzeugt aus dem vorhandenen Hero-Referenzbild die Bild-Ebenen der 2.5D-Hero-
Section, optimiert die lizenzfreien Sektionsfotos zu WebP und leitet aus dem
echten Firmenlogo ein Favicon ab.

Aufruf:  python tools/build-assets.py
Voraussetzung:  pip install Pillow
"""

import os
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_HERO = os.path.join(ROOT, "hero-referenz-terra-cotta-konstanz.png")
SRC_LOGO = os.path.join(ROOT, "tools", "raw", "logo-original.jpg")
RAW = os.path.join(ROOT, "tools", "raw")
OUT = os.path.join(ROOT, "assets", "img")


def save(im, name, quality=74, alpha=False):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "%s.webp" % name)
    img = im if alpha else im.convert("RGB")
    img.save(p, quality=quality, method=6)
    print("   %-40s %6.1f KB" % (os.path.relpath(p, ROOT), os.path.getsize(p) / 1024))


def build_hero():
    """Hero-Ebenen aus dem einzigen vorhandenen Keyvisual.

    Das Referenzbild ist ein flaches, fotografisches Einzelbild ohne
    freigestellte Einzelobjekte. Statt eine nicht vorhandene Objekt-
    Segmentierung vorzutaeuschen, werden ehrliche Bild-Ebenen erzeugt:
    ein unscharfer Hintergrund-Layer (staerkster Weichzeichner, bewegt sich
    am wenigsten), die scharfe Hauptplatte (Motiv, mittlere Bewegung) sowie
    ein Poster-/OG-Fallback. Der "wandernde Glasurreflex" und der
    Vordergrund-Scrim werden bewusst NICHT als Bild, sondern rein in CSS/JS
    erzeugt (siehe assets/css/style.css, .hero__glow), da sie so praeziser
    auf die Objektregion begrenzt und ressourcenschonender animiert werden
    koennen als ein zusaetzliches Bild-Layer.
    """
    print("\n[1/3] Hero-Bildebenen")
    if not os.path.exists(SRC_HERO):
        print("   ! Referenzbild fehlt:", SRC_HERO)
        return
    base = Image.open(SRC_HERO).convert("RGB")
    w, h = base.size
    print("   Quellgroesse: %dx%d" % (w, h))

    # Ebene 1 - Hintergrund: unscharf, leicht aufgehellt, staerker skaliert
    bg = base.resize((int(w * 0.5), int(h * 0.5)), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(16))
    bg = ImageEnhance.Brightness(bg).enhance(1.06)
    bg = ImageEnhance.Color(bg).enhance(0.92)
    bg = bg.resize((1440, int(1440 * h / w)), Image.LANCZOS)
    save(bg, "hero-bg", quality=56)

    # Ebene 2 - Hauptplatte: das scharfe Motiv, Basis fuer Parallaxe und Zoom
    plate = base.resize((1920, int(1920 * h / w)), Image.LANCZOS)
    plate = ImageEnhance.Sharpness(plate).enhance(1.12)
    plate = ImageEnhance.Contrast(plate).enhance(1.03)
    save(plate, "hero-plate", quality=76)

    # Statischer Fallback fuer prefers-reduced-motion / kein JavaScript
    poster = base.resize((1280, int(1280 * h / w)), Image.LANCZOS)
    poster.save(os.path.join(OUT, "hero-poster.jpg"), quality=82, optimize=True, progressive=True)
    print("   %-40s %6.1f KB" % ("assets/img/hero-poster.jpg",
                                 os.path.getsize(os.path.join(OUT, "hero-poster.jpg")) / 1024))

    # Open-Graph-Bild 1200x630
    og = base.copy()
    ow, oh = og.size
    target = 1200 / 630.0
    if ow / oh > target:
        nw = int(oh * target)
        og = og.crop(((ow - nw) // 2, 0, (ow - nw) // 2 + nw, oh))
    else:
        nh = int(ow / target)
        og = og.crop((0, 0, ow, nh))
    og = og.resize((1200, 630), Image.LANCZOS)
    og.save(os.path.join(OUT, "og-image.jpg"), quality=84, optimize=True, progressive=True)
    print("   %-40s %6.1f KB" % ("assets/img/og-image.jpg",
                                 os.path.getsize(os.path.join(OUT, "og-image.jpg")) / 1024))


# Lizenzfreie Pexels-Fotos (Pexels-Lizenz: kostenlos, kommerzielle Nutzung
# erlaubt, keine Zuschreibung erforderlich - https://www.pexels.com/license/)
# Pexels-ID -> (Ausgabename, Zielbreite, Zielseitenverhaeltnis, Crop-Box oder None)
PHOTOS = {
    "27162641": ("foto-drehen", 1200, 4 / 5.0, (430, 0, 1600, 1067)),
    "18798250": ("foto-formen", 1200, 4 / 5.0, None),
    "6611312":  ("foto-atelier", 1600, 16 / 10.0, None),
    "4611612":  ("foto-glasuren", 1200, 1.0, None),
    "27180805": ("foto-zuhause", 1200, 3 / 2.0, None),
}


def smart_crop(im, ratio):
    w, h = im.size
    cur = w / float(h)
    if cur > ratio:
        nw = int(h * ratio)
        left = (w - nw) // 2
        return im.crop((left, 0, left + nw, h))
    nh = int(w / ratio)
    top = int((h - nh) * 0.35)
    return im.crop((0, top, w, top + nh))


def build_photos():
    print("\n[2/3] Sektionsfotos (Pexels, lizenzfrei)")
    if not os.path.isdir(RAW):
        print("   ! Ordner tools/raw fehlt - Fotos werden uebersprungen.")
        return
    for pid, (name, width, ratio, precrop) in PHOTOS.items():
        src = os.path.join(RAW, "%s.jpg" % pid)
        if not os.path.exists(src):
            print("   ! fehlt:", src)
            continue
        im = Image.open(src).convert("RGB")
        if precrop:
            im = im.crop(precrop)
        im = smart_crop(im, ratio)
        im = im.resize((width, int(width / ratio)), Image.LANCZOS)
        im = ImageEnhance.Sharpness(im).enhance(1.1)
        save(im, name, quality=72)


def build_favicon():
    """Favicon aus dem tatsaechlichen Firmenlogo (kein erfundenes Monogramm)."""
    print("\n[3/3] Favicon aus Original-Logo")
    if not os.path.exists(SRC_LOGO):
        print("   ! Logo fehlt:", SRC_LOGO)
        return
    logo = Image.open(SRC_LOGO).convert("RGBA")
    for size in (32, 180, 512):
        im = logo.resize((size, size), Image.LANCZOS)
        p = os.path.join(OUT, "icon-%d.png" % size)
        im.save(p)
        print("   %-40s %6.1f KB" % (os.path.relpath(p, ROOT), os.path.getsize(p) / 1024))
    icon = Image.open(os.path.join(OUT, "icon-512.png"))
    icon.save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    print("   %-40s %6.1f KB" % ("favicon.ico", os.path.getsize(os.path.join(ROOT, "favicon.ico")) / 1024))


if __name__ == "__main__":
    build_hero()
    build_photos()
    build_favicon()
    print("\nFertig.")
