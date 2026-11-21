#!/usr/bin/env python3
"""Patch IronsRPGTweaks 2.2.3 so the sleep module tooltip hook cannot crash.

Root cause (log 2026-11-14 20:38):
    io.redspace.ironsrpgtweaks.sleep_module.SleepCommonEvents.handleTooltips
    calls ServerConfigs.SLEEP_MODULE_ENABLED.get() on every ItemTooltipEvent.
    The second world entry in the same game process fires ItemTooltipEvent while
    TanukiDecor rebuilds its client recipe collections inside
    ReloadableServerResources.updateRegistryTags, before the server config is
    loaded. ModConfigSpec then throws IllegalStateException and the world fails
    to load ("Failed to load level data or datapacks" / safe mode screen).

Fix:
    The Code attribute of handleTooltips is replaced by a body that only does
    `return` (max_stack 0, code `b1`, no exception table, no nested attributes).
    The method keeps its signature and the event subscription, it just stops
    reading the config. The sleep module is disabled in this pack
    (config/irons_rpg_tweaks-server.toml, sleepModuleEnabled = false), so the
    tooltips added by this handler were never shown anyway.

    A shorter body means rewriting the whole Code attribute: attribute_length,
    code_length and the nested LineNumberTable / LocalVariableTable /
    StackMapTable of that method go away, and the bytes after it move. Nothing
    else in the class changes, and the constant pool is untouched.

The class file is parsed by hand (no external dependency).

Usage:
    python3 patch_irons_rpg_tweaks.py           # patch mods/irons_rpg_tweaks-2.2.3.jar
    python3 patch_irons_rpg_tweaks.py --check   # only report what would change
"""

import shutil
import struct
import sys
import zipfile

JAR = "mods/irons_rpg_tweaks-2.2.3.jar"
ORIGINAL = "backups/irons_rpg_tweaks-2.2.3.original.jar"
ENTRY = "io/redspace/ironsrpgtweaks/sleep_module/SleepCommonEvents.class"
METHOD = "handleTooltips"
METHOD_DESC = "(Lnet/neoforged/neoforge/event/entity/player/ItemTooltipEvent;)V"

# The guard this patch removes: getstatic SLEEP_MODULE_ENABLED; invokevirtual
# ConfigValue.get(); checkcast Boolean; invokevirtual booleanValue(); ifne +4;
# return.
GUARD_PREFIX = bytes.fromhex("b20007b6000dc00013b600159a0004")
GUARD_LEN = len(GUARD_PREFIX)

# Minimal replacement Code attribute body: max_stack, max_locals, code_length,
# code (return), exception_table_length, attributes_count. max_locals is filled
# in from the original method.
NEW_BODY = struct.Struct(">HHI")  # max_stack, max_locals, code_length


class Reader:
    def __init__(self, data, pos=0):
        self.data = data
        self.pos = pos

    def u1(self):
        value = self.data[self.pos]
        self.pos += 1
        return value

    def u2(self):
        value = struct.unpack_from(">H", self.data, self.pos)[0]
        self.pos += 2
        return value

    def u4(self):
        value = struct.unpack_from(">I", self.data, self.pos)[0]
        self.pos += 4
        return value

    def skip(self, count):
        self.pos += count


def parse_constant_pool(reader):
    count = reader.u2()
    pool = [None] * count
    index = 1
    while index < count:
        tag = reader.u1()
        if tag == 1:  # Utf8
            length = reader.u2()
            pool[index] = ("utf8", reader.data[reader.pos:reader.pos + length].decode("utf-8", "replace"))
            reader.skip(length)
        elif tag in (3, 4):  # Integer, Float
            reader.skip(4)
        elif tag in (5, 6):  # Long, Double
            reader.skip(8)
            index += 1
        elif tag in (7, 8, 16, 19, 20):  # Class, String, MethodType, Module, Package
            reader.skip(2)
        elif tag in (9, 10, 11, 12, 17, 18):  # refs, NameAndType, Dynamic, InvokeDynamic
            reader.skip(4)
        elif tag == 15:  # MethodHandle
            reader.skip(3)
        else:
            raise SystemExit("unknown constant pool tag %d at %d" % (tag, reader.pos - 1))
        index += 1
    return pool


