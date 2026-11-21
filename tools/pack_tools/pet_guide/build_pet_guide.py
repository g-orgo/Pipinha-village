#!/usr/bin/env python3
"""Builds the "Companheiros" FTB Quests chapter (tameable mob guide, no rewards) from content.json.

Idempotent: rewrites the chapter file, replaces every lang entry of the chapter (stale ones are
removed), regenerates the quest maps of kubejs/server_scripts/entities/petGuideQuests.js, writes the
Redomesticate taming definitions of content.json "taming" (kubejs/data/society/redomesticate/taming
and the entity tags they use) and sets the order of the Tutorial group so the chapter comes before
"I - Getting Started".
Run from anywhere: python3 -I tools/pack_tools/pet_guide/build_pet_guide.py
Print fresh ids for new boxes: python3 -I tools/pack_tools/pet_guide/build_pet_guide.py --new-ids 4
"""
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
QUESTS = ROOT / "config/ftbquests/quests"
LOCALIZER = ROOT / "kubejs/assets/ftbquestlocalizer/lang"
JS = ROOT / "kubejs/server_scripts/entities/petGuideQuests.js"
GROUP = "457DCF55318282CA"  # Tutorial
ORDER = ["companheiros", "getting_started", "ii__building_up_the_farm", "iii__advanced_farming",
         "iv__prismatic_farming", "ivi__mechanical_farming", "profissoes", "botania"]
COINS = {"crown": {"en": "Crowns", "pt": "Moedas de Ouro"},
         "ancient": {"en": "Ancient Coins", "pt": "Moedas Antigas"}}
EGG_LINE = {"en": "Spawn egg: crafting table with &6{m}&r, 4 &6{c}&r, 3 Bone Blocks and an egg.",
            "pt": "Ovo de spawn: bancada com &6{m}&r, 4 &6{c}&r, 3 Blocos de Osso e um ovo."}
# FTB Quests reads ids as signed longs: an id starting with 8-F is replaced on load and the
# lang keys lose their quest. Ids must start with 0-7.
ID_RE = re.compile(r"^[0-7][0-9A-F]{15}$")


def other_ids(filename):
    ids = set()
    for path in (QUESTS / "chapters").glob("*.snbt"):
        if path.stem != filename:
            ids.update(re.findall(r'\bid: "([0-9A-F]{16})"', path.read_text(encoding="utf-8")))
    return ids


def check_ids(content):
    found = [content["chapter"]["id"], content["intro"]["id"], content["intro"]["task"]]
    for mob in content["pets"] + content["others"]:
        found += [mob["id"], mob["task"]]
    bad = [i for i in found if not ID_RE.match(i)]
    dup = {i for i in found if found.count(i) > 1} | (set(found) & other_ids(content["chapter"]["filename"]))
    if bad or dup:
        sys.exit("invalid ids: %s, duplicated ids: %s" % (bad, sorted(dup)))


def pet_lines(content, pet, lang):
    group = content["groups"][pet["group"]]
    lines = [pet["intro"][lang], group["bonus"][lang]]
    if "scare" in group:
        lines.append(group["scare"][lang])
    lines.append(pet["gift"][lang])
    mineral = pet.get("mineral_pt", pet["mineral"]) if lang == "pt" else pet["mineral"]
    lines.append(EGG_LINE[lang].format(m=mineral, c=COINS[pet.get("coin", "crown")][lang]))
    return lines


