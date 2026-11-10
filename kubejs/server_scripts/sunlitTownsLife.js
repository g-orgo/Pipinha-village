// Sunlit Towns: cidades do Lost Cities nascem com moradores, golens, gatos e animais nos currais.
// A fila vem de startup_scripts/sunlitTownsLostCities.js (um item por chunk de cidade gerado).
const $TownEntityType = Java.loadClass("net.minecraft.world.entity.EntityType");
const $TownMobSpawnType = Java.loadClass("net.minecraft.world.entity.MobSpawnType");
const $TownBlockPos = Java.loadClass("net.minecraft.core.BlockPos");
const $TownProfession = Java.loadClass("net.minecraft.world.entity.npc.VillagerProfession");
const $TownBlocks = Java.loadClass("net.minecraft.world.level.block.Blocks");

// profissao por tipo de predio (nome do predio DC); nivel 2 para nao perderem o emprego
// 2026-10-18 (pedido do dono): so profissoes que abrem loja do Sunlit (society_trading,
// villager_profession em kubejs/data/society_trading/shops): cartographer=banker,
// toolsmith=blacksmith, fisherman=fisher, weaponsmith=librarian/witch, farmer=market,
// shepherd=shepherd, fletcher=trader
const TOWN_JOBS = [
  [/fastfood|cafe|restaurant|sushi|convenient|foodtruck/, ["FARMER", "FISHERMAN"]],
  [/office|bank|school|gallery|filmworks|courtyard/, ["CARTOGRAPHER", "WEAPONSMITH"]],
  [/hospital|polyclinic/, ["WEAPONSMITH"]],
  [/hardware|workshop|gasstation/, ["TOOLSMITH", "FLETCHER"]],
  [/clothstore/, ["SHEPHERD", "FLETCHER"]],
  [/flowershop|farmhouse/, ["FARMER"]],
  [/police/, ["TOOLSMITH"]],
  [/hotel|casino|thering|sunken/, ["CARTOGRAPHER", "FLETCHER"]],
  [/pescador|armazemporto/, ["FISHERMAN"]],
  [/alfaiate/, ["SHEPHERD"]],
  [/herbanario|herva|erva|casadecha|sobradocha/, ["WEAPONSMITH", "FARMER"]],
  [/queij|taverninha|chaletaverna|adegavinho/, ["FARMER", "SHEPHERD"]],
  [/deposito/, ["TOOLSMITH", "FLETCHER"]],
];
const TOWN_HOME_JOBS = ["FARMER", "FISHERMAN", "SHEPHERD", "FLETCHER", "TOOLSMITH", "CARTOGRAPHER"];

// blocos cuja aparencia depende dos vizinhos. O Lost Cities acerta fence/wall/pane/bars/stairs
// ao colocar o bloco (ChunkDriver.correct), mas so com o vizinho ja gerado: em borda de chunk
// (nossos parques tem 16x16 = 1 chunk exato) o vizinho ainda e ar e a conexao fica falsa para
// sempre. Hedges do Refurbished/cfm e portoes nem passam pelo correct. Com o chunk carregado,
// recalculamos o estado pelo updateShape de cada lado (Block.updateFromNeighbourShapes), no chunk
// e no anel de 1 bloco dos vizinhos ja carregados (o chunk antigo do lado tambem religa).
// updateNeighborsAt NAO serve: ele so chama neighborChanged (redstone), nao updateShape.
const $TownBlock = Java.loadClass("net.minecraft.world.level.block.Block");
// moveis que se emendam com o vizinho (banco, sofa, mesa, bancada, prateleira, comoda, escrivaninha):
// cada mod calcula a forma no proprio updateShape, entao vale o mesmo recalculo das cercas
const TOWN_CONNECTABLE = /fence|hedge|picket|lattice|_wall|pane|bars|gate|bench|sofa|couch|table|counter|cabinetry|shelf|drawer|desk/;
const $TownHeightmap = Java.loadClass("net.minecraft.world.level.levelgen.Heightmap$Types");
const $TownLeaves = Java.loadClass("net.minecraft.world.level.block.LeavesBlock");
const TOWN_LEAFY = /leaves|hedge/;
const TOWN_MAX_LEAVES = 4;

const townFixConnections = (level, cx, cz, yMin, yMax) => {
  let fixed = 0;
  for (let x = -1; x <= 16; x++) {
    for (let z = -1; z <= 16; z++) {
      let ring = x < 0 || z < 0 || x > 15 || z > 15;
      for (let y = yMin; y <= yMax; y++) {
        let pos = new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z);
        if (ring && !level.isLoaded(pos)) break;
        let st = level.getBlockState(pos);
        if (st.isAir()) continue;
        let key = String(st.getBlock().getDescriptionId());
        if (!TOWN_CONNECTABLE.test(key)) continue;
        // hedges: o updateShape de alguns mods nao religa sozinho; cerca-viva com
        // cerca-viva sempre conecta; com o resto mantem o que ja estava (parede/folha)
        if (/_hedge$/.test(key)) {
          try {
            let ns = st;
            [["north", $TownProps.NORTH, 0, -1], ["south", $TownProps.SOUTH, 0, 1], ["west", $TownProps.WEST, -1, 0], ["east", $TownProps.EAST, 1, 0]].forEach((d) => {
              let nid = String(level.getBlockState(pos.offset(d[2], 0, d[3])).getBlock().getDescriptionId());
              ns = ns.setValue(d[1], /_hedge$/.test(nid) ? true : ns.getValue(d[1]));
            });
            if (!ns.equals(st)) {
              level.setBlock(pos, ns, 18);
              fixed++;
            }
          } catch (err) {}
          continue;
        }
        try {
          let ns = $TownBlock.updateFromNeighbourShapes(st, level, pos);
          // 2 = manda pro cliente, 16 = nao propaga updateShape (evita cascata)
          if (!ns.equals(st) && !ns.isAir()) {
            level.setBlock(pos, ns, 18);
            fixed++;
          }
        } catch (err) {
          // bloco seguro de ignorar: segue para o proximo
        }
        if (fixed >= 800) return fixed; // teto de seguranca por chunk
      }
    }
  }
  return fixed;
};

// Banco do another_furniture em parte de rua: o Lost Cities gira a parte inteira para ruas N-S, mas
// o facing do banco nao acompanha e ele fica de lado para a calcada (costas para nada, lado na
// cerca viva). facing do another_furniture = frente do assento. Se a frente nao estiver livre com
// encosto atras, vira para o unico lado que tem encosto (hedge/folha/bloco cheio) atras e ar na frente.
// Assento ao lado de mesa e de proposito: fica como esta.
const $TownProps = Java.loadClass("net.minecraft.world.level.block.state.properties.BlockStateProperties");
const $TownDirection = Java.loadClass("net.minecraft.core.Direction");
const TOWN_FRONT_SEAT = /(another_furniture\.\w+_bench|furniture\.\w+_bench)$/;
const TOWN_SEAT_TABLE = /table|desk|counter/;
const TOWN_DIRS = [$TownDirection.NORTH, $TownDirection.SOUTH, $TownDirection.WEST, $TownDirection.EAST];

