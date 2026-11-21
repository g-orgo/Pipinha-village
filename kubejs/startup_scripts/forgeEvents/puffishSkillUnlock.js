// Puffish SkillUnlock listener. Puffish calls it on the Java side with no safety net, so an
// error in here would crash the server: the whole body is guarded and only logs. The handler is
// global.runtime.onPuffishSkillUnlock, defined by server_scripts/playerEvents/skillPerkSync.js
// (swapped on /reload). Registered once: startup scripts do not run again on /reload.
console.info("[SOCIETY] puffishSkillUnlock.js loaded");

if (!global.puffishSkillUnlockRegistered) {
  global.puffishSkillUnlockRegistered = true;
  try {
    Java.loadClass("net.puffish.skillsmod.api.SkillsAPI").registerSkillUnlockEvent((player, categoryId, skillId) => {
      try {
        if (global.runtime && global.runtime.onPuffishSkillUnlock) {
          global.runtime.onPuffishSkillUnlock(player, String(categoryId), String(skillId));
        }
      } catch (err) {
        console.error("[SOCIETY] puffishSkillUnlock: " + err);
      }
    });
    console.info("[SOCIETY] puffishSkillUnlock: SkillUnlock listener registered");
  } catch (err) {
    console.error("[SOCIETY] puffishSkillUnlock: registration failed: " + err);
  }
}
