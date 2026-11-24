"""News in one image: Tuesday 24 November 2026.

Draws a one-page editorial front page that sums up the day's world news
and writes it deterministically to /output/entry.png (PNG, 1024x1024).

No network, no randomness, no clock: the same bytes come out every run.
Every headline below was first reported on 24 November 2026 (AP, Reuters,
BBC, UN News, Just Security early edition): Nvidia reinstates Jensen Huang
as CEO and its shares jump 31%; Iran says tankers hit mines in the Strait
of Hormuz; Israel kills Hamas security chief Naeem Abu Nahel in Gaza; an
overnight strike on Zaporizhzhia kills 2 and wounds 40; the ICJ finds
Myanmar guilty of genocide against the Rohingya; NATO vows to defend
space after reports of a Russian nuclear-armed satellite; a car bomb
injures 23 in Villavicencio, Colombia; Saudi strikes in Yemen kill about
25 and the UK sanctions the Houthis; the US blacklists Megaspeed; South
Korea offers rewards to catch AI cheating in its college exam.

Run:  python3 main.py   (writes /output/entry.png)
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, "1" = ink. Only the characters this page uses.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "01010", "01010", "00100", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "·": ("00000", "00000", "01100", "01100", "00000", "00000", "00000"),
    "—": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "–": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
}
BLANK = ("00000",) * 7


def char_w(scale):
    return 6 * scale


def text_w(text, scale):
    return len(text) * char_w(scale) - scale if text else 0


def draw_text(buf, text, x, y, scale, color):
    """Draw upper-case text; unknown glyphs render blank."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch.upper(), BLANK)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(buf, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += char_w(scale)
    return cx


