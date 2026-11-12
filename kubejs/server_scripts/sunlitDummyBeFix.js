// Sunlit: limpa a block entity orfa salva no chunk em 1053,11,659 (bloco de andesita).
// O chunk carrega com NBT de BE para um bloco que nao tem BE -> log "Tried to load a DUMMY block entity".
// Trocar o bloco para ar e de volta remove a entrada orfa pelo caminho vanilla;
// apos o save do chunk o aviso nao volta mais.
const DUMMY_BE_SPOTS = [{ x: 1053, y: 11, z: 659, expect: "minecraft:andesite" }];

ServerEvents.tick((e) => {
  if (global.runtime.sunlitDummyBeFixed) return;
  if (e.server.getTickCount() % 100 !== 0) return;
  let fixed = true;
  DUMMY_BE_SPOTS.forEach((t) => {
    e.server.getAllLevels().forEach((level) => {
      try {
        if (!level.hasChunk(t.x >> 4, t.z >> 4)) {
          fixed = false;
          return;
        }
        let b = level.getBlock(t.x, t.y, t.z);
        if (b.id !== t.expect) return;
        if (!b.entity) return; // ja limpo neste nivel
        b.set("minecraft:air");
        level.getBlock(t.x, t.y, t.z).set(t.expect);
        console.info(`[Sunlit] BE orfa removida em ${t.x},${t.y},${t.z} (${String(level.dimension)})`);
      } catch (err) {
        console.warn(`[Sunlit] falha ao limpar BE orfa: ${err}`);
        fixed = false;
      }
    });
  });
  if (fixed) global.runtime.sunlitDummyBeFixed = true;
});
