// Minimap / large map icons for FTB Chunks.
// - FTB Chunks skips every MISC entity, so villagers and Easy NPC town NPCs never show up.
//   They are added here: villagers with the FTB Chunks villager face, NPCs with their own skin face.
// - Animals use their own face texture (ftblibrary:textures/faces/<ns>/<path>.png or .json, read by
//   FTB Library's EntityIconLoader on 1.21.1); the ones FTB lacks are generated from the real head model
//   by tools/pack_tools/gen_mob_faces.py (never spawn eggs) and live in kubejs/assets/ftblibrary.
const $MapIconEvent = Java.loadClass("dev.ftb.mods.ftbchunks.api.client.event.MapIconEvent");
const $EntityMapIcon = Java.loadClass("dev.ftb.mods.ftbchunks.client.mapicon.EntityMapIcon");
// 1.21.1: EntityIcons moved to FTB Library as EntityIconLoader (NORMAL icon + per-entity face icons).
const $EntityIconLoader = Java.loadClass("dev.ftb.mods.ftblibrary.icon.EntityIconLoader");
const $FTBChunksClientConfig = Java.loadClass("dev.ftb.mods.ftbchunks.client.FTBChunksClientConfig");
const $ImageIcon = Java.loadClass("dev.ftb.mods.ftblibrary.icon.ImageIcon");
const $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
const $Consumer = Java.loadClass("java.util.function.Consumer");
const $EntityType = Java.loadClass("net.minecraft.world.entity.EntityType");
const $LivingEntity = Java.loadClass("net.minecraft.world.entity.LivingEntity");
const $Player = Java.loadClass("net.minecraft.world.entity.player.Player");
const $AbstractVillager = Java.loadClass("net.minecraft.world.entity.npc.AbstractVillager");

// Villager faces come from FTB Library's per-entity icon (profession aware), with the plain dot as fallback.
const sunlitMapEntityFace = (entity) => {
  try {
    let icon = $EntityIconLoader.getIcon(entity);
    if (icon) return icon;
  } catch (err) {
    // Fall back to the plain icon below.
  }
  return $EntityIconLoader.NORMAL;
};
const SUNLIT_MAP_NPC_SKIN_FALLBACK = "minecraft:textures/entity/player/wide/steve.png";
// Easy NPC types drawn with a player skin (64x64 layout: face at 8,8 and hat at 40,8).
const SUNLIT_MAP_SKINNED_NPCS = ["easy_npc:humanoid", "easy_npc:humanoid_slim"];

// Per skin texture id: face + hat icon.
// ImageIcon is built from the ResourceLocation on purpose: Icon.getIcon(String) only makes an ImageIcon
// for ids ending in .png/.jpg, and Easy NPC custom skins are DynamicTextures named minecraft:dynamic/...,
// which getIcon turns into a block atlas sprite (missing texture on the map).
const sunlitMapSkinFaces = {};

const sunlitMapSkinFace = (texture) => {
  const key = String(texture);
  if (!sunlitMapSkinFaces[key]) {
    let location = $ResourceLocation.parse(key);
    let face = new $ImageIcon(location).withUV(8 / 64, 8 / 64, 16 / 64, 16 / 64);
    let hat = new $ImageIcon(location).withUV(40 / 64, 8 / 64, 48 / 64, 16 / 64);
    sunlitMapSkinFaces[key] = face["combineWith(dev.ftb.mods.ftblibrary.icon.Icon)"](hat);
  }
  return sunlitMapSkinFaces[key];
};

const sunlitMapNpcIcon = (entity, typeId) => {
  if (SUNLIT_MAP_SKINNED_NPCS.indexOf(typeId) < 0) return sunlitMapEntityFace(entity);
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

global.runtime.sunlitMapIconHandler = (event) => {
  if (!$FTBChunksClientConfig.MINIMAP_ENTITIES.get()) return;
  const level = Client.level;
  const player = Client.player;
  if (!level || !player) return;
  const heads = $FTBChunksClientConfig.MINIMAP_ENTITY_HEADS.get();

  const entities = level.entitiesForRendering().iterator();
  while (entities.hasNext()) {
    let entity = entities.next();
    if (entity instanceof $Player) continue;
    // KubeJS turns entity.getType() into the id string; the category comes from the registry type.
    let typeId = String(entity.getType());
    let type = $EntityType.byString(typeId).orElse(null);
    if (!type || String(type.getCategory().getName()) !== "misc") continue;
    let isVillager = entity instanceof $AbstractVillager;
    let isNpc = typeId.indexOf("easy_npc:") === 0 && entity instanceof $LivingEntity;
    if (!isVillager && !isNpc) continue;
    if (entity.isInvisibleTo(player)) continue;
    let icon = $EntityIconLoader.NORMAL;
    if (heads) icon = isVillager ? sunlitMapEntityFace(entity) : sunlitMapNpcIcon(entity, typeId);
    event.add(new $EntityMapIcon(entity, icon));
  }
};

// Register once per game session; script reloads only swap global.runtime.sunlitMapIconHandler.
const sunlitMapHookIcons = () => {
  let failed = false;
  const listener = new $Consumer({
    accept: (event) => {
      try {
        if (global.runtime.sunlitMapIconHandler) global.runtime.sunlitMapIconHandler(event);
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

if (!global.runtime.sunlitMapIconHooked) {
  global.runtime.sunlitMapIconHooked = true;
  sunlitMapHookIcons();
}