const townFixSeats = (level, cx, cz, yMin, yMax) => {
  let fixed = 0;
  let isOpen = (st) => st.isAir() || st.canBeReplaced();
  let isBack = (st, p) =>
    !st.isAir() && !TOWN_FRONT_SEAT.test(String(st.getBlock().getDescriptionId())) &&
    (TOWN_LEAFY.test(String(st.getBlock().getDescriptionId())) || st.isCollisionShapeFullBlock(level, p));
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      for (let y = yMin; y <= yMax; y++) {
        let pos = new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z);
        let st = level.getBlockState(pos);
        if (st.isAir() || !TOWN_FRONT_SEAT.test(String(st.getBlock().getDescriptionId()))) continue;
        if (!st.hasProperty($TownProps.HORIZONTAL_FACING)) continue;
        let near = {};
        let table = false;
        TOWN_DIRS.forEach((d) => {
          let p = pos.relative(d);
          let ns = level.getBlockState(p);
          near[String(d)] = [ns, p];
          if (TOWN_SEAT_TABLE.test(String(ns.getBlock().getDescriptionId()))) table = true;
        });
        if (table) continue;
        let good = (d) => {
          let f = near[String(d)], b = near[String(d.getOpposite())];
          return isOpen(f[0]) && isBack(b[0], b[1]);
        };
        let cur = st.getValue($TownProps.HORIZONTAL_FACING);
        if (good(cur)) continue;
        let cands = TOWN_DIRS.filter((d) => good(d));
        if (cands.length == 1) {
          level.setBlock(pos, st.setValue($TownProps.HORIZONTAL_FACING, cands[0]), 18);
          fixed++;
          continue;
        }
        // varias direcoes livres (banco no meio da praca): vira para outro banco/mesa por perto,
        // senao continua como foi gerado
        if (cands.length > 1) {
          let social = cands.filter((d) => {
            for (let i = 1; i <= 3; i++) {
              let q = pos.relative(d, i);
              let qs = level.getBlockState(q);
              let id = String(qs.getBlock().getDescriptionId());
              if (TOWN_FRONT_SEAT.test(id) || TOWN_SEAT_TABLE.test(id)) return true;
              if (!qs.isAir()) break;
            }
            return false;
          });
          if (social.length == 1) {
            level.setBlock(pos, st.setValue($TownProps.HORIZONTAL_FACING, social[0]), 18);
            fixed++;
          }
        }
      }
    }
  }
  return fixed;
};

// O Lost Cities poe colunas de folha na divisa predio/rua (randomLeafBlockChance) que sobem ate o
// telhado, e copas cortadas na borda do chunk viram cubos flutuantes. Pelo topo do heightmap: coluna de
// folha persistente/hedge com mais de 4 blocos e aparada para 4; corrida de folhas sem NENHUM apoio
// (sem tronco, terra, predio ou outra folha nao-persistente ate 6 blocos abaixo) e cubo flutuante
// cortado e sai inteira.
const townTrimLeaves = (level, cx, cz) => {
  let trimmed = 0;
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      let wx = (cx << 4) + x, wz = (cz << 4) + z;
      let y = level.getHeight($TownHeightmap.WORLD_SURFACE, wx, wz) - 1;
      let top = y;
      while (true) {
        let st = level.getBlockState(new $TownBlockPos(wx, y, wz));
        if (!TOWN_LEAFY.test(String(st.getBlock().getDescriptionId()))) break;
        if (st.hasProperty($TownLeaves.PERSISTENT) && !st.getValue($TownLeaves.PERSISTENT)) break;
        y--;
      }
      let bottom = y + 1;
      if (top < bottom) continue;
      // apoio: tronco/madeira, chao solido ou predio ate 6 blocos abaixo da base das folhas
      let supported = false;
      for (let yy = bottom - 1; yy >= bottom - 6; yy--) {
        let st = level.getBlockState(new $TownBlockPos(wx, yy, wz));
        let id = String(st.getBlock().getDescriptionId());
        if (TOWN_LEAFY.test(id)) continue; // outra folha embaixo nao e apoio
        if (!st.isAir()) {
          supported = true;
          break;
        }
      }
      if (!supported) {
        for (let yy = bottom; yy <= top; yy++) {
          level.setBlock(new $TownBlockPos(wx, yy, wz), $TownBlocks.AIR.defaultBlockState(), 18);
          trimmed++;
        }
        continue;
      }
      if (top - bottom + 1 <= TOWN_MAX_LEAVES) continue;
      for (let yy = bottom + TOWN_MAX_LEAVES; yy <= top; yy++) {
        level.setBlock(new $TownBlockPos(wx, yy, wz), $TownBlocks.AIR.defaultBlockState(), 18);
        trimmed++;
      }
    }
  }
  return trimmed;
};

