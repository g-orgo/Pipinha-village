console.info("[SOCIETY] globalDialog.js loaded");
// SVDialog 1.21.1 only registers "dialog show <id>" and shows the dialog to the command source's entity.
// The 1.20.1 form "dialog <target> show <player> <id>" no longer parses, and runCommandSilent hides the
// failure: NPC chatter, gifts and choice dialogs (Artisan book fair, Carpenter) never appeared.
// Every server-side dialog goes through this helper.
global.showDialog = (server, player, dialogId) => {
  try {
    return server.runCommandSilent(`execute as ${player.username} run dialog show ${dialogId}`);
  } catch (err) {
    console.error(`[SOCIETY] showDialog failed for ${dialogId}: ${err}`);
  }
};
