console.info("[SOCIETY] sunlitRetrofitChunks.js loaded");

// Retrofit de chunks antigos das Sunlit Towns (geladeira atravessada, loot em
// bau demais): cada chunk do overworld carregado entra na fila uma vez e o tick
// do servidor (sunlitTownsLife.js:sunlitRetrofitTick) conserta com orcamento
// pequeno. O listener vivia em server_scripts via EVENT_BUS.addListener e
// quebrava o load com "argument type mismatch" (o Rhino nao converte a funcao
// JS em Consumer); aqui usa ForgeEvents.onEvent, padrao do pack (igual ao
// skullCavernChunkManager.js). So enfileira; o conserto continua no servidor.
const $SunlitRetrofitQueue = Java.loadClass("java.util.concurrent.ConcurrentLinkedQueue");
const $SunlitRetrofitSeen = Java.loadClass("java.util.concurrent.ConcurrentHashMap");

global.sunlitRetrofitEnqueue = (dimKey, cx, cz) => {
  try {
    if (!global.sunlitRetrofitQueue) {
      global.sunlitRetrofitQueue = new $SunlitRetrofitQueue();
      global.sunlitRetrofitSeen = new $SunlitRetrofitSeen();
    }
    let key = `${dimKey}|${cx}|${cz}`;
    if (global.sunlitRetrofitSeen.putIfAbsent(key, true) == null) {
      global.sunlitRetrofitQueue.add(key);
    }
  } catch (err) {}
};

NativeEvents.onEvent(Java.loadClass("net.neoforged.neoforge.event.level.ChunkEvent$Load"), (e) => {
  try {
    const { chunk, level } = e;
    if (!level || level.isClientSide()) return;
    if (String(level.dimension) !== "minecraft:overworld") return;
    global.sunlitRetrofitEnqueue("minecraft:overworld", chunk.pos.x, chunk.pos.z);
    // chunk que a fila de povoamento desistiu (ainda nao carregado): agora carregou, volta para a fila
    let townKey = `minecraft:overworld|${chunk.pos.x}|${chunk.pos.z}`;
    if (global.sunlitTownPending && global.sunlitTownPending.remove(townKey) != null && global.sunlitTownSeen.putIfAbsent(townKey, true) == null) {
      global.sunlitTownQueue.add(`${townKey}|0`);
    }
  } catch (err) {}
});
