#!/usr/bin/env python3
"""Typeset the front page for news-image-20261127.

A 1024x1024 newspaper front page for Friday 27 November 2026, built
in PIL on top of six photographs cut from one fresh AI-generated 3x2
collage (assets/entry-source.png, generated in this session, 1920x1280).

Page order, top to bottom:
  * masthead — title, red rule, exact date
  * 2x2 grid of big stories (photo, kicker, headline, subhead)
  * full-width strip with the last two big stories (thumb + text)
  * navy ALSO band with three short items

Running this file writes entry.png next to it and then re-opens the
file to check it: 1024x1024, PNG, at most 1 MiB. The build is fully
deterministic — same input bytes, same output bytes.
"""
from __future__ import annotations

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_PATH = os.path.join(HERE, "assets", "entry-source.png")
OUTPUT_PATH = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
EDGE = 16

# Palette
PAPER = (247, 242, 231)
INK = (18, 18, 18)
RED = (178, 34, 34)
GREY = (90, 88, 82)
NAVY = (20, 36, 62)
GOLD = (232, 190, 90)
PALE = (245, 245, 245)
FRAME = (40, 40, 40)

FONT_DIR = "/usr/share/fonts/truetype/noto"
FONT_FILES = {
    "cond": os.path.join(FONT_DIR, "NotoSans-Condensed.ttf"),
    "cond_bold": os.path.join(FONT_DIR, "NotoSans-CondensedBold.ttf"),
}


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


