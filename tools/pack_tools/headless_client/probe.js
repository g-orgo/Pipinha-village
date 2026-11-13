// Scratch-only client probe. Drives a scripted eating session and logs what happens.
var CameraType = Java.loadClass('net.minecraft.client.CameraType')
var Screenshot = Java.loadClass('net.minecraft.client.Screenshot')
var RL = Java.loadClass('net.minecraft.resources.ResourceLocation')
var Reg = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
var P = { t: 0, joined: -1, step: 0, sub: 0, s: null, dumped: false, start: 0, shots: 0, count: 0 }
var FP = 'FIRST_PERSON', TB = 'THIRD_PERSON_BACK', TF = 'THIRD_PERSON_FRONT'
var SC = global.probeScenarios
function log(s) { console.log('PROBE|' + s) }
function cmd(c) { var srv = Client.getSingleplayerServer(); srv.getCommands().performPrefixedCommand(srv.createCommandSourceStack().withSuppressedOutput(), c) }
function arm() {
  try {
    var pm = Client.getEntityRenderDispatcher().getRenderer(Client.player).getModel()
    var PA = Java.loadClass('dev.kosmx.playerAnim.minecraftApi.PlayerAnimationAccess'); var PR = Java.loadClass('dev.kosmx.playerAnim.minecraftApi.PlayerAnimationRegistry'); var LL = PA.getPlayerAssociatedData(Client.player).get(new RL('sunlit_eating','eating')); var la = LL ? LL.getAnimation() : null; var lay = 'layer=' + (LL ? LL.getClass().getSimpleName() + '/size' + LL.size() + '/active' + LL.isActive() : 'null') + ' anim=' + (la ? la.getClass().getSimpleName() + '/size' + la.size() + '/active' + la.isActive() + '/inner=' + (la.getAnimation() ? la.getAnimation().isActive() + '@' + la.getAnimation().getCurrentTick() : 'null') : 'null'); return lay + ' rArm=' + pm.rightArm.xRot + ',' + pm.rightArm.yRot + ' lArm=' + pm.leftArm.xRot + ' head=' + pm.head.xRot + ' stackActive=' + PA.getPlayerAnimLayer(Client.player).isActive() + ' regKeys=' + PR.getModAnimations('sunlit_eating').keySet()
  } catch (e) { return 'armErr ' + e }
}
function shot(name) { Screenshot.grab(Client.gameDirectory, name + '.png', Client.getMainRenderTarget(), (msg) => {}) }
function dumpModels() {
  var rm = Client.getResourceManager()
  var it = Reg.ITEMS.getEntries().iterator()
  while (it.hasNext()) {
    var ent = it.next(); var item = ent.getValue(); var id = ent.getKey().location()
    var st = item.getDefaultInstance(); var ua = String(st.getUseAnimation())
    if (!(item.isEdible() || ua == 'DRINK' || ua == 'EAT')) continue
    var r = rm.getResource(new RL(id.getNamespace(), 'models/item/' + id.getPath() + '.json'))
    if (!r.isPresent()) { console.log('MODELDUMP|' + id + '|NONE|'); continue }
    var lines = r.get().openAsReader().lines().toArray()
    var s = ''; for (var i = 0; i < lines.length; i++) s += String(lines[i]).trim()
    console.log('MODELDUMP|' + id + '|' + r.get().sourcePackId() + '|' + s)
  }
  log('modeldump done')
}
ClientEvents.tick(() => {
  P.t++
  if (!Client.level || !Client.player) { if (P.t % 200 == 0) log('waiting, screen=' + Client.screen); return }
  if (Client.screen) { log('close screen ' + Client.screen.getClass().getName()); Client.setScreen(null) }
  if (P.joined < 0) { P.joined = P.t; log('joined') ; return }
  var age = P.t - P.joined
  if (age == 100) { if (global.PROBE_DUMP) dumpModels() }
  if (age == 110) { Client.options.hideGui = true; ['time set 6000', 'weather clear', 'gamerule doDaylightCycle false', 'gamemode survival @a', 'effect give @a minecraft:resistance 99999 9 true', 'execute as @a at @s run fill ~-3 ~-1 ~-3 ~3 ~-1 ~3 minecraft:grass_block', 'execute as @a at @s run fill ~-7 ~ ~-7 ~7 ~5 ~7 minecraft:air'].forEach(cmd) }
  if (age < 200) return
  var sc = SC[P.step]
  if (!sc) { if (!P.done) { P.done = true; log('ALLDONE'); Client.stop() } return }
  P.sub++
  if (P.sub < 1) return
  var srv = Client.getSingleplayerServer()
  if (P.sub == 1) {
    Client.options.keyUse.setDown(false)
    Client.options.setCameraType(CameraType.valueOf(sc.cam)); Client.options.hideGui = sc.cam != 'FIRST_PERSON'
    cmd('item replace entity @a hotbar.0 with ' + sc.id + ' ' + (sc.n || 8))
    Client.player.getInventory().selected = 0
    srv.getPlayerList().getPlayers().get(0).getFoodData().setFoodLevel(2)
    Client.player.setXRot(sc.pitch === undefined ? -35 : sc.pitch)
    return
  }
  if (P.sub == 9 && sc.base) { var bm0 = Client.getItemRenderer().getModel(Client.player.getMainHandItem(), Client.level, Client.player, 0); log(sc.id + ' base sprite ' + bm0.getParticleIcon().contents().name()) }
  if (P.sub == 9 && sc.idle) shot('p' + P.step + '_idle')
  // Optional zoom so third person shots show the hand up close.
  if (P.sub == 10 + (sc.delay || 0)) Client.options.fov().set(Java.loadClass('java.lang.Integer').valueOf(String((sc.fov || 70) | 0)))
  if (P.sub == 10 + (sc.delay || 0)) { P.count = Client.player.getMainHandItem().getCount(); log('START ' + sc.id + ' cam=' + sc.cam + ' count=' + P.count + ' held=' + Client.player.getMainHandItem().getId()); Client.options.keyUse.setDown(true); P.start = P.t; return }
  if (P.sub < 10 + (sc.delay || 0)) return
  var el = P.t - P.start
  var using = Client.player.isUsingItem()
  ;if (sc.model && el == sc.model) { var bm = Client.getItemRenderer().getModel(Client.player.getMainHandItem(), Client.level, Client.player, 0); log(sc.id + ' model sprite at t=' + el + ': ' + bm.getParticleIcon().contents().name()) }
  ;(sc.shots || [14, 26]).forEach((at) => { if (el == at) { var AU = Java.loadClass('org.toame.food.utils.AnimationUtils'), EM = Java.loadClass('org.toame.food.additions.Empty'); log(sc.id + ' t=' + el + ' lock[temp=' + AU.temp + ' slot=' + AU.lockedHotbarSlot + ' was=' + AU.wasEatAnimationPlaying + ' playing=' + EM.isEatAnimationPlaying() + ' keyDown=' + Client.options.keyUse.isDown() + ' screen=' + Client.screen + '] using=' + using + ' dur=' + Client.player.getUseItemRemainingTicks() + ' ' + arm()); shot('p' + P.step + '_' + sc.id.replace(':', '_') + '_' + sc.cam + '_' + el) } })
  // Hotbar switch mid animation: "switch": "key" presses the slot 2 key, "scroll" posts a wheel event.
  ;if (sc.switchAt && el == sc.switchAt) {
    var AU2 = Java.loadClass('org.toame.food.utils.AnimationUtils'); var before = AU2.isAnimationLocked()
    Client.options.keyUse.setDown(false); var canceled = false
    if (sc['switch'] == 'scroll') {
      var MSE = Java.loadClass('net.minecraftforge.client.event.InputEvent$MouseScrollingEvent'); var ev = new MSE(-1.0, false, false, false, 0.0, 0.0)
      canceled = Java.loadClass('net.minecraftforge.common.MinecraftForge').EVENT_BUS.post(ev); if (!canceled) Client.player.getInventory().swapPaint(-1.0)
    } else { var w = Client.getWindow().getWindow(); Client.keyboardHandler.keyPress(w, 50, 0, 1, 0); Client.keyboardHandler.keyPress(w, 50, 0, 0, 0) }
    log('SWITCH ' + sc['switch'] + ' lockedBefore=' + before + ' canceled=' + canceled)
  }
  if (sc.switchAt && el == sc.switchAt + 5) {
    var AU3 = Java.loadClass('org.toame.food.utils.AnimationUtils'), EM3 = Java.loadClass('org.toame.food.additions.Empty')
    log('SWITCHED selected=' + Client.player.getInventory().selected + ' locked=' + AU3.isAnimationLocked() + ' playing=' + EM3.isEatAnimationPlaying() + ' held=' + Client.player.getMainHandItem().getId())
    shot('p' + P.step + '_switch_' + sc['switch']); Client.player.getInventory().selected = 0; P.step++; P.sub = -40; return
  }
  var cnt = Client.player.getMainHandItem().getCount(); if (String(Client.player.getMainHandItem().getId()) != sc.id) cnt = -1
  if (cnt < P.count ||  el >= (sc.timeout || 200)) {
    log('RESULT ' + sc.id + ' cam=' + sc.cam + ' consumed=' + (cnt < P.count) + ' after=' + el + ' ticks; rest ' + arm())
    Client.options.keyUse.setDown(false); P.step++; P.sub = -40
  }
})
