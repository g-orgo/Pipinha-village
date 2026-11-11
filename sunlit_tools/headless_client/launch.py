#!/usr/bin/env python3
# Builds the Forge launch command from the version JSONs and execs it. Usage: run.py <gameDir> [extra game args]
import json, os, sys
R=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","..","..","Install"))
G=sys.argv[1]; extra=sys.argv[2:]
f=json.load(open(R+"/versions/forge-47.4.0/forge-47.4.0.json"))
v=json.load(open(R+"/versions/1.20.1/1.20.1.json"))
L=R+"/libraries"
def libs(j):
    out=[]
    for l in j["libraries"]:
        rules=l.get("rules")
        if rules:
            ok=False
            for r in rules:
                m=r.get("os",{}).get("name")
                if m is None or m=="linux": ok = r["action"]=="allow"
            if not ok: continue
        d=l.get("downloads",{}).get("artifact")
        if d and d.get("path"): p=d["path"]
        else:
            a=l["name"].split(":"); g=a[0].replace(".","/")
            cl=("-"+a[3]) if len(a)>3 else ""
            p=f"{g}/{a[1]}/{a[2]}/{a[1]}-{a[2]}{cl}.jar"
        p=L+"/"+p
        if os.path.exists(p) and p not in out: out.append(p)
    return out
cp=libs(f)+[x for x in libs(v) if x not in libs(f)]
cp.append(R+"/versions/forge-47.4.0/forge-47.4.0.jar")
sub={"${library_directory}":L,"${classpath_separator}":":","${version_name}":"forge-47.4.0","${natives_directory}":R+"/natives/forge-47.4.0","${launcher_name}":"x","${launcher_version}":"1","${classpath}":":".join(cp)}
def S(s):
    for k,w in sub.items(): s=s.replace(k,w)
    return s
jvm=[S(a) for a in f["arguments"]["jvm"] if isinstance(a,str)]
java=None
for root,_,files in os.walk(R+"/java/java-runtime-gamma"):
    if "java" in files and root.endswith("bin"): java=root+"/java"; break
cmd=[java,os.environ.get("PROBE_XMX","-Xmx5G"),"-Xms1G","-Djava.library.path="+sub["${natives_directory}"],"-Dorg.lwjgl.librarypath="+sub["${natives_directory}"],"-cp",sub["${classpath}"]]+jvm+[f["mainClass"]]
cmd+=["--username","SunlitBot","--version","forge-47.4.0","--gameDir",G,"--assetsDir",R+"/assets","--assetIndex",v["assetIndex"]["id"],"--uuid","00000000000000000000000000000001","--accessToken","0","--userType","legacy","--versionType","release","--width","1280","--height","720"]
cmd+=f["arguments"]["game"]+extra
print(" ".join(cmd)[:300],flush=True)
os.chdir(G)
os.execv(java,cmd)