// Parques (BuildingInfo.streetType == PARK): o Lost Cities poe o gramado na altura da rua e a parte do parque
// 1 bloco ACIMA dele (generateParkSection(height) e depois generatePart(height + 1)). As partes de parks/ seguem
// uma convencao fixa (polish.rule_park_ground, conferida pelo validate.py): a fatia 0 e a camada do chao e so
// tem chao (terra, caminho, terra arada, agua, piso cheio, tronco); objeto nunca fica na fatia 0.
// Aqui tudo desce 1 bloco, coluna por coluna, sem adivinhar pelo nome do bloco:
// - fatia 0 com chao: a coluna inteira desce e a fatia 0 toma o lugar da grama;
// - fatia 0 vazia: o que estiver acima desce 1 e assenta na grama;
// - qualquer outra coisa na fatia 0 nao veio da parte (vegetacao aleatoria do Lost Cities): fica.
// Block entity (barril com loot, colmeia...) desce com os dados. Roda uma vez por chunk (fila do startup).
const townParkGround = (level, pos, st) => {
  if (st.isAir() || st.hasBlockEntity()) return false;
  if (st.getFluidState().isSource()) return true;
  if (st.isCollisionShapeFullBlock(level, pos)) return true;
  return /(dirt_path|farmland)$/.test(String(st.getBlock().getDescriptionId()));
};
const TOWN_PARK_H = 20;
// cada passo com try proprio: um block entity que nao aceita save/load (NPE de mod) nao pode deixar a coluna
// pela metade; no pior caso o bloco desce sem os dados dele
const townMoveColumn = (level, from, to, n) => {
  let states = [], tags = [];
  for (let k = 0; k < n; k++) {
    let p = from.above(k);
    let st = level.getBlockState(p);
    states.push(st);
    let tag = null;
    if (st.hasBlockEntity()) {
      try {
        let be = level.getBlockEntity(p);
        if (be) tag = be.saveWithoutMetadata();
      } catch (err) {
        tag = null;
      }
    }
    tags.push(tag);
  }
  // limpa os block entities antes de sobrescrever (bau/barril nao derrama nada)
  for (let k = 0; k < n; k++) {
    try {
      if (states[k].hasBlockEntity()) level.removeBlockEntity(from.above(k));
    } catch (err) {}
  }
  for (let k = 0; k < n; k++) {
    let p = to.above(k);
    try {
      if (level.getBlockState(p).hasBlockEntity()) level.removeBlockEntity(p);
    } catch (err) {}
    try {
      level.setBlock(p, states[k], 18);
    } catch (err) {
      // some mod blocks throw inside their placement hooks (the scarecrow of the vegetable plots): write the
      // state straight into the chunk, without callbacks
      level.getChunkAt(p).setBlockState(p, states[k], false);
    }
    if (tags[k]) {
      try {
        let be = level.getBlockEntity(p);
        if (be) {
          be.load(tags[k]);
          be.setChanged();
        }
      } catch (err) {}
    }
  }
  let top = to.above(n);
  if (top.getY() >= from.getY() && top.getY() < from.getY() + n) level.setBlock(top, $TownBlocks.AIR.defaultBlockState(), 18);
};
// coluna do jardim de lote que pode descer: s0 e terreno de jardim (terra, caminho, arado, agua,
// cerca, folha, planta), nao ha estrutura em cima (mais de 4 blocos nao-ar acima de s0 = predio) e
// nenhum bloco de construcao (tabua, tronco, escada, laje, porta, vidro, tijolo, concreto, la, muro,
// armario, fogao, estante) de s0+3 ate TOWN_PARK_H (teto ou telhado), para o piso do predio nunca descer e
// deixar as paredes; banco, mesa e floreira baixos (s0+1, s0+2) ainda descem com o jardim
const TOWN_LOTE_GARDEN = /fence|hedge|leaves|flower|tulip|orchid|allium|azure|oxeye|poppy|dandelion|cornflower|lily|sunflower|lilac|peony|rose|vine|bush|sapling|crop|carrots|potatoes|beetroots|wheat|sweet_berry|stem|cabbages|onions|eggplants/;
const TOWN_LOTE_BUILD = /planks|_log$|_wood$|stairs|_slab$|door|glass|bricks|concrete|wool|_wall$|cabinet|stove|bookshelf/;
const townLoteGardenColumn = (level, s0, st0) => {
  let id = String(st0.getBlock().getDescriptionId());
  let name = id.replace(/^block\./, "").replace(/\./g, ":");
  let garden = /farmland$|dirt_path$|grass_block$|dirt$|podzol$|moss_block$|mycelium$/.test(id) || st0.getFluidState().isSource()
    || TOWN_LOTE_GARDEN.test(name) || (st0.canBeReplaced() && !st0.isAir());
  if (!garden) return false;
  for (let k = 3; k <= TOWN_PARK_H; k++) {
    let bid = String(level.getBlockState(s0.above(k)).getBlock().getDescriptionId()).replace(/^block\./, "").replace(/\./g, ":");
    if (TOWN_LOTE_BUILD.test(bid)) return false;
  }
  let above = 0;
  for (let k = 1; k <= 5; k++) {
    if (!level.getBlockState(s0.above(k)).isAir()) above++;
  }
  return above <= 4;
};

const townLowerPark = (level, cx, cz, ground, forcedLawn) => {
  // altura do gramado: ground-1..ground+1, a que tiver mais grama com a parte (ou ar) em cima
  // forcedLawn (numero): altura do gramado dada pelo chamador, sem detectar
  const forced = typeof forcedLawn === "number";
  let best = forced ? forcedLawn : ground, bestN = -1;
  for (let y = ground - 1; !forced && y <= ground + 1; y++) {
    let n = 0;
    for (let x = 1; x < 15; x++) {
      for (let z = 1; z < 15; z++) {
        if (level.getBlockState(new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z)).is($TownBlocks.GRASS_BLOCK)) n++;
      }
    }
    if (n > bestN) {
      best = y;
      bestN = n;
    }
  }
  if (!forced && bestN < 20) {
    // parque sem gramado exposto (praca de pedra, jardim sob copa fechada): o nivel da
    // cidade e a referencia, senao caminhos ficavam 1 bloco acima da grama para sempre
    best = ground;
  }
  let moved = 0, failed = 0, firstErr = null;
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      try {
        let base = new $TownBlockPos((cx << 4) + x, best, (cz << 4) + z);
        let s0 = base.above();
        let st0 = level.getBlockState(s0);
        if (forced) {
          // so desce coluna de terreno de jardim (terra, caminho, arado, cerca, folha, planta); casa e
          // material de construcao ficam onde estao, senao o predio vizinho era enterrado 1 bloco
          if (!st0.isAir() && townLoteGardenColumn(level, s0, st0)) {
            townMoveColumn(level, s0, base, TOWN_PARK_H);
            moved++;
          }
        } else if (townParkGround(level, s0, st0)) {
          townMoveColumn(level, s0, base, TOWN_PARK_H);
          moved++;
        } else if (st0.isAir()) {
          // coluna de ar: o primeiro bloco nao-ar acima desce ate s0. Na borda do parque (beiral de telhado,
          // s0 e s0+1 vazios e telhado em s0+4) o k sobe ate achar o telhado, senao a peca ficava flutuando
          let k = 1;
          while (k < TOWN_PARK_H && level.getBlockState(s0.above(k)).isAir()) k++;
          if (k < TOWN_PARK_H) {
            townMoveColumn(level, s0.above(k), s0.above(k - 1), TOWN_PARK_H - k + 1);
            moved++;
          }
        } else if (st0.canBeReplaced() && !level.getBlockState(s0.above()).isAir()) {
          // random vegetation of Lost Cities (flower, grass) right under a park piece: it goes away and the piece
          // settles on the lawn instead of standing on top of the flower
          level.setBlock(s0, $TownBlocks.AIR.defaultBlockState(), 18);
          townMoveColumn(level, s0.above(), s0, TOWN_PARK_H);
          moved++;
        }
      } catch (err) {
        failed++;
        if (!firstErr) firstErr = `${x},${z}: ${err}`;
      }
    }
  }
  if (failed) console.warn(`[Sunlit Towns] parque ${cx},${cz}: ${failed} colunas falharam ao descer (${firstErr})`);
  if ((global.sunlitSinkLogged || 0) < 5) {
    global.sunlitSinkLogged = (global.sunlitSinkLogged || 0) + 1;
    console.info(`[Sunlit Towns] parque ${cx},${cz}: ${moved} colunas desceram 1 bloco (gramado em y${best}, ground ${ground})`);
  }
  townRefillGarden(level, cx, cz, best);
  return moved;
};

