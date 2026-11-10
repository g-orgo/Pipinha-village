#!/usr/bin/env python3
# Prepares an isolated copy of the instance; nothing in the real instance is written.
import os, shutil, sys
SRC=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",".."))
DST=sys.argv[1]
os.makedirs(DST+"/mods",exist_ok=True)
os.makedirs(DST+"/resourcepacks",exist_ok=True)
for n in os.listdir(SRC+"/mods"):
    if "CrashAssistant" in n: continue
    p=DST+"/mods/"+n
    if not os.path.islink(p) and os.path.isfile(SRC+"/mods/"+n): os.symlink(SRC+"/mods/"+n,p)
for n in os.listdir(SRC+"/resourcepacks"):
    p=DST+"/resourcepacks/"+n
    if not os.path.lexists(p): os.symlink(SRC+"/resourcepacks/"+n,p)
for d in ["config","defaultconfigs","configureddefaults","kubejs","moonlight-global-datapacks","datapacks","fancymenu_data","patchouli_books","quests_structures","data","local","emojiful"]:
    if os.path.isdir(SRC+"/"+d):
        shutil.rmtree(DST+"/"+d,ignore_errors=True)
        shutil.copytree(SRC+"/"+d,DST+"/"+d,symlinks=True)
shutil.copy(SRC+"/options.txt",DST+"/options.txt")
