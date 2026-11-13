// Mana receiving for KubeJS machines (Botania Revived 2.0.2, NeoForge 1.21.1).
// Machines register a spec with global.registerManaReceiver. The listener below
// exposes each registered block entity as a ManaReceiver through
// BotaniaCapabilities.MANA_RECEIVER, so mana spreaders can fire into it.

global.manaReceiverSpecs = global.manaReceiverSpecs || {}

global.registerManaReceiver = (blockId, spec) => {
  global.manaReceiverSpecs[blockId] = spec
}

// Spec for machines that keep their mana in persistentData "mana" with a fixed cap.
// Bursts are accepted while the machine is below its cap (same as 1.20.1).
global.persistentManaSpec = (maxMana) => ({
  canBurst: (be) => be.persistentData.getInt("mana") < maxMana,
  getMana: (be) => be.persistentData.getInt("mana"),
  isFull: (be) => be.persistentData.getInt("mana") >= maxMana,
  receive: (be, amount) => {
    const current = be.persistentData.getInt("mana")
    const received = Math.min(maxMana - current, amount)
    be.persistentData.putInt("mana", current + received)
  },
})

NativeEvents.onEvent(Java.loadClass("net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent"), (e) => {
  const BuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries")
  const ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation")
  const BotaniaCapabilities = Java.loadClass("velrondevs.botania.api.BotaniaCapabilities")
  const ManaReceiver = Java.loadClass("velrondevs.botania.api.mana.ManaReceiver")

  Object.keys(global.manaReceiverSpecs).forEach((blockId) => {
    const spec = global.manaReceiverSpecs[blockId]
    const type = BuiltInRegistries.BLOCK_ENTITY_TYPE.get(ResourceLocation.parse(blockId))
    if (!type) {
      console.warn("[mana] block entity type not found for " + blockId)
      return
    }
    e.registerBlockEntity(BotaniaCapabilities.MANA_RECEIVER, type, (be, dir) => new JavaAdapter(ManaReceiver, {
      getManaReceiverLevel: () => be.getLevel(),
      getManaReceiverPos: () => be.getBlockPos(),
      getCurrentMana: () => spec.getMana(be),
      isFull: () => spec.isFull(be),
      receiveMana: (amount) => spec.receive(be, amount),
      canReceiveManaFromBursts: () => spec.canBurst(be),
    }))
  })
})
