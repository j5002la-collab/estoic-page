#!/usr/bin/env python3
"""
Generador de imágenes cinematográficas estilo Mensanity.
- Fondos de Unsplash (caminos, niebla, bosques)
- Texto gótico rojo overlay
- Branding Mensanity
- Estilo B: cinematográfico | Estilo C: minimalista oscuro
"""
import sys
import os
import json
import urllib.request
import random
from pathlib import Path

# Add local Pillow
sys.path.insert(0, '/opt/data/site-packages')
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
BG_DIR = BASE_DIR / "backgrounds"
FONT_DIR = BASE_DIR / "fonts"

# Download backgrounds once
BACKGROUNDS = [
    ("foggy-road", "niebla-carretera"),
    ("misty-forest", "bosque-neblina"),
    ("lonely-path", "camino-solitario"),
    ("rainy-street-night", "calle-lluviosa"),
    ("dark-mountains", "montanas-oscuras"),
    ("stormy-sea", "mar-tormenta"),
    ("empty-highway", "carretera-vacia"),
    ("foggy-bridge", "puente-niebla"),
    ("abandoned-road", "carretera-abandonada"),
    ("dark-forest-path", "sendero-oscuro"),
]

def generate_procedural_backgrounds():
    """Generate 12 moody procedural backgrounds using Pillow."""
    BG_DIR.mkdir(exist_ok=True)
    from PIL import ImageDraw

    styles = [
        # (name, r1,g1,b1, r2,g2,b2, gradient_dir, features)
        ("niebla-carretera", 15,15,20, 40,42,48, "center_vignette", "road+fog"),
        ("bosque-neblina", 10,18,12, 20,28,22, "top_vignette", "trees+fog"),
        ("camino-solitario", 20,18,15, 35,32,28, "bottom_light", "path+fog"),
        ("calle-lluviosa", 10,10,18, 25,25,35, "top_vignette", "rain+reflection"),
        ("montanas-oscuras", 8,10,18, 22,25,40, "diagonal_vignette", "mountains"),
        ("mar-tormenta", 5,8,20, 18,22,40, "horizontal_split", "ocean+sky"),
        ("carretera-vacia", 18,16,14, 38,34,30, "center_vignette", "road+fog"),
        ("puente-niebla", 12,14,20, 30,33,42, "top_vignette", "bridge+fog"),
        ("carretera-abandonada", 22,18,14, 40,35,28, "bottom_light", "road+texture"),
        ("sendero-oscuro", 5,12,8, 15,25,18, "center_vignette", "trees+path"),
        ("amanecer-estoico", 20,15,8, 50,35,18, "bottom_light", "sun+horizon"),
        ("tormenta-estoica", 8,8,15, 15,12,30, "diagonal_vignette", "storm+lightning"),
    ]

    for i, (name, r1,g1,b1, r2,g2,b2, grad_dir, features) in enumerate(styles):
        path = BG_DIR / f"{name}.jpg"
        if path.exists():
            continue

        W, H = 1080, 1080
        img = Image.new('RGB', (W, H))
        pixels = img.load()

        # Base gradient
        for y in range(H):
            for x in range(W):
                if grad_dir == "center_vignette":
                    dist = ((x - W//2)**2 + (y - H//2)**2) ** 0.5
                    max_dist = (W**2 + H**2)**0.5 / 2
                    t = min(dist / max_dist, 1.0)
                elif grad_dir == "top_vignette":
                    t = y / H
                elif grad_dir == "bottom_light":
                    t = 1.0 - (y / H)
                elif grad_dir == "diagonal_vignette":
                    t = (x + y) / (W + H)
                elif grad_dir == "horizontal_split":
                    t = 0.5 if y < H//2 else 0.5
                else:
                    t = y / H

                t = t ** 0.6  # Smooth curve
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                pixels[x, y] = (r, g, b)

        draw = ImageDraw.Draw(img)

        # Procedural features
        import random as _r
        _r.seed(i * 42)

        if "fog" in features:
            # Fog layers - horizontal semi-transparent bands
            for _ in range(30):
                fy = _r.randint(0, H - 1)
                fh = _r.randint(40, 200)
                alpha = _r.randint(15, 50)
                color = (180, 185, 195) if _r.random() > 0.5 else (100, 105, 115)
                for dy in range(fh):
                    py = fy + dy
                    if 0 <= py < H:
                        for px in range(0, W, 2):
                            pixels[px, py] = (
                                min(255, pixels[px, py][0] + alpha),
                                min(255, pixels[px, py][1] + alpha),
                                min(255, pixels[px, py][2] + alpha + 5)
                            )

        if "road" in features:
            # Central road/path fading into fog
            road_center = W // 2 + _r.randint(-30, 30)
            for y in range(H // 3, H):
                progress = (y - H//3) / (H - H//3)
                road_w = int(80 + progress * 300)
                alpha = int(40 * (1 - progress * 0.7))
                for dx in range(-road_w // 2, road_w // 2):
                    px = road_center + dx + _r.randint(-1, 1)
                    if 0 <= px < W:
                        r, g, b = pixels[px, y]
                        pixels[px, y] = (
                            min(255, r + alpha),
                            min(255, g + alpha),
                            min(255, b + alpha)
                        )
                # Road edge lines
                for edge in [-1, 1]:
                    ex = road_center + edge * (road_w // 2)
                    for t in range(3):
                        if 0 <= ex + t < W:
                            r, g, b = pixels[ex + t, y]
                            pixels[ex + t, y] = (min(255, r+60), min(255, g+55), min(255, b+50))

        if "rain" in features:
            for _ in range(200):
                rx = _r.randint(0, W - 1)
                ry = _r.randint(0, H - 1)
                length = _r.randint(20, 80)
                for dl in range(length):
                    py = ry + dl
                    if 0 <= py < H:
                        r, g, b = pixels[rx, py]
                        pixels[rx, py] = (min(255, r+70), min(255, g+70), min(255, b+75))

        if "trees" in features:
            for _ in range(20):
                tx = _r.randint(0, W - 1)
                th = _r.randint(100, H // 2)
                for ty in range(H - th, H):
                    tw = int(th * 0.15 * (1 - (ty - (H - th)) / th))
                    for dx in range(-tw, tw):
                        px = tx + dx
                        if 0 <= px < W:
                            r, g, b = pixels[px, ty]
                            pixels[px, ty] = (
                                max(0, r - 40),
                                max(0, g - 20),
                                max(0, b - 50)
                            )

        if "mountains" in features:
            for m in range(3):
                mx = _r.randint(100, W - 100)
                mh = _r.randint(200, 400)
                for y in range(H - mh, H):
                    progress = (y - (H - mh)) / mh
                    mw = int(300 * (1 - progress))
                    for dx in range(-mw, mw):
                        px = mx + dx
                        if 0 <= px < W:
                            r, g, b = pixels[px, y]
                            darkness = int(60 * (1 - progress))
                            pixels[px, y] = (
                                max(0, r - darkness - 20),
                                max(0, g - darkness - 10),
                                max(0, b - darkness)
                            )

        if "sun" in features:
            sx, sy = _r.randint(W//4, 3*W//4), _r.randint(H//3, H//2)
            for y in range(H):
                for x in range(W):
                    dist = ((x - sx)**2 + (y - sy)**2) ** 0.5
                    if dist < 300:
                        glow = int(80 * (1 - dist / 300))
                        r, g, b = pixels[x, y]
                        pixels[x, y] = (
                            min(255, r + glow),
                            min(255, g + int(glow * 0.6)),
                            min(255, b + int(glow * 0.2))
                        )

        # Apply overall darkening vignette
        for y in range(H):
            for x in range(W):
                dist_to_edge = min(x, y, W - x, H - y)
                edge_factor = min(dist_to_edge / 150, 1.0)
                if edge_factor < 1.0:
                    darkness = int(80 * (1 - edge_factor))
                    r, g, b = pixels[x, y]
                    pixels[x, y] = (
                        max(0, r - darkness),
                        max(0, g - darkness),
                        max(0, b - darkness)
                    )

        img.save(path, 'JPEG', quality=90)
        print(f"  🎨 {name}")

_BG_GENERATED = False

def ensure_backgrounds():
    """Ensure procedural backgrounds exist."""
    global _BG_GENERATED
    if _BG_GENERATED:
        return list(BG_DIR.glob("*.jpg"))
    
    bgs = list(BG_DIR.glob("*.jpg"))
    if len(bgs) < 6:
        print("   Generando fondos procedurales...")
        generate_procedural_backgrounds()
    _BG_GENERATED = True
    return list(BG_DIR.glob("*.jpg"))

def get_background_path(category=""):
    """Get a random or category-matched background."""
    bgs = list(BG_DIR.glob("*.jpg"))
    if not bgs:
        return None

    # Map categories to backgrounds
    cat_map = {
        "resilience": ["niebla-carretera", "carretera-vacia"],
        "death": ["niebla-carretera", "puente-niebla"],
        "time": ["carretera-vacia", "carretera-abandonada"],
        "control": ["niebla-carretera", "montanas-oscuras"],
        "emotion": ["lluvia", "mar-tormenta"],
        "fear": ["bosque-neblina", "sendero-oscuro"],
        "purpose": ["niebla-carretera", "montanas-oscuras"],
        "acceptance": ["niebla-carretera", "mar-tormenta"],
        "discipline": ["carretera-vacia", "montanas-oscuras"],
        "wisdom": ["bosque-neblina", "montanas-oscuras"],
        "gratitude": ["bosque-neblina", "niebla-carretera"],
    }

    matching = cat_map.get(category, [])
    if matching:
        candidates = [b for b in bgs if any(m in str(b) for m in matching)]
        if candidates:
            return random.choice(candidates)

    return random.choice(bgs)


def create_cinematic_image(day, quote, author, reflection, hashtags, output_path, bg_path):
    """Style B: Cinematic landscape + red Gothic text + Mensanity branding."""
    W, H = 1080, 1080

    # Open background
    bg = Image.open(bg_path).convert("RGB")
    bg = bg.resize((W, H), Image.LANCZOS)
    bg = ImageEnhance.Color(bg).enhance(0.2)  # Desaturate
    bg = ImageEnhance.Brightness(bg).enhance(0.7)  # Darken
    bg = ImageEnhance.Contrast(bg).enhance(1.3)  # More contrast
    bg = bg.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Create vignette overlay
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Top gradient (heavy black)
    for y in range(300):
        alpha = int(180 * (1 - y / 300))
        draw_overlay.rectangle([(0, y), (W, y + 1)], fill=(0, 0, 0, alpha))

    # Bottom gradient
    for y in range(H - 300, H):
        alpha = int(180 * ((y - (H - 300)) / 300))
        draw_overlay.rectangle([(0, y), (W, y + 1)], fill=(0, 0, 0, alpha))

    # Side gradients
    for x in range(80):
        alpha = int(120 * (1 - x / 80))
        draw_overlay.rectangle([(x, 0), (x + 1, H)], fill=(0, 0, 0, alpha))
        draw_overlay.rectangle([(W - x - 1, 0), (W - x, H)], fill=(0, 0, 0, alpha))

    bg = Image.alpha_composite(bg.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(bg)

    # Try to load fonts
    try:
        title_font = ImageFont.truetype(str(FONT_DIR / "Cinzel-Bold.ttf"), 56)
        quote_font = ImageFont.truetype(str(FONT_DIR / "Cinzel-Bold.ttf"), 44)
        author_font = ImageFont.truetype(str(FONT_DIR / "Cinzel-Regular.ttf"), 28)
        brand_font = ImageFont.truetype(str(FONT_DIR / "Cinzel-Regular.ttf"), 24)
    except:
        # Fallback to default
        title_font = ImageFont.load_default()
        quote_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        brand_font = ImageFont.load_default()

    # Quote text placement - top half, centered
    red = (190, 30, 25)
    dark_red = (140, 20, 15)

    # Determine text size to use
    test_font = quote_font
    if len(quote) > 80:
        test_font = title_font

    # Word wrap
    max_width = 850
    words = quote.split()
    lines = []
    current = []
    for word in words:
        test = ' '.join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=test_font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(' '.join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(' '.join(current))

    # Draw shadow then text
    line_height = 70 if len(lines) <= 3 else 55
    total_height = len(lines) * line_height
    y_start = 200

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=test_font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = y_start + i * line_height

        # Shadow
        draw.text((x + 3, y + 3), line, font=test_font, fill=(0, 0, 0))
        draw.text((x - 1, y - 1), line, font=test_font, fill=(0, 0, 0))
        # Red text
        draw.text((x, y), line, font=test_font, fill=red)

    # Author
    author_y = y_start + len(lines) * line_height + 50
    bbox = draw.textbbox((0, 0), f"— {author}", font=author_font)
    aw = bbox[2] - bbox[0]
    draw.text(((W - aw)//2 + 2, author_y + 2), f"— {author}", font=author_font, fill=(0,0,0))
    draw.text(((W - aw)//2, author_y), f"— {author}", font=author_font, fill=(150, 130, 110))

    # Day badge
    day_text = f"DÍA {day}"
    bbox = draw.textbbox((0, 0), day_text, font=brand_font)
    dw = bbox[2] - bbox[0]
    draw.text((W - dw - 50, 45), day_text, font=brand_font, fill=(120, 110, 100))

    # Mensanity branding at bottom
    brand = "MENSANITY"
    bbox = draw.textbbox((0, 0), brand, font=brand_font)
    bw = bbox[2] - bbox[0]
    draw.text(((W - bw)//2 + 1, H - 55), brand, font=brand_font, fill=(0,0,0))
    draw.text(((W - bw)//2, H - 56), brand, font=brand_font, fill=(90, 90, 100))

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bg.save(output_path, 'PNG', optimize=True)
    return output_path


def create_minimalist_image(day, quote, author, reflection, hashtags, output_path):
    """Style C: Clean dark background + white text (pure Python)."""
    import struct, zlib

    W, H = 1080, 1080
    pixels = bytearray(W * H * 4)

    # Dark gradient background
    for y in range(H):
        t = y / H
        r = int(18 + t * 8)
        g = int(18 + t * 6)
        b = int(22 + t * 10)
        for x in range(W):
            idx = (y * W + x) * 4
            pixels[idx:idx+4] = [r, g, b, 255]

    # Use Pillow for text on top of the dark background
    img = Image.frombytes('RGBA', (W, H), bytes(pixels))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(str(FONT_DIR / "Cinzel-Bold.ttf"), 54)
        quote_font = ImageFont.truetype(str(FONT_DIR / "Cinzel-Bold.ttf"), 40)
        author_font = ImageFont.truetype(str(FONT_DIR / "Cinzel-Regular.ttf"), 26)
        brand_font = ImageFont.truetype(str(FONT_DIR / "Cinzel-Regular.ttf"), 20)
    except:
        title_font = ImageFont.load_default()
        quote_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        brand_font = ImageFont.load_default()

    white = (220, 220, 225)
    gold = (180, 145, 75)
    dim = (120, 120, 135)

    # Day badge
    day_text = f"DÍA {day}"
    bbox = draw.textbbox((0, 0), day_text, font=brand_font)
    dw = bbox[2] - bbox[0]
    draw.text(((W - dw)//2, 70), day_text, font=brand_font, fill=gold)

    # Quote
    words = quote.split()
    lines = []
    current = []
    for word in words:
        test = ' '.join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=quote_font)
        if bbox[2] - bbox[0] > 850 and current:
            lines.append(' '.join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(' '.join(current))

    line_h = 65
    y_start = 250
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=quote_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw)//2, y_start + i * line_h), line, font=quote_font, fill=white)

    # Author
    author_y = y_start + len(lines) * line_h + 45
    bbox = draw.textbbox((0, 0), f"— {author}", font=author_font)
    aw = bbox[2] - bbox[0]
    draw.text(((W - aw)//2, author_y), f"— {author}", font=author_font, fill=gold)

    # Reflection
    refl_lines = []
    current = []
    for word in reflection.split():
        test = ' '.join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=brand_font)
        if bbox[2] - bbox[0] > 800 and current:
            refl_lines.append(' '.join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        refl_lines.append(' '.join(current))

    refl_y_start = author_y + 80
    for i, line in enumerate(refl_lines):
        bbox = draw.textbbox((0, 0), line, font=brand_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw)//2, refl_y_start + i * 30), line, font=brand_font, fill=dim)

    # Mensanity
    brand = "MENSANITY"
    bbox = draw.textbbox((0, 0), brand, font=brand_font)
    bw = bbox[2] - bbox[0]
    draw.text(((W - bw)//2, H - 50), brand, font=brand_font, fill=(70, 70, 85))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG', optimize=True)
    return output_path


def generate_all(style="mixed"):
    """Generate all 100 images. style: 'cinematic', 'minimalist', or 'mixed'."""
    with open(BASE_DIR / "posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    bgs = list(BG_DIR.glob("*.jpg"))

    for post in posts:
        day = post['day']
        filename = f"dia_{day:03d}.png"
        path = IMAGES_DIR / filename

        # Determine style: mixed = alternate B and C
        if style == "mixed":
            use_cinematic = (day % 2 == 1)  # Odd days = B, even = C
        elif style == "cinematic":
            use_cinematic = True
        else:
            use_cinematic = False

        if use_cinematic and bgs:
            bg_path = random.choice(bgs)
            create_cinematic_image(day, post['quote'], post['author'],
                                   post['reflection'], post['hashtags'],
                                   str(path), str(bg_path))
            print(f"  🎬 día_{day:03d} (cinematic)")
        else:
            create_minimalist_image(day, post['quote'], post['author'],
                                    post['reflection'], post['hashtags'],
                                    str(path))
            print(f"  🖤 día_{day:03d} (minimalist)")

    print(f"\n✅ {len(posts)} imágenes generadas.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        style = sys.argv[1]  # 'cinematic', 'minimalist', or 'mixed'
    else:
        style = "mixed"

    print(f"🎨 Generando imágenes (estilo: {style})")
    ensure_backgrounds()
    generate_all(style)
