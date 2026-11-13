import json, os, re, sys, zipfile, collections
root = sys.argv[1]
G = collections.defaultdict(set); src = collections.defaultdict(set)
pat = re.compile(r'(?:^|/)data/([^/]+)/tags/items?/(.+)\.json$')
def feed(name, data, origin):
    m = pat.search(name)
    if not m: return
    t = f"{m.group(1)}:{m.group(2)}"
    try: j = json.loads(data)
    except Exception: return
    for v in j.get("values", []) if isinstance(j, dict) else []:
        i = v.get("id") if isinstance(v, dict) else v
        if isinstance(i, str) and i.startswith("#"):
            G[t].add(i[1:]); src[(t, i[1:])].add(origin)
for d in ["kubejs", "datapacks", "dynamic-data-pack-cache", "moonlight-global-datapacks", "mods", "global_packs", "openloader"]:
    p = os.path.join(root, d)
    for dp, _, fs in os.walk(p):
        for f in fs:
            fp = os.path.join(dp, f)
            if f.endswith(".json"):
                feed(fp.replace(os.sep, "/"), open(fp, "rb").read(), os.path.relpath(fp, root))
            elif f.endswith((".jar", ".zip")):
                try:
                    z = zipfile.ZipFile(fp)
                    for n in z.namelist():
                        if "/tags/item" in n and n.endswith(".json"):
                            feed(n, z.read(n), os.path.relpath(fp, root) + "!" + n)
                except Exception: pass
# Tarjan-free: DFS cycle detection
sys.setrecursionlimit(100000)
color = {}; found = []
def dfs(u, stack):
    color[u] = 1; stack.append(u)
    for v in G.get(u, ()):
        if color.get(v) == 1:
            found.append(stack[stack.index(v):] + [v])
        elif v not in color:
            dfs(v, stack)
    stack.pop(); color[u] = 2
for n in list(G):
    if n not in color: dfs(n, [])
print("nodes", len(G), "cycles", len(found))
for c in found[:10]:
    print(" -> ".join(c))
    for a, b in zip(c, c[1:]):
        print("   ", a, "->", b, ":", sorted(src[(a, b)])[:3])