def split_lines(draw: ImageDraw.ImageDraw, text: str,
                fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Greedy word wrap: every returned line fits inside max_w pixels."""
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def headline_font(draw: ImageDraw.ImageDraw, text: str, start: int,
                  max_w: int, max_lines: int = 2):
    """Largest bold-condensed font (<= start) wrapping into max_lines."""
    size = start
    while size > 13:
        fnt = font("cond_bold", size)
        if len(split_lines(draw, text, fnt, max_w)) <= max_lines:
            return fnt, split_lines(draw, text, fnt, max_w)
        size -= 1
    fnt = font("cond_bold", 13)
    return fnt, split_lines(draw, text, fnt, max_w)


def crop_cover(img: Image.Image, focus: tuple[float, float],
               tw: int, th: int) -> Image.Image:
    """Resize-crop img to exactly tw x th, keeping the focus point in frame."""
    w, h = img.size
    scale = max(tw / w, th / h)
    cw, ch = round(tw / scale), round(th / scale)
    cx, cy = round(focus[0] * w), round(focus[1] * h)
    x0 = min(max(cx - cw // 2, 0), w - cw)
    y0 = min(max(cy - ch // 2, 0), h - ch)
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((tw, th), Image.LANCZOS)


# Cell rectangles measured from this session's collage (1920x1280):
# grey frame ~23px, vertical gutters x=633-652 and x=1267-1286,
# horizontal gutter y=638-658. Each cell is inset a few px past them.
CELLS = {
    "storm": (26, 24, 629, 634),
    "kuwait": (656, 24, 1263, 634),
    "port": (1290, 24, 1894, 634),
    "summit": (26, 662, 629, 1256),
    "bank": (656, 662, 1263, 1256),
    "gaza": (1290, 662, 1894, 1256),
}
FOCUS = {
    "storm": (0.50, 0.55),
    "kuwait": (0.50, 0.55),
    "port": (0.50, 0.50),
    "summit": (0.50, 0.50),
    "bank": (0.50, 0.45),
    "gaza": (0.50, 0.55),
}

PANEL_STORIES = [
    {"cell": "storm", "kicker": "UNITED STATES",
     "head": "STORM SURGE TOPS SANDY",
     "sub": "Thanksgiving nor'easter floods the East Coast"},
    {"cell": "kuwait", "kicker": "KUWAIT",
     "head": "DRONE KILLS TWO IN KUWAIT",
     "sub": "Italy blames Iran; Tehran denies any role"},
    {"cell": "port", "kicker": "TRADE",
     "head": "US UNVEILS TARIFFS ON 14 NATIONS",
     "sub": "China capped at 20%; hearing set for January"},
    {"cell": "summit", "kicker": "EUROPE",
     "head": "EU SPLIT OVER UKRAINE LOAN",
     "sub": "Leaders divided on a $49bn loan to Kyiv"},
]
STRIP_STORIES = [
    {"cell": "bank", "kicker": "EUROPE",
     "head": "SPAIN'S DE COS TO LEAD ECB",
     "sub": "Chosen to succeed Lagarde at the central bank"},
    {"cell": "gaza", "kicker": "GAZA",
     "head": "ISRAELI STRIKES KILL 10 IN GAZA",
     "sub": "Ceasefire under strain for a third night"},
]
ALSO_ITEMS = [
    "EBOLA IN CONGO PASSES 12,000 CASES \u2014 second-largest outbreak on record",
    "NETANYAHU JUDGES URGE DROPPING BRIBERY CHARGE",
    "GUINEA-BISSAU JUNTA DELAYS ELECTION TO 2028",
]

DATE_LINE = "FRIDAY, 27 NOVEMBER 2026"


def draw_masthead(draw: ImageDraw.ImageDraw) -> None:
    draw.text((W // 2, 12), "THE WORLD IN ONE DAY",
              font=font("cond_bold", 62), fill=INK, anchor="ma")
    draw.rectangle((EDGE, 96, W - EDGE, 99), fill=RED)
    draw.text((W // 2, 104), DATE_LINE,
              font=font("cond_bold", 27), fill=INK, anchor="ma")


def draw_panels(page: Image.Image, draw: ImageDraw.ImageDraw,
                src: Image.Image) -> None:
    panel_w, panel_h, photo_h = 490, 300, 170
    xs = [EDGE, 526]
    ys = [140, 452]
    for i, story in enumerate(PANEL_STORIES):
        x, y = xs[i % 2], ys[i // 2]
        x0, y0, x1, y1 = CELLS[story["cell"]]
        photo = crop_cover(src.crop((x0, y0, x1, y1)),
                           FOCUS[story["cell"]], panel_w, photo_h)
        page.paste(photo, (x, y))
        draw.rectangle((x, y, x + panel_w - 1, y + photo_h - 1),
                       outline=FRAME, width=1)
        ty = y + photo_h + 8
        draw.text((x, ty), story["kicker"], font=font("cond_bold", 19),
                  fill=RED)
        ty += 24
        head_fnt, head_lines = headline_font(draw, story["head"], 36, panel_w)
        for line in head_lines:
            draw.text((x, ty), line, font=head_fnt, fill=INK)
            ty += head_fnt.size + 2
        # Subheads sit on a fixed baseline per row (two headline lines
        # reserved) so the two panels of a row line up even when one
        # headline wraps and the other does not.
        sub_y = y + photo_h + 8 + 24 + 2 * (head_fnt.size + 2)
        draw.text((x, sub_y), story["sub"], font=font("cond", 23), fill=GREY)


def draw_strip(page: Image.Image, draw: ImageDraw.ImageDraw,
               src: Image.Image) -> None:
    top, height, thumb_w = 764, 116, 150
    for i, story in enumerate(STRIP_STORIES):
        x = EDGE if i == 0 else 526
        x0, y0, x1, y1 = CELLS[story["cell"]]
        thumb = crop_cover(src.crop((x0, y0, x1, y1)),
                           FOCUS[story["cell"]], thumb_w, height)
        page.paste(thumb, (x, top))
        draw.rectangle((x, top, x + thumb_w - 1, top + height - 1),
                       outline=FRAME, width=1)
        tx = x + thumb_w + 12
        text_w = 490 - thumb_w - 12
        draw.text((tx, top + 2), story["kicker"], font=font("cond_bold", 18),
                  fill=RED)
        head_fnt, head_lines = headline_font(draw, story["head"], 30, text_w)
        ty = top + 24
        for line in head_lines:
            draw.text((tx, ty), line, font=head_fnt, fill=INK)
            ty += head_fnt.size + 1
        sub_fnt = font("cond", 18)
        for line in split_lines(draw, story["sub"], sub_fnt, text_w)[:2]:
            draw.text((tx, ty + 2), line, font=sub_fnt, fill=GREY)
            ty += sub_fnt.size + 1


def draw_also(draw: ImageDraw.ImageDraw) -> None:
    top = 892
    draw.rectangle((0, top, W, H), fill=NAVY)
    draw.text((EDGE, top + 6), "ALSO TODAY", font=font("cond_bold", 22),
              fill=GOLD)
    # Items at 29px for more presence; the shrink loop drops any item
    # that would run past the right edge back to a size that fits.
    y = top + 33
    for item in ALSO_ITEMS:
        size = 29
        while size > 19:
            fnt = font("cond", size)
            if draw.textlength(item, font=fnt) <= W - 34 - EDGE:
                break
            size -= 1
        draw.rectangle((EDGE, y + 9, EDGE + 8, y + 17), fill=RED)
        draw.text((34, y), item, font=fnt, fill=PALE)
        y += 31


def build() -> None:
    src = Image.open(SOURCE_PATH).convert("RGB")
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)
    draw_masthead(draw)
    draw_panels(page, draw, src)
    draw_strip(page, draw, src)
    draw_also(draw)
    page.save(OUTPUT_PATH, "PNG", optimize=True)
    print("wrote", OUTPUT_PATH)


def verify() -> str:
    with Image.open(OUTPUT_PATH) as im:
        assert im.size == (W, H), im.size
        assert im.format == "PNG"
    size = os.path.getsize(OUTPUT_PATH)
    assert size <= 1_048_576, size
    digest = hashlib.sha256(open(OUTPUT_PATH, "rb").read()).hexdigest()
    print(f"verify: 1024x1024 PNG, {size} bytes, sha256 {digest}")
    return digest


if __name__ == "__main__":
    build()
    verify()
