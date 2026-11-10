// Sunlit Towns: ao carregar o mundo, confere com o parser do proprio Minecraft cada estado de bloco
// das paletas do Lost Cities (datapack sunlit_towns). Estado invalido faz o LC abortar o chunk inteiro,
// entao qualquer problema aparece aqui no log como "[Sunlit Towns] INVALIDO".
const $TownStateParser = Java.loadClass("net.minecraft.commands.arguments.blocks.BlockStateParser");
const $TownRegistries = Java.loadClass("net.minecraft.core.registries.Registries");
const $TownJsonParser = Java.loadClass("com.google.gson.JsonParser");
const $TownHashMap = Java.loadClass("java.util.HashMap");
const $TownArrayList = Java.loadClass("java.util.ArrayList");

ServerEvents.loaded((e) => {
  let server = e.server;
  let lookup = server.registryAccess().lookupOrThrow($TownRegistries.BLOCK);
  let seen = {};
  let files = 0, states = 0, bad = 0;
  try {
    // o Rhino trata Map como objeto JS: copia para HashMap e itera por lista de chaves
    let townPalMap = new $TownHashMap(
      server.getResourceManager().listResources("lostcities/palettes", (rl) => rl.getNamespace() == "deceasedcraft" || rl.getNamespace() == "sunlit")
    );
    let townPalKeys = new $TownArrayList(townPalMap.keySet());
    for (let i = 0; i < townPalKeys.size(); i++) {
      let rl = townPalKeys.get(i);
      files++;
      let reader = townPalMap.get(rl).openAsReader();
      let json = $TownJsonParser.parseReader(reader).getAsJsonObject();
      reader.close();
      let palette = json.getAsJsonArray("palette");
      for (let j = 0; j < palette.size(); j++) {
        let o = palette.get(j).getAsJsonObject();
        let list = [];
        if (o.has("block")) list.push(o.get("block").getAsString());
        if (o.has("blocks")) {
          let bl = o.getAsJsonArray("blocks");
          for (let k = 0; k < bl.size(); k++) list.push(bl.get(k).getAsJsonObject().get("block").getAsString());
        }
        list.forEach((s) => {
          if (seen[s]) return;
          seen[s] = true;
          states++;
          try {
            $TownStateParser.parseForBlock(lookup, s, false);
          } catch (err) {
            bad++;
            if (bad <= 30) console.error(`[Sunlit Towns] INVALIDO em ${rl}: ${s} (${err})`);
          }
        });
      }
    }
  } catch (err) {
    console.error(`[Sunlit Towns] checagem falhou: ${err}`);
  }
  console.info(`[Sunlit Towns] ${files} paletas, ${states} estados de bloco conferidos, ${bad} invalidos`);
});
