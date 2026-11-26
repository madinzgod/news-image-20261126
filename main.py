#!/usr/bin/env python3
"""news-image-20261126 V3: one image summing up Thursday 26 November 2026.

Python 3.13, standard library only. No network, no time, no randomness:
the same bytes come out of every run. Writes entry.png into
$MAKEFUN_OUTPUT_DIR (default /output).

Design (authored fresh for this edition): dark navy broadsheet, cream
masthead, lead = Thursday's Asia markets rout with a bar chart plus a
skyline strip, rail = London Tube strike, four features (Kim / Macy's
parade / nor'easter / EU summit), three-column wire of 31 briefs,
footer with the make.fun ref. Own 5x7 pixel typeface as data; own PNG
writer.

V3 changes (see work/v3/AUDIT-V3.md; every change measured first):
- V1 glyphs KEPT: no font variant beat the 85% sheet baseline —
  bold-on-baseline 71%, fringe-AA 40%, redrawn D/N 74%/84%, singles
  K/R/B/M/6 all 85-86% (noise). The typeface stays.
- Lead sub/body 2 -> 3 (rewrapped to 35 chars, pitch 25, head at
  y148): fills the lead dead space; 300px wire OCR 3% -> 6%.
- Rail head 3 -> 4: "LONDON ... STRIKE FROM" now reads at 300px.
- Masthead/date scale-ups (6/4) REVERTED: the large-text sheet
  promised 28% -> 64%, but on the real page the date line vanished
  from the 300px transcript at both scales (tesseract segmentation,
  not legibility); page-level large text tied V2 at 32% either way,
  so the V2 scales stay.
- BoE wire fact corrected 21:30 -> 10:30 UK (Bank of England primary
  source: FSR published 10:30am).
- "THE WIRE" label cut into the divider rule at zero vertical cost.
- Skyline buildings brightened (10,20,36) -> (32,58,92) + 2nd window
  row. Evening sweep: nothing had landed (Europa League/NFL/BoE/EU
  Council all Thu evening) — nothing added.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY = (16, 30, 51)        # page background
NAVY2 = (22, 42, 68)       # panel background
CREAM = (245, 241, 230)    # main text on navy
CREAM_DIM = (214, 208, 192)
GOLD = (242, 183, 5)       # date band, accents
RED = (229, 72, 77)        # down bars, rail band
RED_DK = (178, 34, 44)     # rail band background
GREEN = (46, 196, 182)     # up bars
BLUE = (96, 165, 250)      # politics chip
ORANGE = (251, 146, 60)    # sport chip
TEAL = (45, 212, 191)      # world chip
PURPLE = (192, 132, 252)   # science chip
PAPER = (245, 241, 230)    # masthead background
INK = (16, 30, 51)         # text on paper
GREY = (120, 130, 145)     # hairlines

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, each a 5-bit int (bit 4 = leftmost pixel).
F = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    '-': (0, 0, 0, 0x0E, 0, 0, 0),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '%': (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '+': (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    '=': (0, 0, 0x0E, 0, 0x0E, 0, 0),
    '_': (0, 0, 0, 0, 0, 0, 0x1F),
    '*': (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
}
BLANK = (0, 0, 0, 0, 0, 0, 0)


def tw(s, scale):
    """Pixel width of text s at scale."""
    return len(s) * 6 * scale - scale


def wrap(text, max_chars):
    """Greedy word wrap; returns list of lines, each <= max_chars."""
    lines, cur = [], ""
    for word in text.split(" "):
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Img:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        # Filled triangle via scanline interpolation.
        ys = sorted([(y0, x0), (y1, x1), (y2, x2)])
        (ya, xa), (yb, xb), (yc, xc) = ys
        if yc == ya:
            return
        for y in range(ya, yc + 1):
            if y < yb:
                t1 = (y - ya) / (yb - ya) if yb != ya else 0
                xa_y = xa + (xb - xa) * t1
            else:
                t1 = (y - yb) / (yc - yb) if yc != yb else 0
                xa_y = xb + (xc - xb) * t1
            t2 = (y - ya) / (yc - ya)
            xb_y = xa + (xc - xa) * t2
            lo, hi = int(min(xa_y, xb_y)), int(max(xa_y, xb_y))
            for x in range(lo, hi + 1):
                self.set(x, y, c)

    def text(self, x, y, s, c, scale):
        s = s.upper()
        cx = x
        for ch in s:
            g = F.get(ch, BLANK)
            for r in range(7):
                bits = g[r]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_c(self, x, y, w, s, c, scale):
        self.text(x + max(0, (w - tw(s, scale)) // 2), y, s, c, scale)


# ---------------------------------------------------------------- PNG out
def write_png(img, path):
    raw = bytearray()
    stride = img.w * 3
    for y in range(img.h):
        raw.append(0)
        raw += img.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", img.w, img.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", comp)
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


# ---------------------------------------------------------------- content
# Lead: Thursday Asia markets rout (fresh Thu data, as of 01:39 UTC).
LEAD_HEAD = "ASIA SINKS AGAIN"
LEAD_SUB = "TARIFF FEARS AND AI DOUBTS SEND MARKETS DOWN FOR A SECOND DAY"
LEAD_BODY = ("KOSPI OPENS 3.94% LOWER AND FALLS 4.6% AS THE EXCHANGE "
             "TRIPS A SIDECAR. SAMSUNG -6.7%, SK HYNIX -6.6%. NIKKEI "
             "-2.4%, TAIEX -4.5%. ONLY HONG KONG RISES, +0.8%.")
BARS = [("KOSPI", -4.6, RED), ("NIKKEI", -2.4, RED), ("TAIEX", -4.5, RED),
        ("HANG SENG", +0.8, GREEN), ("SHANGHAI", -0.7, RED)]

RAIL_HEAD = "LONDON TUBE STRIKE FROM MIDDAY"
RAIL_BODY = ("RMT DRIVERS WALK OUT 24 HOURS; CIRCLE, PICCADILLY, "
             "WATERLOO AND CITY LINES SHUT.")

# Features: (scene, kicker, headline, body lines)
FEATURES = [
    ("MISSILE", "PYONGYANG", "KIM SPREADS NUCLEAR ARMS",
     ["KIM JONG UN ORDERS", "TACTICAL NUKES", "WIDER, KCNA SAYS"]),
    ("BALLOON", "NEW YORK", "MACY'S PARADE MOVED TO SAT",
     ["100TH PARADE", "POSTPONED, STORM", "HITS NYC"]),
    ("STORM", "NEW YORK", "STORM HITS 250 MILLION",
     ["60 MPH GUSTS", "250M IN PATH"]),
    ("STARS", "BRUSSELS", "EU MEETS ON UKRAINE CASH",
     ["LEADERS GATHER", "THU-FRI ON BUDGET", "AND 2027 AID"]),
]

CHIP = {"WAR": RED, "POLITICS": BLUE, "BUSINESS": GOLD, "WORLD": TEAL,
        "SCIENCE": PURPLE, "SPORT": ORANGE}

# Wire: (beat, headline, fact) - each line <= 26 chars at scale 2.
WIRE = [
    ("POLITICS", "TAIWAN TARIFF 15% LOWEST", "NOT STACKED ON MFN DUTIES"),
    ("POLITICS", "OVER-70S FACE EYE TESTS", "PROPOSED IN UK PAPERS"),
    ("POLITICS", "BADENOCH WANTS APOLOGY", "OVER INFLUENCERS AT NO 10"),
    ("POLITICS", "MOD READIES FOR CONFLICT", "TELEGRAPH FRONT PAGE"),
    ("POLITICS", "CABINET SPLIT ON MILIBAND", "INDEPENDENT FRONT PAGE"),
    ("POLITICS", "BBC ANTISEMITISM INQUIRY", "TIMES: WORKPLACE INQUIRY"),
    ("POLITICS", "INDIA CONSTITUTION DAY", "SAMVIDHAN DIVAS, 26 NOV"),
    ("POLITICS", "INDIA AIDS NEPAL", "RS 15,000 CR TO NEPAL"),
    ("POLITICS", "IITS ADD 6,000 TECH SEATS", "ROBOTICS, AI, SPACE, 2027"),
    ("POLITICS", "INDIA SPACE ECONOMY $45B", "FROM $9B WITHIN A DECADE"),
    ("WORLD", "CHINA POLICE TO AUSTRALIA", "HUNT ATTACK SUSPECT"),
    ("BUSINESS", "US MARKETS SHUT TODAY", "CLOSED FOR THANKSGIVING"),
    ("BUSINESS", "FLIPKART CEO TO STEP DOWN", "LEAVES IN DECEMBER"),
    ("BUSINESS", "PHILIPPINE STOCKS +0.68%", "PSEI AT 5,493.41 THURSDAY"),
    ("BUSINESS", "MANILA RAISES $1.26B", "STAGFLATION RISK, GDP 2.5"),
    ("BUSINESS", "BANK OF ENGLAND REPORT", "STABILITY REPORT 10:30 UK"),
    ("BUSINESS", "POUNDLAND: 11,000 JOBS", "IN ADMINISTRATION"),
    ("WORLD", "KING TIDES FLOOD PACIFICA", "ROADS SHUT ON CALIF COAST"),
    ("WORLD", "ROYAL BREAK-IN: TWO HELD", "VIA DRAINPIPE, PAPERS SAY"),
    ("WORLD", "81.5M TRAVEL FOR HOLIDAY", "NEARLY 6M FLY, $800 FARES"),
    ("BUSINESS", "OPEC+ MEETS SUNDAY", "2027 QUOTAS ON THE TABLE"),
    ("SCIENCE", "MOSQUITOES CUT VIRUS 68%", "WOLBACHIA TRIAL IN BRAZIL"),
    ("SCIENCE", "RECORD TEMPERATURE STREAK", "GUARDIAN FRONT PAGE"),
    ("BUSINESS", "BRENT $94.82, GOLD $3,573", "WED CLOSES, REPORTED THU"),
    ("SPORT", "BEARS AT LIONS, 1PM ET", "BOTH 8-2, NFC NORTH LEAD"),
    ("SPORT", "EAGLES AT COWBOYS 4:30", "THANKSGIVING GAME TWO"),
    ("SPORT", "CHIEFS AT BILLS 8:20PM", "MAHOMES VS ALLEN"),
    ("SPORT", "IPL AUCTION DRAWS 1,220", "REGISTRATIONS FOR 2027"),
    ("SPORT", "SOORYAVANSHI 204 OFF 53", "AGAINST UAE IN CRICKET"),
    ("SPORT", "GUKESH FACES SINDAROV", "WORLD CHESS CROWN, GENEVA"),
    ("SPORT", "BRITAIN V GERMANY, DAVIS", "QUARTER-FINAL TONIGHT"),
]


# ---------------------------------------------------------------- scenes
def scene_missile(im, x, y, w, h):
    # h = 40 box. Thicker body than V1 (16 wide).
    cx = x + w // 2
    im.tri(cx - 8, y + 12, cx + 8, y + 12, cx, y + 2, CREAM)
    im.rect(cx - 8, y + 12, 16, 16, CREAM)
    im.tri(cx - 8, y + 24, cx - 21, y + 34, cx - 8, y + 28, RED)
    im.tri(cx + 8, y + 24, cx + 21, y + 34, cx + 8, y + 28, RED)
    im.tri(cx - 6, y + 28, cx + 6, y + 28, cx, y + 38, GOLD)
    im.disc(cx, y + 18, 3, NAVY2)


def scene_balloon(im, x, y, w, h):
    # h = 40 box. Bigger envelope than V1 (r 15 in a 40px box).
    cx = x + w // 2
    im.disc(cx, y + 16, 15, RED)
    im.disc(cx - 5, y + 13, 5, (255, 120, 120))
    im.line(cx - 5, y + 29, cx - 3, y + 32, CREAM)
    im.line(cx + 5, y + 29, cx + 3, y + 32, CREAM)
    im.rect(cx - 6, y + 32, 12, 6, GOLD)
    im.disc(x + 16, y + 5, 6, GREY)
    im.disc(x + w - 18, y + 7, 6, GREY)


def scene_storm(im, x, y, w, h):
    # h = 40 box. Cloud + lightning + rain, all inside the box.
    cx = x + w // 2
    im.disc(cx - 10, y + 12, 10, GREY)
    im.disc(cx + 6, y + 9, 11, GREY)
    im.disc(cx + 16, y + 14, 8, GREY)
    im.rect(cx - 22, y + 17, 44, 5, GREY)
    im.line(cx + 2, y + 24, cx - 5, y + 31, GOLD)
    im.line(cx - 5, y + 31, cx + 2, y + 31, GOLD)
    im.line(cx + 2, y + 31, cx - 5, y + 38, GOLD)
    for dx in (-18, -6, 6, 18):
        im.vline(cx + dx, y + 26, 8, BLUE)


def scene_stars(im, x, y, w, h):
    import math
    cx, cy = x + w // 2, y + 20
    r = 17
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx = int(cx + r * math.cos(a))
        sy = int(cy + r * math.sin(a))
        im.disc(sx, sy, 2, GOLD)
    im.disc(cx, cy, 2, GOLD)


SCENES = {"MISSILE": scene_missile, "BALLOON": scene_balloon,
          "STORM": scene_storm, "STARS": scene_stars}


# ---------------------------------------------------------------- build
def build():
    im = Img(W, H, NAVY)

    # Masthead.
    im.rect(0, 0, W, 86, PAPER)
    im.text_c(0, 18, W, "THE WORLD'S NEWS", INK, 5)
    im.hline(0, 86, W, RED)
    im.rect(0, 87, W, 3, GOLD)

    # Date band.
    im.text_c(0, 100, W, "THURSDAY 26 NOVEMBER 2026", GOLD, 3)

    # Lead.
    lx, lw = 16, 636
    im.text(lx, 148, LEAD_HEAD, CREAM, 4)
    y = 148 + 7 * 4 + 12
    for ln in wrap(LEAD_SUB, 35):
        im.text(lx, y, ln, GOLD, 3)
        y += 25
    y += 6
    for ln in wrap(LEAD_BODY, 35):
        im.text(lx, y, ln, CREAM_DIM, 3)
        y += 25
    # Chart panel.
    px, pw = 668, 340
    im.rect(px, 132, pw, 252, NAVY2)
    im.text(px + 12, 142, "ASIA, THU MORNING", GOLD, 2)
    im.text(px + 12, 160, "01:39 UTC", CREAM_DIM, 2)
    by = 196
    for name, val, col in BARS:
        im.text(px + 12, by, name, CREAM, 2)
        bar_x = px + 150
        bar_w = int(abs(val) * 26)
        im.rect(bar_x, by + 2, bar_w, 10, col)
        vtxt = ("+%.1f%%" % val) if val > 0 else ("%.1f%%" % val)
        im.text(bar_x + bar_w + 6, by, vtxt, CREAM, 2)
        by += 32
    # Skyline strip along the panel bottom: trading-city silhouette
    # with red down-arrows (the "US MARKETS CLOSED" line moved out —
    # wire #20 carries it). Panel bottom edge is y=384.
    base = 382
    sky = [(12, 20), (36, 12), (58, 22), (84, 14), (106, 20), (130, 10),
           (152, 18), (176, 12), (198, 22), (224, 14), (246, 20),
           (270, 12), (292, 18), (314, 10)]
    for bx, bh in sky:
        im.rect(px + bx, base - bh, 20, bh, (32, 58, 92))
        im.rect(px + bx + 8, base - bh - 4, 4, 4, (32, 58, 92))
    for wx in (20, 66, 112, 160, 206, 252, 300):
        im.rect(px + wx, base - 8, 2, 3, GOLD)
    for wx in (30, 76, 122, 170, 216, 262, 310):
        im.rect(px + wx, base - 17, 2, 3, GOLD)
    for ax in (46, 140, 234):
        im.tri(px + ax, base - 30, px + ax + 8, base - 30,
               px + ax + 4, base - 22, RED)

    # Rail: Tube strike.
    im.rect(0, 396, W, 64, RED_DK)
    im.text(16, 404, RAIL_HEAD, CREAM, 4)
    im.text(16, 436, RAIL_BODY, CREAM, 2)

    # Features. Height 142 (was 150): funds the pitch-34 wire below.
    # Scene box 40px; headline at +64; body up to 3 lines ends +139.
    fx0, fw, gap = 16, 238, 8
    for i, (scene, kick, head, body) in enumerate(FEATURES):
        fx = fx0 + i * (fw + gap)
        fy = 474
        im.rect(fx, fy, fw, 142, NAVY2)
        im.text(fx + 8, fy + 6, kick, GOLD, 2)
        SCENES[scene](im, fx, fy + 20, fw, 40)
        ty = fy + 64
        for ln in wrap(head, 19):
            im.text(fx + 8, ty, ln, CREAM, 2)
            ty += 15
        for ln in body:
            im.text(fx + 8, ty, ln, CREAM_DIM, 2)
            ty += 15
        if i < 3:
            im.vline(fx + fw + gap // 2, fy + 8, 126, GREY)

    # Wire divider with "THE WIRE" label cut into the rule at zero
    # vertical cost: a navy backing rect breaks the hairline and the
    # gold scale-1 caps sit on it. Rows start 622.
    im.hline(0, 617, W, GREY)
    im.rect(478, 611, 68, 11, NAVY)
    im.text_c(478, 613, 68, "THE WIRE", GOLD, 1)

    # Wire: 3 columns, 11 / 10 / 10 rows, pitch 34, fact at +17.
    # Lines are capped at 25 chars (column text width) - assert so a
    # long line can never overflow into the next column again.
    for beat, head, fact in WIRE:
        assert len(head) <= 25, head
        assert len(fact) <= 25, fact
    cols = [WIRE[0:11], WIRE[11:21], WIRE[21:31]]
    cw = (W - 32 - 2 * 12) // 3
    for ci, col in enumerate(cols):
        cx = 16 + ci * (cw + 12)
        ry = 622
        for beat, head, fact in col:
            im.rect(cx, ry + 3, 8, 8, CHIP[beat])
            im.text(cx + 14, ry, head, CREAM, 2)
            im.text(cx + 14, ry + 17, fact, CREAM_DIM, 2)
            ry += 34

    # Footer.
    im.hline(0, 998, W, GREY)
    im.text_c(0, 1006, W, "THE WORLD'S NEWS - MAKE.FUN/?ref=nnk13219", GOLD, 2)

    return im


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    im = build()
    write_png(im, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
