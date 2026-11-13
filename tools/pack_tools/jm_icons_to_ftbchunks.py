"""Convert JourneyMap entity icons into FTB Chunks map faces.

FTB Chunks (EntityIcons) looks up one texture per entity type at
ftbchunks:textures/faces/<namespace>/<path>.png (non-MISC entities only).
JourneyMap packs ship assets/<namespace>/textures/entity_icon/... with
variants in subfolders. This script picks one icon per entity that is
actually registered in this instance (entity.<ns>.<name> lang keys in the
mod jars) and is not already covered by FTB Chunks or FTB Chunks Modded,
then writes it under kubejs/assets/ftbchunks/textures/faces/.

Usage (from the instance root):
  python3 sunlit_tools/jm_icons_to_ftbchunks.py            # write icons
  python3 sunlit_tools/jm_icons_to_ftbchunks.py --dry-run  # only list
"""
import glob
import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = [
    'resourcepacks/JourneyMap Extended Mob Icons v2.0.zip.disabled',
    'resourcepacks/Icon Journey 1.1.zip.disabled',
]
FTB_JARS = ['mods/ftb-chunks-forge-*.jar', 'mods/ftb-chunks-modded-*.jar']
OUT = os.path.join(ROOT, 'kubejs/assets/ftbchunks/textures/faces')

# Pack namespace typos and explicit picks: entity id -> icon path inside the pack.
ALIASES = {
    'crabbersdelight:crab': 'assets/crabbbersdelight/textures/entity_icon/red_crab.png',
    'hamsters:hamster': 'assets/hamsters/textures/entity_icon/hamster/orange.png',
    'snuffles:snuffle': 'assets/snuffles/textures/entity_icon/snuffle/snuffle_default.png',
    'rottencreatures:undead_miner': 'assets/rottencreatures/textures/entity_icon/undead_miner/undead_miner_stone.png',
    'untitledduckmod:goose': 'assets/untitledduckmod/textures/entity_icon/untitled_goose.png',
    'crittersandcompanions:sea_bunny': 'assets/crittersandcompanions/textures/entity_icon/sea_bunny_blue.png',
}
SKIP = re.compile(r'(^|_)(baby|sleeping|glow)(_|$)|^duckling$|^gosling$')
LANG_KEY = re.compile(r'^entity\.([a-z0-9_.\-]+)\.([a-z0-9_\-]+)$')
ICON = re.compile(r'^assets/([^/]+)/textures/entity_icon/(.+)\.png$')


def registered_entities():
    ents = set()
    for jar in glob.glob(os.path.join(ROOT, 'mods', '*.jar')):
        try:
            z = zipfile.ZipFile(jar)
        except zipfile.BadZipFile:
            continue
        for name in z.namelist():
            if re.match(r'^assets/[^/]+/lang/en_us\.json$', name):
                try:
                    data = json.loads(z.read(name).decode('utf-8', 'ignore'))
                except ValueError:
                    continue
                for key in data:
                    m = LANG_KEY.match(key)
                    if m:
                        ents.add(f'{m.group(1)}:{m.group(2)}')
    return ents


def ftb_faces():
    faces = set()
    for pattern in FTB_JARS:
        for jar in glob.glob(os.path.join(ROOT, pattern)):
            for name in zipfile.ZipFile(jar).namelist():
                m = re.match(r'^assets/ftbchunks/textures/faces/([^/]+)/(.+)\.(png|invisible)$', name)
                if m:
                    faces.add(f'{m.group(1)}:{m.group(2)}')
    return faces


def candidates(path):
    """Entity names a JourneyMap icon path may stand for, best first."""
    parts = path.split('/')
    last = parts[-1]
    out = [parts[0], last, re.sub(r'_\d+$', '', last)]
    return out, last


def score(entity_name, last, parts):
    if SKIP.search(last):
        return None
    if last == entity_name:
        return 0
    if last == f'{entity_name}_1':
        return 1
    if 'default' in last:
        return 2
    if parts[0] == entity_name:
        return 3
    if re.sub(r'_\d+$', '', last) == entity_name:
        return 4
    return None


def main():
    dry = '--dry-run' in sys.argv
    ents = registered_entities()
    have = ftb_faces()
    picks = {}
    for pack in PACKS:
        z = zipfile.ZipFile(os.path.join(ROOT, pack))
        for name in sorted(z.namelist()):
            m = ICON.match(name)
            if not m:
                continue
            ns, path = m.groups()
            cands, last = candidates(path)
            for cand in cands:
                ent = f'{ns}:{cand}'
                if ent not in ents or ent in have or ent in ALIASES:
                    continue
                s = score(cand, last, path.split('/'))
                if s is None:
                    continue
                if ent not in picks or s < picks[ent][0]:
                    picks[ent] = (s, pack, name)
                break
    for ent, icon in ALIASES.items():
        if ent in ents and ent not in have:
            for pack in PACKS:
                if icon in zipfile.ZipFile(os.path.join(ROOT, pack)).namelist():
                    picks[ent] = (0, pack, icon)
    for ent in sorted(picks):
        _, pack, name = picks[ent]
        ns, path = ent.split(':')
        print(f'{ent} <- {os.path.basename(pack)}: {name.split("entity_icon/")[1]}')
        if not dry:
            dest = os.path.join(OUT, ns, f'{path}.png')
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(zipfile.ZipFile(os.path.join(ROOT, pack)).read(name))
    print(f'{len(picks)} icons {"listed" if dry else "written to " + os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    main()
