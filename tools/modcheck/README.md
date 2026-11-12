# modcheck

Light checks for `mods/` without launching the game.

- `python3 -I ranges.py <mods dir> <neoforge version>`: required deps present, version ranges, declared incompatibilities (nested jars included, highest version wins).
- `python3 -I mixscan.py <mods dir>`: mixin classes that reference classes of an installed mod that do not exist in the installed version (the PowerfulJS x Create 6.0.10 crash pattern). Hits whose target already shows as "@Mixin target ... was not found" WARN in `logs/latest.log` are optional and skipped by the game.

Known false positives of `ranges.py`: bare versions (NeoForge treats them as a recommendation) and `1.21-x` vs `1.21.1-x` qualifiers.