def find_code_attribute(data):
    """Return (attribute_start, attribute_end, max_locals, code_offset, code_length)."""
    reader = Reader(data)
    if reader.u4() != 0xCAFEBABE:
        raise SystemExit("not a class file")
    reader.skip(4)
    pool = parse_constant_pool(reader)

    def utf8(index):
        entry = pool[index]
        if not entry or entry[0] != "utf8":
            raise SystemExit("constant %d is not a Utf8" % index)
        return entry[1]

    reader.skip(2 + 2 + 2)  # access_flags, this_class, super_class
    reader.skip(2 * reader.u2())  # interfaces
    fields_count = reader.u2()
    for _ in range(fields_count):
        reader.skip(6)
        for _ in range(reader.u2()):
            reader.skip(2)
            reader.skip(reader.u4())

    methods_count = reader.u2()
    found = []
    for _ in range(methods_count):
        reader.skip(2)
        name = utf8(reader.u2())
        desc = utf8(reader.u2())
        for _ in range(reader.u2()):
            attr_start = reader.pos
            attr_name = utf8(reader.u2())
            length = reader.u4()
            body_start = reader.pos
            if attr_name == "Code" and name == METHOD and desc == METHOD_DESC:
                code_reader = Reader(data, body_start)
                code_reader.skip(4)  # max_stack, max_locals
                code_length = code_reader.u4()
                if 8 + code_length > length:
                    raise SystemExit("code array overflows its attribute")
                found.append({
                    "start": attr_start,
                    "name_index": struct.unpack_from(">H", data, attr_start)[0],
                    "end": body_start + length,
                    "max_locals": struct.unpack_from(">H", data, body_start + 2)[0],
                    "code_offset": code_reader.pos,
                    "code_length": code_length,
                })
            reader.pos = body_start + length
    if len(found) != 1:
        raise SystemExit("expected exactly one Code attribute for %s, found %d" % (METHOD, len(found)))
    return found[0]


def read_entry(jar_path):
    with zipfile.ZipFile(jar_path) as jar:
        return jar.read(ENTRY)


def build_code_attribute(attribute, max_locals):
    body = NEW_BODY.pack(0, max_locals, 1) + b"\xb1" + struct.pack(">HH", 0, 0)
    return struct.pack(">H", attribute["name_index"]) + struct.pack(">I", len(body)) + body


def main():
    check_only = "--check" in sys.argv

    original = read_entry(ORIGINAL)
    current = read_entry(JAR)
    attribute = find_code_attribute(current)
    guard = current[attribute["code_offset"]:attribute["code_offset"] + GUARD_LEN]

    print("guard: %s" % guard.hex(" "))
    if guard != GUARD_PREFIX:
        if guard == b"\xb1":
            print("already patched:", JAR)
            return 0
        raise SystemExit("unexpected code in %s; refusing to patch" % METHOD)

    original_attribute = find_code_attribute(original)
    if original_attribute["code_offset"] != attribute["code_offset"]:
        raise SystemExit("current jar differs from the original; refusing to patch")

    new_attribute = build_code_attribute(attribute, attribute["max_locals"])
    patched = current[:attribute["start"]] + new_attribute + current[attribute["end"]:]

    if check_only:
        print("would replace Code of %s: %d -> %d bytes in %s"
              % (METHOD, attribute["end"] - attribute["start"], len(new_attribute), ENTRY))
        return 0

    tmp = JAR + ".tmp"
    with zipfile.ZipFile(ORIGINAL) as src, zipfile.ZipFile(tmp, "w") as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == ENTRY:
                data = patched
            dst.writestr(info, data)
    shutil.move(tmp, JAR)
    print("patched", JAR)

    attribute = find_code_attribute(read_entry(JAR))
    code = read_entry(JAR)[attribute["code_offset"]:attribute["code_offset"] + attribute["code_length"]]
    if code != b"\xb1" or attribute["code_length"] != 1:
        raise SystemExit("patch did not stick: %r" % code)
    print("patched code: %s (length %d)" % (code.hex(), attribute["code_length"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
