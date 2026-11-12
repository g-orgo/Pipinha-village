// Sunlit Towns: o Lost Cities avisa cada chunk de cidade gerado; aqui so enfileiramos
// (o evento roda nas threads de geracao). O povoamento acontece no tick do servidor,
// em server_scripts/sunlitTownsLife.js, com o chunk ja carregado.
// Tudo dentro de try/catch: excecao aqui aborta a geracao do chunk inteiro.
const $SunlitQueue = Java.loadClass("java.util.concurrent.ConcurrentLinkedQueue");
const $SunlitSeen = Java.loadClass("java.util.concurrent.ConcurrentHashMap");
const $SunlitAssets = Java.loadClass("mcjty.lostcities.worldgen.lost.cityassets.AssetRegistries");
global.sunlitTownQueue = new $SunlitQueue();
// o PostGen pode chegar mais de uma vez para o mesmo chunk: so a primeira entra na fila
// (as edicoes do sunlitTownsLife.js, como baixar o parque, nao podem rodar duas vezes)
global.sunlitTownSeen = new $SunlitSeen();
// chunks que sairam da fila sem estar carregados (DH gera fora do servidor); voltam quando o ChunkEvent$Load disparar
global.sunlitTownPending = new $SunlitSeen();
// no KubeJS "dimension" de um Level e propriedade (ResourceLocation), nao metodo
global.sunlitDimKey = (level) => String(level.dimension);

NativeEvents.onEvent(Java.loadClass("mcjty.lostcities.api.LostCityEvent$PostGenCityChunkEvent"), (e) => {
  try {
    global.sunlitLostCities = e.getLostCities();
    let key = `${global.sunlitDimKey(e.getWorld().getLevel())}|${e.getChunkX()}|${e.getChunkZ()}`;
    if (global.sunlitTownSeen.putIfAbsent(key, true) == null) {
      global.sunlitTownPending.remove(key);
      global.sunlitTownQueue.add(`${key}|0`);
    }
  } catch (err) {
    if (!global.sunlitTownWarned) console.warn(`[Sunlit Towns] fila falhou: ${err}`);
    global.sunlitTownWarned = true;
  }
});

// Casas de schematic (sunlit:vila_*) com a porta para a rua. O Lost Cities nao gira predios: cada casa
// existe nas 4 rotacoes (predio ou multibuilding r0/r90/r180/r270) e ele sorteia uma. Antes de gerar o
// chunk, olhamos os vizinhos do contorno da casa (rua = 3 pontos, praca/parque = 1, predio ou fora da
// cidade = 0) e trocamos o predio do chunk pelo da rotacao cuja frente (global.sunlitFronts, gerado pelo
// schematics.py) da para o lado com mais rua. A conta usa so o contorno da casa inteira, entao todos os
// chunks de um multibuilding escolhem a mesma rotacao. So troca entre rotacoes do mesmo tamanho (3x2 so
// gira 180).
const sunlitSideScore = (n) => {
  if (!n || !n.isCity() || n.hasBuilding) return 0;
  return String(n.streetType) == "PARK" ? 1 : 3;
};
const sunlitRotScore = (sides, fronts) => {
  if (!fronts || !fronts.length) return -1;
  let best = sides[fronts[0]];
  for (let i = 1; i < fronts.length; i++) best = Math.max(best, sides[fronts[i]] * 0.9);
  return best;
};
// RegistryAssetRegistry.get(level, String) and get(level, ResourceLocation) are ambiguous for Rhino even with a
// ResourceLocation argument; look assets up in a map built once from getIterable() instead.
const sunlitAssetMap = (registry, key) => {
  let map = global[key];
  if (!map) {
    map = {};
    let it = registry.getIterable().iterator();
    while (it.hasNext()) {
      let a = it.next();
      map[String(a.getId())] = a;
    }
    global[key] = map;
  }
  return map;
};

