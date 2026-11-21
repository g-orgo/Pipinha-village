#!/usr/bin/env python3
"""Patch Tanuki Decor 21.1.0.2 so its tag listener stops firing tooltips on world load.

Root cause (log 2026-11-14 20:38, 20:39, 20:42):
    tanukidecor.client.ClientRecipeCollections.onUpdateTags re-filters the DIY
    recipe collections still held from the PREVIOUS world and rebuilds a search
    tree that calls ItemStack.getTooltipLines on every result. With
    UpdateCause.SERVER_DATA_LOAD this runs inside WorldLoader, before the server
    configs of the new world are loaded, so any ItemTooltipEvent listener that
    reads a SERVER config throws (Iron's RPG Tweaks did) and the world only opens
    in safe mode. The first entry of a game process works because the list is
    still empty.

Fix:
    Prepend to onUpdateTags:
        if (event.getUpdateCause() == UpdateCause.SERVER_DATA_LOAD) return;
    The client still runs it for CLIENT_PACKET_RECEIVED, and onUpdateRecipes
    rebuilds the list from scratch on join, so nothing is lost.

    Bytes: aload_0; invokevirtual getUpdateCause; getstatic SERVER_DATA_LOAD;
    if_acmpne +4; return  (11 bytes, no switch in the method, so alignment is
    irrelevant). New constant pool entries are appended; StackMapTable gets a
    same_frame at offset 11; LineNumberTable / LocalVariableTable(Type) offsets
    shift by 11 (entries starting at 0 grow instead).

Usage:
    python3 tools/pack_tools/patch_tanukidecor.py           # patch the jar in mods/
    python3 tools/pack_tools/patch_tanukidecor.py --check   # dry run
"""

import os
import shutil
import struct
import sys
import zipfile

JAR = "mods/tanukidecor-21.1.0.2.jar"
ORIGINAL = "backups/tanukidecor-21.1.0.2.original.jar"
ENTRY = "tanukidecor/client/ClientRecipeCollections.class"
METHOD, DESC = "onUpdateTags", "(Lnet/neoforged/neoforge/event/TagsUpdatedEvent;)V"
EVENT = "net/neoforged/neoforge/event/TagsUpdatedEvent"
CAUSE = EVENT + "$UpdateCause"
U2, U4 = struct.Struct(">H"), struct.Struct(">I")


def u2(b, i):
    return U2.unpack_from(b, i)[0]


def u4(b, i):
    return U4.unpack_from(b, i)[0]


