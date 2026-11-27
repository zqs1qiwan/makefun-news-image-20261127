#!/usr/bin/env python3
"""Typeset the 27 November 2026 front page for make.fun news-image.

The page is a 1024x1024 newspaper front built in PIL from six
photographs sliced out of one fresh AI-generated 3x2 collage
(assets/entry-source.png, 1920x1280, made for this competition day).

Everything on the page is described by small data tables near the
top of this file — the masthead, the four feature stories, the two
strip stories and the three short ALSO items — and a single
slot renderer paints each story according to its kind. The script
writes entry.png next to itself and then re-opens the file to
confirm it is a 1024x1024 PNG under 1 MiB, printing its sha256.

The build is deterministic: same source bytes in, same PNG out.
"""
from __future__ import annotations

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "assets", "entry-source.png")
OUT = os.path.join(BASE, "entry.png")

# --- Page geometry -------------------------------------------------------
CANVAS_W, CANVAS_H = 1024, 1024
MARGIN = 16            # outer edge on the left and right
COL_GAP = 20           # gap between the two feature columns
ROW_GAP = 12           # gap between the two feature rows
PANEL_W = 490          # width of one feature panel / strip half
PANEL_H = 300          # height of one feature panel
PHOTO_H = 170          # height of a feature photo
FIRST_ROW_Y = 140      # top of the first feature row
STRIP_TOP = 764        # top of the full-width strip
STRIP_H = 116          # height of the strip
THUMB_W = 150          # width of a strip thumbnail
ALSO_TOP = 892         # top of the navy ALSO band

# --- Palette --------------------------------------------------------------
PALETTE = {
    "paper": (247, 242, 231),
    "ink": (18, 18, 18),
    "red": (178, 34, 34),
    "grey": (90, 88, 82),
    "navy": (20, 36, 62),
    "gold": (232, 190, 90),
    "pale": (245, 245, 245),
    "frame": (40, 40, 40),
}

# --- Typefaces ------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/noto"
_FONT_FILES = {
    False: os.path.join(FONT_DIR, "NotoSans-Condensed.ttf"),
    True: os.path.join(FONT_DIR, "NotoSans-CondensedBold.ttf"),
}
_FONT_CACHE: dict[tuple[bool, int], ImageFont.FreeTypeFont] = {}