def build(content):
    ch = content["chapter"]
    base = "ftbquests.chapter." + ch["filename"]
    loc = {"en": {}, "pt": {}}
    snbt_lang = {}
    quests = []

    def add_text(obj_key, field_key, values):
        for lang in ("en", "pt"):
            loc[lang][field_key] = values[lang]
        snbt_lang[obj_key] = '"{' + field_key + '}"'

    add_text("chapter.%s.title" % ch["id"], base + ".title", ch["title"])
    for lang in ("en", "pt"):
        loc[lang][base + ".subtitle0"] = ch["subtitle"][lang]
    snbt_lang["chapter.%s.chapter_subtitle" % ch["id"]] = '["{' + base + '.subtitle0}"]'

    def add_quest(qid, tid, title, subtitle, lines, task_title):
        qkey = "%s.quest%s" % (base, qid)
        add_text("quest.%s.title" % qid, qkey + ".title", title)
        add_text("quest.%s.quest_subtitle" % qid, qkey + ".subtitle", subtitle)
        add_text("task.%s.title" % tid, qkey + ".task.title", task_title)
        refs = []
        for i in range(len(lines["en"])):
            key = "%s.description%d" % (qkey, i + 1)
            for lang in ("en", "pt"):
                loc[lang][key] = lines[lang][i]
            if refs:
                refs.append('\t\t""')
            refs.append('\t\t"{%s}"' % key)
        snbt_lang["quest.%s.quest_desc" % qid] = "[\n" + "\n".join(refs) + "\n\t]"

    intro = content["intro"]
    add_quest(intro["id"], intro["task"], intro["title"], intro["subtitle"], intro["lines"], intro["task_title"])
    quests.append("\t\t{\n\t\t\ticon: { id: \"%s\" }\n\t\t\tid: \"%s\"\n\t\t\tsize: 2.0d\n"
                  "\t\t\ttasks: [{\n\t\t\t\tid: \"%s\"\n\t\t\t\ttype: \"checkmark\"\n\t\t\t}]\n"
                  "\t\t\tx: 0.0d\n\t\t\ty: 0.0d\n\t\t}" % (intro["icon"], intro["id"], intro["task"]))
    for mob in content["pets"] + content["others"]:
        if "group" in mob:
            lines = {lang: pet_lines(content, mob, lang) for lang in ("en", "pt")}
            sub, task_title = content["groups"][mob["group"]]["sub"], content["task_titles"]["pet"]
        else:
            lines, sub = mob["lines"], mob["sub"]
            task_title = content["task_titles"][mob.get("complete", "tame")]
        if len(lines["en"]) != len(lines["pt"]):
            sys.exit("en/pt line count differs: " + mob["key"])
        add_quest(mob["id"], mob["task"], mob["title"], sub, lines, task_title)
        quests.append("\t\t{\n\t\t\tid: \"%s\"\n\t\t\ttasks: [{\n\t\t\t\tid: \"%s\"\n"
                      "\t\t\t\titem: { count: 1, id: \"%s\" }\n\t\t\t\ttype: \"item\"\n\t\t\t}]\n"
                      "\t\t\tx: %.1fd\n\t\t\ty: %.1fd\n\t\t}" % (mob["id"], mob["task"], mob["egg"], mob["x"], mob["y"]))

    chapter = ("{\n\tautofocus_id: \"%s\"\n\tdefault_hide_dependency_lines: false\n\tdefault_quest_shape: \"\"\n"
               "\tfilename: \"%s\"\n\tgroup: \"%s\"\n\ticon: {\n\t\tid: \"%s\"\n\t}\n\tid: \"%s\"\n\timages: [ ]\n"
               "\torder_index: 0\n\tquest_links: [ ]\n\tquests: [\n%s\n\t]\n}\n"
               % (intro["id"], ch["filename"], GROUP, ch["icon"], ch["id"], "\n".join(quests)))
    # Minecraft's I18n.get runs String.format on the text: a lone % shows "Format error".
    loc = {lang: {k: v.replace("%", "%%") for k, v in loc[lang].items()} for lang in loc}
    return chapter, snbt_lang, loc


def merge_snbt_lang(path, entries, marker):
    """Drops every entry that points to this chapter's keys, then appends the new ones."""
    lines = path.read_text(encoding="utf-8").rstrip().split("\n")
    if lines[-1] != "}":
        sys.exit("unexpected end of %s" % path)
    kept, entry = [], []
    for line in lines[1:-1]:
        if line.startswith("\t") and not line.startswith("\t\t") and not line.startswith("\t]"):
            kept += [] if marker in "\n".join(entry) else entry
            entry = []
        entry.append(line)
    kept += [] if marker in "\n".join(entry) else entry
    new = ["\t%s: %s" % (key, entries[key]) for key in sorted(entries)]
    path.write_text("\n".join([lines[0]] + kept + new + ["}"]) + "\n", encoding="utf-8")
    return len(lines) - 2 - len(kept), len(new)