// Hortas: terra arada com ar em cima e sem plantacao ganha a cultura vizinha (ou a primeira
// achada no chunk). Cobre perdas em jogo (colheita, coelho, afundamento, geracao parcial):
// o jardim volta a encher sozinho, sem regen. So planta o ano todo (o que o datapack ja usa).
const townRefillGarden = (level, cx, cz, lawn) => {
  let model = null;
  for (let y = lawn - 2; y <= lawn + 8 && !model; y++) {
    for (let x = 0; x < 16 && !model; x++) {
      for (let z = 0; z < 16 && !model; z++) {
        let st = level.getBlockState(new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z));
        let id = String(st.getBlock().getDescriptionId());
        if (/crop$|carrots|potatoes|beetroots|wheat|eggplants|_bush$|grape/.test(id) && id.indexOf("onion") < 0 && id.indexOf("wild_") < 0) model = st;
      }
    }
  }
  if (!model) {
    // chunk sem planta nenhuma: cultura de ano todo da lista do polish.py (carrots/potatoes), uma por horta
    let pick = townRandom(cx, cz)() < 0.5 ? $TownBlocks.CARROTS : $TownBlocks.POTATOES;
    model = pick.defaultBlockState();
  }
  let refilled = 0;
  for (let y = lawn - 2; y <= lawn + 8; y++) {
    for (let x = 0; x < 16; x++) {
      for (let z = 0; z < 16; z++) {
        let soil = new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z);
        if (!String(level.getBlockState(soil).getBlock().getDescriptionId()).endsWith("farmland")) continue;
        let top = soil.above();
        if (!level.getBlockState(top).isAir()) continue;
        try {
          level.setBlock(top, model, 3);
          refilled++;
        } catch (err) {}
      }
    }
  }
  return refilled;
};

// Camas, prateleiras, sacos, fogoes...: o Lost Cities grava o estado do bloco mas nao cria o block
// entity (so cria para os que recebem loot). Cama sem block entity fica INVISIVEL ate um bloco
// vizinho atualizar. Level.getBlockEntity na thread do servidor cria o que falta (IMMEDIATE) e
// sendBlockUpdated manda o bloco de novo para o cliente montar o dele. (LevelChunk.getBlockEntity(pos,
// tipo) e ambiguo no Rhino e Map do Java vira objeto de chaves: por isso so Level.getBlockEntity.)
const townFixBlockEntities = (level, cx, cz, yMin, yMax) => {
  let made = 0;
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      for (let y = yMin; y <= yMax; y++) {
        let pos = new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z);
        let st = level.getBlockState(pos);
        if (st.isAir() || !st.hasBlockEntity()) continue;
        try {
          if (level.getBlockEntity(pos)) {
            level.sendBlockUpdated(pos, st, st, 3);
            made++;
          }
        } catch (err) {
          // block entity que nao gosta de nascer assim: segue
        }
      }
    }
  }
  return made;
};

const townRandom = (cx, cz) => {
  // Park-Miller: cabe em double sem perder precisao (o Rhino nao garante Math.imul)
  let s = (Math.abs(cx * 73856 + cz * 19349 + 12345) % 2147483646) + 1;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
};

// indoor = so dentro de predio (algo solido ate 5 blocos acima): sem morador nascendo em telhado
const TOWN_BAD_FLOOR = /leaves|hedge|fence|_wall|glass|pane|bars|trapdoor/;
const townCovered = (level, x, y, z) => {
  for (let dy = 2; dy <= 5; dy++) {
    if (!level.getBlockState(new $TownBlockPos(x, y + dy, z)).isAir()) return true;
  }
  return false;
};

// tall = iron golem (~2.7 x 1.4): needs 3 blocks of air in the whole 3x3 column around the spot
const townTallClear = (level, x, y, z) => {
  for (let dx = -1; dx <= 1; dx++) {
    for (let dz = -1; dz <= 1; dz++) {
      for (let dy = 0; dy <= 2; dy++) {
        if (!level.getBlockState(new $TownBlockPos(x + dx, y + dy, z + dz)).isAir()) return false;
      }
    }
  }
  return true;
};

const townSpots = (level, cx, cz, yMin, yMax, rnd, want, indoor, tall) => {
  let spots = [];
  for (let i = 0; i < 40 && spots.length < want; i++) {
    let x = (cx << 4) + 1 + Math.floor(rnd() * 14);
    let z = (cz << 4) + 1 + Math.floor(rnd() * 14);
    let townFloors = [];
    for (let y = yMin; y <= yMax; y++) {
      let floor = level.getBlockState(new $TownBlockPos(x, y - 1, z));
      if (floor.isAir() || !floor.getFluidState().isEmpty()) continue;
      if (TOWN_BAD_FLOOR.test(String(floor.getBlock().getDescriptionId()))) continue;
      if (!level.getBlockState(new $TownBlockPos(x, y, z)).isAir()) continue;
      if (!level.getBlockState(new $TownBlockPos(x, y + 1, z)).isAir()) continue;
      if (tall && !townTallClear(level, x, y, z)) continue;
      if (indoor && !townCovered(level, x, y, z)) continue;
      townFloors.push(y);
    }
    if (townFloors.length) spots.push([x, townFloors[Math.floor(rnd() * townFloors.length)], z]);
  }
  return spots;
};

const townSpawn = (level, type, spot, rnd, job) => {
  let pos = new $TownBlockPos(spot[0], spot[1], spot[2]);
  let mob = type.create(level);
  if (!mob) return;
  // moveTo(double,double,double,float,float) nao resolve no Rhino (os 2 ultimos sao float
  // e o Rhino passa tudo como double -> m_20219_ nao encontrado). setPos so usa doubles.
  mob.setPos(spot[0] + 0.5, spot[1], spot[2] + 0.5);
  mob.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), $TownMobSpawnType.STRUCTURE, null, null);
  if (job) mob.setVillagerData(mob.getVillagerData().setProfession($TownProfession[job]).setLevel(2));
  mob.setPersistenceRequired();
  level.addFreshEntity(mob);
};

// Fauna da cidade (mods do pack; id que nao existir no jogo e ignorado). Mais bicho que morador.
const $TownEntities = Java.loadClass("net.minecraftforge.registries.ForgeRegistries").ENTITY_TYPES;
const $TownRL = Java.loadClass("net.minecraft.resources.ResourceLocation");
const TOWN_FAUNA_PARK = ["minecraft:chicken", "minecraft:cat", "untitledduckmod:duck", "untitledduckmod:goose",
  "crittersandcompanions:red_panda", "crittersandcompanions:ferret", "autumnity:snail", "autumnity:turkey", "wildernature:squirrel",
  "wildernature:hedgehog", "hamsters:hamster", "faunaandorchestra:butterfly", "longwings:butterfly", "crittersandcompanions:dragonfly",
  "minecraft:frog", "minecraft:parrot"];
const TOWN_FAUNA_FARM = ["minecraft:cow", "minecraft:sheep", "minecraft:pig", "minecraft:chicken", "minecraft:chicken", "meadow:wooly_cow",
  "meadow:wooly_sheep", "wildernature:minisheep", "untitledduckmod:goose", "untitledduckmod:duck", "autumnity:turkey", "minecraft:goat"];
// 2026-10-10: coelho fora da rua (come plantacao de cenoura madura e deixava slots vazios;
// AGENTS.md ja vetava, mas tinha voltado para a lista).
const TOWN_FAUNA_STREET = ["minecraft:cat", "minecraft:cat", "wildernature:dog", "wildernature:squirrel", "minecraft:chicken",
  "untitledduckmod:duck"];
