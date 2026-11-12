# Batch order (KubeJS 6 -> 7 manual port), shared by every batch operator

NEW root: `/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Pipinha's Village`.
**ROOT RULE: your shell starts in the OLD instance. Start EVERY shell command with
`cd "/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Pipinha's Village" &&` and use absolute
paths under the NEW root for Read/Edit/Write. Every relative path in any order means the NEW root.
Never read line numbers from, or edit, the OLD instance.**
OLD reference (read-only): `/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley`.

Goal: every file of YOUR batch (in `tools/kjsport/batches.json`) loads on KubeJS 7 / NeoForge 1.21.1
with the same behavior as in 1.20.1. Sites to fix are listed per file in `tools/kjsport/WORKLIST2.md`.

Allowed files: only the files of your batch, plus `tools/kjsport/REPORT_<batch>.md`.
The batch `server-globals` may also create `kubejs/startup_scripts/zz_port_globals_server.js`.
Never run `tools/kjsport/mechanical.py` or `mechanical2.py`. Other operators are editing other batches.

API: use only names in `tools/kjsport/API_NOTES.md` or names you verify yourself in the jars
(`mods/*.jar`, Minecraft classes in
`/var/home/Orgo/Documentos/curseforge/minecraft/Install/libraries/net/minecraft/client/1.21.1-20240808.144430/client-1.21.1-20240808.144430-srg.jar`,
NeoForge in `.../Install/libraries/net/neoforged/neoforge/21.1.265/neoforge-21.1.265-universal.jar`).
For member signatures use javap in a DETACHED container:
`docker run -d --name <batch>-javap -v <dir>:/w:z -w /w eclipse-temurin:21-jdk sh -c 'javap -cp x.jar <class>'`,
wait until `docker inspect -f '{{.State.Running}}'` is false, `docker logs ... 2>&1 | tail -n 60`, `docker rm`.
Never attached, never `logs -f`. Never guess a name.

Working method (keeps you well under budget):
- Never read whole files. For each site in WORKLIST2.md read only ~15 lines around it (`sed -n 'A,Bp'`).
- Batch all javap lookups of your batch into ONE detached container run.
- dropped_manual removals are pre-approved by the owner: just do them and list them.
- One syntax-check run at the end for all changed files.

Globals decision (brain, 2026-11-12):
- Global FUNCTIONS and static tables defined in server/client scripts move to a startup script
  (keep the same `global.<name>`), together with the file-local consts/helpers they use
  (`Java.loadClass` aliases are fine in startup). If a server file only defines globals, move the
  whole file to `kubejs/startup_scripts/` with a `zz_port_` prefix instead of extracting.
- Mutable RUNTIME state (caches, pending lists, leaderboards, "already logged" flags) uses the container
  created in `kubejs/startup_scripts/000_port_runtime.js` (priority 10000, loads first): `global.runtime.<name>` (read and write).
  Never `global.<name> = ...` outside startup.
- Readers in other files keep calling `global.<name>(...)` (functions) or switch to
  `global.runtime.<name>` (state). Grep all of `kubejs/` for readers of every name you change.
- Forge registries: `ForgeRegistries.X.getValue(rl)` -> `BuiltInRegistries.<X singular>.get(rl)`
  (`net.minecraft.core.registries.BuiltInRegistries`: ATTRIBUTE, ENTITY_TYPE, ITEM, BLOCK...; verify the field).
  `getForgePersistentData()` -> `getPersistentData()` (verify on the entity class in the NeoForge jar).
- Startup top-level code must not read `global.runtime`; use it only inside event callbacks.

Quality Food decision (brain, 2026-11-12, verified with javap):
- Item quality is the data component `quality_food:quality`, NOT custom data. Old reads like
  `stack.nbt.quality_food.quality` (or a ported `customData...quality_food...`) become
  `global.getQualityLevel(stack)` (0..3); writes become `global.setQualityLevel(stack, level)`
  (0 removes). Helpers live in `kubejs/startup_scripts/000_port_quality.js`; do not edit it.
- Creating a stack with quality: create it with `Item.of(...)`, then `global.setQualityLevel(stack, n)`.
- Block/animal quality (`LevelData`, `AnimalData` capabilities) moved to NeoForge data attachments in
  `de.cadentem.quality_food.core.attachments.*`: verify with javap before porting; if unclear, guard as
  a no-op with a `// 1.21.1:` comment and list it.

Bountiful decision (brain, 2026-11-12): `playerEvents/bountyCompatItems.js` (tag objectives on bounty papers)
is disabled: replace its body with a no-op and the comment `// 1.21.1: Bountiful 8 stores bounties in data
components; tag objectives to be redone in the bounty pool data`. List it.

Rules per category:
- nbt: item NBT -> components (`customData`, `setCustomData`, `get/set`, `Item.of('id[minecraft:custom_data={...}]')`);
  entity/player `persistentData` stays.
- rename callbacks: check every method the callback calls on `event` against the new event class.
- NativeEvents.onEvent: pass `Java.loadClass('<neoforge event class>')`; verify the class.
- forge_unresolved / recon_class: find the 1.21.1 class; if none, guard the feature as a no-op with
  `// 1.21.1: <class> removed, feature disabled` and list it.
- global (server-globals batch): `global.x = <static table>` moves to `zz_port_globals_server.js`
  with the same name; runtime state becomes a module-level `let` or `server.persistentData`. Keep readers working.
- tag_kept: switch `forge:X` to an existing `c:` tag of the same type if one exists in the jars
  (`data/c/tags/item/...`), else keep and list.
- dropped_manual: content of mods that left the pack (Botania, Botania Seeds, Splendid Slimes,
  Create: Splendid Cogs, cfm, redeco, croptania, farmlife, gensokyo and the DROPPED list in
  `tools/dataport/REPORT.md`): remove it, keeping the surrounding logic valid. List removals.
- `society:` ids never change. No "Sunlit" in user-visible strings (ids, data keys and identifiers stay).
- Code and comments in English, existing style, no refactors beyond the port.

Validation: Rhino syntax check of every changed file with `tools/kjsport/syntax/` (see how
`tools/kjsport/mechanical.py` invokes it), Docker detached, container `kjs-syntax-<batch>`: 0 failures.
Then `grep -nE '\.nbt\b|getNbt\(|setNbt\(|withNBT|getOrCreateTag' <your files>` returns nothing
(or only lines you justify).

Opencode: do not use it; work directly.
Budget: stop at ~60k tokens with an exact done/remaining file list.
Report (max ~15 lines) in chat and in `tools/kjsport/REPORT_<batch>.md`: files done, sites fixed per
category, features disabled, removals, syntax result, remaining.
