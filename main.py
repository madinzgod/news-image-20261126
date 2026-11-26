"""news-image-20261126 V14 (two fact rewords + kicker dedupe):
one image summing up Thursday 26 November 2026.

Python 3.13, standard library only. No network, no time, no randomness:
the same bytes come out of every run. Writes entry.png into
$MAKEFUN_OUTPUT_DIR (default /output).

V14 changes (see work/v14/AUDIT-V14.md and work/v14/FACTCHECK-V14.md):
two wire facts reworded — IPL "REGISTRATIONS FOR 2027" ->
"1,220 REGISTER FOR 2027", and Davis Cup "QUARTER-FINAL TONIGHT" ->
"TIE 1-1, DOUBLES DECIDE" (verified: Norrie beat Struff 6-3 3-6 6-2,
Fery lost 6-3 6-2 to Zverev, tie 1-1, Reuters + The Times) — and the
storm feature kicker deduped ("NEW YORK" -> "EAST COAST"). Full-size
wire-all 160/257 (62%, V13 152/253), 300px wire 14/257 (V13 13/253),
300px large 10/28 (tie) — all reproduced exactly on a fresh re-run.
Honest accounting: the IPL gain is cross-talk (220/OFF/53 now read;
the reworded fact itself reads no better than the old one), while the
Davis Cup gain is direct (TIE/1/1/DOUBLES/DECIDE all read, plus
BRITAIN/GERMANY). Wire pitch 34 -> 33 tested and REJECTED (126/253,
catastrophic — rows merge in OCR segmentation). Evening sweep: Europa
League and NFL not started; EU Council deadlocked, no conclusions;
Davis Cup decider still to play — re-check after ~02:00 WIB Fri
27 Nov. No glyph work: the typeface is at its measured ceiling.

V13 changes (see work/v13/AUDIT-V13.md and work/v13/FACTCHECK-V13.md):
the 5x7 typeface's $ loses its middle vertical stroke (sheet L1 ties
the 242/253 baseline — but fixes 3 $ signs on the sheet, $45B/$1.26B/
$3,573, which the word scorer cannot count since $/# are not word
characters). On the page the full-size wire-all reaches 152/253 (60%,
V12 151/253), 300px wire 13/253 (tie), 300px large 10/28 (tie) — all
reproduced exactly on a fresh re-run. The +1 is one word (BRENT) on
the line holding the redrawn $, i.e. segmentation cross-talk from 72
changed pixels, NOT a direct $ read — stated plainly, this is the
smallest possible promotion. The other V13 sheet mechanisms all
failed: O pinched waist 173/253 (reads as 8), I mid-tick 179/253
(reads as +/t), V sharp point 234/253 (reads as Y), Q late tail ties
242/253. Evening sweep: nothing has landed (Europa League and NFL
kick off overnight, EU Council Friday) — nothing invented.

V12 changes (see work/v12/AUDIT-V12.md and work/v12/FACTCHECK-V12.md):
the 5x7 typeface's 0 loses its slash and becomes a NARROWER oval than O
(sheet H2: 242/254 vs the 234 baseline — the second sheet win in a row,
all gains attributable to the 0; the I/Q/$ redraws in sheet H cost
words and were dropped, and selective-wide J scored 210/254 and was
rejected). On the page the full-size wire-all reaches 151/253 (60%,
V11 142/254), 300px wire 13/253 (V11 11/254), 300px large 10/28 (V11
9/28) — all reproduced exactly on a fresh re-run. The Bank of England
Financial Stability Report landed 10:30 GMT (verified from the Bank's
own FPC Record + official post, corroborated by Financial News), so
the wire fact "STABILITY REPORT 10:30 UK" becomes the verified
finding "CUTS BANK CAPITAL FLOORS". No rail/feature/wire row moves;
no text-pair change. Evening sweep: Europa League and NFL kick off
overnight, EU Council conclusions Friday — nothing invented.

V10 changes (see work/v10/AUDIT-V10.md and work/v10/FACTCHECK-V10.md):
the chart-panel dead band is gone — the skyline is +14px taller (V8's
B, now in a small combination) and each red down-arrow's tip sits
exactly on the roofline beneath it instead of floating 6-10px above
it; the footer rule/text move +2px (wire-to-footer gap 4px -> 6px).
No rail/feature/wire row moves; no wire text; no text-pair change.
The sheet battery's two new mechanisms both failed (HALO fringe
31/254, catastrophic; dim facts cost nothing, 232/254 vs 230 baseline
noise) — no typeface change. Evening sweep: nothing had landed at
build time (~16:25 WIB) — BoE report due 17:30 WIB, Europa League
and NFL overnight, EU Council conclusions Friday."""

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
STORM = (170, 180, 195)    # V9 R: storm cloud only (6.92:1 on NAVY2)
SKY = (72, 110, 160)       # V9 S: skyline buildings (2.77:1 on NAVY2)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, each a 5-bit int (bit 4 = leftmost pixel).
F = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1C, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x13),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x15, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x13),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x0A, 0x0A, 0x0E),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x06, 0x09, 0x09, 0x09, 0x09, 0x09, 0x06),  # V12 H2: narrow oval, no slash
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
    '$': (0x04, 0x0F, 0x10, 0x0E, 0x01, 0x1E, 0x04),  # V13 L1: broken vertical stroke
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
        self.bold = True  # V6: double-strike set pixels (scale >= 2)
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
        # V6 BOLD: every set pixel is double-struck +1px to the right
        # (scale >= 2 only; at scale 1 the +1px would fuse adjacent
        # glyphs). Advance is unchanged, so no layout moves and no
        # text overflows: strokes get thicker, spacing stays. Sheet
        # test: BOLD 230/254 (91%) vs baseline 217/254 (85%).
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
                        if scale >= 2 and self.bold:
                            self.rect(cx + col * scale + 1, y + r * scale,
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
             "-2.4%, TAIEX -4.5%. ONLY HONG KONG RISES, +0.8%. "
             "NIKKEI'S OPEN: 261 LOWER AT 58,383.")
