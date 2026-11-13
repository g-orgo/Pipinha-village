"""Builds the hostile spawn toggle button textures used by
kubejs/startup_scripts/hostileSpawnToggle.js.

Each sheet is 64x64. Column u=0 is "hostile mobs spawn", column u=20 is
"hostile mobs do not spawn" (same face with a red slash). Rows: v=0 normal,
v=20 hovered, v=40 disabled, like ImageButton expects (yDiffTex = 20).

The frame is cut from the 20 px wide button of each pack's widgets.png
(left 10 px + right 10 px of the 200 px bar, same as vanilla Button does), so
the toggle matches the difficulty button next to it. The glyph uses the same
palette as the lock icon of that pack.

Usage (from the instance root):
  python3 sunlit_tools/gen_hostile_toggle_icons.py <vanilla widgets.png> <excalibur widgets.png>
"""
import sys
from pathlib import Path

from PIL import Image

OUT_DIR = Path("kubejs/assets/kubejs/textures/gui")

# widgets.png rows of the 200x20 button bar.
BAR_ROWS = {"normal": 66, "hover": 86, "disabled": 46}

# Creeper face, 8x8 inside a 1 px outline. "F" face, "L" lit top edge, "D" feature.
FACE = [
    "LLLLLLLL",
    "FDDFFDDF",
    "FDDFFDDF",
    "FFFDDFFF",
    "FFDDDDFF",
    "FFDDDDFF",
    "FFDFFDFF",
    "FFFFFFFF",
]

PALETTES = {
    "vanilla": {
        "outline": (0, 0, 0),
        "L": (214, 214, 214),
        "F": (170, 170, 170),
        "D": (69, 69, 69),
        "slash": (176, 46, 38),
        "disabled_mix": (111, 111, 111),
    },
    "excalibur": {
        "outline": (42, 34, 28),
        "L": (187, 160, 131),
        "F": (156, 130, 101),
        "D": (42, 34, 28),
        "slash": (138, 51, 36),
        "disabled_mix": (70, 57, 45),
    },
}


def mix(color, other, amount):
    return tuple(round(c * (1 - amount) + o * amount) for c, o in zip(color, other))


def frame(widgets, row):
    bar = widgets.crop((0, row, 200, row + 20))
    out = Image.new("RGBA", (20, 20))
    out.paste(bar.crop((0, 0, 10, 20)), (0, 0))
    out.paste(bar.crop((190, 0, 200, 20)), (10, 0))
    return out


def draw_glyph(img, pal, disabled, slashed):
    def put(x, y, color):
        if disabled:
            color = mix(color, pal["disabled_mix"], 0.55)
        img.putpixel((x, y), color + (255,))

    ox, oy = 5, 5
    for i in range(10):
        put(ox + i, oy, pal["outline"])
        put(ox + i, oy + 9, pal["outline"])
        put(ox, oy + i, pal["outline"])
        put(ox + 9, oy + i, pal["outline"])
    for y, line in enumerate(FACE):
        for x, key in enumerate(line):
            put(ox + 1 + x, oy + 1 + y, pal[key])
    if slashed:
        for i in range(3, 17):
            put(i, i, pal["slash"])
            if i + 1 <= 16:
                put(i + 1, i, pal["slash"])


def build(widgets_path, pal):
    widgets = Image.open(widgets_path).convert("RGBA")
    sheet = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for col, slashed in ((0, False), (20, True)):
        for row_v, state in ((0, "normal"), (20, "hover"), (40, "disabled")):
            tile = frame(widgets, BAR_ROWS[state])
            draw_glyph(tile, pal, state == "disabled", slashed)
            sheet.paste(tile, (col, row_v))
    return sheet


def main():
    vanilla, excalibur = sys.argv[1], sys.argv[2]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build(vanilla, PALETTES["vanilla"]).save(OUT_DIR / "hostile_spawns.png")
    build(excalibur, PALETTES["excalibur"]).save(OUT_DIR / "hostile_spawns_excalibur.png")
    print("written:", OUT_DIR / "hostile_spawns.png", OUT_DIR / "hostile_spawns_excalibur.png")


if __name__ == "__main__":
    main()
