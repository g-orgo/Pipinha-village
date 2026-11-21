console.info("[SOCIETY] skillBooks.js loaded");

// Skill books of the "books" tree. Learning a book unlocks its skill (0 points) and the mirror node
// of the same perk in its own tree; skillPerkSync.js does the mirror and reapplies the rewards.
// The learned check reads the Puffish state, so it does not depend on stages.
const SKILL_BOOK_API = Java.loadClass("net.puffish.skillsmod.api.SkillsAPI");
const SKILL_BOOK_TREE = "society:books";
const SKILL_BOOK_BOOKS = [
  { id: "society:alias_moss", skillId: "b2zbjhxyrcwlwb9e" },
  { id: "society:animal_fancy", skillId: "dk83vl5zi9fw3ovi" },
  { id: "society:banana_karenina", skillId: "76yv8nz8x47d80oe" },
  { id: "society:brine_and_punishment", skillId: "p5dklukq9ggwgfa4" },
  { id: "society:bluegill_meridian", skillId: "9ax835fydbyuvjkx" },
  { id: "society:bullfish_jobs", skillId: "pirgo25ykt4bsbdo" },
  { id: "society:canadian_and_famous", skillId: "x52wa6t39ywp17zu" },
  { id: "society:first_aid_guide", skillId: "12wl5sjx8vy7q0xl" },
  { id: "society:hitting_hard_and_soft", skillId: "t07mtr3euiz40jb0" },
  { id: "society:no_name_for_the_sheep", skillId: "uzxujhppzlyg5d03" },
  { id: "society:intro_to_algorithms", skillId: "gv808dy0r2fo6ire" },
  { id: "society:paradise_crop", skillId: "3grtavzaxp3xbp67" },
  { id: "society:slouching_towards_artistry", skillId: "pitrguemps2735n3" },
  { id: "society:debt_caverns", skillId: "bh5306iiysq2692k" },
  { id: "society:frogs_bounty_bazaar", skillId: "3fgcne477ni1rjxx" },
  { id: "society:phenomenology_of_treasure", skillId: "z68vn1cf2lucfbos" },
  { id: "society:slime_contain_protect", skillId: "uj8tnf4jgm0xyp13" },
  { id: "society:the_spark_also_rises", skillId: "n3wgu1edjjl2t511" },
  { id: "society:universal_methods_of_farming", skillId: "dm3efjm3y57v34ir" },
  { id: "society:wuthering_logs", skillId: "y1xltbgkupmcoe0i" },
  { id: "society:pond_house_five", skillId: "ajxn495vvckv1pow" },
  { id: "society:the_quality_of_the_earth", skillId: "y99a5jkv7tmu7vmc" },
  { id: "society:the_red_and_the_black", skillId: "ysthrzir822oedus" },
  { id: "society:women_who_run_with_the_plushies", skillId: "2vo8noqvq4aj1egy" },
  { id: "society:the_metamorphosize", skillId: "gjvl3ej2fhc4cwzb" },
];

// True when the book skill is already UNLOCKED for the player. Logs and returns false on error.
const skillBookIsLearned = (player, skillId) => {
  let learned = false;
  let category = null;
  let optional = null;
  let i = 0;
  let categories = null;
  try {
    categories = SKILL_BOOK_API.streamCategories().toList();
    for (i = 0; i < categories.size(); i++) {
      if (String(categories.get(i).getId()) === SKILL_BOOK_TREE) category = categories.get(i);
    }
    if (category) {
      optional = category.getSkill(skillId);
      if (optional.isPresent()) learned = String(optional.get().getState(player)) === "UNLOCKED";
    }
  } catch (err) {
    console.error("[SOCIETY] skillBooks: state check failed for " + skillId + ": " + err);
  }
  return learned;
};

SKILL_BOOK_BOOKS.forEach((book) => {
  ItemEvents.rightClicked(book.id, (e) => {
    const { player, item, server } = e;
    if (!skillBookIsLearned(player, book.skillId)) {
      server.runCommandSilent(
        `puffish_skills skills unlock ${player.username} ${SKILL_BOOK_TREE} ${book.skillId}`
      );
      player.tell(Text.translatable("society.skill_book.learn").green());
      server.runCommandSilent(
        `playsound minecraft:block.enchantment_table.use block @a ${player.x} ${player.y} ${player.z}`
      );
      item.count--;
      global.addItemCooldown(player, item, 20);
    } else {
      player.tell(Text.translatable("society.skill_book.already_learn").red());
      global.addItemCooldown(player, item, 20);
    }
  });
});