// 2026-10-10 (pedido do dono): grupo de entidades (villagers OU animais) nao nasce a menos de
// 8 chunks de outro grupo. Registro em persistentData, mesmo padrao do waystone (TOWN_WAYSTONE_MIN).
// 2026-10-18: villagers tem lista propria ("sunlitVillagers", 6 chunks) para os animais nao
// ocuparem as vagas dos grupos de moradores.
const TOWN_FAUNA_MIN = 8;
const TOWN_VILLAGER_MIN = 6;
const townFaunaList = (level, key) => String(level.persistentData.getString(key || "sunlitFauna") || "").split(";").filter((e) => e.length);
const townFaunaNear = (level, cx, cz, key, min) => townFaunaList(level, key).some((e) => {
  let p = e.split(",");
  let dx = Math.abs(parseInt(p[0]) - cx), dz = Math.abs(parseInt(p[1]) - cz);
  return Math.max(dx, dz) < (min || TOWN_FAUNA_MIN);
});
const townFaunaAdd = (level, cx, cz, key) => {
  let list = townFaunaList(level, key);
  if (list.indexOf(`${cx},${cz}`) < 0) list.push(`${cx},${cz}`);
  level.persistentData.putString(key || "sunlitFauna", list.join(";"));
};
const townEntity = (id) => {
  let rl = new $TownRL(id);
  return $TownEntities.containsKey(rl) ? $TownEntities.getValue(rl) : null;
};
const townSpawnId = (level, ids, spot, rnd) => {
  for (let t = 0; t < 4; t++) {
    let type = townEntity(ids[Math.floor(rnd() * ids.length)]);
    if (type) {
      townSpawn(level, type, spot, rnd);
      return;
    }
  }
};

// Armor stands: clutter.py writes minecraft:structure_void where a stand goes (Lost Cities cannot place
// entities). Here the marker becomes a stand dressed by the house theme (house name suffix).
const $TownItems = Java.loadClass("net.minecraftforge.registries.ForgeRegistries").ITEMS;
const $TownSlot = Java.loadClass("net.minecraft.world.entity.EquipmentSlot");
const TOWN_ARMOR_SETS = [
  [/fer$|fer\//, [["minecraft:iron_helmet", "minecraft:iron_chestplate", "minecraft:iron_leggings", "minecraft:iron_boots", "minecraft:iron_sword"],
    ["minecraft:chainmail_helmet", "minecraft:chainmail_chestplate", "minecraft:chainmail_leggings", "minecraft:chainmail_boots", "minecraft:shield"],
    ["minecraft:leather_helmet", "minecraft:leather_chestplate", "minecraft:leather_leggings", "minecraft:leather_boots", "minecraft:bow"]]],
  [/cre$|cre\//, [["create:copper_diving_helmet", "create:copper_backtank", "minecraft:leather_leggings", "create:copper_diving_boots", "create:wrench"],
    ["create:goggles", "minecraft:leather_chestplate", "minecraft:leather_leggings", "minecraft:leather_boots", "create:wrench"]]],
  [/enc$|enc\/|alq$|alq\//, [["minecraft:golden_helmet", "minecraft:leather_chestplate", "minecraft:leather_leggings", "minecraft:golden_boots", "minecraft:book"],
    ["minecraft:leather_helmet", "minecraft:leather_chestplate", "minecraft:leather_leggings", "minecraft:leather_boots", "minecraft:glass_bottle"]]],
  [/./, [["minecraft:leather_helmet", "minecraft:leather_chestplate", "minecraft:leather_leggings", "minecraft:leather_boots", ""],
    ["minecraft:chainmail_helmet", "minecraft:leather_chestplate", "", "minecraft:leather_boots", ""],
    ["", "minecraft:iron_chestplate", "minecraft:iron_leggings", "", ""]]],
];
const TOWN_ARMOR_SLOTS = ["HEAD", "CHEST", "LEGS", "FEET", "MAINHAND"];
const townArmorStands = (level, cx, cz, yMin, yMax, name, rnd) => {
  let sets = TOWN_ARMOR_SETS.find((p) => p[0].test(name))[1];
  let made = 0;
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      for (let y = yMin; y <= yMax; y++) {
        let pos = new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z);
        if (!level.getBlockState(pos).is($TownBlocks.STRUCTURE_VOID)) continue;
        level.setBlock(pos, $TownBlocks.AIR.defaultBlockState(), 3);
        let stand = $TownEntityType.ARMOR_STAND.create(level);
        if (!stand) continue;
        stand.setPos(pos.getX() + 0.5, y, pos.getZ() + 0.5);
        stand.setYRot(Math.floor(rnd() * 4) * 90);
        let set = sets[Math.floor(rnd() * sets.length)];
        for (let i = 0; i < 5; i++) {
          if (!set[i]) continue;
          let rl = new $TownRL(set[i]);
          if (!$TownItems.containsKey(rl)) continue;
          stand.setItemSlot($TownSlot[TOWN_ARMOR_SLOTS[i]], Item.of(set[i]));
        }
        level.addFreshEntity(stand);
        made++;
      }
    }
  }
  return made;
};

// predio que e moradia (1 morador por casa; algumas ficam vazias)
const TOWN_HOME = /vila_|casa|house|cabin|cottage|apartment|condo|home|chale|sobrado|villager|farmhouse|fazenda|padaria|cozinhakaleido|adega/;

// chunk com terra arada no nivel do terreo: horta de lote (o terreo do datapack usa farmland)
const townHasFarmland = (level, cx, cz, y) => {
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      let st = level.getBlockState(new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z));
      if (/farmland$/.test(String(st.getBlock().getDescriptionId()))) return true;
    }
  }
  return false;
};

