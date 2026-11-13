#!/usr/bin/env python3
"""Offline preview of a first person Immersive Eating model at given animation times.

Follows the GeckoLib 4 conventions (bedrock x mirrored, bone rotation (-x, -y, z), order Z, Y, X
around the pivot, keyframes added to the rest pose) and draws textured cubes with a painter's
sort per texel. The camera is an approximation of the first person view, good to judge shapes,
colors and what hides what; it is not a pixel match of the game.

Usage: preview.py <name> <out.png> [t1,t2,...] [--cam x,y,z] [--pitch deg] [--fov deg]
<name> is the file stem under kubejs/assets/food/{geo,animations,textures/item}.
"""
import argparse
import json
import math

import mat as np
from PIL import Image, ImageDraw

ROOT = "kubejs/assets/food"
W, H = 640, 360


def rot(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler(r):
    # GeckoLib: bedrock (x, y, z) degrees -> rotZ(z) * rotY(-y) * rotX(-x)
    return rot("z", r[2]) @ rot("y", -r[1]) @ rot("x", -r[0])


def sample(track, t):
    if track is None:
        return None
    if isinstance(track, list):
        return [float(v) for v in track]
    if "vector" in track:
        return [float(v) for v in track["vector"]]
    keys = sorted((float(k), v["vector"] if isinstance(v, dict) else v) for k, v in track.items())
    if t <= keys[0][0]:
        return [float(v) for v in keys[0][1]]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return [float(a) + (float(b) - float(a)) * f for a, b in zip(v0, v1)]
    return [float(v) for v in keys[-1][1]]


def bone_matrices(bones, anim, t):
    """Returns name -> 4x4 world matrix in GeckoLib space (x mirrored)."""
    by_name = {b["name"]: b for b in bones}
    out = {}

    def world(name):
        if name in out:
            return out[name]
        b = by_name[name]
        parent = world(b["parent"]) if b.get("parent") in by_name else np.eye(4)
        track = anim.get(name, {})
        r = list(b.get("rotation", [0, 0, 0]))
        dr = sample(track.get("rotation"), t)
        if dr:
            r = [a + d for a, d in zip(r, dr)]
        p = sample(track.get("position"), t) or [0, 0, 0]
        s = sample(track.get("scale"), t)
        s = s if s else [1, 1, 1]
        piv = np.array([-b["pivot"][0], b["pivot"][1], b["pivot"][2]], dtype=float)
        m = np.eye(4)
        np.set_col(m, 3, [-p[0], p[1], p[2]])
        m2 = np.eye(4)
        np.set_block(m2, 3, 3, euler(r) @ np.diag(s))
        tp, tn = np.eye(4), np.eye(4)
        np.set_col(tp, 3, piv)
        np.set_col(tn, 3, piv * -1)
        out[name] = parent @ m @ tp @ m2 @ tn
        return out[name]

    for b in bones:
        world(b["name"])
    return out


FACE_CORNERS = {  # unit cube corners per face, ordered top-left, top-right, bottom-right, bottom-left of the uv
    "north": [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)],
    "south": [(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)],
    "east": [(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)],
    "west": [(1, 1, 1), (1, 1, 0), (1, 0, 0), (1, 0, 1)],
    "up": [(1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)],
    "down": [(1, 0, 1), (0, 0, 1), (0, 0, 0), (1, 0, 0)],
}
SHADE = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "east": 0.65, "west": 0.65}