def typeface(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    """Return (and cache) a Noto Sans Condensed face at the given size."""
    key = (bold, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(_FONT_FILES[bold], size)
    return _FONT_CACHE[key]


# --- Source photographs ---------------------------------------------------
# Cell boxes were measured off this day's collage: a grey frame of about
# 23px, vertical gutters at x=633-652 and x=1267-1286, and a horizontal
# gutter at y=638-658. Each box is inset a few pixels past the gutters.
# The focus point keeps the interesting part of each photo in frame
# when it is cropped to its slot shape.
PHOTOS = {
    "storm":  {"box": (26, 24, 629, 634),   "focus": (0.50, 0.55)},
    "kuwait": {"box": (656, 24, 1263, 634), "focus": (0.50, 0.55)},
    "port":   {"box": (1290, 24, 1894, 634), "focus": (0.50, 0.50)},
    "summit": {"box": (26, 662, 629, 1256), "focus": (0.50, 0.50)},
    "bank":   {"box": (656, 662, 1263, 1256), "focus": (0.50, 0.45)},
    "gaza":   {"box": (1290, 662, 1894, 1256), "focus": (0.50, 0.55)},
}

# --- Stories --------------------------------------------------------------
TITLE = "THE WORLD IN ONE DAY"
DATE_LINE = "FRIDAY, 27 NOVEMBER 2026"

# (photo key, kicker, headline, subhead) — the four big panels.
FEATURES = [
    ("storm", "UNITED STATES", "STORM SURGE TOPS SANDY",
     "Thanksgiving nor'easter floods the East Coast"),
    ("kuwait", "KUWAIT", "DRONE KILLS TWO IN KUWAIT",
     "Italy blames Iran; Tehran denies any role"),
    ("port", "TRADE", "US UNVEILS TARIFFS ON 14 NATIONS",
     "China capped at 20%; hearing set for January"),
    ("summit", "EUROPE", "EU SPLIT OVER UKRAINE LOAN",
     "Leaders divided on a $49bn loan to Kyiv"),
]

# (photo key, kicker, headline, subhead) — the two strip stories.
STRIPS = [
    ("bank", "EUROPE", "SPAIN'S DE COS TO LEAD ECB",
     "Chosen to succeed Lagarde at the central bank"),
    ("gaza", "GAZA", "ISRAELI STRIKES KILL 10 IN GAZA",
     "Ceasefire under strain for a third night"),
]

ALSO = [
    "EBOLA IN CONGO PASSES 12,000 CASES \u2014 second-largest outbreak on record",
    "NETANYAHU JUDGES URGE DROPPING BRIBERY CHARGE",
    "GUINEA-BISSAU JUNTA DELAYS ELECTION TO 2028",
]


# --- Text helpers ---------------------------------------------------------
def wrap_lines(draw, text, fnt, limit):
    """Yield the lines of `text` word-wrapped to fit `limit` pixels.

    Words accumulate onto the current line until the next word would
    overflow it; the line is then emitted and a fresh one started.
    """
    words = text.split()
    current: list[str] = []
    width = 0.0
    space_w = draw.textlength(" ", font=fnt)
    for word in words:
        word_w = draw.textlength(word, font=fnt)
        extra = word_w if not current else space_w + word_w
        if current and width + extra > limit:
            yield " ".join(current)
            current = [word]
            width = word_w
        else:
            current.append(word)
            width += extra
    if current:
        yield " ".join(current)


def fit_headline(draw, text, ceiling, limit, max_lines=2):
    """Biggest bold face (at most `ceiling`) wrapping into `max_lines`."""
    for size in range(ceiling, 12, -1):
        fnt = typeface(True, size)
        wrapped = list(wrap_lines(draw, text, fnt, limit))
        if len(wrapped) <= max_lines:
            return fnt, wrapped
    fnt = typeface(True, 13)
    return fnt, list(wrap_lines(draw, text, fnt, limit))


def fit_single_line(draw, text, ceiling, floor, limit):
    """Largest regular face (between `floor` and `ceiling`) fitting one line."""
    size = ceiling
    while size > floor:
        fnt = typeface(False, size)
        if draw.textlength(text, font=fnt) <= limit:
            return fnt
        size -= 1
    return typeface(False, floor)


def cover(source, photo_key, size):
    """Crop one collage cell to `size`, keeping its focus point in frame."""
    spec = PHOTOS[photo_key]
    tile = source.crop(spec["box"])
    return ImageOps.fit(tile, size, method=Image.LANCZOS,
                        centering=spec["focus"])


# --- Page sections --------------------------------------------------------
def paint_header(draw):
    """Masthead: title, red rule, exact date."""
    draw.text((CANVAS_W // 2, 12), TITLE, font=typeface(True, 62),
              fill=PALETTE["ink"], anchor="ma")
    draw.rectangle([MARGIN, 96, CANVAS_W - MARGIN, 99], fill=PALETTE["red"])
    draw.text((CANVAS_W // 2, 104), DATE_LINE, font=typeface(True, 27),
              fill=PALETTE["ink"], anchor="ma")


def paint_feature(page, draw, source, cell, kicker, head, sub, x, y):
    """One 2x2-grid panel: photo on top, kicker, headline, subhead."""
    photo = cover(source, cell, (PANEL_W, PHOTO_H))
    page.paste(photo, (x, y))
    draw.rectangle([x, y, x + PANEL_W - 1, y + PHOTO_H - 1],
                   outline=PALETTE["frame"], width=1)
    text_top = y + PHOTO_H + 8
    draw.text((x, text_top), kicker, font=typeface(True, 19),
              fill=PALETTE["red"])
    head_fnt, head_lines = fit_headline(draw, head, 36, PANEL_W)
    line_y = text_top + 24
    for line in head_lines:
        draw.text((x, line_y), line, font=head_fnt, fill=PALETTE["ink"])
        line_y += head_fnt.size + 2
    # The subhead sits on a fixed baseline two headline lines below the
    # kicker, so the two panels of a row line up even when one headline
    # wraps and the other does not.
    sub_y = text_top + 24 + 2 * (head_fnt.size + 2)
    draw.text((x, sub_y), sub, font=typeface(False, 23),
              fill=PALETTE["grey"])


def paint_strip(page, draw, source, cell, kicker, head, sub, x, y):
    """One half of the full-width strip: thumbnail left, text right."""
    thumb = cover(source, cell, (THUMB_W, STRIP_H))
    page.paste(thumb, (x, y))
    draw.rectangle([x, y, x + THUMB_W - 1, y + STRIP_H - 1],
                   outline=PALETTE["frame"], width=1)
    tx = x + THUMB_W + 12
    text_w = PANEL_W - THUMB_W - 12
    draw.text((tx, y + 2), kicker, font=typeface(True, 18),
              fill=PALETTE["red"])
    head_fnt, head_lines = fit_headline(draw, head, 30, text_w)
    line_y = y + 24
    for line in head_lines:
        draw.text((tx, line_y), line, font=head_fnt, fill=PALETTE["ink"])
        line_y += head_fnt.size + 1
    sub_fnt = typeface(False, 18)
    for line in list(wrap_lines(draw, sub, sub_fnt, text_w))[:2]:
        draw.text((tx, line_y + 2), line, font=sub_fnt, fill=PALETTE["grey"])
        line_y += sub_fnt.size + 1


def paint_also(draw):
    """Navy footer band with three short items at 29px."""
    draw.rectangle([0, ALSO_TOP, CANVAS_W, CANVAS_H], fill=PALETTE["navy"])
    draw.text((MARGIN, ALSO_TOP + 6), "ALSO TODAY", font=typeface(True, 22),
              fill=PALETTE["gold"])
    y = ALSO_TOP + 33
    for item in ALSO:
        # Shrink any item that would run past the right edge.
        fnt = fit_single_line(draw, item, 29, 19, CANVAS_W - 34 - MARGIN)
        draw.rectangle([MARGIN, y + 9, MARGIN + 8, y + 17],
                       fill=PALETTE["red"])
        draw.text((34, y), item, font=fnt, fill=PALETTE["pale"])
        y += 31


# --- Build ----------------------------------------------------------------
def assemble():
    """Lay out the whole front page and return it as a PIL image."""
    source = Image.open(SRC).convert("RGB")
    page = Image.new("RGB", (CANVAS_W, CANVAS_H), PALETTE["paper"])
    draw = ImageDraw.Draw(page)
    paint_header(draw)
    for row in range(2):
        for col in range(2):
            cell, kicker, head, sub = FEATURES[row * 2 + col]
            x = MARGIN + col * (PANEL_W + COL_GAP)
            y = FIRST_ROW_Y + row * (PANEL_H + ROW_GAP)
            paint_feature(page, draw, source, cell, kicker, head, sub, x, y)
    for i, (cell, kicker, head, sub) in enumerate(STRIPS):
        x = MARGIN + i * (PANEL_W + COL_GAP)
        paint_strip(page, draw, source, cell, kicker, head, sub, x, STRIP_TOP)
    paint_also(draw)
    return page


def build():
    page = assemble()
    page.save(OUT, "PNG", optimize=True)
    print("wrote", OUT)


def verify():
    """Re-open entry.png and check size, format, byte budget and hash."""
    with Image.open(OUT) as im:
        assert im.size == (CANVAS_W, CANVAS_H), im.size
        assert im.format == "PNG"
    nbytes = os.path.getsize(OUT)
    assert nbytes <= 1_048_576, nbytes
    digest = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print(f"verify: {CANVAS_W}x{CANVAS_H} PNG, {nbytes} bytes, sha256 {digest}")
    return digest


if __name__ == "__main__":
    build()
    verify()
