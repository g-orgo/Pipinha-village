// Scratch-only client probe: renders each entity in TARGETS facing the viewer (inventory-style
// orthographic render, as the player sees it with EMF / Fresh Animations) into an offscreen target
// with a magenta background and saves render_<ns>_<path>.png in the game folder. One RENDER|{json}
// line per entity carries the pixel layout (feet position, scale, eye height, bounding box) that
// sunlit_tools/gen_mob_faces_render.py uses to crop the head.
// run_render_probe.sh replaces __TARGETS__ with the id list before copying this file.
var TARGETS = __TARGETS__
var Reg = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
var RL = Java.loadClass('net.minecraft.resources.ResourceLocation')
var MC = Java.loadClass('net.minecraft.client.Minecraft')
var TextureTarget = Java.loadClass('com.mojang.blaze3d.pipeline.TextureTarget')
var RenderSystem = Java.loadClass('com.mojang.blaze3d.systems.RenderSystem')
var VertexSorting = Java.loadClass('com.mojang.blaze3d.vertex.VertexSorting')
var Matrix4f = Java.loadClass('org.joml.Matrix4f')
var Quaternionf = Java.loadClass('org.joml.Quaternionf')
var GuiGraphics = Java.loadClass('net.minecraft.client.gui.GuiGraphics')
var InventoryScreen = Java.loadClass('net.minecraft.client.gui.screens.inventory.InventoryScreen')
var Screenshot = Java.loadClass('net.minecraft.client.Screenshot')
var Base64 = Java.loadClass('java.util.Base64')
var LivingEntity = Java.loadClass('net.minecraft.world.entity.LivingEntity')
var SIZE = 512, FEET = 480, PX = 160 // 160 px per block = 10 px per model pixel
var P = { t: 0, joined: -1, i: 0, done: false }

function renderOne(id) {
  var ns = id.split(':')[0], path = id.split(':')[1]
  var rec = { id: id }
  var type = Reg.ENTITY_TYPES.getValue(new RL(ns, path))
  if (!type) { rec.error = 'no entity type'; return rec }
  var e = type.create(Client.level)
  if (!e || !(e instanceof LivingEntity)) { rec.error = 'not living'; return rec }
  var pl = Client.player
  e.setPos(pl.getX(), pl.getY(), pl.getZ())
  e.yBodyRot = 180; e.yBodyRotO = 180; e.setYRot(180); e.setXRot(0); e.yHeadRot = 180; e.yHeadRotO = 180
  var bw = Number(e.getBbWidth()), bh = Number(e.getBbHeight()), eye = Number(e.getEyeHeight())
  var scale = PX
  // KubeJS has no JS Math object here
  if (bh * scale > FEET - 16) scale = ((FEET - 16) / bh) | 0
  if (bw * scale > SIZE - 32) { var sw = ((SIZE - 32) / bw) | 0; if (sw < scale) scale = sw }
  rec.bw = bw; rec.bh = bh; rec.eye = eye; rec.scale = scale; rec.feet = FEET; rec.cx = SIZE / 2; rec.size = SIZE
  var target = new TextureTarget(SIZE, SIZE, true, MC.ON_OSX)
  target.setClearColor(1, 0, 1, 1)
  target.clear(MC.ON_OSX)
  target.bindWrite(true)
  var proj = RenderSystem.getProjectionMatrix()
  RenderSystem.setProjectionMatrix(new Matrix4f().setOrtho(0, SIZE, SIZE, 0, 1000, 3000), VertexSorting.ORTHOGRAPHIC_Z)
  var mv = RenderSystem.getModelViewStack()
  mv.pushPose()
  mv.setIdentity()
  mv.translate(0, 0, -2000)
  RenderSystem.applyModelViewMatrix()
  try {
    var g = new GuiGraphics(Client, Client.renderBuffers().bufferSource())
    InventoryScreen.renderEntityInInventory(g, SIZE / 2, FEET, scale, new Quaternionf().rotateZ(3.141592653589793), null, e)
    g.flush()
    var img = Screenshot.takeScreenshot(target)
    // NativeImage.writeToFile is ambiguous in Rhino (File / Path); the PNG bytes go to the log as base64
    rec.png = String(Base64.getEncoder().encodeToString(img.asByteArray()))
    img.close()
  } catch (err) {
    rec.error = String(err)
  }
  mv.popPose()
  RenderSystem.applyModelViewMatrix()
  RenderSystem.setProjectionMatrix(proj, VertexSorting.ORTHOGRAPHIC_Z)
  target.destroyBuffers()
  Client.getMainRenderTarget().bindWrite(true)
  if (e.discard) e.discard()
  return rec
}

ClientEvents.tick(() => {
  P.t++
  if (P.done || !Client.level || !Client.player) return
  if (P.joined < 0) { P.joined = P.t; console.log('RENDER|joined'); return }
  if (P.t - P.joined < 40) return
  // a few per tick keeps each tick short
  for (var n = 0; n < 8 && P.i < TARGETS.length; n++, P.i++) {
    var rec
    try { rec = renderOne(TARGETS[P.i]) } catch (err) { rec = { id: TARGETS[P.i], error: String(err) } }
    console.log('RENDER|' + JSON.stringify(rec))
  }
  if (P.i >= TARGETS.length) {
    console.log('RENDER|ALLDONE')
    P.done = true
    Client.stop()
  }
})
