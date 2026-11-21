console.info("[SOCIETY] faceNote.js loaded");

// 1.20.1: society:face_note came from the society jar and opened the FriendshipScreen, a list
// of every villager with their hearts. In 1.21.1 the item only exists as a KubeJS registration
// (registerSocietyModItems.js), so this script prints the same list in chat.
// Friendship lives in player.persistentData.npcData[<npcId>].friendship: 0 to 500 points,
// -1 while the player has not talked to that NPC yet. One heart is 100 points.
const faceNoteNpcs = [
  "banker",
  "blacksmith",
  "carpenter",
  "fisher",
  "librarian",
  "market",
  "shepherd",
  "trader",
  "wise_oak",
  "witch",
];
const FACE_NOTE_MAX_HEARTS = 5;

const faceNoteHearts = (friendship) => {
  let hearts = Math.floor(friendship / 100);
  if (hearts < 0) hearts = 0;
  if (hearts > FACE_NOTE_MAX_HEARTS) hearts = FACE_NOTE_MAX_HEARTS;
  return Text.of(
    `§c${"❤".repeat(hearts)}§8${"❤".repeat(FACE_NOTE_MAX_HEARTS - hearts)}`
  );
};

ItemEvents.rightClicked("society:face_note", (e) => {
  const { player, server } = e;
  let npcData;
  if (player.isFake()) return;

  npcData = player.persistentData.npcData;
  player.tell(Text.translatable("menu.society.friendship_menu").gold());
  faceNoteNpcs.forEach((npcId) => {
    let entry;
    let friendship;
    let line;
    entry = npcData ? npcData[npcId] : null;
    friendship = entry ? global.nbtNum(entry.friendship) : -1;
    line = Text.translatable(`dialog.npc.${npcId}.name`)
      .white()
      .append(Text.of(" "));
    if (friendship < 0) {
      line = line.append(
        Text.translatable("tooltip.society.face_note.unknown").darkGray()
      );
    } else {
      line = line
        .append(faceNoteHearts(friendship))
        .append(Text.of(` §7${friendship}/500`));
    }
    player.tell(line);
  });
  server.runCommandSilent(
    `playsound minecraft:item.book.page_turn player ${player.username} ${player.x} ${player.y} ${player.z} 0.6 1`
  );
});
