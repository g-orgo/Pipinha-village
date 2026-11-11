import struct

def w_str(s):
    b = s.encode('utf-8')
    return struct.pack('>H', len(b)) + b

def w_payload(tid, val):
    if tid == 0: return b''
    if tid == 1: return struct.pack('>b', val)
    if tid == 2: return struct.pack('>h', val)
    if tid == 3: return struct.pack('>i', val)
    if tid == 4: return struct.pack('>q', val)
    if tid == 5: return struct.pack('>f', val)
    if tid == 6: return struct.pack('>d', val)
    if tid == 7: return struct.pack('>i', len(val)) + bytes(val)
    if tid == 8: return w_str(val)
    if tid == 9:
        et, items = val
        out = struct.pack('B', et) + struct.pack('>i', len(items))
        for it in items: out += w_payload(et, it)
        return out
    if tid == 10:
        out = b''
        for name, (ctid, cval) in val.items():
            out += struct.pack('B', ctid) + w_str(name) + w_payload(ctid, cval)
        return out + b'\x00'
    if tid == 11:
        out = struct.pack('>i', len(val))
        for v in val: out += struct.pack('>i', v)
        return out
    if tid == 12:
        out = struct.pack('>i', len(val))
        for v in val:
            if v >= 2**63: v -= 2**64
            out += struct.pack('>q', v)
        return out
    raise ValueError(tid)

def w_tag(name, tid, val):
    return struct.pack('B', tid) + w_str(name) + w_payload(tid, val)
