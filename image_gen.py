#!/usr/bin/env python3
"""
Generador de imágenes estoicas — Python PURO, sin dependencias.
Estilo que funcionó en el Día 1: texto bitmap sobre fondo oscuro degradado.
1080x1080 PNG.
"""
import struct
import zlib
import json
import os
import sys
import textwrap
import random
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "images"

# ═══════════════════════════════════════════════════════════════
# PNG Writer (pure Python)
# ═══════════════════════════════════════════════════════════════
def create_png(width, height, pixels):
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc

    raw = bytearray((width * 4 + 1) * height)
    for y in range(height):
        row_start = y * (width * 4 + 1)
        raw[row_start] = 0
        src_start = y * width * 4
        raw[row_start + 1:row_start + 1 + width * 4] = pixels[src_start:src_start + width * 4]

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(bytes(raw))) +
            chunk(b'IEND', b''))

# ═══════════════════════════════════════════════════════════════
# Bitmap Font (5x7, built-in)
# ═══════════════════════════════════════════════════════════════
FONT_DATA = {
    'A':[0b01110,0b10001,0b10001,0b11111,0b10001,0b10001,0b10001],
    'B':[0b11110,0b10001,0b11110,0b10001,0b10001,0b10001,0b11110],
    'C':[0b01110,0b10001,0b10000,0b10000,0b10000,0b10001,0b01110],
    'D':[0b11110,0b10001,0b10001,0b10001,0b10001,0b10001,0b11110],
    'E':[0b11111,0b10000,0b11110,0b10000,0b10000,0b10000,0b11111],
    'F':[0b11111,0b10000,0b11110,0b10000,0b10000,0b10000,0b10000],
    'G':[0b01110,0b10001,0b10000,0b10111,0b10001,0b10001,0b01110],
    'H':[0b10001,0b10001,0b11111,0b10001,0b10001,0b10001,0b10001],
    'I':[0b01110,0b00100,0b00100,0b00100,0b00100,0b00100,0b01110],
    'J':[0b00111,0b00001,0b00001,0b00001,0b00001,0b10001,0b01110],
    'K':[0b10001,0b10010,0b11100,0b10000,0b11100,0b10010,0b10001],
    'L':[0b10000,0b10000,0b10000,0b10000,0b10000,0b10000,0b11111],
    'M':[0b10001,0b11011,0b10101,0b10001,0b10001,0b10001,0b10001],
    'N':[0b10001,0b10001,0b11001,0b10101,0b10011,0b10001,0b10001],
    'O':[0b01110,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
    'P':[0b11110,0b10001,0b10001,0b11110,0b10000,0b10000,0b10000],
    'Q':[0b01110,0b10001,0b10001,0b10001,0b10101,0b10010,0b01101],
    'R':[0b11110,0b10001,0b10001,0b11110,0b10010,0b10001,0b10001],
    'S':[0b01111,0b10000,0b01110,0b00001,0b00001,0b10001,0b01110],
    'T':[0b11111,0b00100,0b00100,0b00100,0b00100,0b00100,0b00100],
    'U':[0b10001,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
    'V':[0b10001,0b10001,0b10001,0b10001,0b10001,0b01010,0b00100],
    'W':[0b10001,0b10001,0b10001,0b10101,0b10101,0b11011,0b10001],
    'X':[0b10001,0b10001,0b01010,0b00100,0b01010,0b10001,0b10001],
    'Y':[0b10001,0b10001,0b01010,0b00100,0b00100,0b00100,0b00100],
    'Z':[0b11111,0b00001,0b00010,0b00100,0b01000,0b10000,0b11111],
    '0':[0b01110,0b10001,0b10011,0b10101,0b11001,0b10001,0b01110],
    '1':[0b00100,0b01100,0b00100,0b00100,0b00100,0b00100,0b01110],
    '2':[0b01110,0b10001,0b00001,0b00110,0b01000,0b10000,0b11111],
    '3':[0b01110,0b10001,0b00001,0b00110,0b00001,0b10001,0b01110],
    '4':[0b00010,0b00110,0b01010,0b10010,0b11111,0b00010,0b00010],
    '5':[0b11111,0b10000,0b11110,0b00001,0b00001,0b10001,0b01110],
    '6':[0b01110,0b10001,0b10000,0b11110,0b10001,0b10001,0b01110],
    '7':[0b11111,0b00001,0b00010,0b00100,0b01000,0b01000,0b01000],
    '8':[0b01110,0b10001,0b10001,0b01110,0b10001,0b10001,0b01110],
    '9':[0b01110,0b10001,0b10001,0b01111,0b00001,0b10001,0b01110],
    ' ':[0b00000]*7, '.':[0,0,0,0,0,0,0b00100],
    ',':[0,0,0,0,0,0b00100,0b01000], ':':[0,0,0b00100,0,0,0b00100,0],
    ';':[0,0,0b00100,0,0,0b00100,0b01000], '!':[0b00100]*5+[0,0b00100],
    '?':[0b01110,0b10001,0b00001,0b00110,0b00100,0,0b00100],
    '-':[0]*3+[0b11111]+[0]*3, '—':[0]*3+[0b11111]+[0]*3,
    '\'':[0b00100,0b00100]+[0]*5, '"':[0b01010,0b01010]+[0]*5,
    '(':[0b00010,0b00100,0b01000,0b01000,0b01000,0b00100,0b00010],
    ')':[0b01000,0b00100,0b00010,0b00010,0b00010,0b00100,0b01000],
    '[':[0b01110,0b01000]*3+[0b01110],
    ']':[0b01110,0b00010]*3+[0b01110],
    '¿':[0,0b00100,0,0b00100,0b01000,0b10001,0b01110],
    '¡':[0b00100,0]+[0b00100]*5,
    'á':[0b00010,0b00100,0b01110,0b10001,0b11111,0b10001,0b10001],
    'é':[0b00010,0b00100,0b01110,0b10001,0b11111,0b10000,0b01110],
    'í':[0b00010,0b00100,0b01110,0b00100,0b00100,0b00100,0b01110],
    'ó':[0b00010,0b00100,0b01110,0b10001,0b10001,0b10001,0b01110],
    'ú':[0b00010,0b00100,0b10001,0b10001,0b10001,0b10011,0b01101],
    'ñ':[0,0b01010,0b10100,0b11110,0b10001,0b10001,0b10001],
    'Ñ':[0b01010,0b10100,0b10001,0b11001,0b10101,0b10011,0b10001],
}

def get_char_bitmap(ch):
    if ch in FONT_DATA:
        return FONT_DATA[ch]
    u = ch.upper()
    if u in FONT_DATA:
        return FONT_DATA[u]
    return FONT_DATA[' ']

def draw_text(pixels, width, height, text, x, y, color, scale=1):
    cur_x = x
    for ch in text:
        bm = get_char_bitmap(ch)
        char_w = 5
        for row in range(7):
            for col in range(char_w):
                if (bm[row] >> (char_w - 1 - col)) & 1:
                    for sy in range(scale):
                        for sx in range(scale):
                            px = cur_x + col * scale + sx
                            py = y + row * scale + sy
                            if 0 <= px < width and 0 <= py < height:
                                idx = (py * width + px) * 4
                                pixels[idx:idx+4] = color
        cur_x += (char_w + 1) * scale

def text_width(text, scale=1, spacing=1):
    w = 0
    for ch in text:
        w += (6 if ch != ' ' else 3) + spacing
    return w * scale - spacing

def wrap_text(text, max_chars):
    words = text.split(' ')
    lines = []
    current = ''
    for word in words:
        if len(word) > max_chars:
            if current:
                lines.append(current.strip())
                current = ''
            for i in range(0, len(word), max_chars):
                lines.append(word[i:i+max_chars])
        elif len(current + ' ' + word) <= max_chars or not current:
            current = (current + ' ' + word).strip()
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

# ═══════════════════════════════════════════════════════════════
# Image Generator
# ═══════════════════════════════════════════════════════════════
def generate_stoic_image(day, quote, author, reflection, hashtags, output_path):
    W, H = 1080, 1080
    pixels = bytearray(W * H * 4)

    # Elegant dark gradient background
    for y in range(H):
        t = y / H
        r = int(15 + t * 12)
        g = int(14 + t * 10)
        b = int(20 + t * 14)
        for x in range(W):
            idx = (y * W + x) * 4
            pixels[idx:idx+4] = [r, g, b, 255]

    # Subtle radial glow in center
    cx, cy = W // 2, H // 3
    for y in range(H):
        for x in range(W):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            glow = max(0, int(15 * (1 - dist / 600)))
            if glow > 0:
                idx = (y * W + x) * 4
                pixels[idx] = min(255, pixels[idx] + glow)
                pixels[idx+2] = min(255, pixels[idx+2] + glow // 2)

    # Colors
    white = [225, 225, 230, 255]
    gold = [195, 155, 80, 255]
    dim = [140, 140, 155, 255]
    very_dim = [90, 90, 105, 255]
    accent_red = [190, 50, 40, 255]

    # Top ornamental line
    for x in range(W//4, 3*W//4):
        for ty in range(2):
            idx = ((55 + ty) * W + x) * 4
            pixels[idx:idx+4] = gold

    # Day badge
    day_text = f"DIA {day}"
    day_scale = 3
    dw = text_width(day_text, day_scale)
    draw_text(pixels, W, H, day_text, (W - dw)//2, 80, gold, day_scale)

    # Decorative quotes
    draw_text(pixels, W, H, '❝', W//2 - 250, 170, accent_red, 4)
    draw_text(pixels, W, H, '❞', W//2 + 210, 170, accent_red, 4)

    # Quote (main attraction)
    quote_scale = 5 if len(quote) < 60 else 4
    max_chars = 18 if quote_scale == 5 else 22
    lines = wrap_text(quote, max_chars)
    line_h = 7 * quote_scale + 12

    quote_y_start = 220
    for i, line in enumerate(lines):
        lw = text_width(line, quote_scale)
        lx = (W - lw) // 2
        ly = quote_y_start + i * line_h
        draw_text(pixels, W, H, line, lx, ly, white, quote_scale)

    # Author
    author_text = f"— {author}"
    author_scale = 3
    aw = text_width(author_text, author_scale)
    author_y = quote_y_start + len(lines) * line_h + 50
    draw_text(pixels, W, H, author_text, (W - aw)//2, author_y, gold, author_scale)

    # Separator
    sep_y = author_y + 55
    for x in range(W//3, 2*W//3):
        idx = (sep_y * W + x) * 4
        pixels[idx:idx+4] = very_dim

    # Reflection (smaller, subtle)
    refl_scale = 2
    refl_lines = wrap_text(reflection, 48)
    refl_line_h = 7 * refl_scale + 6
    refl_y_start = sep_y + 35

    for i, line in enumerate(refl_lines):
        lw = text_width(line, refl_scale)
        lx = (W - lw) // 2
        ly = refl_y_start + i * refl_line_h
        if ly + 14 > H - 80:
            break
        draw_text(pixels, W, H, line, lx, ly, dim, refl_scale)

    # Bottom section: MENSANITY branding + hashtags
    brand = "M E N S A N I T Y"
    brand_scale = 2
    bw = text_width(brand, brand_scale, spacing=2)
    draw_text(pixels, W, H, brand, (W - bw)//2, H - 60, very_dim, brand_scale)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    png_data = create_png(W, H, pixels)
    with open(output_path, 'wb') as f:
        f.write(png_data)


def generate_all():
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(BASE_DIR / "posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    for post in posts:
        filename = f"dia_{post['day']:03d}.png"
        path = OUTPUT_DIR / filename
        generate_stoic_image(
            day=post['day'],
            quote=post['quote'],
            author=post['author'],
            reflection=post['reflection'],
            hashtags=post['hashtags'],
            output_path=str(path)
        )
        print(f"  ✅ {filename}")

    print(f"\n🎉 {len(posts)} imágenes generadas.")


if __name__ == "__main__":
    generate_all()
