// Scratch-only client probe for the mob face generator (sunlit_tools/gen_mob_faces.py).
// For each entity id in TARGETS it finds the head ModelPart, walks the model tree and logs one
// FACE|<json> line per entity: texture id, the pack that serves it, the root-to-head chain of part
// poses, and the head subtree with every cube's polygons (vertex pos, u, v and polygon normal).
// run_faces_probe.sh replaces the __TARGETS__ placeholder with the id list before copying this file.
var TARGETS = __TARGETS__
var Reg = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
var RL = Java.loadClass('net.minecraft.resources.ResourceLocation')
var P = { t: 0, joined: -1, done: false, schema: false }
var PART = 'net.minecraft.client.model.geom.ModelPart'
// Copies into public JDK classes: Rhino cannot call methods of non-public collection classes
// (Collections$Unmodifiable*, ImmutableCollections, Guava internals).
var HashMap = Java.loadClass('java.util.HashMap')
var ArrayList = Java.loadClass('java.util.ArrayList')
var VEC = 'org.joml.Vector3f'

function fieldsOf(cls) {
  var out = []
  var c = cls
  while (c) {
    var fs = c.getDeclaredFields()
    for (var i = 0; i < fs.length; i++) { fs[i].setAccessible(true); out.push(fs[i]) }
    c = c.getSuperclass()
  }
  return out
}
function fieldsTyped(obj, tname) {
  var fs = fieldsOf(obj.getClass()), out = []
  for (var i = 0; i < fs.length; i++) if (fs[i].getType().getName() == tname) out.push(fs[i])
  return out
}
function floatsOf(obj) {
  var o = {}, fs = fieldsOf(obj.getClass())
  for (var i = 0; i < fs.length; i++) if (fs[i].getType().getName() == 'float') o[String(fs[i].getName())] = Number(fs[i].get(obj))
  return o
}
// Vector3f: its float fields in declaration order (x, y, z).
function vecOf(v) {
  var out = [], fs = fieldsOf(v.getClass())
  for (var i = 0; i < fs.length; i++) if (fs[i].getType().getName() == 'float') out.push(Number(fs[i].get(v)))
  return out
}
function kidsOf(part) {
  var out = [], mf = fieldsTyped(part, 'java.util.Map')
  for (var i = 0; i < mf.length; i++) {
    var m = mf[i].get(part)
    if (!m) continue
    new HashMap(m).forEach(function (k, v) { out.push({ key: String(k), part: v }) })
  }
  return out
}
function cubesOf(part) {
  var out = [], lf = fieldsTyped(part, 'java.util.List')
  for (var i = 0; i < lf.length; i++) {
    var l = lf[i].get(part)
    if (!l) continue
    var al = new ArrayList(l)
    for (var j = 0; j < al.size(); j++) out.push(al.get(j))
  }
  return out
}
function polysOf(cube) {
  var out = [], fs = fieldsOf(cube.getClass()), arr = null
  for (var i = 0; i < fs.length; i++) if (fs[i].getType().isArray()) { arr = fs[i].get(cube); break }
  if (!arr) return out
  for (var j = 0; j < arr.length; j++) {
    var pf = fieldsOf(arr[j].getClass()), verts = null, normal = null
    for (var k = 0; k < pf.length; k++) {
      var t = pf[k].getType()
      if (t.isArray()) verts = pf[k].get(arr[j])
      else if (t.getName() == VEC) normal = pf[k].get(arr[j])
    }
    var vs = []
    for (var m = 0; m < verts.length; m++) {
      // Vertex fields are SRG-named; declaration order is pos, u, v
      var vx = verts[m], uv = [], pos = null, vfs = fieldsOf(vx.getClass())
      for (var n = 0; n < vfs.length; n++) {
        if (vfs[n].getType().getName() == VEC) pos = vfs[n].get(vx)
        else if (vfs[n].getType().getName() == 'float') uv.push(Number(vfs[n].get(vx)))
      }
      vs.push([vecOf(pos), uv[0], uv[1]])
    }
    out.push({ n: vecOf(normal), v: vs })
  }
  return out
}
function dumpNode(part, key) {
  var node = { k: key, p: floatsOf(part), c: [], ch: [], cls: String(part.getClass().getName()), lf: [] }
  var af = fieldsOf(part.getClass())
  for (var a = 0; a < af.length; a++) {
    var ft = af[a].getType()
    if (ft.isPrimitive()) continue
    var av = af[a].get(part)
    if (av == null) continue
    var sz = -1
    if (av.getClass().isArray()) sz = Number(av.length)
    else { try { sz = Number(av.size()) } catch (e) { sz = -1 } }
    node.lf.push(String(af[a].getName()) + ':' + String(ft.getName()) + ':' + sz)
  }
  var cubes = cubesOf(part)
  for (var i = 0; i < cubes.length; i++) node.c.push({ polys: polysOf(cubes[i]) })
  var kids = kidsOf(part)
  for (var j = 0; j < kids.length; j++) node.ch.push(dumpNode(kids[j].part, kids[j].key))
  return node
}
// Returns [{key, part}, ...] from the root down to the first part matching pred(part, key), or null.
function findChain(part, key, pred) {
  var here = { key: key, part: part }
  if (pred(part, key)) return [here]
  var kids = kidsOf(part)
  for (var i = 0; i < kids.length; i++) {
    var sub = findChain(kids[i].part, kids[i].key, pred)
    if (sub) return [here].concat(sub)
  }
  return null
}
// Field names are SRG-obfuscated at runtime, so the head is found by its children-map key 'head'
// (a plain string) searched under every ModelPart field of the model.
// EMF (Entity Model Features) renames the vanilla head child to 'EMF_head', so an exact 'head' key is
// tried first and any key containing 'head' is the fallback.
function locateHead(model) {
  var pf = fieldsTyped(model, PART)
  var exact = function (p, k) { return String(k).toLowerCase() == 'head' }
  var loose = function (p, k) { return String(k).toLowerCase().indexOf('head') >= 0 }
  for (var pass = 0; pass < 2; pass++) {
    for (var i = 0; i < pf.length; i++) {
      var chain = findChain(pf[i].get(model), 'root', pass == 0 ? exact : loose)
      if (chain) return { chain: chain, field: (pass == 0 ? 'child:head' : 'child:like-head') + ' via ' + pf[i].getName() }
    }
  }
  return null
}
function schemaOnce(model) {
  if (P.schema) return
  P.schema = true
  var names = function (obj) { var out = [], fs = fieldsOf(obj.getClass()); for (var i = 0; i < fs.length; i++) if (fs[i].getType().getName() == 'float') out.push(String(fs[i].getName())); return out }
  var pf = fieldsTyped(model, PART)
  var part = pf.length ? pf[0].get(model) : null
  var refs = []
  if (part) { var rf = fieldsOf(part.getClass()); for (var r = 0; r < rf.length; r++) if (rf[r].getType().getName() != 'float') refs.push(String(rf[r].getName()) + ':' + String(rf[r].getType().getName())) }
  var keys = []
  if (part) { var ks = kidsOf(part); for (var q = 0; q < ks.length; q++) keys.push(ks[q].key) }
  console.log('FACE|SCHEMA|' + JSON.stringify({ part: part ? names(part) : [], refs: refs, keys: keys, modelFields: fieldsTyped(model, PART).length, modelRefs: fieldsOf(model.getClass()).map(function (f) { return String(f.getName()) + ':' + String(f.getType().getName()) }) }))
}
var ROOTS = null
// ModelLayerLocation for an entity: exact model id with layer "main", else same namespace whose model path
// equals or contains the entity path.
function layerFor(ns, path) {
  if (!ROOTS) ROOTS = Java.loadClass('net.minecraft.client.model.geom.LayerDefinitions').createRoots()
  var best = null, rank = 9
  new HashMap(ROOTS).forEach(function (loc, def) {
    var m = loc.getModel()
    if (String(m.getNamespace()) != ns) return
    var mp = String(m.getPath()), main = String(loc.getLayer()) == 'main'
    var r = mp == path ? (main ? 0 : 1) : (mp.indexOf(path) >= 0 ? (main ? 2 : 3) : 9)
    if (r < rank) { rank = r; best = { loc: loc, def: def } }
  })
  return best
}
function probeOne(id) {
  var ns = id.indexOf(':') > 0 ? id.split(':')[0] : 'minecraft'
  var path = id.indexOf(':') > 0 ? id.split(':')[1] : id
  var rec = { id: ns + ':' + path }
  var type = Reg.ENTITY_TYPES.getValue(new RL(ns, path))
  if (!type) { rec.error = 'no entity type'; return rec }
  var inst = type.create(Client.level)
  var r = Client.getEntityRenderDispatcher().getRenderer(inst)
  if (!r) { rec.error = 'no renderer'; return rec }
  rec.renderer = String(r.getClass().getName())
  var loc = r.getTextureLocation(inst)
  rec.tex = String(loc)
  try { rec.pack = String(Client.getResourceManager().getResource(loc).get().sourcePackId()) } catch (e) { rec.pack = 'ERR ' + e }
  // The rendered model is wrapped by Entity Model Features + Fresh Animations (empty EMF_head placeholder),
  // so the head comes from the unmodified layer definitions (vanilla + Forge-registered mod layers).
  var lay = layerFor(ns, path)
  if (!lay) {
    var m = r.getModel ? r.getModel() : null
    rec.model = m ? String(m.getClass().getName()) : 'none'
    rec.unsupported = (rec.renderer.indexOf('geckolib') >= 0 || rec.model.indexOf('geckolib') >= 0) ? 'geckolib' : 'no layer definition'
    if (inst.discard) inst.discard(); return rec
  }
  rec.layer = String(lay.loc)
  var root = lay.def.bakeRoot()
  var found = null
  var exact = function (p, k) { return String(k).toLowerCase() == 'head' }
  var loose = function (p, k) { return String(k).toLowerCase().indexOf('head') >= 0 }
  var hc = findChain(root, "root", exact) || findChain(root, "root", loose)
  if (hc) found = { chain: hc, field: 'layer:' + rec.layer }
  if (!found) { rec.unsupported = 'no head ModelPart'; if (inst.discard) inst.discard(); return rec }
  rec.head_via = found.field
  var chain = found.chain, head = chain[chain.length - 1]
  rec.chain = []
  for (var i = 0; i < chain.length - 1; i++) rec.chain.push({ k: chain[i].key, p: floatsOf(chain[i].part) })
  rec.head = dumpNode(head.part, head.key)
  if (inst.discard) inst.discard()
  return rec
}
ClientEvents.tick(() => {
  P.t++
  if (!Client.level || !Client.player) return
  if (P.joined < 0) { P.joined = P.t; console.log('FACE|joined'); return }
  if (P.t - P.joined < 40 || P.done) return
  P.done = true
  for (var i = 0; i < TARGETS.length; i++) {
    var rec
    try { rec = probeOne(TARGETS[i]) } catch (e) { rec = { id: TARGETS[i], error: String(e) } }
    console.log('FACE|' + JSON.stringify(rec))
  }
  console.log('FACE|ALLDONE')
  Client.stop()
})
