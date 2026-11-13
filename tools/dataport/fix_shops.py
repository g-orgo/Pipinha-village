"""Convert society_trading shop files from the 1.20.1 item format to the 1.21.1 format.

1.20.1 item stacks look like {"item": "ns:id", "count": N, "nbt": "{...}"}.
1.21.1 item stacks (ItemStack codec) look like {"id": "ns:id", "count": N, "components": {...}}.

Rules applied to every item stack in kubejs/data/society_trading/shops/*.json:
- "item" becomes "id".
- StoredEnchantments nbt on minecraft:enchanted_book becomes the
  minecraft:stored_enchantments component.
- society:villager with {type:{id:"society:X"}} becomes society:villager_home with
  minecraft:custom_data {"type": "X"}, the shape npcInvite.js reads in 1.21.1.
- Any other nbt has no verified 1.21.1 mapping. It is kept under "legacy_nbt",
  which the codec ignores, so the data is not lost and the owner can decide.

The script is idempotent: already converted stacks (with "id") are left alone.

Usage: python3 fix_shops.py [--dry-run]
"""

import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SHOPS = os.path.join(ROOT, "kubejs", "data", "society_trading", "shops")

STACK_KEYS = {"item", "count", "nbt"}  # keys consumed by the conversion; other keys are kept
ENCHANT_RE = re.compile(r'\{StoredEnchantments:\s*\[\{id:\s*"([^"]+)",\s*lvl:\s*(\d+)s?\}\]\}')
VILLAGER_RE = re.compile(r'\{type:\{id:\s*"society:([a-z_]+)"\}\}')
INVITATION_RE = re.compile(r'\{"?type"?:\s*\{"?id"?:\s*"(society:[a-z_]+)"\}\}')  # SNBT or JSON-quoted


def parse_snbt(text):
    """Parse the subset of SNBT used by the shop files (compounds, lists, strings, numbers)."""
    pos = 0

    def skip():
        nonlocal pos
        while pos < len(text) and text[pos] in " \t\r\n":
            pos += 1

    def value():
        nonlocal pos
        skip()
        ch = text[pos]
        if ch == "{":
            pos += 1
            out = {}
            skip()
            while text[pos] != "}":
                key = string_or_word()
                skip()
                if text[pos] != ":":
                    raise ValueError("expected ':'")
                pos += 1
                out[key] = value()
                skip()
                if text[pos] == ",":
                    pos += 1
                    skip()
            pos += 1
            return out
        if ch == "[":
            pos += 1
            out = []
            skip()
            if text[pos:pos + 2] in ("B;", "I;", "L;"):
                pos += 2
            while text[pos] != "]":
                out.append(value())
                skip()
                if text[pos] == ",":
                    pos += 1
            pos += 1
            return out
        if ch in "\"'":
            return string_or_word()
        match = re.compile(r"[-+]?\d+(\.\d+)?[bslfdBSLFD]?(?=[,\]}\s]|$)").match(text, pos)
        if not match:
            return string_or_word()  # bare word such as owner_name:Ace
        pos = match.end()
        token = match.group(0)
        if match.group(1) or token[-1] in "fdFD":
            return float(token.rstrip("bslfdBSLFD"))
        return int(token.rstrip("bslBSL"))

    def string_or_word():
        nonlocal pos
        skip()
        if text[pos] in "\"'":
            quote = text[pos]
            pos += 1
            chars = []
            while text[pos] != quote:
                if text[pos] == "\\":
                    pos += 1
                chars.append(text[pos])
                pos += 1
            pos += 1
            return "".join(chars)
        start = pos
        while pos < len(text) and (text[pos].isalnum() or text[pos] in "_.+-"):
            pos += 1
        if pos == start:
            raise ValueError("empty token")
        return text[start:pos]

    result = value()
    skip()
    if pos != len(text):
        raise ValueError("trailing data")
    return result


def worn_blueprint_components(nbt):
    """The 1.21.1 worn blueprint keeps its fields in custom_data (see WornBlueprint.class);
    the damage moves to its component and the translated display block is dropped,
    because the name and author lore come from the blueprint's translation keys."""
    data = parse_snbt(nbt)
    damage = data.pop("Damage", None)
    data.pop("display", None)
    components = {"minecraft:custom_data": data}
    if damage is not None:
        components["minecraft:damage"] = damage
    return components


