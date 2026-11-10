// Minimap / large map icons for FTB Chunks.
// - FTB Chunks skips every MISC entity, so villagers and Easy NPC town NPCs never show up.
//   They are added here: villagers with the FTB Chunks villager face, NPCs with their own skin face.
// - Animals without a face texture show as a plain dot. They get their spawn egg as icon,
//   written into EntityIcons.ENTITY_ICONS so FTB Chunks draws them with its own rules
//   (surface only, heads toggle). The map is rebuilt on resource reload, so it is refilled lazily.
const $MapIconEvent = Java.loadClass("dev.ftb.mods.ftbchunks.api.client.event.MapIconEvent");
const $EntityMapIcon = Java.loadClass("dev.ftb.mods.ftbchunks.client.mapicon.EntityMapIcon");
const $EntityIcons = Java.loadClass("dev.ftb.mods.ftbchunks.client.mapicon.EntityIcons");
const $FTBChunksClientConfig = Java.loadClass("dev.ftb.mods.ftbchunks.client.FTBChunksClientConfig");
const $FTBIcon = Java.loadClass("dev.ftb.mods.ftblibrary.icon.Icon");
const $ItemIcon = Java.loadClass("dev.ftb.mods.ftblibrary.icon.ItemIcon");
const $Consumer = Java.loadClass("java.util.function.Consumer");
const $EntityType = Java.loadClass("net.minecraft.world.entity.EntityType");
const $LivingEntity = Java.loadClass("net.minecraft.world.entity.LivingEntity");
const $Enemy = Java.loadClass("net.minecraft.world.entity.monster.Enemy");
const $Player = Java.loadClass("net.minecraft.world.entity.player.Player");
const $AbstractVillager = Java.loadClass("net.minecraft.world.entity.npc.AbstractVillager");
const $ForgeSpawnEggItem = Java.loadClass("net.minecraftforge.common.ForgeSpawnEggItem");
const $ForgeRegistries = Java.loadClass("net.minecraftforge.registries.ForgeRegistries");
const $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");

const SUNLIT_MAP_VILLAGER_ICON = $FTBIcon.getIcon("ftbchunks:textures/faces/minecraft/villager.png");
const SUNLIT_MAP_NPC_SKIN_FALLBACK = "minecraft:textures/entity/player/wide/steve.png";
// Easy NPC types drawn with a player skin (64x64 layout: face at 8,8 and hat at 40,8).
const SUNLIT_MAP_SKINNED_NPCS = ["easy_npc:humanoid", "easy_npc:humanoid_slim"];

// Per entity type id: spawn egg icon, or null when the type has no egg (keeps the dot).
const sunlitMapEggIcons = {};
// Per skin texture id: face + hat icon.
const sunlitMapSkinFaces = {};

const sunlitMapSkinFace = (texture) => {
  const key = String(texture);
  if (!sunlitMapSkinFaces[key]) {
    let face = $FTBIcon.getIcon(key).withUV(8 / 64, 8 / 64, 16 / 64, 16 / 64);
    let hat = $FTBIcon.getIcon(key).withUV(40 / 64, 8 / 64, 48 / 64, 16 / 64);
    sunlitMapSkinFaces[key] = face.combineWith(hat);
  }
  return sunlitMapSkinFaces[key];
};

const sunlitMapNpcIcon = (entity, typeId) => {
  if (SUNLIT_MAP_SKINNED_NPCS.indexOf(typeId) < 0) return SUNLIT_MAP_VILLAGER_ICON;
  let texture = SUNLIT_MAP_NPC_SKIN_FALLBACK;
  try {
    let renderer = Client.getEntityRenderDispatcher().getRenderer(entity);
    let location = renderer ? renderer.getTextureLocation(entity) : null;
    if (location) texture = location;
  } catch (err) {
    // Keep the default skin face.
  }
  return sunlitMapSkinFace(texture);
};

const sunlitMapEggIcon = (type, typeId) => {
  if (sunlitMapEggIcons.hasOwnProperty(typeId)) return sunlitMapEggIcons[typeId];
  let egg = $ForgeSpawnEggItem.fromEntityType(type);
  if (!egg) {
    let eggId = new $ResourceLocation(typeId + "_spawn_egg");
    if ($ForgeRegistries.ITEMS.containsKey(eggId)) egg = $ForgeRegistries.ITEMS.getValue(eggId);
  }
  const icon = egg ? $ItemIcon.getItemIcon(egg) : null;
  sunlitMapEggIcons[typeId] = icon;
  return icon;
};

const sunlitMapIsAnimal = (entity, category) =>
  entity instanceof $LivingEntity && !(entity instanceof $Enemy) && category !== "monster";

global.sunlitMapIconHandler = (event) => {
  if (!$FTBChunksClientConfig.MINIMAP_ENTITIES.get()) return;
  const level = Client.level;
  const player = Client.player;
  if (!level || !player) return;
  const heads = $FTBChunksClientConfig.MINIMAP_ENTITY_HEADS.get();
  const known = $EntityIcons.ENTITY_ICONS;

  const entities = level.entitiesForRendering().iterator();
  while (entities.hasNext()) {
    let entity = entities.next();
    if (entity instanceof $Player) continue;
    let type = entity.getType();
    let category = String(type.getCategory().getName());
    let typeId = String($EntityType.getKey(type));

    if (category === "misc") {
      let isVillager = entity instanceof $AbstractVillager;
      let isNpc = typeId.indexOf("easy_npc:") === 0 && entity instanceof $LivingEntity;
      if (!isVillager && !isNpc) continue;
      if (entity.isInvisibleTo(player)) continue;
      let icon = $EntityIcons.NORMAL;
      if (heads) icon = isVillager ? SUNLIT_MAP_VILLAGER_ICON : sunlitMapNpcIcon(entity, typeId);
      event.add(new $EntityMapIcon(entity, icon));
      continue;
    }

    if (known.containsKey(type) || !sunlitMapIsAnimal(entity, category)) continue;
    let egg = sunlitMapEggIcon(type, typeId);
    if (egg) known.put(type, egg);
  }
};

// Register once per game session; script reloads only swap global.sunlitMapIconHandler.
const sunlitMapHookIcons = () => {
  let failed = false;
  const listener = new $Consumer({
    accept: (event) => {
      try {
        if (global.sunlitMapIconHandler) global.sunlitMapIconHandler(event);
      } catch (err) {
        if (!failed) {
          failed = true;
          console.error("[minimapIcons] " + err);
        }
      }
    },
  });
  $MapIconEvent.MINIMAP.register(listener);
  $MapIconEvent.LARGE_MAP.register(listener);
};

if (!global.sunlitMapIconHooked) {
  global.sunlitMapIconHooked = true;
  sunlitMapHookIcons();
}
