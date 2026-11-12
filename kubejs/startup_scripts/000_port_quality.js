// priority: 9999
// Quality Food 2.x (1.21.1) stores item quality in the data component `quality_food:quality`
// (record Quality(type, level, effects)), not in the old `quality_food: {quality: N}` item NBT.
// Every script reads and writes item quality through these helpers.
(() => {
  const $QualityUtils = Java.loadClass('de.cadentem.quality_food.util.QualityUtils')
  const $Quality = Java.loadClass('de.cadentem.quality_food.core.codecs.Quality')
  const $QFComponents = Java.loadClass('de.cadentem.quality_food.registry.QFComponents')
  const $ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
  const $Optional = Java.loadClass('java.util.Optional')
  // Same levels as the old NBT value: 1 iron, 2 gold, 3 diamond.
  const QUALITY_TYPES = { 1: 'iron', 2: 'gold', 3: 'diamond' }

  // Returns 0 (no quality) to 3 (diamond).
  global.getQualityLevel = (stack) => {
    if (!stack || stack.isEmpty()) return 0
    if (!$QualityUtils.hasQuality(stack)) return 0
    const quality = $QualityUtils.getQuality(stack)
    return quality ? quality.level() : 0
  }

  // Sets the quality level (0 removes it). Returns true when the stack changed.
  global.setQualityLevel = (stack, level) => {
    if (!stack || stack.isEmpty()) return false
    const type = QUALITY_TYPES[level]
    if (!type) {
      if (!$QualityUtils.hasQuality(stack)) return false
      stack.remove($QFComponents.QUALITY_DATA_COMPONENT.get())
      return true
    }
    const quality = new $Quality($ResourceLocation.parse('quality_food:' + type), level, $Optional.empty())
    return $QualityUtils.applyQuality(stack, quality)
  }
})()