def merge_json_lang(path, entries, prefix):
    """Replaces this chapter's keys in place (first old key's position), keeping the rest as is."""
    old = json.loads(path.read_text(encoding="utf-8"))
    out, placed = {}, False
    for key, value in old.items():
        if key.startswith(prefix):
            if not placed:
                out.update(entries)
                placed = True
        else:
            out[key] = value
    if not placed:
        out.update(entries)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(entries)


def write_js(content):
    text = JS.read_text(encoding="utf-8")
    mobs = content["pets"] + content["others"]
    pairs = [(e, m) for m in mobs for e in [m["entity"]] + m.get("also", [])]
    quests = "".join('    "%s": "%s",\n' % (e, m["id"]) for e, m in pairs)
    interact = "".join('    "%s": true,\n' % e for e, m in pairs if m.get("complete") == "interact")
    block = ("  // BEGIN generated by tools/pack_tools/pet_guide/build_pet_guide.py\n"
             "  const PET_GUIDE_QUESTS = {\n%s  };\n  const INTERACT_ONLY = {\n%s  };\n  // END generated\n"
             % (quests, interact))
    new, count = re.subn(r"  // BEGIN generated.*?  // END generated\n", lambda m: block, text, flags=re.S)
    if count != 1:
        sys.exit("generated block not found in %s" % JS)
    JS.write_text(new, encoding="utf-8")


def write_taming(content):
    """Redomesticate taming definitions (any Mob becomes tameable with the item) for the mobs with
    no taming of their own. Each definition points to an entity tag with optional entries, so an id
    that a mod stops registering never breaks the datapack registry (and the world load)."""
    defs = ROOT / "kubejs/data/society/redomesticate/taming"
    tags = ROOT / "kubejs/data/society/tags/entity_type/tameable"
    for folder in (defs, tags):
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("*.json"):
            old.unlink()
    boxed = {e for m in content["pets"] + content["others"] for e in [m["entity"]] + m.get("also", [])}
    seen = set()
    for group, data in content["taming"].items():
        dup = seen & set(data["entities"])
        if dup:
            sys.exit("entity in two taming groups: %s" % sorted(dup))
        seen |= set(data["entities"])
        missing = [e for e in data["entities"] if e not in boxed]
        if missing:
            sys.exit("taming entity without a guide box: %s" % missing)
        tag = {"replace": False, "values": [{"id": e, "required": False} for e in data["entities"]]}
        (tags / (group + ".json")).write_text(json.dumps(tag, indent=2) + "\n", encoding="utf-8")
        definition = {"entities": "#society:tameable/" + group, "items": data["items"]}
        (defs / (group + ".json")).write_text(json.dumps(definition, indent=2) + "\n", encoding="utf-8")
    return len(content["taming"]), len(seen)


def set_order():
    changed = []
    for index, name in enumerate(ORDER):
        path = QUESTS / "chapters" / (name + ".snbt")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        new = re.sub(r"^\torder_index: \d+$", "\torder_index: %d" % index, text, count=1, flags=re.M)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.append("%s=%d" % (name, index))
    return changed


def main():
    content = json.loads((HERE / "content.json").read_text(encoding="utf-8"))
    if sys.argv[1:2] == ["--new-ids"]:
        taken = other_ids("")
        for _ in range(int(sys.argv[2])):
            new = "%016X" % random.getrandbits(63)
            print(new if new not in taken else "retry")
        return
    check_ids(content)
    chapter, snbt_lang, loc = build(content)
    name = content["chapter"]["filename"]
    out = QUESTS / "chapters" / (name + ".snbt")
    out.write_text(chapter, encoding="utf-8")
    print("chapter:", out.relative_to(ROOT), "quests:", chapter.count("\n\t\t{\n"))
    print("snbt lang (removed, added):", merge_snbt_lang(QUESTS / "lang/en_us.snbt", snbt_lang, "ftbquests.chapter.%s." % name))
    prefix = "ftbquests.chapter.%s." % name
    print("en_us.json keys:", merge_json_lang(LOCALIZER / "en_us.json", loc["en"], prefix))
    print("pt_br.json keys:", merge_json_lang(LOCALIZER / "pt_br.json", loc["pt"], prefix))
    write_js(content)
    print("taming (definitions, mobs):", write_taming(content))
    print("order changed:", set_order() or "none")


if __name__ == "__main__":
    main()
