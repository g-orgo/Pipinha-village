console.info("[SOCIETY] skillRefund.js loaded");

// Profession rework refund (2026-10-26): every point spent in every Puffish
// Skills tree is given back once per player, keeping experience and levels.
// Bump the version in the key to run a new refund after a future rework.
const $SkillsAPI = Java.loadClass("net.puffish.skillsmod.api.SkillsAPI");
const SKILL_REFUND_KEY = "sunlit_skill_refund_v1";
const SKILL_CATEGORIES_DIR = "kubejs/data/society/puffish_skills/categories";

// Lock commands of the command rewards of one tree (perk stages and shipping
// bin multipliers), read from its definitions.json so new nodes are covered.
// Walked with the Gson API: a missing key on a Rhino-wrapped Java map throws.
const skillLockCommands = (categoryPath) => {
  let commands = [];
  let definitions = JsonIO.readJson(`${SKILL_CATEGORIES_DIR}/${categoryPath}/definitions.json`);
  if (!definitions || !definitions.isJsonObject()) return commands;
  definitions.getAsJsonObject().entrySet().forEach((entry) => {
    let definition = entry.getValue();
    if (!definition.isJsonObject() || !definition.getAsJsonObject().has("rewards")) return;
    let rewards = definition.getAsJsonObject().getAsJsonArray("rewards");
    for (let i = 0; i < rewards.size(); i++) {
      let reward = rewards.get(i).getAsJsonObject();
      if (!reward.has("type") || String(reward.get("type").getAsString()) !== "puffish_skills:command") continue;
      if (!reward.has("data") || !reward.getAsJsonObject("data").has("lock_command")) continue;
      let lockCommand = String(reward.getAsJsonObject("data").get("lock_command").getAsString()).trim();
      if (lockCommand.length) commands.push(lockCommand);
    }
  });
  return commands;
};

const refundSkillPoints = (server, player) => {
  let refunded = 0;
  // Puffish loads exactly the categories listed in config.json, so a new tree
  // (e.g. mercantil) is refunded without touching this script.
  $SkillsAPI.streamCategories().toList().forEach((category) => {
    let categoryPath = String(category.getId().getPath());
    try {
      // Puffish only reads and resets unlocked trees; locked ones are opened just
      // for the reset and closed again, so the profession locks stay as they were.
      let wasUnlocked = category.isUnlocked(player);
      if (!wasUnlocked) category.unlock(player);
      refunded += category.getSpentPoints(player);
      category.resetSkills(player);
      if (!wasUnlocked) category.lock(player);
    } catch (err) {
      console.error(`[skillRefund] reset failed for ${categoryPath}: ${err}`);
    }
    try {
      skillLockCommands(categoryPath).forEach((command) => {
        server.runCommandSilent(`execute as ${player.username} run ${command}`);
      });
    } catch (err) {
      console.error(`[skillRefund] perk cleanup failed for ${categoryPath}: ${err}`);
    }
  });
  player.persistentData.putBoolean(SKILL_REFUND_KEY, true);
  console.info(`[skillRefund] ${player.username}: ${refunded} points refunded`);
  if (refunded > 0) {
    player.tell(
      global.translatableWithFallback(
        "society.skill_refund.done",
        "The profession system was reworked: every skill point you had spent was given back."
      ).gold()
    );
  }
};

PlayerEvents.loggedIn((e) => {
  let { server, player } = e;
  if (player.persistentData.getBoolean(SKILL_REFUND_KEY)) return;
  // Runs after the login handlers (profession sync) have settled the trees.
  server.scheduleInTicks(40, () => {
    if (player.persistentData.getBoolean(SKILL_REFUND_KEY)) return;
    refundSkillPoints(server, player);
  });
});
