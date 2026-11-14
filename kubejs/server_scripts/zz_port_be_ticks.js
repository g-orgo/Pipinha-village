// KubeJS 7 passes BlockEntityTickKubeEvent, which has no `entity` field.
// Build the 1.20.1-style entity facade the handlers expect from the block entity.
const portBeFacade = (e) => {
  let be = e.block.blockEntity;
  let attachments = {};
  let it = be.attachments.entrySet().iterator();
  while (it.hasNext()) {
    let en = it.next();
    attachments[en.getKey()] = en.getValue();
  }
  return {
    level: e.level,
    block: e.block,
    x: e.block.x,
    y: e.block.y,
    z: e.block.z,
    inventory: attachments.inventory,
    tick: e.getTick(),
    cycle: e.getCycle(),
    persistentData: be.data,
    attachments: attachments,
    setChanged: () => be.setChanged()
  };
};

Object.keys(global.portBeTicks).forEach((id) => {
  BlockEvents.blockEntityTick(id, (e) => global.portBeTicks[id](portBeFacade(e)));
});
