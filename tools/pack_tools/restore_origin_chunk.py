"""Puts the chunks around (0,0) back from a save backup zip (game closed). Usage:
python3 -I sunlit_tools/restore_origin_chunk.py "<save>" "<backup.zip>" [--radius 2]
Why: at server start the ALI mod builds one of every entity and the Brewery rope knot reads the block at 0,0,0.
A full chunk needs its neighbours generated up to light, so without the 5x5 around the origin the server
generates terrain synchronously before the first tick (minutes with Lithosphere, world load stuck at 0%).
Chunks already in the save are left alone; only missing ones are copied (raw sectors, any status)."""
import os, subprocess, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrofit_hedges import read_region

save, backup = sys.argv[1], sys.argv[2]
radius = int(sys.argv[sys.argv.index('--radius') + 1]) if '--radius' in sys.argv else 2
if subprocess.run("pgrep -a java | grep -qi singleplayer", shell=True).returncode == 0:
    sys.exit('game is running: close it first')
name = os.path.basename(os.path.normpath(save))
want = {}
for cx in range(-radius, radius + 1):
    for cz in range(-radius, radius + 1):
        want.setdefault((cx >> 5, cz >> 5), []).append((cx & 31) + (cz & 31) * 32)
restored = 0
with zipfile.ZipFile(backup) as z:
    for (rx, rz), idxs in sorted(want.items()):
        try:
            src = z.read(f'{name}/region/r.{rx}.{rz}.mca')
        except KeyError:
            continue
        dst = os.path.join(save, 'region', f'r.{rx}.{rz}.mca')
        raw = open(dst, 'rb').read() if os.path.exists(dst) else b''
        body = bytearray(raw if len(raw) >= 8192 else bytes(8192))
        for i in idxs:
            loc = int.from_bytes(src[4 * i:4 * i + 4], 'big')
            if not loc or int.from_bytes(body[4 * i:4 * i + 4], 'big'):
                continue  # missing in the backup, or already in the save
            off, sectors = (loc >> 8) * 4096, loc & 0xFF
            body += bytes((-len(body)) % 4096)
            start = len(body) // 4096
            body += src[off:off + sectors * 4096]
            body[4 * i:4 * i + 4] = ((start << 8) | sectors).to_bytes(4, 'big')
            body[4096 + 4 * i:4100 + 4 * i] = src[4096 + 4 * i:4100 + 4 * i]
            restored += 1
        open(dst, 'wb').write(bytes(body))
        ok = len(read_region(dst)[1])
        print(f'r.{rx}.{rz}.mca: {ok} chunks readable')
print('restored', restored, 'chunks around (0,0) from', os.path.basename(backup))
