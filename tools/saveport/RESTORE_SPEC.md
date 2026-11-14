# restore_items.py: spec

Repairs item data lost when "Solito solamente" (1.20.1) was converted to 1.21.1. Written by an
operator, dry-run by the operator, `--apply` only by the brain.

## Paths

- OLD (read only, never write): `/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley/saves/Solito solamente`
- NEW: `/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Pipinha's Village/saves/Solito solamente`
- Player: `playerdata/94835476-d653-44a5-8e00-d4fe3441e950.dat` (gzip) and `.cosarmor` (uncompressed NBT).

## Helpers to reuse (do not reimplement)

- `tools/saveport/convert_save.py`: `chunks_of(path)` -> `(raw, [(idx, root, err)])`, `read_dat`, `val`,
  and its old->new item id remap (namespace renames from `tools/modcheck/namespace_renames.tsv` + `id_map.tsv`).
- `tools/pack_tools/nbtmini.py` (compound = dict name -> (tagtype, value); list = (elemtype, [values])),
  `tools/pack_tools/nbtwrite.py` (`w_tag`), `tools/lcport/retrofit_hedges.py` or `tools/pack_tools` (`write_region(path, raw, changed)`).
- Tag ids: 1 byte, 3 int, 4 long, 8 string, 9 list, 10 compound, 11 int array.
- 1.21 chunk root has `block_entities` at root. Entities: `NEW/entities/*.mca`, root `Entities`.

## Cause

The vanilla DataFixer only upgrades vanilla containers. Modded BEs kept `{Slot, id, Count:byte, tag}`;
1.21 mods read them as count 1 with no components, some came back empty, BEs whose type id changed
(doapi:*) were dropped, Curios came back empty, and items the DataFixer did convert keep the quality in
`minecraft:custom_data` while Quality Food 2 reads `quality_food:quality`.
Measured: 281 stacks reset to count 1, 65 stacks lost tag data (non-vanilla BEs at the same position).

## 1.21 stack format

`{id:string, count:int, components:{...}}` (omit `components` when empty). Slot keys:
ContainerHelper/most mods `Slot` byte; NeoForge ItemStackHandler `{Size:int, Items:[{Slot:int,...}]}`
(also Curios Stacks); KubeJS 7 attachment `attachments:{inventory:[{slot:byte, id, count, components}]}`.

## convert_stack(old) -> new

Verify each modded component id and value type in its jar (`unzip -p` the class, read strings). If one
cannot be verified, put that key in `minecraft:custom_data` instead and report it.

- `Damage` (nonzero) -> `minecraft:damage` int
- `display.Name` -> `minecraft:custom_name` string; `display.Lore` -> `minecraft:lore` list of strings;
  `display.color` -> `minecraft:dyed_color` `{rgb:int}`
- `Enchantments` `[{id,lvl}]` -> `minecraft:enchantments` `{levels:{id:int}}`; `StoredEnchantments` -> `minecraft:stored_enchantments` same
- `Potion` -> `minecraft:potion_contents` `{potion:string}`; `RepairCost` -> `minecraft:repair_cost` int
- `quality_food:{quality:N}` -> `quality_food:quality` = `{type:"quality_food:iron"|"quality_food:gold"|"quality_food:diamond"` for 1|2|3, `level:int N}`
  (verified: QFComponents registers "quality" in namespace quality_food; Quality codec fields type, level, effects; omit effects)
- sophisticated backpacks: `contentsUuid` -> `sophisticatedcore:storage_uuid` (int array), `inventorySlots` ->
  `sophisticatedcore:number_of_inventory_slots` int, `upgradeSlots` -> `sophisticatedcore:number_of_upgrade_slots` int; drop `renderInfo`, `sortBy`
- numismatics: `AccountID` -> `numismatics:card_account_id`, `UUID` on id cards -> `numismatics:id_card_uuid`
  (int array; verify card_account_id codec type, else custom_data)
- `BlockEntityTag` with empty Items: drop
- every other key (SunlitWear, portable_blueprints fields, constructionstick:options, ...) -> `minecraft:custom_data` compound

## Steps

Only where NEW still has the block/BE at the same x,y,z. Never create chunks.

1. Counts/components: every non-vanilla BE present at the same position in OLD and NEW. Walk the NEW BE for
   item compounds; match the OLD stack by (slot value from Slot/slot, remapped id). If NEW count==1 and OLD
   Count>1 set count; if OLD had tag and NEW has no components set components. Never touch a stack whose id
   or slot no longer matches (the owner has played since).
2. Emptied BEs (NEW inventory empty, OLD had items):
   - `legendarysurvivaloverhaul:heater` (OLD id `...legendarysurvivaloverhaulheater_block_entity`): `Items`, Slot byte (check jar)
   - KubeJS `society:feeding_trough`, `shippingbin:basic_shipping_bin`: OLD `attachments:[{items:[...]}]` -> NEW `attachments.inventory`, slot byte
   - `bonsaitrees4:bonsaipot`: OLD `saplingItemStacks`/`soilItemStacks`/`outputItemStacks` -> NEW `inv.sapling`/`inv.soil`/`inv.output` (ItemStackHandler)
   - `bakery:storage` (OLD `doapi:storage`): `Items`, Slot byte
3. Missing BEs (block present in NEW, BE absent): OLD `doapi:cabinet` -> new `{id:"bakery:cabinet", x,y,z, keepPacked:0b, Items}`;
   OLD `doapi:storage` under a bakery display block -> find the block's BE type and keys in the bakery jar (OLD had `size` + `Items`);
   `supplementaries:jar`: check the jar format, else skip and report. Skip `bountiful:board-be`, lootr, `create:clipboard`
   (report the clipboard text from OLD at -10238 73 8345).
4. Curios: OLD `ForgeCaps."curios:inventory".Curios[*].StacksHandler.Stacks.Items` -> NEW `"neoforge:attachments"."curios:inventory".Curios[same Identifier].StacksHandler.Stacks.Items`
   (Slot int, stacks via convert_stack), only when NEW Items is empty. Expected: head (sunglasses, demonhorns), back (copper_backpack),
   card (orange_card), chat_color (yellow_dye x2), belt (toolbelt:belt), charm (lantern x18). Cosarmor: add components from OLD tags to matching slots.
5. Quality everywhere in NEW (region BEs, entities, playerdata Inventory/EnderItems/curios, cosarmor): an item whose
   `components."minecraft:custom_data"` has `quality_food:{quality:N}` -> `quality_food:quality` as above; remove the key from
   custom_data, drop custom_data if empty.

## CLI

- `python3 -I tools/saveport/restore_items.py --dry-run` (default): per-step counts; writes `tools/saveport/RESTORE_REPORT.md`
  (totals, per-position lists for steps 2-4, skipped items with reason).
- `--apply`: refuses if a java process with "Pipinha" in its command line runs; first zips NEW to
  `saves/Solito solamente backup-antes-restaurar-itens-2026-11-13.zip`; writes only changed chunks/files. Idempotent.