const townPopulate = (level, cx, cz) => {
  let lc = global.sunlitLostCities;
  if (!lc) return null;
  let info = lc.getLostInfo(level);
  if (!info) return null;
  let ci = info.getChunkInfo(cx, cz);
  if (!ci || !ci.isCity()) return null;
  let rnd = townRandom(cx, cz);
  let ground = info.getRealHeight(ci.getCityLevel());
  let building = ci.getBuildingType();
  let park = !building && ci.parkType && String(ci.streetType) == "PARK" && ci.getStreetSlopeDirection() == null;
  if (park) {
    try {
      townLowerPark(level, cx, cz, ground);
    } catch (sinkErr) {
      console.warn(`[Sunlit Towns] falha ao baixar o parque no chunk ${cx},${cz}: ${sinkErr}`);
    }
  }
  // predio que e so jardim de lote (sunlitTownsLotes.js): o terreo dele desce como parque
  let loteKey = building ? String(building) : "";
  let loteName = loteKey.replace(/_c[0-9]+(?=\/|$)/, "");
  let loteListed = !!(building && global.sunlitLoteBuildings && (global.sunlitLoteBuildings[loteKey] || global.sunlitLoteBuildings[loteName]));
  if (loteListed) {
    try {
      townLowerPark(level, cx, cz, ground, ground - 1);
      if ((global.sunlitLoteLogged || 0) < 8) {
        global.sunlitLoteLogged = (global.sunlitLoteLogged || 0) + 1;
        console.info(`[Sunlit Towns] jardim de lote rebaixado no chunk ${cx},${cz}: key=${loteKey} ground=${ground}`);
      }
    } catch (loteErr) {
      console.warn(`[Sunlit Towns] falha ao baixar o jardim de lote no chunk ${cx},${cz}: ${loteErr}`);
    }
  }
  try {
    townWaystones(level, cx, cz, ground);
  } catch (wsErr) {
    console.warn(`[Sunlit Towns] falha ao conferir waystone no chunk ${cx},${cz}: ${wsErr}`);
  }

  // feno no chao marca curral (sunlit:parks/curral) ou celeiro -> animais de fazenda
  let hay = 0;
  for (let x = 0; x < 16 && hay < 3; x++) {
    for (let z = 0; z < 16; z++) {
      for (let y = ground; y <= ground + 2; y++) {
        if (level.getBlockState(new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z)).is($TownBlocks.HAY_BLOCK)) hay++;
      }
    }
  }
  if (hay >= 3) {
    // 2026-10-10: curral entra na regra dos 8 chunks e nasce com 2 bichos (era 3-5)
    if (townFaunaNear(level, cx, cz)) return [ground, ground + 2];
    townFaunaAdd(level, cx, cz);
    townSpots(level, cx, cz, ground, ground + 2, rnd, 2).forEach((s) => townSpawnId(level, TOWN_FAUNA_FARM, s, rnd));
    return [ground, ground + 2];
  }

  if (building) {
    let name = String(building).replace(/_c[0-9]+(?=\/|$)/, "");
    let floors = Math.max(1, ci.getNumFloors());
    // nucleos raros: no multibuilding so o chunk do canto (0,0) povoa
    let mb = ci.getMultiBuildingInfo();
    let corner = !mb || (mb.offsetX() == 0 && mb.offsetZ() == 0);
    try {
      townArmorStands(level, cx, cz, ground - 7, ground + floors * 6, name, rnd);
    } catch (asErr) {
      console.warn(`[Sunlit Towns] falha ao criar armor stand no chunk ${cx},${cz}: ${asErr}`);
    }
    try {
      townRefillGarden(level, cx, cz, ground);
    } catch (rfErr) {}
    if (corner) {
      let jobs = TOWN_HOME_JOBS;
      TOWN_JOBS.forEach((pair) => {
        if (pair[0].test(name)) jobs = pair[1];
      });
      // nucleos de moradores: 2026-10-18 (pedido do dono): ~5% das casas / ~4% dos comercios
      // tem 2-3 villagers com profissao de loja Sunlit + 1 iron golem sempre; grupos a 6+ chunks
      // de outro grupo de villagers (lista propria). O resto nasce vazio.
      let groupChance = TOWN_HOME.test(name) ? 0.05 : 0.04;
      if (rnd() < groupChance && !townFaunaNear(level, cx, cz, "sunlitVillagers", TOWN_VILLAGER_MIN)) {
        let villagers = townSpots(level, cx, cz, ground, ground + floors * 6, rnd, 2 + Math.floor(rnd() * 2), true);
        if (villagers.length) {
          townFaunaAdd(level, cx, cz, "sunlitVillagers");
          villagers.forEach((s) => townSpawn(level, $TownEntityType.VILLAGER, s, rnd, jobs[Math.floor(rnd() * jobs.length)]));
          // golem only where it fits (3 high, 3x3 free); no spot -> no golem
          let golem = townSpots(level, cx, cz, ground, ground + 3, rnd, 1, false, true);
          if (!golem.length) golem = townSpots(level, cx, cz, ground, ground + floors * 6, rnd, 1, true, true);
          golem.forEach((s) => townSpawn(level, $TownEntityType.IRON_GOLEM, s, rnd));
        }
      }
      if (rnd() < 0.08 && !townFaunaNear(level, cx, cz)) {
        townFaunaAdd(level, cx, cz);
        townSpots(level, cx, cz, ground, ground + floors * 6, rnd, 1, true).forEach((s) =>
          townSpawnId(level, ["minecraft:cat", "minecraft:cat", "wildernature:dog", "minecraft:parrot", "hamsters:hamster"], s, rnd)
        );
      }
    }
    // quintal da casa: 2026-10-10: 7% com 1 bicho (era 35% com 1-2), na regra dos 8 chunks
    if (rnd() < 0.07 && !townFaunaNear(level, cx, cz)) {
      townFaunaAdd(level, cx, cz);
      townSpots(level, cx, cz, ground, ground + 2, rnd, 1).forEach((s) => townSpawnId(level, TOWN_FAUNA_PARK, s, rnd));
    }
    return [ground, ground + floors * 6, name];
  }

  if (park) {
    // pracas, hortas, jardins: so bichos. 2026-10-10: metade dos parques vazia, resto com 1
    // bicho (era 2-4 sempre), na regra dos 8 chunks.
    if (rnd() < 0.5 && !townFaunaNear(level, cx, cz)) {
      townFaunaAdd(level, cx, cz);
      townSpots(level, cx, cz, ground, ground + 3, rnd, 1).forEach((s) => townSpawnId(level, TOWN_FAUNA_PARK, s, rnd));
    }
    return [ground, ground + 4];
  }

  // ruas: 2026-10-10: 5% com 1 bicho (era 25%), na regra dos 8 chunks
  if (rnd() < 0.05 && !townFaunaNear(level, cx, cz)) {
    townFaunaAdd(level, cx, cz);
    townSpots(level, cx, cz, ground, ground + 3, rnd, 1).forEach((s) => townSpawnId(level, TOWN_FAUNA_STREET, s, rnd));
  }
  return [ground, ground + 4];
};

// Waystones: no maximo um a cada 5 chunks. Os chunks com waystone ficam em level.persistentData
// (sunlitWaystones = "x,z;x,z;..."); waystone novo a menos de 5 chunks (em x e z) de outro sai e vira um
// poste de pedra com lanterna. setBlock com flag 3 deixa o mod Waystones tirar o registro dele.
const TOWN_WAYSTONE_MIN = 5;
const townWaystones = (level, cx, cz, ground) => {
  let found = [];
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      for (let y = ground - 1; y <= ground + 8; y++) {
        let pos = new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z);
        let st = level.getBlockState(pos);
        if (st.isAir()) continue;
        let id = String(st.getBlock().getDescriptionId());
        if (!/waystone$/.test(id) || /block\.waystones\.(portstone|sharestone|warp_plate)/.test(id)) continue;
        let half = st.getValues().toString();
        if (half.indexOf("half=upper") >= 0) continue;
        found.push(pos);
      }
    }
  }
  if (!found.length) return;
  let data = level.persistentData;
  let list = String(data.getString("sunlitWaystones") || "")
    .split(";")
    .filter((e) => e.length);
  let near = list.some((e) => {
    let p = e.split(",");
    let dx = Math.abs(parseInt(p[0]) - cx), dz = Math.abs(parseInt(p[1]) - cz);
    return (dx || dz) && dx < TOWN_WAYSTONE_MIN && dz < TOWN_WAYSTONE_MIN;
  });
  if (!near) {
    if (list.indexOf(`${cx},${cz}`) < 0) list.push(`${cx},${cz}`);
    data.putString("sunlitWaystones", list.join(";"));
    return;
  }
  found.forEach((pos) => {
    level.setBlock(pos.above(), $TownBlocks.AIR.defaultBlockState(), 3);
    level.setBlock(pos, $TownBlocks.STONE_BRICK_WALL.defaultBlockState(), 3);
    level.setBlock(pos.above(), $TownBlocks.LANTERN.defaultBlockState(), 3);
  });
  console.info(`[Sunlit Towns] waystone em ${cx},${cz} removido: outro a menos de ${TOWN_WAYSTONE_MIN} chunks`);
};

