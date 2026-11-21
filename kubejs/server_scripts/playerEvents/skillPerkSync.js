console.info("[SOCIETY] skillPerkSync.js loaded");

// Puffish 0.19 does not apply the puffish_skills:command rewards of unlocked skills in the
// 1.21.1 save (skills show as unlocked, stages and attributes missing). This script reapplies
// them on login and on each SkillUnlock, and mirrors the 25 skill-book perks as nodes of their
// own tree, unlocked together with the book at no cost. Stages are only added, never removed.
// Definitions are walked with the Gson API: a missing key on a Rhino-wrapped Java map throws.
const SKILL_PERK_API = Java.loadClass("net.puffish.skillsmod.api.SkillsAPI");
const SKILL_PERK_DIR = "kubejs/data/society/puffish_skills/categories";
const SKILL_PERK_BOOKS = "books";
const SKILL_PERK_MIRROR = "book_";
const SKILL_PERK_NAMESPACE = "society";
const SKILL_PERK_STAGE = /^kubejs stages add @s (\S+)$/;

// Reads a JSON file of a tree as a JsonObject, or null when it is missing or not an object.
const skillPerkReadObject = (path) => {
  let json = null;
  let object = null;
  json = JsonIO.readJson(path);
  if (json && json.isJsonObject()) object = json.getAsJsonObject();
  return object;
};

// Unlock commands of the puffish_skills:command rewards of one definition.
const skillPerkCommandsOf = (definitions, definitionId) => {
  let commands = [];
  let definition = null;
  let rewards = null;
  let reward = null;
  let data = null;
  let command = null;
  let i = 0;
  if (!definitions.has(definitionId)) return commands;
  definition = definitions.get(definitionId);
  if (!definition.isJsonObject() || !definition.getAsJsonObject().has("rewards")) return commands;
  rewards = definition.getAsJsonObject().getAsJsonArray("rewards");
  for (i = 0; i < rewards.size(); i++) {
    reward = rewards.get(i).getAsJsonObject();
    if (!reward.has("type") || String(reward.get("type").getAsString()) !== "puffish_skills:command") continue;
    if (!reward.has("data")) continue;
    data = reward.get("data").getAsJsonObject();
    if (!data.has("unlock_command")) continue;
    command = String(data.get("unlock_command").getAsString()).trim();
    if (command.length) commands.push(command);
  }
  return commands;
};

// Adds the skills of one tree to the index: unlock commands per skill, book ids per books skill,
// and the mirror node of each book (definition "book_<id>" in its own tree).
const skillPerkIndexTree = (index, path) => {
  let definitions = null;
  let skills = null;
  definitions = skillPerkReadObject(SKILL_PERK_DIR + "/" + path + "/definitions.json");
  skills = skillPerkReadObject(SKILL_PERK_DIR + "/" + path + "/skills.json");
  if (!definitions || !skills) return;
  skills.entrySet().forEach((entry) => {
    let skillId = null;
    let node = null;
    let definitionId = null;
    skillId = String(entry.getKey());
    node = entry.getValue().getAsJsonObject();
    if (!node.has("definition")) return;
    definitionId = String(node.get("definition").getAsString());
    index.commands[path + "/" + skillId] = skillPerkCommandsOf(definitions, definitionId);
    if (path === SKILL_PERK_BOOKS) index.bookDefinitions[skillId] = definitionId;
    if (definitionId.indexOf(SKILL_PERK_MIRROR) === 0) {
      index.mirrors[definitionId.substring(SKILL_PERK_MIRROR.length)] = { tree: path, skillId: skillId };
    }
  });
};

// Index of every society tree, rebuilt on each use so /reload and data edits are picked up.
const skillPerkBuildIndex = () => {
  let index = { commands: {}, mirrors: {}, bookDefinitions: {}, bookMirror: {} };
  let paths = [];
  SKILL_PERK_API.streamCategories().toList().forEach((category) => {
    let id = null;
    id = category.getId();
    if (String(id.getNamespace()) === SKILL_PERK_NAMESPACE) paths.push(String(id.getPath()));
  });
  paths.forEach((path) => skillPerkIndexTree(index, path));
  Object.keys(index.bookDefinitions).forEach((skillId) => {
    let bookId = null;
    bookId = index.bookDefinitions[skillId];
    if (index.mirrors[bookId]) index.bookMirror[skillId] = index.mirrors[bookId];
  });
  return index;
};

