console.info("[SOCIETY] boulderQuestStages.js loaded");

// Quests Additions (the "break a block" quest task) has no 1.21.1 port. The five
// boulder quests in the "iv__prismatic_farming" chapter now use gamestage tasks,
// and this grants the matching stage the first time the player breaks each boulder.
const boulderQuestStages = {
  "society:stone_boulder": "quest_broke_stone_boulder",
  "society:ice_boulder": "quest_broke_ice_boulder",
  "society:sandstone_boulder": "quest_broke_sandstone_boulder",
  "society:blackstone_boulder": "quest_broke_blackstone_boulder",
  "society:end_stone_boulder": "quest_broke_end_stone_boulder",
};

BlockEvents.broken(Object.keys(boulderQuestStages), (e) => {
  const { player, block } = e;
  if (!player) return;
  const stage = boulderQuestStages[String(block.id)];
  if (stage && !player.stages.has(stage)) player.stages.add(stage);
});
