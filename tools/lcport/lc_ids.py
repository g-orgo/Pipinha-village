"""Known block/item id scanner for the Lost Cities port.

Reads blockstates and item models from every jar in mods/ (including nested
jars under META-INF/jarjar), from kubejs/assets, and from the vanilla jar.
Uses only the standard library and never extracts a jar to disk.
"""

import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODS = os.path.join(ROOT, "mods")
KUBEJS_ASSETS = os.path.join(ROOT, "kubejs", "assets")
VANILLA_JAR = "/var/home/Orgo/Documentos/curseforge/minecraft/Install/versions/1.21.1/1.21.1.jar"


def _scan_zip(zf, blocks, items, nested, depth=0):
    for name in zf.namelist():
        low = name.lower()
        if low.startswith("assets/") and "/blockstates/" in low and low.endswith(".json"):
            parts = name.split("/")
            if len(parts) >= 4:
                ns = parts[1]
                base = parts[-1][:-5]
                blocks.add(ns + ":" + base)
        elif low.startswith("assets/") and "/models/item/" in low and low.endswith(".json"):
            parts = name.split("/")
            if len(parts) >= 5:
                ns = parts[1]
                base = parts[-1][:-5]
                items.add(ns + ":" + base)
        elif name.startswith("META-INF/jarjar/") and low.endswith(".jar"):
            try:
                data = zf.read(name)
                import io
                with zipfile.ZipFile(io.BytesIO(data)) as inner:
                    nested.append(inner)
            except Exception:
                pass


def _scan_jar(path, blocks, items):
    try:
        with zipfile.ZipFile(path) as zf:
            nested = []
            _scan_zip(zf, blocks, items, nested)
            while nested:
                inner = nested.pop()
                _scan_zip(inner, blocks, items, nested)
    except Exception:
        pass


def scan_known_ids():
    blocks = set()
    items = set()
    if os.path.isdir(MODS):
        for fn in sorted(os.listdir(MODS)):
            if fn.lower().endswith(".jar"):
                _scan_jar(os.path.join(MODS, fn), blocks, items)
    if os.path.isfile(VANILLA_JAR):
        _scan_jar(VANILLA_JAR, blocks, items)
    if os.path.isdir(KUBEJS_ASSETS):
        for ns in sorted(os.listdir(KUBEJS_ASSETS)):
            bs = os.path.join(KUBEJS_ASSETS, ns, "blockstates")
            if os.path.isdir(bs):
                for fn in os.listdir(bs):
                    if fn.endswith(".json"):
                        blocks.add(ns + ":" + fn[:-5])
            im = os.path.join(KUBEJS_ASSETS, ns, "models", "item")
            if os.path.isdir(im):
                for fn in os.listdir(im):
                    if fn.endswith(".json"):
                        items.add(ns + ":" + fn[:-5])
    kjs_items, kjs_blocks = _scan_kubejs_registrations()
    items |= kjs_items
    blocks |= kjs_blocks
    items |= blocks
    return blocks, items