const skillPerkFindTree = (path) => {
  let found = null;
  SKILL_PERK_API.streamCategories().toList().forEach((category) => {
    let id = null;
    id = category.getId();
    if (String(id.getNamespace()) === SKILL_PERK_NAMESPACE && String(id.getPath()) === path) found = category;
  });
  return found;
};

const skillPerkIsUnlocked = (player, category, skillId) => {
  let optional = null;
  let unlocked = false;
  optional = category.getSkill(skillId);
  if (optional.isPresent()) unlocked = String(optional.get().getState(player)) === "UNLOCKED";
  return unlocked;
};

// Unlocks the mirror node of a book in its own tree, when it is not unlocked yet.
const skillPerkUnlockMirror = (server, player, mirror) => {
  let category = null;
  category = skillPerkFindTree(mirror.tree);
  if (!category || skillPerkIsUnlocked(player, category, mirror.skillId)) return;
  server.runCommandSilent(
    "puffish_skills skills unlock " + String(player.username) + " " + SKILL_PERK_NAMESPACE + ":" + mirror.tree + " " + mirror.skillId
  );
};

// Reapplies one unlocked skill: stages are added to the player, other commands run as the player.
const skillPerkApply = (server, player, index, path, skillId) => {
  let commands = null;
  let name = null;
  let command = null;
  let stageMatch = null;
  let i = 0;
  name = String(player.username);
  commands = index.commands[path + "/" + skillId] || [];
  for (i = 0; i < commands.length; i++) {
    command = commands[i];
    stageMatch = SKILL_PERK_STAGE.exec(command);
    if (stageMatch) {
      if (!player.stages.has(stageMatch[1])) player.stages.add(stageMatch[1]);
    } else {
      server.runCommandSilent("execute as " + name + " at " + name + " run " + command);
    }
  }
  if (path === SKILL_PERK_BOOKS && index.bookMirror[skillId]) {
    skillPerkUnlockMirror(server, player, index.bookMirror[skillId]);
  }
};

// Login pass: every unlocked skill of every unlocked society tree, then the stage-based attributes.
const skillPerkSyncPlayer = (server, player) => {
  let index = null;
  let unlockedSkills = 0;
  let name = String(player.username);
  try {
    index = skillPerkBuildIndex();
    SKILL_PERK_API.streamCategories().toList().forEach((category) => {
      let id = null;
      let path = null;
      id = category.getId();
      if (String(id.getNamespace()) !== SKILL_PERK_NAMESPACE || !category.isUnlocked(player)) return;
      path = String(id.getPath());
      category.streamSkills().toList().forEach((skill) => {
        let skillId = null;
        skillId = String(skill.getId());
        if (String(skill.getState(player)) !== "UNLOCKED") return;
        unlockedSkills++;
        try {
          skillPerkApply(server, player, index, path, skillId);
        } catch (err) {
          console.error("[skillPerkSync] " + path + "/" + skillId + " failed for " + name + ": " + err);
        }
      });
    });
    global.addAttributesFromStages(player, server);
    console.info("[skillPerkSync] " + name + ": " + unlockedSkills + " unlocked skills reapplied");
  } catch (err) {
    console.error("[skillPerkSync] login sync failed for " + name + ": " + err);
  }
};

// Handler called by startup_scripts/forgeEvents/puffishSkillUnlock.js. Only society trees.
global.runtime.onPuffishSkillUnlock = (player, categoryId, skillId) => {
  let prefix = SKILL_PERK_NAMESPACE + ":";
  let path = null;
  let server = null;
  if (categoryId.indexOf(prefix) !== 0) return;
  path = categoryId.substring(prefix.length);
  server = player.server;
  server.scheduleInTicks(1, () => {
    let index = null;
    try {
      index = skillPerkBuildIndex();
      skillPerkApply(server, player, index, path, skillId);
    } catch (err) {
      console.error("[skillPerkSync] unlock " + path + "/" + skillId + " failed: " + err);
    }
  });
};

// After skillRefund.js (40 ticks), so the trees are settled before the perks are reapplied.
PlayerEvents.loggedIn((e) => {
  let server = null;
  let player = null;
  server = e.server;
  player = e.player;
  server.scheduleInTicks(100, () => {
    skillPerkSyncPlayer(server, player);
  });
});
