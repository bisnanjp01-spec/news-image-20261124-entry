#!/usr/bin/env python3
"""news-image-20261124: one image summing up Tuesday 24 November 2026.

Draws a newspaper front page (1024x1024 PNG) with six real stories of the
day, each with a short factual label and a simple pictogram, plus a briefs
strip. Pure Python 3.13 standard library: no network, no files read, no
randomness, no clock. The same bytes are written on every run.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
WHITE = (255, 255, 255)
INK = (17, 17, 17)
NAVY = (20, 33, 61)
RED = (193, 39, 45)
BLUE = (37, 99, 168)
SKY = (174, 205, 226)
GREEN = (46, 125, 50)
LGREEN = (198, 226, 190)
GOLD = (217, 164, 65)
LGOLD = (246, 226, 180)
GRAY = (110, 110, 110)
LGRAY = (228, 228, 228)
DARKGREEN = (27, 94, 32)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, '#' = on. Uppercase, digits and punctuation only;
# all copy is written in capitals so the whole page uses this one font.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".####", ".....", ".####", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "*": (".....", ".#.#.", "..#..", ".###.", "..#..", ".#.#.", "....."),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y - t // 2, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x - t // 2, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = x1 - x0, y1 - y0
        n = max(abs(dx), abs(dy), 1)
        for s in range(n + 1):
            x = x0 + dx * s // n
            y = y0 + dy * s // n
            self.rect(x - t // 2, y - t // 2, t, t, c)

    def circle(self, cx, cy, r, c, fill=True):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            if fill:
                self.rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)
            else:
                self.set(cx - dx, cy + dy, c)
                self.set(cx + dx, cy + dy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, t)))
            self.rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)

    def triangle(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)

        def sign(ax, ay, bx, by, cx, cy):
            return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)

        d = sign(x0, y0, x1, y1, x2, y2)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                a = sign(xx, yy, x0, y0, x1, y1)
                b = sign(xx, yy, x1, y1, x2, y2)
                cc = sign(xx, yy, x2, y2, x0, y0)
                if (d > 0 and a >= 0 and b >= 0 and cc >= 0) or (
                    d < 0 and a <= 0 and b <= 0 and cc <= 0
                ):
                    self.set(xx, yy, c)

    def star(self, cx, cy, r1, r2, points, c):
        pts = []
        for i in range(points * 2):
            r = r1 if i % 2 == 0 else r2
            a = math.pi * i / points - math.pi / 2
            pts.append(
                (int(cx + r * math.cos(a)), int(cy + r * math.sin(a)))
            )
        for i in range(points):
            self.triangle([pts[i * 2], pts[i * 2 + 1], (cx, cy)], c)
            self.triangle(
                [pts[i * 2 + 1], pts[(i * 2 + 2) % (points * 2)], (cx, cy)], c
            )

    # -- text -------------------------------------------------------------
    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def draw_text(self, x, y, s, scale, c):
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.rect(
                            x + col * scale, y + row * scale, scale, scale, c
                        )
            x += 6 * scale

    def text_center(self, cx, y, s, scale, c):
        self.draw_text(cx - self.text_width(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, max_w, scale):
        words = s.split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- pictures
def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, BLUE)
    cv.circle(cx, cy, r, INK, fill=False)
    cv.ellipse(cx - r // 3, cy - r // 4, r // 3, r // 5, GREEN)
    cv.ellipse(cx + r // 3, cy + r // 4, r // 4, r // 5, GREEN)
    cv.ellipse(cx + r // 5, cy - r // 2, r // 5, r // 6, GREEN)
    cv.ellipse(cx - r // 2, cy + r // 3, r // 5, r // 6, GREEN)
    # crack: a red zig-zag across the globe
    cv.line(cx - r + 6, cy - r // 3, cx - r // 4, cy + r // 6, RED, 5)
    cv.line(cx - r // 4, cy + r // 6, cx + r // 5, cy - r // 4, RED, 5)
    cv.line(cx + r // 5, cy - r // 4, cx + r - 6, cy + r // 3, RED, 5)


def draw_ship_strike(cv, x, y, w, h):
    # sea
    cv.rect(x, y, w, h, SKY)
    sea_y = y + h - 26
    cv.rect(x, sea_y, w, 26, BLUE)
    cv.line(x + 8, sea_y + 8, x + w - 8, sea_y + 8, WHITE, 2)
    cv.line(x + 20, sea_y + 17, x + w - 20, sea_y + 17, WHITE, 2)
    # ship hull + mast
    hx, hy = x + w // 2 - 52, sea_y - 8
    cv.triangle([(hx, hy), (hx + 104, hy), (hx + 88, hy + 16)], INK)
    cv.rect(hx + 14, hy + 16, 76, 8, INK)
    cv.vline(hx + 52, hy - 26, 26, INK, 3)
    cv.rect(hx + 52, hy - 26, 22, 12, RED)
    # drone above, dashed line down to the ship
    dx, dy = x + w - 52, y + 14
    cv.rect(dx - 10, dy - 3, 20, 6, INK)
    cv.circle(dx - 12, dy - 5, 4, INK)
    cv.circle(dx + 12, dy - 5, 4, INK)
    cv.line(dx, dy + 6, hx + 88, hy - 2, INK, 2)
    # explosion starburst on the hull
    cv.star(hx + 88, hy - 2, 16, 7, 8, GOLD)
    cv.star(hx + 88, hy - 2, 9, 4, 8, RED)


def draw_chip(cv, x, y, w, h):
    cv.rect(x, y, w, h, LGREEN)
    cx, cy = x + w // 2, y + h // 2
    # pins hugging the chip body only
    for i in range(4):
        px = cx - 39 + i * 22
        cv.rect(px, cy - 30, 7, 7, GOLD)
        cv.rect(px, cy + 23, 7, 7, GOLD)
        py = cy - 33 + i * 22
        cv.rect(cx - 58, py, 7, 7, GOLD)
        cv.rect(cx + 51, py, 7, 7, GOLD)
    cv.rect(cx - 51, cy - 23, 102, 46, GREEN)
    cv.rect(cx - 51, cy - 23, 102, 3, INK)
    cv.rect(cx - 51, cy + 20, 102, 3, INK)
    cv.rect(cx - 51, cy - 23, 3, 46, INK)
    cv.rect(cx + 48, cy - 23, 3, 46, INK)
    cv.rect(cx - 26, cy - 14, 52, 28, DARKGREEN)
    cv.text_center(cx, cy - 10, "NV", 2, WHITE)
    # bold up arrow on the right
    ax = x + w - 18
    cv.line(ax, y + h - 12, ax, y + 12, INK, 4)
    cv.line(ax, y + 12, ax - 9, y + 24, INK, 4)
    cv.line(ax, y + 12, ax + 9, y + 24, INK, 4)


def draw_satellite(cv, x, y, w, h):
    cv.rect(x, y, w, h, NAVY)
    # stars
    for sx, sy in [(14, 10), (30, 22), (w - 18, 12), (w - 34, 26), (w // 2, 8)]:
        cv.star(x + sx, y + sy, 4, 2, 4, WHITE)
    cx, cy = x + w // 2 - 20, y + h // 2
    # panels + body
    cv.rect(cx - 52, cy - 10, 40, 20, BLUE)
    cv.rect(cx + 34, cy - 10, 40, 20, BLUE)
    cv.line(cx - 12, cy, cx - 52, cy, GOLD, 2)
    cv.line(cx + 22, cy, cx + 34, cy, GOLD, 2)
    cv.rect(cx - 12, cy - 12, 34, 24, GRAY)
    cv.hline(cx - 12, cy - 12, 34, INK, 2)
    cv.hline(cx - 12, cy + 12, 34, INK, 2)
    cv.vline(cx - 12, cy - 12, 24, INK, 2)
    cv.vline(cx + 22, cy - 12, 24, INK, 2)
    cv.line(cx + 22, cy - 12, cx + 34, cy - 24, GOLD, 2)
    cv.circle(cx + 34, cy - 24, 3, GOLD)
    cv.circle(cx + 34, cy - 24, 3, GOLD)
    # red warning triangle
    tx, ty = x + w - 34, y + h - 30
    cv.triangle([(tx, ty - 14), (tx - 13, ty + 10), (tx + 13, ty + 10)], RED)
    cv.text_center(tx, ty - 8, "!", 2, WHITE)


def draw_scales(cv, x, y, w, h):
    cv.rect(x, y, w, h, LGOLD)
    cx, cy = x + w // 2, y + h // 2 + 4
    cv.vline(cx, cy - 26, 52, INK, 4)
    cv.line(cx - 40, cy - 26, cx + 40, cy - 26, INK, 4)
    cv.circle(cx, cy - 26, 4, INK)
    for sgn in (-1, 1):
        px = cx + sgn * 40
        cv.line(px, cy - 26, px, cy - 8, INK, 2)
        cv.triangle([(px - 16, cy - 8), (px + 16, cy - 8), (px, cy + 10)], GOLD)
        cv.line(px - 16, cy - 8, px + 16, cy - 8, INK, 2)
    cv.rect(cx - 20, cy + 26, 40, 5, INK)


def draw_virus(cv, x, y, w, h):
    cv.rect(x, y, w, h, (246, 214, 214))
    cx, cy = x + w // 2, y + h // 2
    for a in range(0, 360, 30):
        rad = math.radians(a)
        x1 = cx + int(20 * math.cos(rad))
        y1 = cy + int(20 * math.sin(rad))
        x2 = cx + int(30 * math.cos(rad))
        y2 = cy + int(30 * math.sin(rad))
        cv.line(x1, y1, x2, y2, RED, 3)
        cv.circle(x2, y2, 3, RED)
    cv.circle(cx, cy, 20, RED)
    cv.circle(cx - 6, cy - 5, 4, WHITE)
    cv.circle(cx + 7, cy + 6, 3, WHITE)
    cv.circle(cx + 6, cy - 8, 2, WHITE)


# ---------------------------------------------------------------- layout
def panel(cv, x, y, w, h, kicker, headline, sub, draw_pic, pic_bg):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK)  # border via outline below
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)
    pic_h = 64
    cv.rect(x + 2, y + 2, w - 4, pic_h, pic_bg)
    draw_pic(cv, x + 2, y + 2, w - 4, pic_h)
    ty = y + pic_h + 12
    cv.draw_text(x + 12, ty, kicker, 2, RED)
    ty += 24
    for line in headline:
        cv.draw_text(x + 12, ty, line, 3, INK)
        ty += 26
    ty += 4
    for line in cv.wrap(sub, w - 24, 2):
        cv.draw_text(x + 12, ty, line, 2, INK)
        ty += 17


def main():
    cv = Canvas(W, H, PAPER)

    # masthead
    cv.text_center(W // 2, 26, "THE WORLD IN ONE DAY", 5, NAVY)
    cv.hline(24, 92, W - 48, INK, 3)
    cv.text_center(W // 2, 100, "TUESDAY 24 NOVEMBER 2026", 3, RED)
    cv.hline(24, 128, W - 48, INK, 2)

    # lead story: COP31 collapse
    lx, ly, lw, lh = 24, 142, W - 48, 288
    cv.rect(lx, ly, lw, lh, WHITE)
    cv.rect(lx, ly, lw, 2, INK)
    cv.rect(lx, ly + lh - 2, lw, 2, INK)
    cv.rect(lx, ly, 2, lh, INK)
    cv.rect(lx + lw - 2, ly, 2, lh, INK)
    cv.draw_text(lx + 16, ly + 16, "CLIMATE - ANTALYA, TURKEY", 2, RED)
    cv.draw_text(lx + 16, ly + 46, "CLIMATE TALKS", 4, INK)
    cv.draw_text(lx + 16, ly + 82, "COLLAPSE", 4, INK)
    ty = ly + 132
    for line in cv.wrap(
        "COP31 ENDS WITH NO DEAL AFTER NATIONS SPLIT OVER FOSSIL FUELS. "
        "MORE THAN 90 COUNTRIES REJECTED THE FINAL TEXT.",
        560, 2,
    ):
        cv.draw_text(lx + 16, ty, line, 2, INK)
        ty += 17
    cv.draw_text(lx + 16, ty + 10, "THE SUMMIT RAN ALMOST 50 HOURS", 2, NAVY)
    cv.draw_text(lx + 16, ty + 30, "INTO OVERTIME BEFORE IT FAILED.", 2, NAVY)
    draw_globe(cv, lx + lw - 150, ly + 130, 92)
    cv.rect(lx + lw - 268, ly + 218, 150, 34, RED)
    cv.text_center(lx + lw - 193, ly + 226, "NO DEAL", 3, WHITE)

    # row 2: three stories
    cols = [24, 353, 682]
    pw, ph = 317, 252
    panel(
        cv, cols[0], 442, pw, ph,
        "CONFLICT - LIBYA",
        ["UKRAINE HITS", "RUSSIAN SHIPS", "OFF LIBYA"],
        "KYIV SAYS ITS DRONES SANK ONE WARSHIP AT BENGHAZI.",
        draw_ship_strike, SKY,
    )
    panel(
        cv, cols[1], 442, pw, ph,
        "TECHNOLOGY",
        ["NVIDIA BRINGS", "BACK HUANG"],
        "HUANG RETURNS AS CHIEF DAYS AFTER RESIGNING, AFTER "
        "PRESSURE FROM TRUMP.",
        draw_chip, LGREEN,
    )
    panel(
        cv, cols[2], 442, pw, ph,
        "SECURITY - EUROPE",
        ["RUSSIA WARNS", "ESTONIA OF", "OPEN WAR"],
        "MOSCOW WARNS ESTONIA OF OPEN WAR. ALLIES FEAR A NUCLEAR "
        "WEAPON IN SPACE.",
        draw_satellite, NAVY,
    )

    # row 3: two stories + briefs
    panel(
        cv, cols[0], 706, pw, ph,
        "JUSTICE - THE HAGUE",
        ["MYANMAR GUILTY", "OF GENOCIDE"],
        "THE COURT RULES MYANMAR COMMITTED GENOCIDE. 14 NATIONS "
        "BACK THE RULING.",
        draw_scales, LGOLD,
    )
    panel(
        cv, cols[1], 706, pw, ph,
        "HEALTH - UNITED STATES",
        ["US LOSES", "MEASLES-FREE", "STATUS"],
        "AMERICA LOSES ITS MEASLES ELIMINATION STATUS AFTER MORE "
        "THAN 25 YEARS.",
        draw_virus, (246, 214, 214),
    )
    # briefs panel
    bx, by = cols[2], 706
    cv.rect(bx, by, pw, ph, WHITE)
    cv.rect(bx, by, pw, 2, INK)
    cv.rect(bx, by + ph - 2, pw, 2, INK)
    cv.rect(bx, by, 2, ph, INK)
    cv.rect(bx + pw - 2, by, 2, ph, INK)
    cv.rect(bx + 2, by + 2, pw - 4, 40, NAVY)
    cv.text_center(bx + pw // 2, by + 12, "IN BRIEF", 3, WHITE)
    briefs = [
        "NEPAL: 5.6 QUAKE STRIKES NEAR THE CHINA BORDER.",
        "SANOFI AGREES TO BUY US BIOTECH INSMED FOR $41BN.",
        "US STATES SUE MUSK FIRMS OVER GROK IMAGES.",
    ]
    ty = by + 58
    for b in briefs:
        cv.draw_text(bx + 12, ty, "*", 2, RED)
        for line in cv.wrap(b, pw - 40, 2):
            cv.draw_text(bx + 28, ty, line, 2, INK)
            ty += 17
        ty += 12

    # footer
    cv.hline(24, 976, W - 48, INK, 2)
    cv.text_center(
        W // 2, 986, "THE DAY IN SIX STORIES - TUESDAY 24 NOVEMBER 2026", 2, NAVY
    )

    # encode PNG (filter 0, deterministic)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += cv.px[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s %d bytes" % (path, len(png)))


if __name__ == "__main__":
    main()