const sunlitFaceStreet = (e) => {
  let fronts = global.sunlitFronts;
  let npcFronts = global.sunlitNpcFronts;
  if (!fronts && !npcFronts) return;
  let world = e.getWorld();
  let info = e.getLostCities().getLostInfo(world.getLevel());
  if (!info) return;
  let cx = e.getChunkX(), cz = e.getChunkZ();
  let ci = info.getChunkInfo(cx, cz);
  if (!ci || !ci.hasBuilding) return;
  let m = /vila_([a-z0-9_]+)\/r(\d+)c\d\d$/.exec(String(ci.getBuildingType()));
  if (!m) return;
  // casas de schematic em global.sunlitFronts; predios de NPC do Portable Blueprints em global.sunlitNpcFronts
  let house = (fronts && fronts[m[1]]) || (npcFronts && npcFronts[m[1]]);
  if (!house) return;
  let rot = m[2];
  let mb = ci.getMultiBuildingInfo();
  // a house inside a themed lot (multi_cx_*) turns on its own, like a single-chunk house
  if (mb && !/multi_vila_/.test(String(mb.buildingType()))) mb = null;
  let ox = 0, oz = 0, w = 1, h = 1;
  if (mb) {
    ox = mb.offsetX();
    oz = mb.offsetZ();
    w = mb.w();
    h = mb.h();
  }
  let x0 = cx - ox, z0 = cz - oz;
  let sides = { north: 0, south: 0, west: 0, east: 0 };
  for (let i = 0; i < w; i++) {
    sides.north += sunlitSideScore(info.getChunkInfo(x0 + i, z0 - 1)) / w;
    sides.south += sunlitSideScore(info.getChunkInfo(x0 + i, z0 + h)) / w;
  }
  for (let j = 0; j < h; j++) {
    sides.west += sunlitSideScore(info.getChunkInfo(x0 - 1, z0 + j)) / h;
    sides.east += sunlitSideScore(info.getChunkInfo(x0 + w, z0 + j)) / h;
  }
  let best = rot, bestScore = house[rot] ? sunlitRotScore(sides, house[rot].fronts) : -1;
  ["0", "90", "180", "270"].forEach((r) => {
    let v = house[r];
    if (!v || v.dims[0] != w || v.dims[1] != h) return;
    let sc = sunlitRotScore(sides, v.fronts);
    if (sc > bestScore + 0.001) {
      best = r;
      bestScore = sc;
    }
  });
  if (best == rot) return;
  // single chunk: same building name with the other rotation (works for sunlit:vila_<house>/r<rot>c00 and for
  // the lot copies sunlit:cx/<lot>_<i>_vila_<house>/r<rot>c00)
  let name = String(ci.getBuildingType()).replace(/\/r\d+c(\d\d)$/, `/r${best}c$1`);
  if (name.indexOf(":") < 0) name = `sunlit:${name}`;
  if (mb) {
    let multi = sunlitAssetMap($SunlitAssets.MULTI_BUILDINGS, "sunlitMultiMap")[`sunlit:multi_vila_${m[1]}_r${best}`];
    if (!multi) return;
    name = String(multi.getBuilding(ox, oz));
  }
  let building = sunlitAssetMap($SunlitAssets.BUILDINGS, "sunlitBuildingMap")[name];
  if (!building) return;
  ci.setBuildingType(building, ci.getNumCellars(), ci.getNumFloors(), ci.groundLevel);
  if ((global.sunlitFaceLogged || 0) < 8) {
    global.sunlitFaceLogged = (global.sunlitFaceLogged || 0) + 1;
    console.info(`[Sunlit Towns] casa ${m[1]} em ${cx},${cz} virada para a rua: r${rot} -> r${best}`);
  }
};

NativeEvents.onEvent(Java.loadClass("mcjty.lostcities.api.LostCityEvent$PreGenCityChunkEvent"), (e) => {
  try {
    sunlitFaceStreet(e);
  } catch (err) {
    if (!global.sunlitFaceWarned) console.warn(`[Sunlit Towns] virar casa para a rua falhou: ${err}`);
    global.sunlitFaceWarned = true;
  }
});
