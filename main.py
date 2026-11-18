#!/usr/bin/env python3
"""news-image-20261117 entry v5: Tuesday 17 November 2026 world news.

An EDIT of v4 (same structure, same 20 verified stories, same facts):
masthead + BY THE NUMBERS strip + dot-grid world map with pins 1-10 +
3 leads with flag chips + ALSO ON TUESDAY list (11-20) + DATE CHECK +
sources footer. What v5 changes:

1. SMOOTH SERIF RENDERING, no pixel art. All text is drawn with PIL
   and Liberation Serif / Liberation Sans TTF files bundled in this
   directory (fonts/), loaded by relative path, so the program runs
   standalone from its own directory with no system fonts and no
   network. (v4 used a hand-made 5x7 bitmap font; Je ruled pixel art
   out.)
2. FLAT ILLUSTRATIONS on the 3 lead cards (PIL shapes only): a
   Crimean bridge with smoke, a Hormuz map with drones and arrows,
   and a Quad table with 4 flags. Each illustration carries a region
   tag bar, the way top 1 tags its leads.
3. REGION TAGS on every lead (EUROPE - UKRAINE WAR, MIDDLE EAST -
   IRAN WAR, ASIA - DIPLOMACY).
4. The small 2-line legend under the map (stories 4-10) is replaced
   by a proper 2-row numbered list, one story per cell, so it reads
   at 300 px instead of blurring into a wrapped blob.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
The program writes <output>/entry.png. Two runs write byte-identical
files. All facts are the verified 17 November 2026 stories; contested
claims are marked as claims.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024

BASE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(BASE, "fonts")

# ---------------------------------------------------------------- palette
# v4's own visual identity, kept: warm paper, deep navy ink, red pins,
# teal land. (The top entries are black + red on cream; this one is
# navy + red + teal.)
PAPER = (247, 243, 232)
PAPER2 = (238, 231, 214)
CARD = (252, 250, 244)
INK = (24, 33, 54)
NAVY = (16, 36, 72)
NAVY2 = (23, 52, 96)
GOLD = (176, 112, 22)
GOLD_LT = (250, 235, 200)
RED = (178, 34, 34)
RED_DK = (140, 24, 24)
TEAL = (13, 116, 110)
TEAL_DK = (16, 90, 84)
TEAL_LT = (204, 231, 228)
SKY = (186, 214, 228)
SKY_DK = (150, 190, 212)
GREY = (100, 107, 122)
GREY_LT = (190, 186, 172)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

# Flag colours.
SAFFRON = (255, 153, 51)
INDIA_GREEN = (19, 136, 8)
NAVY_FLAG = (0, 0, 128)
UKR_BLUE = (0, 91, 187)
UKR_YELLOW = (255, 213, 0)
RUS_BLUE = (0, 57, 166)
IRAN_GREEN = (0, 122, 61)
IRAN_RED = (218, 0, 0)
AUS_BLUE = (0, 40, 104)
JAPAN_RED = (188, 0, 45)

# ---------------------------------------------------------------- fonts
# Bundled TTFs, loaded by relative path. No system fonts, no network.
_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _cache[key]


def serif_b(size):
    return font("LiberationSerif-Bold.ttf", size)


def serif(size):
    return font("LiberationSerif-Regular.ttf", size)


def serif_i(size):
    return font("LiberationSerif-Italic.ttf", size)


def sans_b(size):
    return font("LiberationSans-Bold.ttf", size)


def sans(size):
    return font("LiberationSans-Regular.ttf", size)


# ---------------------------------------------------------------- text
def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = s.split()
    if not words:
        return [""]
    lines = []
    cur = words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def text(draw, s, x, y, f, fill, anchor="la"):
    """Draw text; anchor like PIL ('la' = left, ascender-top)."""
    draw.text((x, y), s, font=f, fill=fill, anchor=anchor)


def text_c(draw, s, cx, y, f, fill):
    draw.text((cx, y), s, font=f, fill=fill, anchor="ma")


def text_r(draw, s, x, y, f, fill):
    draw.text((x, y), s, font=f, fill=fill, anchor="ra")


def para(draw, lines, x, y, f, fill, leading):
    """Draw lines top-aligned; returns the y just below the last line."""
    for ln in lines:
        text(draw, ln, x, y, f, fill)
        y += leading
    return y

# ---------------------------------------------------------------- world map
# v4's own coarse world map: 24 rows x 64 columns, equirectangular,
# '#' = land. Drawn from general geography knowledge (row = 7.5 degrees
# of latitude, column = 5.625 degrees of longitude). Antarctica is a
# band at the bottom.
MAP_ROWS = (
    "................................................................",
    ".........#########......#####.............#################.....",
    "...##################..#####..#################################.",
    "....##################.....#..##################################",
    ".......################.....####################################",
    "......#################.....###########.#####################...",
    "......###############........################.......#######.##..",
    ".......#############.........#################...###.####...#...",
    ".......#####.................################....###.####.......",
    "........####................#####.......###......##..####.......",
    ".........###.................########............#...####.......",
    "............####.............#############............######....",
    "............#####.............############.............######...",
    ".............#####.............##########.................####..",
    ".............#####.............#####....#................######.",
    "..............####.............####......................######.",
    "..............###.........................................####.#",
    "..............##..............................................#.",
    "..............#.................................................",
    "..............#.................................................",
    "................................................................",
    "................................................................",
    ".....######################################################.....",
    "........################################################........",
)
MAP_COLS = 64
MAP_ROWS_N = 24
# Map geometry (v5: step 10, centred). Pin circles/chips keep v4's
# hand-tuned absolute positions; only the leader-line targets move.
MAP_X0 = 192
MAP_Y0 = 224
MAP_STEP = 10

# The day's 10 biggest stories, pinned on the map.
# (grid_col, grid_row) is the true location; (px, py) is where the
# numbered pin circle is drawn, with a thin leader line to the true
# spot. chip: (x, y, w, label) — small navy label next to the pin.
PINS = (
    # 1 Crimea — road span of the Kerch bridge falls into the sea
    {"n": 1, "col": 38, "row": 6, "px": 588, "py": 278,
     "chip": (606, 288, 96, "CRIMEA")},
    # 2 Hormuz — Iran drones hit US radar in Bahrain; US strikes back
    # (narrow chip + smaller font so it does not cover pin 3's true spot)
    {"n": 2, "col": 42, "row": 8, "px": 640, "py": 318,
     "chip": (660, 314, 64, "HORMUZ"), "fs": 13},
    # 3 Manila — Trump's first Quad summit, critical-minerals deals
    {"n": 3, "col": 53, "row": 10, "px": 756, "py": 368,
     "chip": (730, 388, 72, "QUAD")},
    # 4 DR Congo — Ebola tops 11,000 cases (WHO)
    {"n": 4, "col": 40, "row": 12, "px": 620, "py": 396,
     "chip": (640, 388, 84, "EBOLA")},
    # 5 Antalya — COP31 split over the fossil-fuel phase-out draft
    {"n": 5, "col": 37, "row": 7, "px": 555, "py": 320,
     "chip": (448, 348, 84, "COP31")},
    # 6 United States — US, Mexico, Bolivia lose measles-free status
    {"n": 6, "col": 15, "row": 7, "px": 330, "py": 306,
     "chip": (296, 268, 108, "MEASLES")},
    # 7 United States — Nvidia quarter $115.8bn, doubles; Dow falls 849
    {"n": 7, "col": 10, "row": 7, "px": 268, "py": 306,
     "chip": (172, 268, 96, "NVIDIA")},
    # 8 Gaza — truce at risk; 1.4m face acute hunger
    {"n": 8, "col": 38, "row": 8, "px": 592, "py": 328,
     "chip": (618, 348, 72, "GAZA")},
    # 9 Mongolia — president says he will resign
    {"n": 9, "col": 51, "row": 6, "px": 730, "py": 294,
     "chip": (748, 286, 120, "MONGOLIA")},
    # 10 Serbia — student-led list takes 140 of 250 parliament seats
    {"n": 10, "col": 36, "row": 6, "px": 545, "py": 278,
     "chip": (440, 286, 84, "SERBIA")},
)

# Stories 4-10, shown as a proper numbered list under the map (v4 had
# them as two wrapped small lines that blurred at 300 px).
MID = (
    (4, "EBOLA 11,000+"),
    (5, "COP31 SPLIT"),
    (6, "MEASLES-FREE LOST"),
    (7, "NVIDIA DOUBLES"),
    (8, "GAZA TRUCE AT RISK"),
    (9, "MONGOLIA CHIEF TO QUIT"),
    (10, "SERBIA STUDENT MPS"),
)


# ---------------------------------------------------------------- flags
# Small programmatic flag chips (rectangles of colour, no assets, no
# network), the way top 1 puts flag chips in its Quad panel and cards.
# A thin ink border makes the chip read on paper.
FLAG_W = 40
FLAG_H = 26
FLAG_GAP = 8


def _stripes(draw, x, y, w, h, colors):
    """Fill (x, y, w, h) with horizontal bands, one per colour."""
    n = len(colors)
    for i, c in enumerate(colors):
        y0 = y + i * h // n
        y1 = y + (i + 1) * h // n
        draw.rectangle([x, y0, x + w - 1, y1 - 1], fill=c)


def draw_flag(draw, code, x, y, w=FLAG_W, h=FLAG_H):
    """Draw one flag chip (w x h) at (x, y), with a border."""
    if code == "JP":  # Japan: white field, red disc
        draw.rectangle([x, y, x + w - 1, y + h - 1], fill=WHITE)
        draw.ellipse([x + w // 2 - 6, y + h // 2 - 6,
                      x + w // 2 + 6, y + h // 2 + 6], fill=JAPAN_RED)
    elif code == "IN":  # India: saffron / white / green + navy wheel
        _stripes(draw, x, y, w, h, (SAFFRON, WHITE, INDIA_GREEN))
        draw.ellipse([x + w // 2 - 3, y + h // 2 - 3,
                      x + w // 2 + 3, y + h // 2 + 3], fill=NAVY_FLAG)
    elif code == "US":  # USA: red/white stripes + blue canton + stars
        _stripes(draw, x, y, w, h,
                 (RED, WHITE, RED, WHITE, RED, WHITE, RED))
        draw.rectangle([x, y, x + 16, y + 13], fill=NAVY_FLAG)
        for sx in (3, 8, 13):
            for sy in (3, 8):
                draw.rectangle([x + sx, y + sy, x + sx + 1, y + sy],
                               fill=WHITE)
    elif code == "AU":  # Australia: blue field, Union Jack canton, stars
        draw.rectangle([x, y, x + w - 1, y + h - 1], fill=AUS_BLUE)
        cx, cy, cw, ch = x, y, 20, 13
        draw.rectangle([cx, cy, cx + cw - 1, cy + ch - 1], fill=WHITE)
        draw.line([cx, cy, cx + cw - 1, cy + ch - 1], fill=RED, width=1)
        draw.line([cx + cw - 1, cy, cx, cy + ch - 1], fill=RED, width=1)
        draw.rectangle([cx + cw // 2 - 1, cy, cx + cw // 2 + 1,
                        cy + ch - 1], fill=RED)
        draw.rectangle([cx, cy + ch // 2 - 1, cx + cw - 1,
                        cy + ch // 2 + 1], fill=RED)
        for sx, sy in ((30, 8), (34, 18), (26, 20)):
            draw.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                         fill=WHITE)
    elif code == "UA":  # Ukraine: blue over yellow
        _stripes(draw, x, y, w, h, (UKR_BLUE, UKR_YELLOW))
    elif code == "RU":  # Russia: white / blue / red
        _stripes(draw, x, y, w, h, (WHITE, RUS_BLUE, RED))
    elif code == "IR":  # Iran: green / white / red + red emblem dot
        _stripes(draw, x, y, w, h, (IRAN_GREEN, WHITE, IRAN_RED))
        draw.ellipse([x + w // 2 - 2, y + h // 2 - 2,
                      x + w // 2 + 2, y + h // 2 + 2], fill=IRAN_RED)
    # Thin border so the chip reads on paper.
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=1)


# ---------------------------------------------------------------- lead art
# Flat illustrations for the 3 lead cards, drawn with PIL shapes only
# (polygons, ellipses, rectangles — no image assets, no network).
# Each panel is ILL_W wide; the bottom ILL_CAP strip is a navy caption
# bar carrying the region tag, like top 1's caption strips.
ILL_W = 312
ILL_H = 56
ILL_CAP = 16


def _caption(draw, x, y, label):
    draw.rectangle([x, y + ILL_H - ILL_CAP, x + ILL_W - 1, y + ILL_H - 1],
                   fill=NAVY)
    text(draw, label, x + 8, y + ILL_H - ILL_CAP + 2, sans_b(12), GOLD_LT)


def ill_bridge(draw, x, y):
    """Lead 1: the Kerch bridge over the strait, one span broken."""
    # Sky, sea, and a low sun haze.
    draw.rectangle([x, y, x + ILL_W - 1, y + ILL_H - ILL_CAP - 1],
                   fill=(186, 214, 228))
    sea_y = y + 28
    draw.rectangle([x, sea_y, x + ILL_W - 1, y + ILL_H - ILL_CAP - 1],
                   fill=(47, 111, 143))
    # Wave dashes.
    for wx in range(x + 8, x + ILL_W - 8, 22):
        draw.line([wx, sea_y + 9, wx + 12, sea_y + 9], fill=WHITE, width=2)
    # Bridge deck across the whole panel, with pillars into the sea.
    deck_y = y + 22
    draw.rectangle([x, deck_y, x + ILL_W - 1, deck_y + 4], fill=(52, 58, 64))
    for px_ in (x + 40, x + 120, x + 250):
        draw.rectangle([px_, deck_y + 4, px_ + 5, sea_y + 12],
                       fill=(52, 58, 64))
    # The broken span: a tilted segment falling into the sea, mid-right.
    draw.polygon([(x + 178, deck_y + 1), (x + 232, deck_y + 1),
                  (x + 224, deck_y + 22), (x + 186, deck_y + 22)],
                 fill=(140, 24, 24))
    draw.polygon([(x + 232, deck_y + 1), (x + 244, deck_y + 1),
                  (x + 240, deck_y + 12), (x + 236, deck_y + 12)],
                 fill=(52, 58, 64))
    # Smoke puffs above the break.
    for cx, cy, r in ((x + 206, y + 10, 7), (x + 216, y + 6, 9),
                      (x + 228, y + 11, 6)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 120, 120))
    # A small jet silhouette, top left.
    draw.polygon([(x + 18, y + 10), (x + 34, y + 12), (x + 18, y + 15),
                  (x + 24, y + 12)], fill=(20, 20, 20))
    _caption(draw, x, y, "EUROPE  ·  UKRAINE WAR")


def ill_hormuz(draw, x, y):
    """Lead 2: the Strait of Hormuz — sand, sea, drones, a tanker."""
    # Sea, with sand on both shores.
    draw.rectangle([x, y, x + ILL_W - 1, y + ILL_H - ILL_CAP - 1],
                   fill=(120, 178, 205))
    draw.polygon([(x, y), (x + 92, y), (x + 52, y + 20), (x, y + 26)],
                 fill=(222, 200, 150))
    draw.polygon([(x + ILL_W, y + ILL_H - ILL_CAP), (x + ILL_W, y + 18),
                  (x + 238, y + 34), (x + 262, y + ILL_H - ILL_CAP)],
                 fill=(222, 200, 150))
    # Dotted red drone path arcing across the strait.
    for t in range(0, 21):
        fx = t / 20.0
        dx = x + 60 + int(fx * 190)
        dy = y + 30 - int(14 * (1 - (2 * fx - 1) ** 2))
        draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=RED)
    # Two drone silhouettes on the path.
    for dx, dy in ((x + 118, y + 16), (x + 196, y + 18)):
        draw.line([dx - 9, dy - 4, dx + 9, dy + 4], fill=(20, 20, 20),
                  width=2)
        draw.line([dx - 9, dy + 4, dx + 9, dy - 4], fill=(20, 20, 20),
                  width=2)
        draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(20, 20, 20))
    # Red X where drones were downed.
    draw.line([x + 152, y + 26, x + 162, y + 36], fill=RED, width=3)
    draw.line([x + 162, y + 26, x + 152, y + 36], fill=RED, width=3)
    # A tanker, bottom left.
    draw.rectangle([x + 16, y + 32, x + 62, y + 40], fill=(40, 40, 40))
    draw.rectangle([x + 22, y + 26, x + 34, y + 32], fill=(178, 34, 34))
    draw.rectangle([x + 40, y + 26, x + 52, y + 32], fill=(255, 255, 255))
    text(draw, "IRAN", x + 10, y + 4, sans_b(11), INK)
    text(draw, "HORMUZ", x + ILL_W - 58, y + ILL_H - ILL_CAP - 15,
         sans_b(11), INK)
    _caption(draw, x, y, "MIDDLE EAST  ·  IRAN WAR")


def ill_quad(draw, x, y):
    """Lead 3: the Quad leaders' table — four flags on a table."""
    # Lavender wall, wooden table.
    draw.rectangle([x, y, x + ILL_W - 1, y + ILL_H - ILL_CAP - 1],
                   fill=(226, 214, 240))
    table_y = y + ILL_H - ILL_CAP - 12
    draw.rectangle([x, table_y, x + ILL_W - 1, table_y + 11],
                   fill=(122, 84, 52))
    # Four flags standing on the table, with country labels below.
    codes = ("US", "IN", "JP", "AU")
    labels = ("US", "INDIA", "JAPAN", "AUSTRALIA")
    fx = x + 22
    for code, lab in zip(codes, labels):
        draw_flag(draw, code, fx, table_y - 26, 40, 26)
        # Pole.
        draw.line([fx + 40, table_y - 26, fx + 40, table_y],
                  fill=INK, width=1)
        text_c(draw, lab, fx + 20, table_y + 1, sans_b(9), WHITE)
        fx += 40 + 26
    _caption(draw, x, y, "ASIA  ·  DIPLOMACY")