ServerEvents.tick((e) => {
  if (e.server.getTickCount() % 2) return;
  let queue = global.sunlitTownQueue;
  if (queue && !queue.isEmpty()) {
  let levels = {};
  e.server.getAllLevels().forEach((l) => (levels[global.sunlitDimKey(l)] = l));
  // time budget per tick: post-processing a town chunk (lowering parks, waystones, armor stands, mobs) is
  // heavy; without a budget fast flying through new towns made the server fall seconds behind
  let started = Date.now();
  for (let n = queue.size(), done = 0; n > 0 && done < 6 && Date.now() - started < 25; n--) {
    let item = queue.poll();
    if (!item) break;
    let f = String(item).split("|");
    let level = levels[f[0]];
    if (!level) continue;
    let x = parseInt(f[1]), z = parseInt(f[2]), tries = parseInt(f[3]);
    if (!level.hasChunk(x, z)) {
      // chunk ainda nao terminou de carregar: tenta de novo depois; apos 300 tentativas (~15 s) o chunk vai
      // para global.sunlitTownPending e volta para a fila quando o ChunkEvent$Load disparar (sunlitRetrofitChunks.js)
      if (tries < 300) queue.add(`${f[0]}|${x}|${z}|${tries + 1}`);
      else if (global.sunlitTownPending) {
        let pendKey = `${f[0]}|${x}|${z}`;
        global.sunlitTownSeen.remove(pendKey);
        global.sunlitTownPending.put(pendKey, true);
      }
      continue;
    }
    try {
      let span = townPopulate(level, x, z);
      if (span) {
        try {
          // casas de schematic (sunlit:vila_*) tem arvores de verdade no jardim: copa nao e coluna de folha
          if (!/vila_/.test(String(span[2] || ""))) townTrimLeaves(level, x, z);
        } catch (leafErr) {
          console.warn(`[Sunlit Towns] falha ao aparar folhas no chunk ${x},${z}: ${leafErr}`);
        }
        try {
          townFixBlockEntities(level, x, z, span[0] - 7, span[1] + 2);
        } catch (beErr) {
          console.warn(`[Sunlit Towns] falha ao criar block entities no chunk ${x},${z}: ${beErr}`);
        }
        if (span.length >= 3) {
          // predio (tem nome): geladeira com as costas na parede e no maximo
          // 2-3 baus com loot por andar (regra 2026-10-09)
          try {
            townFixFridges(level, x, z, span[0] - 7, span[1] + 2);
          } catch (frErr) {
            console.warn(`[Sunlit Towns] falha ao girar geladeiras no chunk ${x},${z}: ${frErr}`);
          }
          try {
            townCapLoot(level, x, z, span[0] - 7, span[1] + 2, ((g) => (y) => (y < g ? -1 : Math.floor((y - g) / 6)))(span[0]));
          } catch (lootErr) {
            console.warn(`[Sunlit Towns] falha ao limitar loot no chunk ${x},${z}: ${lootErr}`);
          }
        }
        try {
          townFixSeats(level, x, z, span[0] - 1, span[1] + 1);
        } catch (seatErr) {
          console.warn(`[Sunlit Towns] falha ao virar bancos no chunk ${x},${z}: ${seatErr}`);
        }
        try {
          townFixConnections(level, x, z, span[0] - 1, span[1] + 1);
        } catch (fixErr) {
          console.warn(`[Sunlit Towns] falha ao reconectar chunk ${x},${z}: ${fixErr}`);
        }
      }
    } catch (err) {
      console.warn(`[Sunlit Towns] falha ao povoar chunk ${x},${z}: ${err}`);
    }
    done++;
  }
  }
  try {
    sunlitRetrofitTick(e);
  } catch (rtErr) {
    console.warn(`[Sunlit Towns] falha no retrofit: ${rtErr}`);
  }
});

// ---------------------------------------------------------------- retrofit de chunks antigos (2026-10-09)
// Chunks que a regeneracao manteve (jogador/cama/claim) ainda tem a geracao velha:
// geladeira atravessada e loot em bau demais. Cada chunk carregado entra na fila uma
// vez (visto em memoria) e o tick conserta com orcamento pequeno. Idempotente: chunk
// novo ja vem certo do datapack e o conserto nao acha nada.
const TOWN_FRIDGE = /refurbished_furniture\.(light|dark)_(fridge|freezer)$/;
const TOWN_LOOTBOX = /chest|barrel|fridge|freezer|cabinet|drawer|crate|cooler|basket|sack|shulker|dresser|desk|bookcase|basin|sink|toilet|jar|coffer/;
const TOWN_FIXDIRS = ["north", "south", "west", "east"];
const TOWN_FIXOFF = { north: [0, -1], south: [0, 1], west: [-1, 0], east: [1, 0] };
const $RetrofitQueue = Java.loadClass("java.util.concurrent.ConcurrentLinkedQueue");
const $RetrofitSeen = Java.loadClass("java.util.concurrent.ConcurrentHashMap");

const townSolidWall = (level, pos) => {
  try {
    let st = level.getBlockState(pos);
    if (!st || st.isAir()) return false;
    let id = String(st.getBlock().getDescriptionId());
    if (/_hedge$|leaves/.test(id)) return false;
    return st.isCollisionShapeFullBlock(level, pos);
  } catch (err) {
    return false;
  }
};