def patch_class(d):
    count = u2(d, 8)
    i, k, utf, classes = 10, 1, {}, {}
    while k < count:
        t = d[i]
        if t == 1:
            n = u2(d, i + 1)
            utf[k] = d[i + 3:i + 3 + n].decode()
            i += 3 + n
        elif t in (5, 6):
            i, k = i + 9, k + 1
        elif t in (7, 8, 16, 19, 20):
            if t == 7:
                classes[k] = u2(d, i + 1)
            i += 3
        elif t == 15:
            i += 4
        else:
            i += 5
        k += 1
    cp_end = i
    if "getUpdateCause" in utf.values():
        raise SystemExit("already patched")
    event_cls = next(c for c, n in classes.items() if utf[n] == EVENT)

    new, nxt = bytearray(), count
    def add(tag, payload):
        nonlocal nxt
        new.extend(bytes([tag]) + payload)
        nxt += 1
        return nxt - 1
    def utf8(s):
        b = s.encode()
        return add(1, U2.pack(len(b)) + b)
    nat_m = add(12, U2.pack(utf8("getUpdateCause")) + U2.pack(utf8("()L%s;" % CAUSE)))
    mref = add(10, U2.pack(event_cls) + U2.pack(nat_m))
    cause_cls = add(7, U2.pack(utf8(CAUSE)))
    nat_f = add(12, U2.pack(utf8("SERVER_DATA_LOAD")) + U2.pack(utf8("L%s;" % CAUSE)))
    fref = add(9, U2.pack(cause_cls) + U2.pack(nat_f))
    prefix = bytes([0x2A, 0xB6]) + U2.pack(mref) + b"\xb2" + U2.pack(fref) + b"\xa6\x00\x04\xb1"
    shift = len(prefix)

    def skip_member(j):
        n, j = u2(d, j + 6), j + 8
        for _ in range(n):
            j += 6 + u4(d, j + 2)
        return j

    # access, this_class, super_class, then interfaces, fields, methods.
    i = cp_end + 6
    i += 2 + 2 * u2(d, i)
    j = i + 2
    for _ in range(u2(d, i)):
        j = skip_member(j)
    i = j
    j = i + 2
    for _ in range(u2(d, i)):
        if (utf[u2(d, j + 2)], utf[u2(d, j + 4)]) == (METHOD, DESC):
            break
        j = skip_member(j)
    else:
        raise SystemExit("method not found")
    a = j + 8
    while utf[u2(d, a)] != "Code":
        a += 6 + u4(d, a + 2)
    alen, max_stack, max_locals, clen = u4(d, a + 2), u2(d, a + 6), u2(d, a + 8), u4(d, a + 10)
    code = d[a + 14:a + 14 + clen]
    p = a + 14 + clen
    if u2(d, p):
        raise SystemExit("unexpected exception table")
    p += 2
    attrs = bytearray()
    n_attrs, q = u2(d, p), p + 2
    for _ in range(n_attrs):
        an, ln = utf[u2(d, q)], u4(d, q + 2)
        body = bytearray(d[q + 6:q + 6 + ln])
        if an == "StackMapTable":
            # The old first frame moves by `shift` too, and now follows the new
            # frame at `shift`: its delta becomes old_offset + shift - shift - 1.
            first = body[2]
            if 0 < first < 64 or 64 < first < 128:
                body[2] = first - 1
            elif first in (247, 248, 249, 250, 251, 252, 253, 254, 255):
                U2.pack_into(body, 3, u2(body, 3) - 1)
            else:
                raise SystemExit("unexpected first frame %d" % first)
            U2.pack_into(body, 0, u2(body, 0) + 1)
            body = body[:2] + bytes([shift]) + body[2:]
        elif an == "LineNumberTable":
            for e in range(u2(body, 0)):
                o = 2 + 4 * e
                if u2(body, o):
                    U2.pack_into(body, o, u2(body, o) + shift)
        elif an in ("LocalVariableTable", "LocalVariableTypeTable"):
            for e in range(u2(body, 0)):
                o = 2 + 10 * e
                if u2(body, o):
                    U2.pack_into(body, o, u2(body, o) + shift)
                else:
                    U2.pack_into(body, o + 2, u2(body, o + 2) + shift)
        attrs += U2.pack(u2(d, q)) + U4.pack(len(body)) + body
        q += 6 + ln
    new_code = U2.pack(max(max_stack, 2)) + U2.pack(max_locals) + U4.pack(clen + shift) + prefix + code
    new_code += b"\x00\x00" + U2.pack(n_attrs) + attrs
    out = (d[:8] + U2.pack(nxt) + d[10:cp_end] + bytes(new) + d[cp_end:a]
           + U2.pack(u2(d, a)) + U4.pack(len(new_code)) + new_code + d[a + 6 + alen:])
    return out


def main():
    check = "--check" in sys.argv
    src = ORIGINAL if os.path.exists(ORIGINAL) else JAR
    with zipfile.ZipFile(src) as z:
        patched = patch_class(z.read(ENTRY))
        print("%s: %d -> %d bytes" % (ENTRY, len(z.read(ENTRY)), len(patched)))
        if check:
            return
        if not os.path.exists(ORIGINAL):
            shutil.copy2(JAR, ORIGINAL)
        tmp = JAR + ".tmp"
        with zipfile.ZipFile(tmp, "w") as out:
            for info in z.infolist():
                data = patched if info.filename == ENTRY else z.read(info)
                out.writestr(info, data, compress_type=info.compress_type)
    os.replace(tmp, JAR)
    print("patched", JAR, "(original in %s)" % ORIGINAL)


if __name__ == "__main__":
    main()