# ---------------------------------------------------------------- content
# The day's stories. 10 pinned on the map + 10 one-liners = 20 stories.
# Same verified facts as v4; only the rendering changed.
LEADS = (
    # (pin number, headline lines, sub line, flag chips, illustration)
    (1, ("CRIMEA", "BRIDGE HIT"),
     "Second day of strikes on the Kerch Strait",
     ("UA", "RU"), "bridge"),
    (2, ("IRAN DRONES,", "US STRIKE"),
     "Drones hit US radar in Bahrain; US hits back",
     ("IR", "US"), "hormuz"),
    (3, ("MINERALS", "QUAD DEAL"),
     "Trump's first Quad summit in Manila",
     ("US", "IN", "JP", "AU"), "quad"),
)

NUMBERS = (
    # (big number, label, colour)
    ("11,000+", "EBOLA IN DR CONGO", TEAL_DK),
    ("$115.8BN", "NVIDIA QUARTER", NAVY),
    ("-849", "DOW POINTS", RED),
    ("1,441", "DRONES CLAIMED DOWN", NAVY),
)

ALSO = (
    "BANGLADESH POLICE TEAR-GAS GARMENT WORKERS",
    "RUSSIAN AN-12 CRASHES IN SIBERIA, 19 DEAD",
    "MOZAMBIQUE PUTS OPPOSITION LEADER ON TRIAL",
    "SUDAN CIVILIAN TOLL REACHES 2,230 - UN",
    "CYCLONE NEARS INDIA, THOUSANDS EVACUATE",
    "KYIV BRIDGES HIT IN FRESH RUSSIAN STRIKES",
    "JAPAN SCRAMBLES JETS OVER AIRSPACE FEARS",
    "BRAZIL WIN 7-0",
    "FRANCE PUBLIC-SECTOR STRIKE: 146,000 MARCH",
    "DEUTSCHE BANK SHARES FALL IN DATA LEAK",
)

