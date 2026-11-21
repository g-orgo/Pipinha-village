// Clothing from any mod can also be worn in the matching Curios slot, the same way it is worn
// in the regular armor slot: head -> curios:head, chest -> curios:body, feet -> curios:feet.
// Real armor stays out: every vanilla piece (leather, chainmail, iron, gold, diamond, netherite,
// turtle, copper from VanillaBackport) and the armor sets of other mods.
// Curios does not read the item's armor attributes, so clothing in a Curios slot gives no
// armor points; the LSO temperature values do count there (LSO reads Curios slots).

// Logs the tagged and skipped items to logs/kubejs/server.log on every tag load.
const PIPINHA_CLOTHING_CURIOS_DEBUG = true;

const PIPINHA_CLOTHING_CURIOS_SLOTS = { head: "curios:head", chest: "curios:body", feet: "curios:feet" };

// Whole namespaces whose wearables are armor or functional gear, not clothing.
const PIPINHA_ARMOR_NAMESPACES = ["minecraft", "botania", "create", "aquaculture", "mapperbase", "geckojs"];

// Single armor pieces or functional gear inside clothing mods (regex over the item id).
const PIPINHA_ARMOR_ITEM_PATTERNS = [
  /^autumnity:snail_shell_chestplate$/,
  /^netherdepthsupgrade:soul_sucker_boots$/,
  /^etcetera:tidal_helmet$/,
  /^quark:backpack$/,
  /^windswept:wooden_.*bucket$/,
];

// Wearables whose natural Curios slot is not the one of their armor slot.
const PIPINHA_CLOTHING_CURIOS_OVERRIDES = { "crabbersdelight:pearl_necklace": "curios:necklace" };

ServerEvents.tags("item", (e) => {
  let registries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
  let equipableClass = Java.loadClass("net.minecraft.world.item.Equipable");
  let blockItemClass = Java.loadClass("net.minecraft.world.item.BlockItem");
  let added = {};
  let skipped = [];
  let failures = 0;
  let id = "";
  let item = null;
  let equipable = null;
  let slotName = "";
  let tag = null;
  let namespace = "";
  let isArmor = false;

  registries.ITEM.keySet().forEach((key) => {
    try {
      id = String(key);
      item = registries.ITEM.get(key);
      // Skulls, carved pumpkins and other wearable blocks are not clothing.
      if (item instanceof blockItemClass) return;
      equipable = equipableClass.get(item.getDefaultInstance());
      if (equipable == null) return;
      slotName = String(equipable.getEquipmentSlot().getName());
      tag = PIPINHA_CLOTHING_CURIOS_OVERRIDES[id] || PIPINHA_CLOTHING_CURIOS_SLOTS[slotName];
      if (!tag) return;
      namespace = id.split(":")[0];
      isArmor =
        PIPINHA_ARMOR_NAMESPACES.indexOf(namespace) >= 0 ||
        PIPINHA_ARMOR_ITEM_PATTERNS.some((pattern) => pattern.test(id));
      if (isArmor) {
        skipped.push(id);
        return;
      }
      e.add(tag, id);
      if (!added[tag]) added[tag] = [];
      added[tag].push(id);
    } catch (err) {
      failures++;
      if (failures <= 3) console.error(`[clothingCurios] failed on ${id}: ${err}`);
    }
  });

  if (PIPINHA_CLOTHING_CURIOS_DEBUG) {
    try {
      Object.keys(added).forEach((t) => {
        console.info(`[clothingCurios] ${t} +${added[t].length}: ${added[t].join(", ")}`);
      });
      console.info(`[clothingCurios] armor left out (${skipped.length}): ${skipped.join(", ")}`);
      if (failures > 0) console.info(`[clothingCurios] ${failures} items failed`);
    } catch (logErr) {
      console.error(`[clothingCurios] debug log failed: ${logErr}`);
    }
  }
});
