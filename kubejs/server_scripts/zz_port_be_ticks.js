// KubeJS 7 passes BlockEntityTickKubeEvent, which has no `entity` field.
// Build the 1.20.1-style entity facade the handlers expect from the block entity.
// LevelBlock exposes the block entity as getEntity() (`block.entity`); `blockEntity` does not exist.
const portBeFacade = (e) => {
  let be = e.block.entity;
  let attachments = {};
  let it;
  let en;
  if (!be) return null;
  if (be.attachments) {
    it = be.attachments.entrySet().iterator();
    while (it.hasNext()) {
      en = it.next();
      attachments[en.getKey()] = en.getValue();
    }
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
  BlockEvents.blockEntityTick(id, (e) => {
    let facade = portBeFacade(e);
    if (facade) global.portBeTicks[id](facade);
  });
});