DATE_CHECK = (
    "DATE CHECK - We left out stories from before 17 Nov on purpose.",
    "Ebola passed 11,000 on 10 Nov; today's news is the WHO update.",
)

FOOTER = (
    "EVERY STORY HERE HAPPENED OR WAS FIRST REPORTED ON TUESDAY "
    "17 NOVEMBER 2026.",
    "CONTESTED CLAIMS ARE MARKED AS CLAIMS. SOURCES: REUTERS, AP, AFP, "
    "BBC, AL JAZEERA, WHO, UN.",
)


# ---------------------------------------------------------------- layout
def draw_header(draw):
    draw.rectangle([0, 0, W - 1, 7], fill=NAVY)
    draw.rectangle([0, 8, W - 1, 129], fill=NAVY)
    text(draw, "THE WORLD IN ONE DAY", 40, 16, sans_b(20), GOLD)
    text(draw, "TUESDAY 17 NOVEMBER 2026", 40, 38, serif_b(48), WHITE)
    text_r(draw, "20 STORIES", 984, 42, serif_b(30), GOLD)
    text_r(draw, "6 CONTINENTS", 984, 76, sans(20), WHITE)
    draw.rectangle([0, 130, W - 1, 135], fill=GOLD_LT)


def draw_numbers(draw):
    draw.rectangle([0, 136, W - 1, 197], fill=PAPER2)
    cells = (40, 276, 512, 748)
    for i, (num, label, color) in enumerate(NUMBERS):
        cx = cells[i] + 118
        # Numbers sit on a baseline so the comma in 11,000+ / 1,441
        # cannot collide with the label underneath.
        draw.text((cx, 168), num, font=serif_b(40), fill=color,
                  anchor="ms")
        text_c(draw, label, cx, 178, sans(16), GREY)
    for x in (276, 512, 748):
        draw.line([x, 142, x, 196], fill=GREY_LT, width=2)


