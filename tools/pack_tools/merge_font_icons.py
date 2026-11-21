"""Merge the pack's colored font icons into Excalibur's nonlatin_european.png.

Problem: Excalibur_V26.3_01.zip ships its own minecraft:font/nonlatin_european.png with
plain white glyphs. The pack draws its tooltip icons (coin, seasons, weather, tools...)
as colored glyphs in that same sheet, so with Excalibur on top they render as white dots.

Fix: SocietyCoins.zip sits above Excalibur in the pack order. It gets a sheet that is
Excalibur's sheet with only the pack's icon cells pasted from pipinha_overrides.zip,
so every other glyph keeps Excalibur's style.

Usage: python3 -I tools/pack_tools/merge_font_icons.py   (from the instance root)
"""
import io
import os
import shutil
import sys
import zipfile

from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
INSTANCE = os.path.dirname(os.path.dirname(BASE))
PACKS = os.path.join(INSTANCE, "resourcepacks")
SHEET = "assets/minecraft/textures/font/nonlatin_european.png"
ICON_SOURCE = os.path.join(PACKS, "pipinha_overrides.zip")
BASE_SOURCE = os.path.join(PACKS, "Excalibur_V26.3_01.zip")
TARGET = os.path.join(PACKS, "SocietyCoins.zip")
CELL = 8

# (row, column) of each custom icon in the vanilla 1.21.1 nonlatin_european layout.
ICON_CELLS = [
    (17, 3),  # U+2600 sun
    (19, 12), (19, 13), (19, 14), (19, 15),  # season icons
    (29, 13),  # U+25CF coin (tooltip.society.coins)
    (52, 1), (52, 2), (52, 3), (52, 4), (52, 10), (52, 12), (52, 13), (52, 14), (52, 15),
    (53, 0),
    (62, 13), (62, 15),
    (63, 9), (63, 10), (63, 11), (63, 12), (63, 13),
    (64, 4), (64, 5), (64, 6), (64, 7), (64, 8),
    (65, 4),
]


def read_sheet(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        return Image.open(io.BytesIO(z.read(SHEET))).convert("RGBA")


def main():
    icons = read_sheet(ICON_SOURCE)
    merged = read_sheet(BASE_SOURCE)
    if icons.size != merged.size:
        sys.exit(f"sheet size mismatch: {icons.size} vs {merged.size}")
    for row, col in ICON_CELLS:
        box = (col * CELL, row * CELL, (col + 1) * CELL, (row + 1) * CELL)
        merged.paste(icons.crop(box), box)
    png = io.BytesIO()
    merged.save(png, format="PNG", optimize=True)

    tmp = TARGET + ".tmp"
    with zipfile.ZipFile(TARGET) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            if info.filename != SHEET:
                dst.writestr(info, src.read(info.filename))
        dst.writestr(SHEET, png.getvalue())
    shutil.move(tmp, TARGET)
    print(f"{len(ICON_CELLS)} icon cells merged into {os.path.relpath(TARGET, INSTANCE)}")


if __name__ == "__main__":
    main()