def render(name, times, cam, pitch, fov, out):
    geo = json.load(open(f"{ROOT}/geo/{name}.geo.json"))["minecraft:geometry"][0]
    tex = Image.open(f"{ROOT}/textures/item/{name}.png").convert("RGBA")
    tw, th = geo["description"]["texture_width"], geo["description"]["texture_height"]
    sx, sy = tex.width / tw, tex.height / th
    anim = json.load(open(f"{ROOT}/animations/{name}.animation.json"))["animations"]["eat"]["bones"]
    frames = []
    view = rot("x", -pitch)
    f = (H / 2) / math.tan(math.radians(fov) / 2)
    for t in times:
        mats = bone_matrices(geo["bones"], anim, t)
        polys = []
        for b in geo["bones"]:
            if b["name"] in ("leftArm", "rightArm"):
                color_override = (200, 160, 128, 255)
            else:
                color_override = None
            for c in b.get("cubes", []):
                o, size = c["origin"], c["size"]
                x0 = -(o[0] + size[0])
                base = np.array([x0, o[1], o[2]], dtype=float)
                cm = np.eye(4)
                if c.get("rotation"):
                    cp = np.array([-c["pivot"][0], c["pivot"][1], c["pivot"][2]], dtype=float)
                    tp, tn, rr = np.eye(4), np.eye(4), np.eye(4)
                    np.set_col(tp, 3, cp)
                    np.set_col(tn, 3, cp * -1)
                    np.set_block(rr, 3, 3, euler(c["rotation"]))
                    cm = tp @ rr @ tn
                m = mats[b["name"]] @ cm
                for face, corners in FACE_CORNERS.items():
                    uv = c.get("uv", {}).get(face)
                    if uv is None:
                        continue
                    pts = [m @ np.append(base + np.array(k) * np.array(size), 1) for k in corners]
                    pts = [view @ (p[:3] - cam) for p in pts]
                    u0, v0 = uv["uv"]
                    uw, vh = uv["uv_size"]
                    nu, nv = max(1, min(16, int(abs(round(uw))))), max(1, min(16, int(abs(round(vh)))))
                    tl, tr, br, bl = pts
                    for j in range(nv):
                        for i in range(nu):
                            a0, a1, b0, b1 = i / nu, (i + 1) / nu, j / nv, (j + 1) / nv
                            q = [tl + (tr - tl) * a + ((bl + (br - bl) * a) - (tl + (tr - tl) * a)) * bb
                                 for a, bb in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
                            if any(p[2] > -0.5 for p in q):
                                continue
                            px = int((u0 + uw * (i + 0.5) / nu) * sx)
                            py = int((v0 + vh * (j + 0.5) / nv) * sy)
                            px, py = min(max(px, 0), tex.width - 1), min(max(py, 0), tex.height - 1)
                            col = color_override or tex.getpixel((px, py))
                            if col[3] < 16:
                                continue
                            k = SHADE[face]
                            col = tuple(int(ch * k) for ch in col[:3]) + (255,)
                            depth = sum(p[2] for p in q) / 4
                            scr = [(W / 2 + p[0] * f / -p[2], H / 2 - p[1] * f / -p[2]) for p in q]
                            polys.append((depth, scr, col))
        im = Image.new("RGBA", (W, H), (110, 140, 170, 255))
        d = ImageDraw.Draw(im)
        for _, scr, col in sorted(polys, key=lambda x: x[0]):
            d.polygon(scr, fill=col)
        d.text((4, 4), f"{name} t={t:.2f}", fill=(255, 255, 255, 255))
        frames.append(im)
    cols = 2 if len(frames) > 1 else 1
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGBA", (W * cols, H * rows))
    for n, im in enumerate(frames):
        sheet.paste(im, ((n % cols) * W, (n // cols) * H))
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("out")
    ap.add_argument("times", nargs="?", default="0.6,1.2,2.0,3.0")
    ap.add_argument("--cam", default="0,6,15")  # measured against the headless client, 2026-11-11
    ap.add_argument("--pitch", type=float, default=-3)
    ap.add_argument("--fov", type=float, default=70)
    a = ap.parse_args()
    render(a.name, [float(t) for t in a.times.split(",")], np.array([float(v) for v in a.cam.split(",")]),
           a.pitch, a.fov, a.out)


if __name__ == "__main__":
    main()
