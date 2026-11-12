// priority: 9998
// KubeJS 7 (1.21.1): item NBT is gone. Custom item data lives in the CUSTOM_DATA data component.
// These helpers give the batch scripts the old `stack.nbt` read/write behavior on top of components.
(() => {
  const $DataComponents = Java.loadClass('net.minecraft.core.component.DataComponents')
  const $CustomData = Java.loadClass('net.minecraft.world.item.component.CustomData')
  const $CompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag')

  // Returns a copy of the stack's custom data tag (empty tag when the stack has none).
  global.getItemCustomTag = (stack) => {
    if (!stack || stack.isEmpty()) return new $CompoundTag()
    const data = stack.get($DataComponents.CUSTOM_DATA)
    return data ? data.copyTag() : new $CompoundTag()
  }

  // Replaces the stack's custom data tag with the given CompoundTag.
  global.setItemCustomTag = (stack, tag) => {
    if (!stack || stack.isEmpty()) return
    $CustomData.set($DataComponents.CUSTOM_DATA, stack, tag)
  }
})()