def invitation_components(nbt):
    """society:invitation keeps the target as a plain string in custom_data.
    npcInvite.js calls getString("type") and strips the "society:" prefix, so a compound
    {id: ...} would be read as an empty string and the invitation would do nothing."""
    return {"minecraft:custom_data": {"type": INVITATION_RE.fullmatch(nbt.strip()).group(1)}}


def convert_stack(stack, report):
    """Return the converted stack, or the same dict if it is not an item stack."""
    if not isinstance(stack, dict) or "item" not in stack or not isinstance(stack["item"], str):
        return stack

    item = stack["item"]
    out = {"id": item}
    if "count" in stack:
        out["count"] = stack["count"]

    nbt = stack.get("nbt")
    if nbt is not None:
        m_ench = ENCHANT_RE.fullmatch(nbt.strip()) if isinstance(nbt, str) else None
        m_vill = VILLAGER_RE.fullmatch(nbt.strip()) if isinstance(nbt, str) else None
        if item == "minecraft:enchanted_book" and m_ench:
            out["components"] = {
                "minecraft:stored_enchantments": {
                    "levels": {"minecraft:" + m_ench.group(1).split(":", 1)[1]: int(m_ench.group(2))}
                }
            }
            report["enchanted_book"] += 1
        elif item == "society:villager" and m_vill:
            out["id"] = "society:villager_home"
            out["components"] = {"minecraft:custom_data": {"type": m_vill.group(1)}}
            report["villager"] += 1
        elif item == "portable_blueprints:worn_blueprint" and parses(nbt):
            out["components"] = worn_blueprint_components(nbt)
            report["worn_blueprint"] += 1
        elif item == "society:invitation" and INVITATION_RE.fullmatch(nbt.strip()):
            out["components"] = invitation_components(nbt)
            report["invitation"] += 1
        elif item == "supplementaries:cartographers_quill":
            report["quill"] += 1  # plain quill: the map decoration nbt is dropped
        elif item == "patchouli:guide_book" and parses(nbt) and "patchouli:book" in parse_snbt(nbt):
            out["components"] = {"minecraft:custom_data": parse_snbt(nbt)}
            report["patchouli"] += 1
        else:
            out["legacy_nbt"] = nbt
            report["legacy_nbt"] += 1
    for key, value in stack.items():
        if key not in STACK_KEYS:
            out[key] = value  # e.g. priceModifier, carried over untouched
    report["stacks"] += 1
    return out


def parses(nbt):
    try:
        parse_snbt(nbt)
        return True
    except (ValueError, IndexError):
        return False


def retry_legacy(stack, report):
    """Map a stack already converted (has "id") whose nbt was parked under legacy_nbt."""
    nbt = stack["legacy_nbt"]
    item = stack["id"]
    if item == "portable_blueprints:worn_blueprint" and parses(nbt):
        stack["components"] = worn_blueprint_components(nbt)
    elif item == "patchouli:guide_book" and parses(nbt) and "patchouli:book" in parse_snbt(nbt):
        stack["components"] = {"minecraft:custom_data": parse_snbt(nbt)}
    elif item == "society:invitation" and INVITATION_RE.fullmatch(nbt.strip()):
        stack["components"] = invitation_components(nbt)
    elif item == "supplementaries:cartographers_quill":
        pass  # plain quill: drop the map decoration nbt
    else:
        return stack
    del stack["legacy_nbt"]
    report["legacy_remapped"] += 1
    return stack


def convert(node, report):
    if isinstance(node, dict):
        if "item" in node and isinstance(node.get("item"), str):
            return convert_stack(node, report)
        if "legacy_nbt" in node and isinstance(node.get("id"), str):
            return retry_legacy(node, report)
        return {k: convert(v, report) for k, v in node.items()}
    if isinstance(node, list):
        return [convert(x, report) for x in node]
    return node


def main():
    dry = "--dry-run" in sys.argv
    report = {
        "files": 0, "stacks": 0, "enchanted_book": 0, "villager": 0, "legacy_nbt": 0,
        "worn_blueprint": 0, "patchouli": 0, "legacy_remapped": 0, "invitation": 0, "quill": 0,
    }
    for path in sorted(glob.glob(os.path.join(SHOPS, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        data = json.loads(text)
        before = dict(report)
        new = convert(data, report)
        if report == before:
            continue
        report["files"] += 1
        indent = "\t" if "\n\t" in text else 2
        new_text = json.dumps(new, indent=indent, ensure_ascii=False) + "\n"
        if not dry and new_text != text:
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new_text)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