def draw_map(draw):
    text(draw, "WHERE IT HAPPENED", 40, 202, serif_b(28), NAVY)
    text_r(draw, "PINS 1-10 = THE DAY'S BIGGEST STORIES", 984, 208,
           sans(16), GREY)
    # Ocean + land dots.
    draw.rectangle([MAP_X0, MAP_Y0,
                    MAP_X0 + MAP_COLS * MAP_STEP - 1,
                    MAP_Y0 + MAP_ROWS_N * MAP_STEP - 1], fill=SKY)
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row):
            if ch == "#":
                cx = MAP_X0 + c * MAP_STEP + 5
                cy = MAP_Y0 + r * MAP_STEP + 5
                draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=TEAL_DK)
    # Border.
    draw.rectangle([MAP_X0, MAP_Y0,
                    MAP_X0 + MAP_COLS * MAP_STEP - 1,
                    MAP_Y0 + MAP_ROWS_N * MAP_STEP - 1],
                   outline=NAVY, width=2)
    # Pins: leader line, true spot, numbered circle, label chip.
    for pin in PINS:
        tx = MAP_X0 + pin["col"] * MAP_STEP + 5
        ty = MAP_Y0 + pin["row"] * MAP_STEP + 5
        px_, py_ = pin["px"], pin["py"]
        draw.line([px_, py_, tx, ty], fill=RED, width=2)
        draw.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=WHITE)
        draw.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], outline=RED, width=2)
        draw.ellipse([px_ - 13, py_ - 13, px_ + 13, py_ + 13], fill=RED)
        draw.ellipse([px_ - 13, py_ - 13, px_ + 13, py_ + 13],
                     outline=WHITE, width=2)
        draw.text((px_, py_), str(pin["n"]), font=serif_b(16), fill=WHITE,
                  anchor="mm")
        cx, cy, cw, label = pin["chip"]
        draw.rectangle([cx, cy, cx + cw - 1, cy + 19], fill=NAVY)
        draw.text((cx + cw // 2, cy + 10), label,
                  font=sans_b(pin.get("fs", 15)), fill=WHITE, anchor="mm")
    # Stories 4-10 as a proper numbered list (v4: two wrapped small
    # lines that blurred at 300 px). 4 columns x 2 rows, one per cell.
    cols = (40, 284, 528, 772)
    cells = list(MID) + [(None, "PINS 1-10 = TOP STORIES")]
    for i, (n, label) in enumerate(cells):
        x = cols[i % 4]
        y = 468 + (i // 4) * 19
        if n is None:
            text(draw, label, x, y, sans(14), GREY)
        else:
            text(draw, str(n), x, y, serif_b(16), RED)
            tw = draw.textlength(str(n), font=serif_b(16))
            text(draw, label, x + tw + 6, y, serif(16), INK)


def draw_leads(draw):
    cols = (32, 356, 680)
    for i, (n, head, sub, flags, art) in enumerate(LEADS):
        x = cols[i]
        # Flat illustration panel on top of the card.
        if art == "bridge":
            ill_bridge(draw, x, 508)
        elif art == "hormuz":
            ill_hormuz(draw, x, 508)
        else:
            ill_quad(draw, x, 508)
        # Number box + flag chips.
        draw.rectangle([x, 570, x + 29, 570 + 29], fill=RED)
        draw.text((x + 15, 570 + 15), str(n), font=serif_b(20), fill=WHITE,
                  anchor="mm")
        fx = x + 38
        for code in flags:
            draw_flag(draw, code, fx, 570)
            fx += FLAG_W + FLAG_GAP
        # Headline (2 lines, serif bold) + one-line summary.
        text(draw, head[0], x, 606, serif_b(40), INK)
        text(draw, head[1], x, 652, serif_b(40), INK)
        text(draw, sub, x, 702, serif(16), GREY)
    for x in (348, 672):
        draw.line([x, 574, x, 720], fill=GREY_LT, width=2)


def draw_also(draw):
    draw.rectangle([40, 728, 983, 731], fill=NAVY)
    text(draw, "ALSO ON TUESDAY", 40, 736, serif_b(28), NAVY)
    text_r(draw, "MORE OF THE DAY, IN BRIEF", 984, 740, sans(16), GREY)
    for i, item in enumerate(ALSO):
        y = 762 + i * 20
        if i % 2 == 0:
            draw.rectangle([40, y - 4, 983, y + 15], fill=PAPER2)
        text(draw, str(11 + i), 40, y, serif_b(19), RED)
        text(draw, item, 88, y, serif(19), INK)


def draw_honesty(draw):
    draw.rectangle([40, 964, 983, 991], fill=PAPER2)
    draw.rectangle([40, 964, 45, 991], fill=RED)
    text(draw, DATE_CHECK[0], 56, 967, serif(14), INK)
    text(draw, DATE_CHECK[1], 56, 980, serif(14), INK)
    text_c(draw, FOOTER[0], 512, 996, serif(12), GREY)
    text_c(draw, FOOTER[1], 512, 1008, serif(12), GREY)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_header(draw)
    draw_numbers(draw)
    draw_map(draw)
    draw_leads(draw)
    draw_also(draw)
    draw_honesty(draw)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    build().save(path, format="PNG")
    size = os.path.getsize(path)
    print("wrote %s (%d bytes)" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
