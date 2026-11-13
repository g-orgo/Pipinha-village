// 1.21.1: quest pages live in the create:clipboard_content data component.
// Entries are text-only, same as the 1.20.1 NBT pages: "<count> x <name>", unchecked.
const CreateDataComponents = Java.loadClass("com.simibubi.create.AllDataComponents");
const ClipboardContent = Java.loadClass("com.simibubi.create.content.equipment.clipboard.ClipboardContent");
const ClipboardEntry = Java.loadClass("com.simibubi.create.content.equipment.clipboard.ClipboardEntry");
const ClipboardType = Java.loadClass("com.simibubi.create.content.equipment.clipboard.ClipboardOverrides$ClipboardType");
const ArrayList = Java.loadClass("java.util.ArrayList");
const MinecraftComponent = Java.loadClass("net.minecraft.network.chat.Component");

global.buildClipboardPages = (pages) => {
  const javaPages = new ArrayList();
  for (const page of pages || []) {
    const javaEntries = new ArrayList();
    for (const entry of page.Entries) {
      const text = JSON.parse(`${entry.Text}`).text;
      javaEntries.add(new ClipboardEntry(false, MinecraftComponent.literal(text)));
    }
    javaPages.add(javaEntries);
  }
  return javaPages;
};

BlockEvents.rightClicked("society:fish_pond_manager", (e) => {
  const { item, hand, player, level, block } = e;
  if (hand !== "MAIN_HAND" || item !== "create:clipboard") return;
  global.addItemCooldown(player, item, 10);
  player.swing();
  const pages = global.getQuestItems(block, level);
  const content = new ClipboardContent(
    ClipboardType.WRITTEN,
    global.buildClipboardPages(pages),
    false
  );
  item.set(CreateDataComponents.CLIPBOARD_CONTENT, content);
  e.cancel();
});