def _scan_kubejs_registrations():
    """Ids registered by KubeJS startup scripts. Many have no model file in kubejs/assets,
    so they are collected from create() literals, namespaced string literals in startup
    scripts, item/block textures and en_us lang keys."""
    import json
    import re
    items, blocks = set(), set()
    startup = os.path.join(ROOT, "kubejs", "startup_scripts")
    # Only create("ns:id") literals and society:* literals: other namespaced strings in the
    # scripts are references to mod items (tables, aliases), not registrations.
    create_lit = re.compile(r"""create\(\s*['"]([a-z0-9_.-]+:[a-z0-9_/.-]+)['"]""")
    society_lit = re.compile(r"""['"](society:[a-z0-9_/.-]+)['"]""")
    for dp, _, fns in os.walk(startup):
        for fn in fns:
            if fn.endswith(".js"):
                with open(os.path.join(dp, fn), encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
                for m in create_lit.finditer(text):
                    items.add(m.group(1))
                for m in society_lit.finditer(text):
                    items.add(m.group(1))
    if os.path.isdir(KUBEJS_ASSETS):
        # Textures and lang only for the pack's own namespace: other folders in kubejs/assets
        # hold leftovers copied from 1.20.1 for mods that no longer register those ids.
        for ns in [n for n in os.listdir(KUBEJS_ASSETS) if n == "society"]:
            for kind, target in (("item", items), ("block", blocks)):
                tex = os.path.join(KUBEJS_ASSETS, ns, "textures", kind)
                if os.path.isdir(tex):
                    for fn in os.listdir(tex):
                        if fn.endswith(".png"):
                            target.add(ns + ":" + fn[:-4])
            lang = os.path.join(KUBEJS_ASSETS, ns, "lang", "en_us.json")
            if os.path.isfile(lang):
                try:
                    keys = json.load(open(lang, encoding="utf-8"))
                except Exception:
                    keys = {}
                for k in keys:
                    parts = k.split(".")
                    if len(parts) == 3 and parts[0] in ("item", "block"):
                        items.add(parts[1] + ":" + parts[2])
                        if parts[0] == "block":
                            blocks.add(parts[1] + ":" + parts[2])
    return items, blocks


_BLOCKSTATES = {}


def _iter_blockstate_blobs():
    """Yield (rel_path, raw_bytes) for every blockstates json, jars included."""
    if os.path.isdir(MODS):
        for fn in sorted(os.listdir(MODS)):
            if not fn.lower().endswith(".jar"):
                continue
            try:
                with zipfile.ZipFile(os.path.join(MODS, fn)) as zf:
                    inner_zips = []
                    for name in zf.namelist():
                        if name.startswith("assets/") and "/blockstates/" in name and name.endswith(".json"):
                            yield name, zf.read(name)
                        elif name.startswith("META-INF/jarjar/") and name.lower().endswith(".jar"):
                            import io
                            try:
                                inner_zips.append(zipfile.ZipFile(io.BytesIO(zf.read(name))))
                            except Exception:
                                pass
                    while inner_zips:
                        inner = inner_zips.pop()
                        try:
                            for name in inner.namelist():
                                if name.startswith("assets/") and "/blockstates/" in name and name.endswith(".json"):
                                    yield name, inner.read(name)
                                elif name.startswith("META-INF/jarjar/") and name.lower().endswith(".jar"):
                                    import io
                                    try:
                                        inner_zips.append(zipfile.ZipFile(io.BytesIO(inner.read(name))))
                                    except Exception:
                                        pass
                        finally:
                            inner.close()
            except Exception:
                continue
    if os.path.isfile(VANILLA_JAR):
        try:
            with zipfile.ZipFile(VANILLA_JAR) as zf:
                for name in zf.namelist():
                    if name.startswith("assets/") and "/blockstates/" in name and name.endswith(".json"):
                        yield name, zf.read(name)
        except Exception:
            pass
    if os.path.isdir(KUBEJS_ASSETS):
        for ns in sorted(os.listdir(KUBEJS_ASSETS)):
            d = os.path.join(KUBEJS_ASSETS, ns, "blockstates")
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if fn.endswith(".json"):
                    with open(os.path.join(d, fn), "rb") as fh:
                        yield "assets/%s/blockstates/%s" % (ns, fn), fh.read()


def _load_blockstates():
    if _BLOCKSTATES:
        return _BLOCKSTATES
    for rel, raw in _iter_blockstate_blobs():
        parts = rel.split("/")
        if len(parts) < 4:
            continue
        key = parts[1] + ":" + parts[-1][:-5]
        if key in _BLOCKSTATES:
            continue
        try:
            _BLOCKSTATES[key] = json.loads(raw.decode("utf-8"))
        except Exception:
            _BLOCKSTATES[key] = None
    return _BLOCKSTATES


def blockstate_json(block_id):
    """Return the parsed blockstates json of a block id, or None."""
    return _load_blockstates().get(block_id)


def collect_state_keys(node, keys):
    """Collect property names from a blockstates json (variants or multipart)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("variants",):
                for state in node[k]:
                    if state:
                        for prop in state.split(","):
                            keys.add(prop.split("=")[0])
            elif k == "when":
                for cond in (node[k] if isinstance(node[k], list) else [node[k]]):
                    if isinstance(cond, dict):
                        for prop in cond:
                            if prop in ("OR", "AND"):
                                continue
                            keys.add(prop.split("|")[0])
            else:
                collect_state_keys(v, keys)
    elif isinstance(node, list):
        for v in node:
            collect_state_keys(v, keys)
    return keys


def accepted_states(block_id):
    """Return {prop: set(values)} accepted by a block, or None if unknown."""
    bs = blockstate_json(block_id)
    if bs is None:
        return None
    out = {}
    if "variants" in bs:
        for state in bs["variants"]:
            if not state:
                continue
            for prop in state.split(","):
                k, _, v = prop.partition("=")
                out.setdefault(k, set()).add(v)
    # multipart: properties appear in "when"; their values are not enumerated,
    # so accept any value for those property names.
    keys = collect_state_keys(bs, set())
    for k in keys:
        out.setdefault(k, None)
    return out
