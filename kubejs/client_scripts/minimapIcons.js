// Minimap / large map icons for FTB Chunks.
// - FTB Chunks skips every MISC entity, so villagers and Easy NPC town NPCs never show up.
//   They are added here: villagers with the FTB Chunks villager face, NPCs with their own skin face.
// - Animals use their own face texture (ftbchunks:textures/faces/<ns>/<path>.png); the ones FTB Chunks
//   lacks are generated from the real head model by sunlit_tools/gen_mob_faces.py (never spawn eggs).
const $MapIconEvent = Java.loadClass("dev.ftb.mods.ftbchunks.api.client.event.MapIconEvent");
const $EntityMapIcon = Java.loadClass("dev.ftb.mods.ftbchunks.client.mapicon.EntityMapIcon");
// 1.21.1: dev.ftb.mods.ftbchunks.client.mapicon.EntityIcons removed, so the heads-off default icon is disabled.
const $FTBChunksClientConfig = Java.loadClass("dev.ftb.mods.ftbchunks.client.FTBChunksClientConfig");
const $FTBIcon = Java.loadClass("dev.ftb.mods.ftblibrary.icon.Icon");
const $ImageIcon = Java.loadClass("dev.ftb.mods.ftblibrary.icon.ImageIcon");
const $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
const $Consumer = Java.loadClass("java.util.function.Consumer");
const $EntityType = Java.loadClass("net.minecraft.world.entity.EntityType");
const $LivingEntity = Java.loadClass("net.minecraft.world.entity.LivingEntity");
const $Player = Java.loadClass("net.minecraft.world.entity.player.Player");
const $AbstractVillager = Java.loadClass("net.minecraft.world.entity.npc.AbstractVillager");

const SUNLIT_MAP_VILLAGER_ICON = $FTBIcon["getIcon(java.lang.String)"]("ftbchunks:textures/faces/minecraft/villager.png");
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
    let location = new $ResourceLocation(key);
    let face = new $ImageIcon(location).withUV(8 / 64, 8 / 64, 16 / 64, 16 / 64);
    let hat = new $ImageIcon(location).withUV(40 / 64, 8 / 64, 48 / 64, 16 / 64);
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
    // 1.21.1: EntityIcons removed; without heads there is no default icon to use, so skip.
    if (!heads) continue;
    let icon = isVillager ? SUNLIT_MAP_VILLAGER_ICON : sunlitMapNpcIcon(entity, typeId);
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
