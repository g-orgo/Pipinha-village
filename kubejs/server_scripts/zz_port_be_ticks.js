Object.keys(global.portBeTicks).forEach((id) => { BlockEvents.blockEntityTick(id, (e) => global.portBeTicks[id](e.entity)); });