const townFixFridges = (level, cx, cz, yMin, yMax) => {
  let fixed = 0;
  let wallOk = (st, p) => {
    if (!st || st.isAir()) return false;
    let id = String(st.getBlock().getDescriptionId());
    if (/_hedge$|leaves/.test(id)) return false;
    try {
      if (st.isCollisionShapeFullBlock(level, p)) return true;
    } catch (err) {}
    return /glass|pane|window/.test(id);
  };
  let frontOk = (st) => !st || st.isAir() || st.canBeReplaced();
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      for (let y = yMin; y <= yMax; y++) {
        let pos = new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z);
        let st = level.getBlockState(pos);
        if (st.isAir() || !TOWN_FRIDGE.test(String(st.getBlock().getDescriptionId()))) continue;
        if (!st.hasProperty($TownProps.HORIZONTAL_FACING)) continue;
        let below = level.getBlockState(pos.below());
        if (!below.isAir() && TOWN_FRIDGE.test(String(below.getBlock().getDescriptionId()))) continue;
        let cur = String(st.getValue($TownProps.HORIZONTAL_FACING));
        let good = (d) => {
          let b = TOWN_FIXOFF[d], f = TOWN_FIXOFF[{ north: "south", south: "north", west: "east", east: "west" }[d]];
          let ws = level.getBlockState(pos.offset(b[0], 0, b[1]));
          let fs = level.getBlockState(pos.offset(f[0], 0, f[1]));
          let fs2 = level.getBlockState(pos.offset(f[0], 1, f[1]));
          return wallOk(ws, pos.offset(b[0], 0, b[1])) && frontOk(fs) && frontOk(fs2);
        };
        let want = null;
        if (good(cur)) continue;
        for (let i = 0; i < TOWN_FIXDIRS.length && !want; i++) {
          let d = TOWN_FIXDIRS[i];
          if (d == cur) continue;
          let b = TOWN_FIXOFF[d];
          // primeira passada: so parede solida; a segunda aceita vidro/vidraca
          if (!townSolidWall(level, pos.offset(b[0], 0, b[1]))) continue;
          if (good(d)) want = d;
        }
        if (!want) {
          for (let i = 0; i < TOWN_FIXDIRS.length && !want; i++) {
            let d = TOWN_FIXDIRS[i];
            if (d == cur) continue;
            let b = TOWN_FIXOFF[d];
            if (wallOk(level.getBlockState(pos.offset(b[0], 0, b[1])), pos.offset(b[0], 0, b[1]))) want = d;
          }
        }
        if (!want || want == cur) continue;
        let dir = { north: $TownDirection.NORTH, south: $TownDirection.SOUTH, west: $TownDirection.WEST, east: $TownDirection.EAST }[want];
        if (!dir) continue;
        try {
          level.setBlock(pos, st.setValue($TownProps.HORIZONTAL_FACING, dir), 18);
          let up = pos.above();
          let us = level.getBlockState(up);
          if (!us.isAir() && TOWN_FRIDGE.test(String(us.getBlock().getDescriptionId())) && us.hasProperty($TownProps.HORIZONTAL_FACING)) {
            level.setBlock(up, us.setValue($TownProps.HORIZONTAL_FACING, dir), 18);
          }
          fixed++;
        } catch (err) {}
      }
    }
  }
  return fixed;
};

// no maximo 2 baus com loot por faixa de 6 blocos (3 se a faixa for maior):
// tira a LootTable dos excedentes (o bau vazio continua de mobilia). So mexe em
// loot sunlit: (dungeon, quests e outros mods ficam como estao).
const townCapLoot = (level, cx, cz, yMin, yMax, bandFn) => {
  let bands = {};
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      for (let y = yMin; y <= yMax; y++) {
        let pos = new $TownBlockPos((cx << 4) + x, y, (cz << 4) + z);
        let st = level.getBlockState(pos);
        if (st.isAir() || !TOWN_LOOTBOX.test(String(st.getBlock().getDescriptionId()))) continue;
        let be = null;
        try {
          be = level.getBlockEntity(pos);
        } catch (err) {
          be = null;
        }
        if (!be) continue;
        let lt = null;
        try {
          let tag = be.saveWithoutMetadata();
          if (tag.contains("LootTable")) lt = tag.getString("LootTable");
        } catch (err) {}
        if (!lt || lt.indexOf("sunlit:") != 0) continue;
        let id = String(st.getBlock().getDescriptionId());
        let prio = /chest$|barrel$/.test(id) ? 0 : (TOWN_FRIDGE.test(id) ? 1 : 2);
        let b = bandFn(y);
        (bands[b] = bands[b] || []).push({ pos: pos, prio: prio, y: y, z: z, x: x });
      }
    }
  }
  let cut = 0;
  Object.keys(bands).forEach((b) => {
    let list = bands[b];
    if (list.length <= 2) return;
    let keep = list.length > 6 ? 3 : 2;
    list.sort((a, c) => (a.prio - c.prio) || (a.y - c.y) || (a.z - c.z) || (a.x - c.x));
    for (let i = keep; i < list.length; i++) {
      try {
        let be = level.getBlockEntity(list[i].pos);
        if (!be) continue;
        let tag = be.saveWithoutMetadata();
        if (!tag.contains("LootTable")) continue;
        tag.remove("LootTable");
        tag.remove("LootTableSeed");
        be.load(tag);
        be.setChanged();
        cut++;
      } catch (err) {}
    }
  });
  return cut;
};

const townRetrofitChunk = (level, cx, cz) => {
  let yMin = null, yMax = null, bandFn = (y) => Math.floor(y / 6);
  try {
    let lc = global.sunlitLostCities;
    if (lc) {
      let info = lc.getLostInfo(level);
      if (info) {
        let ci = info.getChunkInfo(cx, cz);
        if (ci && ci.isCity()) {
          let ground = info.getRealHeight(ci.getCityLevel());
          yMin = ground - 7;
          yMax = ground + Math.max(1, ci.getNumFloors()) * 6 + 2;
          bandFn = (y) => (y < ground ? -1 : Math.floor((y - ground) / 6));
        }
      }
    }
  } catch (err) {}
  if (yMin === null) {
    let sMin = 1e9, sMax = -1e9;
    for (let x = 0; x < 16; x += 4) {
      for (let z = 0; z < 16; z += 4) {
        let h = level.getHeight($TownHeightmap.WORLD_SURFACE, (cx << 4) + x, (cz << 4) + z);
        if (h < sMin) sMin = h;
        if (h > sMax) sMax = h;
      }
    }
    yMin = sMin - 10;
    yMax = sMax + 40;
  }
  let f = 0, c = 0;
  try {
    f = townFixFridges(level, cx, cz, yMin, yMax);
  } catch (err) {}
  try {
    c = townCapLoot(level, cx, cz, yMin, yMax, bandFn);
  } catch (err) {}
  return [f, c];
};

const sunlitRetrofitTick = (e) => {
  let queue = global.sunlitRetrofitQueue;
  if (!queue || queue.isEmpty()) return;
  let levels = {};
  e.server.getAllLevels().forEach((l) => (levels[global.sunlitDimKey(l)] = l));
  let started = Date.now();
  for (let n = queue.size(), done = 0; n > 0 && done < 2 && Date.now() - started < 20; n--) {
    let item = queue.poll();
    if (!item) break;
    let f = String(item).split("|");
    let level = levels[f[0]];
    if (!level) continue;
    let x = parseInt(f[1]), z = parseInt(f[2]);
    if (!level.hasChunk(x, z)) continue;
    try {
      let r = townRetrofitChunk(level, x, z);
      if (r[0] + r[1] > 0) console.info(`[Sunlit Towns] retrofit ${x},${z}: ${r[0]} geladeiras, ${r[1]} baus sem loot`);
    } catch (err) {
      console.warn(`[Sunlit Towns] falha no retrofit ${x},${z}: ${err}`);
    }
    done++;
  }
};

// O ouvinte de ChunkEvent$Load mora em
// startup_scripts/forgeEvents/sunlitRetrofitChunks.js (ForgeEvents.onEvent):
// a versao antiga aqui via EVENT_BUS.addListener quebrava o load com
// "argument type mismatch". A fila (global.sunlitRetrofitQueue) e drenada pelo
// sunlitRetrofitTick acima; chunks novos ja vem certos do datapack.
