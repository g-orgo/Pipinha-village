import struct, zlib

class NBTReader:
    def __init__(self, data):
        self.d = data; self.p = 0
    def rb(self, n):
        v = self.d[self.p:self.p+n]; self.p += n; return v
    def read_tag(self, tid=None):
        if tid is None:
            tid = self.rb(1)[0]
            if tid == 0: return None
            name = self.read_str()
        else:
            name = None
        val = self.read_payload(tid)
        return (name, tid, val)
    def read_str(self):
        (ln,) = struct.unpack('>H', self.rb(2))
        return self.rb(ln).decode('utf-8')
    def read_payload(self, tid):
        if tid == 0: return None
        if tid == 1: return struct.unpack('>b', self.rb(1))[0]
        if tid == 2: return struct.unpack('>h', self.rb(2))[0]
        if tid == 3: return struct.unpack('>i', self.rb(4))[0]
        if tid == 4: return struct.unpack('>q', self.rb(8))[0]
        if tid == 5: return struct.unpack('>f', self.rb(4))[0]
        if tid == 6: return struct.unpack('>d', self.rb(8))[0]
        if tid == 7:
            (ln,) = struct.unpack('>i', self.rb(4)); return self.rb(ln)
        if tid == 8: return self.read_str()
        if tid == 9:
            et = self.rb(1)[0]; (ln,) = struct.unpack('>i', self.rb(4))
            return (et, [self.read_payload(et) for _ in range(ln)])
        if tid == 10:
            d = {}
            while True:
                t = self.read_tag()
                if t is None: break
                d[t[0]] = (t[1], t[2])
            return d
        if tid == 11:
            (ln,) = struct.unpack('>i', self.rb(4))
            return [struct.unpack('>i', self.rb(4))[0] for _ in range(ln)]
        if tid == 12:
            (ln,) = struct.unpack('>i', self.rb(4))
            return [struct.unpack('>q', self.rb(8))[0] for _ in range(ln)]
        raise ValueError(f'bad tag {tid}')

def read_region_chunk(path, cx, cz):
    with open(path,'rb') as f:
        hdr = f.read(8192)
    lx, lz = cx & 31, cz & 31
    (loc,) = struct.unpack('>I', hdr[4*(lx+lz*32):4*(lx+lz*32)+4])
    if loc == 0: return None
    off, cnt = (loc >> 8)*4096, (loc & 255)*4096
    with open(path,'rb') as f:
        f.seek(off)
        (ln,) = struct.unpack('>I', f.read(4))
        comp = f.read(1)[0]
        raw = f.read(ln-1)
    data = zlib.decompress(raw) if comp==2 else raw
    r = NBTReader(data)
    return r.read_tag()
