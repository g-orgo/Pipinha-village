console.info("[SOCIETY] updateBountyBoard.js loaded");

// 1.21.1: item stacks inside block entity NBT keep their data under "components"
// (not "tag"), and Bountiful 8 stores the decree data in the "bountiful:decree_data"
// component. Seasonal decrees are switched to the current season on right click.
const DECREE_DATA_KEY = "bountiful:decree_data";

BlockEvents.rightClicked("bountiful:bountyboard", (e) => {
  const { level, block } = e;
  const seasonalBounties = ["summer", "spring", "autumn", "winter"];
  const blockNbt = block.getEntityData();
  const inv = blockNbt.decree_inv;
  if (!inv || !inv.Items) return;
  const decrees = inv.Items;
  let hasChanged = false;
  for (let index = 0; index < decrees.length; index++) {
    const components = decrees[index].components;
    if (!components || components[DECREE_DATA_KEY] === undefined || components[DECREE_DATA_KEY] === null) {
      continue;
    }
    const data = String(components[DECREE_DATA_KEY]);
    const isSeasonal = seasonalBounties.some((season) => data.includes(season));
    if (isSeasonal) {
      decrees[index].components[DECREE_DATA_KEY] = {
        ids: [global.getSeasonFromLevel(level)],
      };
      hasChanged = true;
    }
  }
  if (hasChanged) {
    global.setBlockEntityData(block, blockNbt);
  }
});
