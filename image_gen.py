#!/usr/bin/env python3
"""
Generador de imágenes estoicas para Facebook.
Python puro — sin Pillow, sin dependencias.
Genera PNGs de 1080x1080 con fondo oscuro y texto centrado.
"""
import struct
import zlib
import json
import os
import textwrap
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "images"

# ── PNG writer (pure Python) ──────────────────────────────────────────
def create_png(width, height, pixels):
    """Crea un PNG desde una lista de bytes RGBA. pixels: list[bytes] de 4 bytes por pixel."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc

    # Efficient raw data construction using bytearray
    raw = bytearray((width * 4 + 1) * height)
    for y in range(height):
        row_start = y * (width * 4 + 1)
        raw[row_start] = 0  # filter byte
        src_start = y * width * 4
        raw[row_start + 1:row_start + 1 + width * 4] = pixels[src_start:src_start + width * 4]
    raw = bytes(raw)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(raw)) +
            chunk(b'IEND', b''))

# ── Bitmap font (5x7 pixels per char, ASCII printable) ────────────────
# Simplified font bitmap for A-Z, a-z, 0-9, basic punctuation
FONT_DATA = {
    # Each char: list of 7 rows, each row 5 bits (MSB left)
    'A': [0b01110,0b10001,0b10001,0b11111,0b10001,0b10001,0b10001],
    'B': [0b11110,0b10001,0b11110,0b10001,0b10001,0b10001,0b11110],
    'C': [0b01110,0b10001,0b10000,0b10000,0b10000,0b10001,0b01110],
    'D': [0b11110,0b10001,0b10001,0b10001,0b10001,0b10001,0b11110],
    'E': [0b11111,0b10000,0b11110,0b10000,0b10000,0b10000,0b11111],
    'F': [0b11111,0b10000,0b11110,0b10000,0b10000,0b10000,0b10000],
    'G': [0b01110,0b10001,0b10000,0b10111,0b10001,0b10001,0b01110],
    'H': [0b10001,0b10001,0b11111,0b10001,0b10001,0b10001,0b10001],
    'I': [0b01110,0b00100,0b00100,0b00100,0b00100,0b00100,0b01110],
    'J': [0b00111,0b00001,0b00001,0b00001,0b00001,0b10001,0b01110],
    'K': [0b10001,0b10010,0b11100,0b10000,0b11100,0b10010,0b10001],
    'L': [0b10000,0b10000,0b10000,0b10000,0b10000,0b10000,0b11111],
    'M': [0b10001,0b11011,0b10101,0b10001,0b10001,0b10001,0b10001],
    'N': [0b10001,0b10001,0b11001,0b10101,0b10011,0b10001,0b10001],
    'O': [0b01110,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
    'P': [0b11110,0b10001,0b10001,0b11110,0b10000,0b10000,0b10000],
    'Q': [0b01110,0b10001,0b10001,0b10001,0b10101,0b10010,0b01101],
    'R': [0b11110,0b10001,0b10001,0b11110,0b10010,0b10001,0b10001],
    'S': [0b01111,0b10000,0b01110,0b00001,0b00001,0b10001,0b01110],
    'T': [0b11111,0b00100,0b00100,0b00100,0b00100,0b00100,0b00100],
    'U': [0b10001,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
    'V': [0b10001,0b10001,0b10001,0b10001,0b10001,0b01010,0b00100],
    'W': [0b10001,0b10001,0b10001,0b10101,0b10101,0b11011,0b10001],
    'X': [0b10001,0b10001,0b01010,0b00100,0b01010,0b10001,0b10001],
    'Y': [0b10001,0b10001,0b01010,0b00100,0b00100,0b00100,0b00100],
    'Z': [0b11111,0b00001,0b00010,0b00100,0b01000,0b10000,0b11111],
    '0': [0b01110,0b10001,0b10011,0b10101,0b11001,0b10001,0b01110],
    '1': [0b00100,0b01100,0b00100,0b00100,0b00100,0b00100,0b01110],
    '2': [0b01110,0b10001,0b00001,0b00110,0b01000,0b10000,0b11111],
    '3': [0b01110,0b10001,0b00001,0b00110,0b00001,0b10001,0b01110],
    '4': [0b00010,0b00110,0b01010,0b10010,0b11111,0b00010,0b00010],
    '5': [0b11111,0b10000,0b11110,0b00001,0b00001,0b10001,0b01110],
    '6': [0b01110,0b10001,0b10000,0b11110,0b10001,0b10001,0b01110],
    '7': [0b11111,0b00001,0b00010,0b00100,0b01000,0b01000,0b01000],
    '8': [0b01110,0b10001,0b10001,0b01110,0b10001,0b10001,0b01110],
    '9': [0b01110,0b10001,0b10001,0b01111,0b00001,0b10001,0b01110],
    ' ': [0b00000,0b00000,0b00000,0b00000,0b00000,0b00000,0b00000],
    '.': [0b00000,0b00000,0b00000,0b00000,0b00000,0b00000,0b00100],
    ',': [0b00000,0b00000,0b00000,0b00000,0b00000,0b00100,0b01000],
    ':': [0b00000,0b00000,0b00100,0b00000,0b00000,0b00100,0b00000],
    ';': [0b00000,0b00000,0b00100,0b00000,0b00000,0b00100,0b01000],
    '!': [0b00100,0b00100,0b00100,0b00100,0b00100,0b00000,0b00100],
    '?': [0b01110,0b10001,0b00001,0b00110,0b00100,0b00000,0b00100],
    '-': [0b00000,0b00000,0b00000,0b11111,0b00000,0b00000,0b00000],
    '—': [0b00000,0b00000,0b00000,0b11111,0b00000,0b00000,0b00000],
    '\'':[0b00100,0b00100,0b00000,0b00000,0b00000,0b00000,0b00000],
    '"': [0b01010,0b01010,0b00000,0b00000,0b00000,0b00000,0b00000],
    '(': [0b00010,0b00100,0b01000,0b01000,0b01000,0b00100,0b00010],
    ')': [0b01000,0b00100,0b00010,0b00010,0b00010,0b00100,0b01000],
    '[': [0b01110,0b01000,0b01000,0b01000,0b01000,0b01000,0b01110],
    ']': [0b01110,0b00010,0b00010,0b00010,0b00010,0b00010,0b01110],
    '¿': [0b00000,0b00100,0b00000,0b00100,0b01000,0b10001,0b01110],
    '¡': [0b00100,0b00000,0b00100,0b00100,0b00100,0b00100,0b00100],
    'á': [0b00010,0b00100,0b01110,0b10001,0b11111,0b10001,0b10001],
    'é': [0b00010,0b00100,0b01110,0b10001,0b11111,0b10000,0b01110],
    'í': [0b00010,0b00100,0b01110,0b00100,0b00100,0b00100,0b01110],
    'ó': [0b00010,0b00100,0b01110,0b10001,0b10001,0b10001,0b01110],
    'ú': [0b00010,0b00100,0b10001,0b10001,0b10001,0b10011,0b01101],
    'ñ': [0b00000,0b01010,0b10100,0b11110,0b10001,0b10001,0b10001],
    'Ñ': [0b01010,0b10100,0b10001,0b11001,0b10101,0b10011,0b10001],
}

def get_char_bitmap(ch):
    """Return 7x5 bitmap for a character, or space if not found."""
    ch = ch.upper()
    if ch in FONT_DATA:
        return FONT_DATA[ch]
    # Try original case
    for k in FONT_DATA:
        if k == ch:
            return FONT_DATA[k]
    return FONT_DATA[' ']

def text_size(text, scale=1, letterspacing=1):
    """Calculate pixel width of text at given scale."""
    w = 0
    for ch in text:
        if ch == ' ':
            w += 3
        else:
            w += 5
        w += letterspacing
    h = 7 * scale
    return w * scale - letterspacing, h

def draw_text(pixels, width, height, text, x, y, color, scale=1):
    """Draw text onto pixel buffer at position (x,y) with given color."""
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

def wrap_text(text, max_chars_per_line):
    """Wrap text at word boundaries, with forced breaks on max chars."""
    words = text.split(' ')
    lines = []
    current = ''
    for word in words:
        if len(word) > max_chars_per_line:
            if current:
                lines.append(current.strip())
                current = ''
            # Force split long word
            for i in range(0, len(word), max_chars_per_line):
                lines.append(word[i:i+max_chars_per_line])
        elif len(current + ' ' + word) <= max_chars_per_line or not current:
            current = (current + ' ' + word).strip()
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate_stoic_image(day, quote, author, reflection, hashtags, output_path):
    """Generate a stoic quote image and save as PNG."""
    W, H = 1080, 1080
    pixels = bytearray(W * H * 4)

    # Dark background gradient (deep charcoal to near-black)
    for y in range(H):
        t = y / H
        r = int(20 + t * 5)
        g = int(20 + t * 5)
        b = int(25 + t * 8)
        for x in range(W):
            idx = (y * W + x) * 4
            pixels[idx:idx+4] = [r, g, b, 255]

    # White-ish text color
    white = [220, 220, 225, 255]
    accent = [180, 140, 80, 255]  # Gold accent
    dim = [130, 130, 140, 255]    # Dim for author

    # Draw day badge
    day_text = f"DIA {day}"
    day_scale = 3
    day_w, day_h = text_size(day_text, day_scale)
    draw_text(pixels, W, H, day_text, (W - day_w) // 2, 60, accent, day_scale)

    # Draw quote (large font)
    quote_scale = 4
    max_chars = 24  # Max chars per line at scale 4 on 1080px
    lines = wrap_text(quote, max_chars)
    line_h = 7 * quote_scale + 10

    # Center the quote block vertically
    total_quote_h = len(lines) * line_h
    quote_y_start = 220  # Start after day badge

    # Add decorative quotes
    draw_text(pixels, W, H, '"', W//2 - text_size(quote, quote_scale)[0]//2 - 30,
              quote_y_start - 10, accent, 5)

    for i, line in enumerate(lines):
        lw, _ = text_size(line, quote_scale)
        lx = (W - lw) // 2
        ly = quote_y_start + i * line_h
        draw_text(pixels, W, H, line, lx, ly, white, quote_scale)

    # Draw author
    author_text = f"— {author}"
    author_scale = 3
    aw, ah = text_size(author_text, author_scale)
    author_y = quote_y_start + len(lines) * line_h + 40
    draw_text(pixels, W, H, author_text, (W - aw) // 2, author_y, accent, author_scale)

    # Draw reflection (smaller text, bottom)
    refl_scale = 2
    refl_lines = wrap_text(reflection, 48)
    refl_line_h = 7 * refl_scale + 6
    refl_total = len(refl_lines) * refl_line_h
    refl_y_start = H - refl_total - 60

    # Separator line
    sep_y = refl_y_start - 20
    for x in range(W//4, 3*W//4):
        idx = (sep_y * W + x) * 4
        pixels[idx:idx+4] = dim

    for i, line in enumerate(refl_lines):
        lw, _ = text_size(line, refl_scale)
        lx = (W - lw) // 2
        ly = refl_y_start + i * refl_line_h
        draw_text(pixels, W, H, line, lx, ly, dim, refl_scale)

    # Hashtags at very bottom
    hash_text = hashtags.split(' ')[0] + ' ' + hashtags.split(' ')[1]  # First 2 hashtags
    hash_scale = 1
    hw, _ = text_size(hash_text, hash_scale)
    draw_text(pixels, W, H, hash_text, (W - hw) // 2, H - 25, accent, hash_scale)

    # Save PNG
    png_data = create_png(W, H, pixels)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(png_data)
    return output_path


def generate_all_images():
    """Generate images for all 100 posts."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    with open(BASE_DIR / "posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    for post in posts:
        filename = f"dia_{post['day']:03d}.png"
        path = OUTPUT_DIR / filename

        # Skip if already generated
        # if path.exists():
        #     continue

        generate_stoic_image(
            day=post['day'],
            quote=post['quote'],
            author=post['author'],
            reflection=post['reflection'],
            hashtags=post['hashtags'],
            output_path=str(path)
        )
        print(f"✅ {filename}")

    print(f"\n🎉 {len(posts)} imágenes generadas en {OUTPUT_DIR}/")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        generate_all_images()
    else:
        # Generate one test image
        test_path = str(OUTPUT_DIR / "test.png")
        OUTPUT_DIR.mkdir(exist_ok=True)
        generate_stoic_image(
            day=1,
            quote="No son las cosas las que perturban a los hombres, sino las opiniones que tienen de ellas.",
            author="Epicteto",
            reflection="Cada vez que algo te moleste, pregúntate: ¿es el hecho o mi interpretación? Cambia la narrativa y cambiarás tu realidad.",
            hashtags="#estoicismo #Epicteto #pazinterior",
            output_path=test_path
        )
        # Show file info
        size = os.path.getsize(test_path)
        print(f"✅ Imagen de prueba: {test_path} ({size/1024:.1f} KB)")
        print(f"   Para generar las 100: python3 image_gen.py all")
