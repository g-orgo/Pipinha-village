// Scratch-only client probe: lists living entity types for the mob face generator.
// Logs one ENT| line per registered type: id|category|living|renderer class|texture|model class|head part.
var Reg = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
var RL = Java.loadClass('net.minecraft.resources.ResourceLocation')
var Living = Java.loadClass('net.minecraft.world.entity.LivingEntity')
var HeadedModel = Java.loadClass('net.minecraft.client.model.HeadedModel')
var P = { t: 0, joined: -1, done: false }
function headName(model) {
  try {
    if (model instanceof HeadedModel) return 'HeadedModel'
    var f = model.getClass().getFields()
    for (var i = 0; i < f.length; i++) if (String(f[i].getName()).toLowerCase() == 'head') return 'field:head'
  } catch (e) {}
  return 'none'
}
function faceExists(ns, path) {
  try {
    return Client.getResourceManager().getResource(new RL('ftbchunks', 'textures/faces/' + ns + '/' + path + '.png')).isPresent() ? 'Y' : 'N'
  } catch (e) { return 'E' }
}
ClientEvents.tick(() => {
  P.t++
  if (!Client.level || !Client.player) return
  if (P.joined < 0) { P.joined = P.t; console.log('ENT|joined'); return }
  if (P.t - P.joined < 40 || P.done) return
  P.done = true
  var it = Reg.ENTITY_TYPES.getEntries().iterator()
  while (it.hasNext()) {
    var ent = it.next(); var type = ent.getValue(); var id = ent.getKey().location()
    var cat = String(type.getCategory().getName())
    var living = 'N', rend = '-', tex = '-', model = '-', head = '-'
    try {
      var inst = type.create(Client.level)
      living = (inst instanceof Living) ? 'Y' : 'N'
      if (living == 'Y') {
        var r = Client.getEntityRenderDispatcher().getRenderer(inst)
        if (r) {
          rend = String(r.getClass().getName())
          var loc = r.getTextureLocation(inst); tex = String(loc)
          var m = r.getModel ? r.getModel() : null
          if (m) { model = String(m.getClass().getName()); head = headName(m) }
        }
        if (inst.discard) inst.discard()
      }
    } catch (e) { rend = 'ERR ' + e }
    console.log('ENT|' + id + '|' + cat + '|' + living + '|' + rend + '|' + tex + '|' + model + '|' + head + '|face=' + faceExists(id.getNamespace(), id.getPath()))
  }
  console.log('ENT|ALLDONE')
  Client.stop()
})