BARS = [("KOSPI", -4.6, RED), ("NIKKEI", -2.4, RED), ("TAIEX", -4.5, RED),
        ("HANG SENG", +0.8, GREEN), ("SHANGHAI", -0.7, RED)]

RAIL_HEAD = "LONDON TUBE STRIKE FROM MIDDAY"
RAIL_BODY = ("RMT DRIVERS WALK OUT 24 HOURS; CIRCLE, PICCADILLY, "
             "WATERLOO AND CITY LINES SHUT.")

# Features: (scene, kicker, headline, body lines)
FEATURES = [
    ("MISSILE", "PYONGYANG", "KIM SPREADS NUKES",
     ["KIM JONG UN ORDERS", "TACTICAL NUKES", "WIDER, KCNA SAYS"]),
    ("BALLOON", "NEW YORK", "MACY'S PARADE MOVED",
     ["100TH PARADE", "POSTPONED BY STORM", "MOVED TO SAT"]),
    ("STORM", "EAST COAST", "STORM HITS 250M",
     ["60 MPH GUSTS", "250M IN PATH", "HEAVY RAIN, WIND"]),
    ("STARS", "BRUSSELS", "EU MEETS ON UKRAINE",
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
    ("BUSINESS", "BANK OF ENGLAND REPORT", "CUTS BANK CAPITAL FLOORS"),
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
    ("SPORT", "IPL AUCTION DRAWS 1,220", "1,220 REGISTER FOR 2027"),  # V14: IPL fact reword
    ("SPORT", "SOORYAVANSHI 204 OFF 53", "AGAINST UAE IN CRICKET"),
    ("SPORT", "GUKESH FACES SINDAROV", "WORLD CHESS CROWN, GENEVA"),
    ("SPORT", "BRITAIN V GERMANY, DAVIS", "TIE 1-1, DOUBLES DECIDE"),  # V14: Davis Cup partial result (verified)
]


# ---------------------------------------------------------------- scenes
def scene_missile(im, x, y, w, h):
    # h = 52 box. Wider body (20) and longer flame than V3.
    cx = x + w // 2
    im.tri(cx - 13, y + 14, cx + 13, y + 14, cx, y + 2, CREAM)
    im.rect(cx - 13, y + 14, 26, 20, CREAM)
    im.tri(cx - 13, y + 26, cx - 32, y + 40, cx - 13, y + 32, RED)
    im.tri(cx + 13, y + 26, cx + 32, y + 40, cx + 13, y + 32, RED)
    im.tri(cx - 8, y + 34, cx + 8, y + 34, cx, y + 50, GOLD)
    im.disc(cx, y + 22, 5, NAVY2)


def scene_balloon(im, x, y, w, h):
    # h = 52 box. Envelope r19 (was r15 in a 40px box).
    cx = x + w // 2
    im.disc(cx, y + 20, 22, RED)
    im.disc(cx - 8, y + 15, 7, (255, 120, 120))
    im.line(cx - 6, y + 42, cx - 4, y + 45, CREAM)
    im.line(cx + 6, y + 42, cx + 4, y + 45, CREAM)
    im.rect(cx - 8, y + 45, 16, 7, GOLD)
    im.disc(x + 16, y + 6, 7, GREY)
    im.disc(x + w - 18, y + 8, 7, GREY)


def scene_storm(im, x, y, w, h):
    # h = 52 box. Bigger cloud, longer lightning, lower rain.
    cx = x + w // 2
    im.disc(cx - 13, y + 13, 14, STORM)
    im.disc(cx + 9, y + 9, 15, STORM)
    im.disc(cx + 21, y + 15, 10, STORM)
    im.rect(cx - 29, y + 19, 58, 7, STORM)
    im.line(cx + 2, y + 27, cx - 7, y + 36, GOLD)
    im.line(cx - 7, y + 36, cx + 3, y + 36, GOLD)
    im.line(cx + 3, y + 36, cx - 7, y + 48, GOLD)
    for dx in (-26, -9, 9, 26):
        im.vline(cx + dx, y + 33, 12, BLUE)


def scene_stars(im, x, y, w, h):
    import math
    cx, cy = x + w // 2, y + 26
    r = 24
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx = int(cx + r * math.cos(a))
        sy = int(cy + r * math.sin(a))
        im.disc(sx, sy, 4, GOLD)
    im.disc(cx, cy, 4, GOLD)


SCENES = {"MISSILE": scene_missile, "BALLOON": scene_balloon,
          "STORM": scene_storm, "STARS": scene_stars}


# ---------------------------------------------------------------- build
def build():
    im = Img(W, H, NAVY)
    im.bold = False

    # Masthead.
    im.rect(0, 0, W, 86, PAPER)
    im.text_c(0, 25, W, "THE WORLD'S NEWS", INK, 5)
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
    # with red down-arrows. V5: brighter (48,80,120) and taller
    # (+8px) so the silhouette actually reads; windows 3x3, arrows
    # 12 wide. Panel bottom edge is y=384.
    base = 382
    # V10 G2: B (skyline +14px, V8's B) + arrow tips seated exactly
    # on the new rooflines beneath each tip.
    sky = [(12, 42), (36, 32), (58, 44), (84, 34), (106, 42), (130, 30),
           (152, 40), (176, 32), (198, 44), (224, 34), (246, 42),
           (270, 32), (292, 40), (314, 30)]
    for bx, bh in sky:
        im.rect(px + bx, base - bh, 20, bh, SKY)
        im.rect(px + bx + 8, base - bh - 4, 4, 4, SKY)
    for wx in (20, 66, 112, 160, 206, 252, 300):
        im.rect(px + wx, base - 8, 3, 3, GOLD)
    for wx in (30, 76, 122, 170, 216, 262, 310):
        im.rect(px + wx, base - 17, 3, 3, GOLD)
    for ax, top, tip in ((46, 338, 350), (140, 340, 352), (234, 336, 348)):
        im.tri(px + ax, top, px + ax + 12, top,
               px + ax + 6, tip, RED)

    # Rail: Tube strike.
    im.rect(0, 396, W, 64, RED_DK)
    im.text(16, 404, RAIL_HEAD, CREAM, 4)
    im.text(16, 436, RAIL_BODY, CREAM, 2)
    # Tube roundel in the empty right end of the head row.
    im.disc(988, 418, 12, CREAM)
    im.disc(988, 418, 9, RED)
    im.rect(976, 415, 24, 6, NAVY)

    # Features. Height 142 (was 150): funds the pitch-34 wire below.
    # Scene box 52px; single-line headline at +78; body up to 3 lines
    # ends +137. Head/body lines capped at 19 chars (scale-2 width).
    for _, _, head, body in FEATURES:
        assert len(head) <= 19, head
        for ln in body:
            assert len(ln) <= 19, ln
    fx0, fw, gap = 16, 238, 8
    for i, (scene, kick, head, body) in enumerate(FEATURES):
        fx = fx0 + i * (fw + gap)
        fy = 474
        im.rect(fx, fy, fw, 142, NAVY2)
        im.text(fx + 8, fy + 6, kick, GOLD, 2)
        SCENES[scene](im, fx, fy + 20, fw, 52)
        ty = fy + 78
        for ln in wrap(head, 19):
            im.text(fx + 8, ty, ln, CREAM, 2)
            ty += 15
        for ln in body:
            im.text(fx + 8, ty, ln, CREAM_DIM, 2)
            ty += 15
        if i < 3:
            im.vline(fx + fw + gap // 2, fy + 8, 134, GREY)

    # Wire divider: hairline only (V9 Q). The "THE WIRE" label + navy
    # backing is dropped: its backing rect ate 5px of feature boxes 2
    # and 3 (341 NAVY px, y611-616) and the 6px gap cannot hold an
    # 11px label. Rows start 622.
    im.hline(0, 617, W, GREY)

    # Wire: 3 columns, 11 / 10 / 10 rows, pitch 34, fact at +17.
    # V6c: bold ONLY here (isolation: does the 300px-wire drop of the
    # full-bold page come from wire bold or from bold elsewhere?).
    im.bold = True
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

    # Footer. V10 X10: rule/text +2px (wire-to-footer gap 4px -> 6px).
    im.hline(0, 1000, W, GREY)
    im.text_c(0, 1008, W, "THE WORLD'S NEWS - MAKE.FUN/?ref=nnk13219", GOLD, 2)

    return im


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    im = build()
    write_png(im, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