def text_center(buf, cx, y, text, scale, color):
    draw_text(buf, text, cx - text_w(text, scale) // 2, y, scale, color)


def wrap(text, scale, max_w):
    """Greedy word wrap; returns lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
def new_canvas(color):
    buf = bytearray(W * H * 3)
    r, g, b = color
    for i in range(0, len(buf), 3):
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b
    return buf


def fill_rect(buf, x, y, w, h, color):
    r, g, b = color
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            o = base + (xx - x0) * 3
            buf[o] = r
            buf[o + 1] = g
            buf[o + 2] = b


def frame(buf, x, y, w, h, color, t=2):
    fill_rect(buf, x, y, w, t, color)
    fill_rect(buf, x, y + h - t, w, t, color)
    fill_rect(buf, x, y, t, h, color)
    fill_rect(buf, x + w - t, y, t, h, color)


def fill_circle(buf, cx, cy, rad, color):
    for yy in range(cy - rad, cy + rad + 1):
        dx = int((rad * rad - (yy - cy) ** 2) ** 0.5)
        fill_rect(buf, cx - dx, yy, dx * 2 + 1, 1, color)


def ring(buf, cx, cy, rad, color, t=3):
    for yy in range(cy - rad, cy + rad + 1):
        dx = int((rad * rad - (yy - cy) ** 2) ** 0.5)
        dx2 = int(max(0, (rad - t) ** 2 - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) < rad - t else 0
        fill_rect(buf, cx - dx, yy, dx - dx2, 1, color)
        fill_rect(buf, cx + dx2 + 1, yy, dx - dx2, 1, color)


def hline(buf, x, y, w, color, t=2):
    fill_rect(buf, x, y, w, t, color)


def vline(buf, x, y, h, color, t=2):
    fill_rect(buf, x, y, t, h, color)


# ---------------------------------------------------------------- png
def write_png(buf, path):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += buf[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- palette
PAPER = (246, 241, 231)
CARD = (255, 255, 255)
INK = (20, 20, 20)
NAVY = (18, 38, 66)
RED = (178, 34, 34)
BLUE = (29, 78, 137)
GREEN = (27, 94, 32)
LGREEN = (200, 230, 201)
GOLD = (176, 124, 30)
TEAL = (14, 116, 110)
PURPLE = (88, 48, 128)
GREY = (90, 90, 90)
LGREY = (232, 228, 220)


def draw_chip(buf, x, y, w, h):
    """A green computer chip with gold pins and a rising arrow."""
    fill_rect(buf, x, y, w, h, LGREEN)
    cx, cy = x + w // 2, y + h // 2
    for i in range(4):
        px = cx - 33 + i * 22
        fill_rect(buf, px, cy - 30, 7, 7, GOLD)
        fill_rect(buf, px, cy + 23, 7, 7, GOLD)
        py = cy - 33 + i * 22
        fill_rect(buf, cx - 58, py, 7, 7, GOLD)
        fill_rect(buf, cx + 51, py, 7, 7, GOLD)
    fill_rect(buf, cx - 51, cy - 23, 102, 46, GREEN)
    frame(buf, cx - 51, cy - 23, 102, 46, INK, 3)
    fill_rect(buf, cx - 24, cy - 12, 48, 24, (20, 60, 25))
    draw_text(buf, "NV", cx - 21, cy - 9, 2, (255, 255, 255))
    ax = x + w - 16
    fill_rect(buf, ax - 2, y + 14, 4, h - 26, INK)
    for i in range(10):
        fill_rect(buf, ax - 2 - i, y + 14 + i, 4, 4, INK)
        fill_rect(buf, ax - 2 + i, y + 14 + i, 4, 4, INK)


def draw_ship(buf, x, y, w, h):
    """A tanker on a strait, with a mine bobbing beside it."""
    fill_rect(buf, x, y, w, h, (174, 205, 226))
    sea = y + h - 24
    fill_rect(buf, x, sea, w, 24, BLUE)
    hline(buf, x + 10, sea + 8, w - 20, CARD, 2)
    hline(buf, x + 24, sea + 16, w - 48, CARD, 2)
    hx, hy = x + w // 2 - 46, sea - 6
    # hull: tapered block
    fill_rect(buf, hx, hy, 92, 12, INK)
    fill_rect(buf, hx + 8, hy - 14, 60, 14, INK)
    fill_rect(buf, hx + 30, hy - 30, 6, 16, INK)
    fill_rect(buf, hx + 36, hy - 30, 20, 10, RED)
    # mine: spiked circle
    mx, my = x + 26, sea - 12
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        fill_rect(buf, mx + dx * 10 - 2, my + dy * 10 - 2, 5, 5, INK)
    fill_circle(buf, mx, my, 9, INK)
    fill_circle(buf, mx, my, 4, RED)


def draw_satellite(buf, x, y, w, h):
    """A satellite under a warning triangle, on night blue."""
    fill_rect(buf, x, y, w, h, NAVY)
    for sx, sy in ((16, 12), (34, 26), (w - 20, 14), (w - 40, 28)):
        fill_rect(buf, x + sx, y + sy, 3, 3, CARD)
    cx, cy = x + w // 2 - 14, y + h // 2
    fill_rect(buf, cx - 52, cy - 9, 38, 18, BLUE)
    fill_rect(buf, cx + 34, cy - 9, 38, 18, BLUE)
    fill_rect(buf, cx - 14, cy - 12, 42, 24, GREY)
    frame(buf, cx - 14, cy - 12, 42, 24, INK, 2)
    fill_rect(buf, cx + 28, cy - 12, 6, 24, GOLD)
    # warning triangle bottom-right
    tx, ty = x + w - 26, y + h - 24
    for i in range(15):
        fill_rect(buf, tx - 14 + i, ty - 14 + i, 28 - 2 * i, 2, RED)
    draw_text(buf, "!", tx - 3, ty - 8, 2, CARD)


def draw_scales(buf, x, y, w, h):
    """Balanced scales of justice on pale gold."""
    fill_rect(buf, x, y, w, h, (246, 226, 180))
    cx, cy = x + w // 2, y + h // 2 + 4
    vline(buf, cx, cy - 26, 52, INK, 4)
    hline(buf, cx - 40, cy - 26, 80, INK, 4)
    fill_circle(buf, cx, cy - 26, 4, INK)
    for sgn in (-1, 1):
        px = cx + sgn * 40
        vline(buf, px, cy - 26, 18, INK, 2)
        for i in range(15):
            fill_rect(buf, px - 15 + i, cy - 8 + i, 30 - 2 * i, 2, GOLD)
        hline(buf, px - 15, cy - 8, 30, INK, 2)
    hline(buf, cx - 20, cy + 26, 40, INK, 5)


def draw_flame(buf, x, y, w, h):
    """A blast flash: concentric gold diamonds on dark red."""
    fill_rect(buf, x, y, w, h, (120, 20, 20))
    cx, cy = x + w // 2, y + h // 2
    for r, col in ((30, GOLD), (21, (240, 180, 40)), (12, CARD)):
        for i in range(-r, r + 1):
            fill_rect(buf, cx + i, cy - (r - abs(i)) // 2, 1, r - abs(i), col)


def draw_globe(buf, x, y, w, h):
    """A cracked globe: blue seas, green land, red fault line."""
    fill_rect(buf, x, y, w, h, (210, 225, 238))
    cx, cy = x + w // 2, y + h // 2
    fill_circle(buf, cx, cy, 34, BLUE)
    ring(buf, cx, cy, 34, INK, 3)
    fill_circle(buf, cx - 12, cy - 10, 9, GREEN)
    fill_circle(buf, cx + 12, cy + 10, 8, GREEN)
    fill_circle(buf, cx + 8, cy - 14, 5, GREEN)
    # red zig-zag crack
    pts = [(cx - 30, cy - 12), (cx - 10, cy + 4), (cx + 6, cy - 10),
           (cx + 26, cy + 8)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(n + 1):
            fill_rect(buf, x0 + (x1 - x0) * s // n - 2,
                      y0 + (y1 - y0) * s // n - 2, 5, 5, RED)


# ---------------------------------------------------------------- story cards
def card(buf, x, y, w, h, tag, tag_color, title, body, draw_pic):
    fill_rect(buf, x, y, w, h, CARD)
    frame(buf, x, y, w, h, INK, 2)
    fill_rect(buf, x, y, w, 8, tag_color)
    pic_h = 62
    draw_pic(buf, x + 2, y + 10, w - 4, pic_h)
    ty = y + 10 + pic_h + 8
    draw_text(buf, tag, x + 12, ty, 2, tag_color)
    ty += 22
    for line in wrap(title, 3, w - 24):
        draw_text(buf, line, x + 12, ty, 3, INK)
        ty += 26
    ty += 4
    for line in wrap(body, 2, w - 24):
        draw_text(buf, line, x + 12, ty, 2, GREY)
        ty += 15


def main():
    buf = new_canvas(PAPER)
    m = 28  # margin

    # ---- masthead
    text_center(buf, W // 2, 22, "THE WORLD IN ONE DAY", 7, NAVY)
    hline(buf, m, 92, W - 2 * m, INK, 3)
    text_center(buf, W // 2, 102, "TUESDAY 24 NOVEMBER 2026", 3, RED)
    hline(buf, m, 132, W - 2 * m, INK, 2)

    # ---- hero: Nvidia
    hx, hy, hw, hh = m, 146, W - 2 * m, 240
    fill_rect(buf, hx, hy, hw, hh, CARD)
    frame(buf, hx, hy, hw, hh, INK, 3)
    fill_rect(buf, hx, hy, hw, 8, GREEN)
    draw_text(buf, "TOP STORY  ·  TECHNOLOGY", hx + 18, hy + 22, 2, GREEN)
    draw_text(buf, "HUANG IS BACK", hx + 18, hy + 48, 8, INK)
    draw_text(buf, "NVIDIA REINSTATES JENSEN HUANG", hx + 18, hy + 116, 3, INK)
    draw_text(buf, "AS CHIEF EXECUTIVE", hx + 18, hy + 142, 4, INK)
    ty = hy + 178
    for line in wrap("THE BOARD BROUGHT BACK ITS FOUNDER LESS THAN TWO "
                     "WEEKS AFTER HE RESIGNED. MARKETS CHEERED.",
                     2, 600):
        draw_text(buf, line, hx + 18, ty, 2, GREY)
        ty += 17
    # right: chip + jump
    px, py, pw, ph = hx + 640, hy + 22, 300, 120
    draw_chip(buf, px, py, pw, ph)
    draw_text(buf, "+31%", px + 8, hy + 150, 7, GREEN)
    draw_text(buf, "NVIDIA SHARES IN ONE DAY", px + 8, hy + 206, 2, GREY)
    draw_text(buf, "S&P 500 +4.73%  ·  NIKKEI +3.91%", hx + 18, hy + 218, 2, NAVY)

    # ---- grid of six stories: 3 cols x 2 rows
    cw, ch, gap = 304, 196, 16
    y0, y1 = 400, 612
    card(buf, m, y0, cw, ch, "HORMUZ", RED,
         "TANKERS HIT MINES IN HORMUZ",
         "TEHRAN TIGHTENS STRAIT CURBS.", draw_ship)
    card(buf, m + cw + gap, y0, cw, ch, "GAZA", RED,
         "HAMAS SECURITY CHIEF KILLED",
         "ISRAELI STRIKE IN GAZA KILLS SEVEN.", draw_flame)
    card(buf, m + 2 * (cw + gap), y0, cw, ch, "UKRAINE", BLUE,
         "ZAPORIZHZHIA STRIKE KILLS 2",
         "OVERNIGHT HIT ON FLATS WOUNDS 40.", draw_globe)
    card(buf, m, y1, cw, ch, "JUSTICE", PURPLE,
         "MYANMAR GUILTY OF GENOCIDE",
         "ICJ LANDMARK RULING.", draw_scales)
    card(buf, m + cw + gap, y1, cw, ch, "SPACE", NAVY,
         "NATO VOWS TO DEFEND SPACE",
         "AFTER REPORTS OF A RUSSIAN SPACE WEAPON.", draw_satellite)
    card(buf, m + 2 * (cw + gap), y1, cw, ch, "AMERICAS", TEAL,
         "CAR BOMB INJURES 23",
         "BLAST IN VILLAVICENCIO, COLOMBIA.", draw_flame)

    # ---- also today band
    bx, by, bw, bh = m, 814, W - 2 * m, 118
    fill_rect(buf, bx, by, bw, bh, NAVY)
    draw_text(buf, "ALSO TODAY", bx + 16, by + 12, 3, GOLD)
    items = [
        ("US BLACKLISTS MEGASPEED", "CLOUD FIRM IN THE NVIDIA SCANDAL."),
        ("SEOUL PAYS TO CATCH AI CHEATS", "$375,000 REWARDS TO CATCH CHEATS."),
        ("YEMEN: 25 DEAD IN STRIKES", "SAUDI STRIKES; UK SANCTIONS HOUTHIS."),
        ("INDONESIA FACTORY FIRE", "26 KILLED, DOZENS MISSING IN BANTEN."),
    ]
    col_w = (bw - 32) // 2
    for i, (head, sub) in enumerate(items):
        ix = bx + 16 + (i % 2) * col_w
        iy = by + 48 + (i // 2) * 36
        draw_text(buf, head, ix, iy, 2, CARD)
        sy = iy + 16
        for line in wrap(sub, 2, col_w - 12):
            draw_text(buf, line, ix, sy, 2, (170, 190, 210))
            sy += 14

    # ---- footer
    hline(buf, m, 948, W - 2 * m, INK, 2)
    text_center(buf, W // 2, 960,
                "24 NOVEMBER 2026  ·  TEN STORIES THAT DEFINED THE DAY", 2, NAVY)
    text_center(buf, W // 2, 984,
                "SOURCES: AP  ·  REUTERS  ·  BBC  ·  UN NEWS  ·  JUST SECURITY",
                2, GREY)

    out = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    size = write_png(buf, out)
    print("wrote %s %d bytes" % (out, size))


if __name__ == "__main__":
    main()
