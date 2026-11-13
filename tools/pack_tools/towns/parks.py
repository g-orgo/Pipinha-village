"""Partes novas Sunlit: hortas, curral, pomar, praca, feira e jardim (parques) e
fonte, canteiro, poco e postes (decoracao de rua). Slice 0 = primeira camada acima do gramado.

Regra das hortas (2026-10-06): so plantas que crescem o ANO TODO em qualquer estacao
(Serene Seasons: fora da lista de tags sazonais = sempre fertil; fora de estacao mostra
"Cannot grow" e nao nasce) e sem trava de bioma (planta de bioma X so nasceria no bioma X;
nao plantamos essas nas cidades). Fora: trigo/beterraba (verao+outono/outono), repolho
(outono+inverno), alface/morango (primavera), aveia (verao), cevada (outono+inverno),
abobrinha (verao), pepino (primavera), samambaias do LSO (suspeita de trava termica).
Dentro: batata/cenoura (sempre ferteis), nabo, brocolis, couve-flor, alho, batata-doce
(Veggies Delight), alface/pimenta do Kaleidoscope e berinjela (Cultural Delights).
"""
import mapping as M
import mix as MIX
from itemcheck import bad_crop

PARK_WEIGHTS = {'horta': 1.6, 'horta_mista': 1.6, 'horta_sobrevivencia': 1.2, 'horta_graos': 1.0, 'curral': 1.6, 'pomar': 1.0,
                'pomar_frutas': 1.2, 'celeiro': 1.0, 'praca': 1.6, 'praca_waystone': 2.0, 'feira': 1.2, 'jardim': 1.6}
# zona rural (citystyle sunlit:rural) e docas (sunlit:docas, so em rio/praia)
RURAL_PARK_WEIGHTS = {'horta': 2.0, 'horta_mista': 2.0, 'horta_sobrevivencia': 2.0, 'horta_graos': 2.0, 'curral': 2.2,
                      'pomar': 1.5, 'pomar_frutas': 2.2, 'celeiro': 2.0, 'praca_waystone': 1.5, 'jardim': 0.6}
DOCAS_PARK_WEIGHTS = {'doca': 3.0, 'feira': 1.5, 'praca': 1.0, 'praca_waystone': 1.5, 'jardim': 0.8, 'celeiro': 0.5}
FOUNTAIN_WEIGHTS = {'fonte': 1.0, 'canteiro': 1.0, 'poco': 0.7, 'postes': 0.8, 'waystone_rua': 1.0}


def grid():
    return [[' '] * 16 for _ in range(16)]


def rect(g, x0, z0, x1, z1, c, fill=True):
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            if fill or x in (x0, x1) or z in (z0, z1):
                g[z][x] = c


def put(g, pts, c):
    for x, z in pts:
        g[z][x] = c


def validate(pal):
    out = [{'char': ' ', 'block': 'minecraft:air'}]
    for ch, st in pal.items():
        bid, props = M.parse(st)
        assert M.exists(bid), f'bloco inexistente em parque: {bid}'
        assert not bad_crop(bid), f'bloco proibido pelo modpack em parque: {bid}'
        st = M.fmt(bid, M.clean_props(bid, props))
        mixed = MIX.blocks_for(st)
        out.append({'char': ch, 'blocks': mixed} if mixed else {'char': ch, 'block': st})
    return out


def part(name, slices, pal, folder):
    return name, folder, {'name': name, 'xsize': 16, 'zsize': 16,
                          'refpalette': f'sunlit:{folder}/{name}_palette',
                          'slices': [[''.join(r) for r in s] for s in slices]}, validate(pal)


def fence_ring(g, c='f', gate='E', gates=((7, 0), (8, 0), (7, 15), (8, 15))):
    rect(g, 0, 0, 15, 15, c, fill=False)
    put(g, gates, gate)


def horta(mixed=False):
    s0, s1, s2, s3 = grid(), grid(), grid(), grid()
    fence_ring(s0)
    rect(s0, 1, 1, 14, 14, 'p')                      # caminho de terra
    crops = ['P', 'C', 'T', 'G'] if not mixed else ['T', 'B', 'C', 'S', 'L', 'H']
    # NOTE (2026-10-09): talhoes com 4 de largura (3..6 e 9..12): a borda ficava a 5 blocos do
    # canal e secava (hidratacao alcanca 4), a planta quebrava e o talhao esvaziava.
    for i, (z0, z1) in enumerate([(2, 3), (5, 6), (9, 10), (12, 13)]):
        for side, (x0, x1) in enumerate([(3, 6), (9, 12)]):
            rect(s0, x0, z0, x1, z1, 'F')
            rect(s1, x0, z0, x1, z1, crops[(i * 2 + side) % len(crops)])
    rect(s0, 7, 2, 8, 13, 'w')                       # canal de irrigacao
    put(s0, [(7, 7), (8, 7), (7, 8), (8, 8)], 'p')   # ponte do caminho
    # espantalho e cantos
    # NOTE (2026-10-09): o feno do espantalho era a chave 'H', que a paleta abaixo REDEFINIA
    # para chili_crop: o feno nunca nascia e a abobora flutuava. Feno agora e 'Y'.
    put(s1, [(1, 1)], 'c'); put(s1, [(14, 1)], 'b'); put(s1, [(1, 14)], 'h'); put(s1, [(14, 14)], 'h')
    put(s1, [(4, 8)], 'f'); put(s2, [(4, 8)], 'Y'); put(s3, [(4, 8)], 'J')
    for x, z in [(0, 0), (15, 0), (0, 15), (15, 15)]:
        put(s1, [(x, z)], 'f'); put(s2, [(x, z)], 'l')
    pal = {'f': 'minecraft:spruce_fence', 'E': 'minecraft:spruce_fence_gate[facing=north]', 'p': 'minecraft:dirt_path',
           'F': 'minecraft:farmland[moisture=7]', 'w': 'minecraft:water', 'c': 'minecraft:composter[level=4]',
           'b': 'minecraft:barrel[facing=up]', 'h': 'minecraft:hay_block[axis=y]', 'Y': 'minecraft:hay_block[axis=y]',
           'J': 'minecraft:carved_pumpkin[facing=south]', 'l': 'minecraft:lantern',
           'P': 'minecraft:beetroots[age=3]', 'C': 'veggiesdelight:bellpepper_crop[age=5]',
           'T': 'veggiesdelight:turnip_crop[age=5]', 'G': 'veggiesdelight:garlic_crop[age=5]',
           'B': 'veggiesdelight:broccoli_crop[age=5]', 'S': 'veggiesdelight:sweet_potato_crop[age=5]',
           'L': 'kaleidoscope_cookery:lettuce_crop[age=7]', 'H': 'kaleidoscope_cookery:chili_crop[age=7]'}
    return part('horta_mista' if mixed else 'horta', [s0, s1, s2, s3], pal, 'parks')


def curral():
    s0, s1, s2, s3 = grid(), grid(), grid(), grid()
    fence_ring(s0, gates=((7, 0), (8, 0)))
    # abrigo de madeira no fundo (cobertura de laje sobre postes)
    for x, z in [(10, 11), (14, 11), (10, 14), (14, 14)]:
        put(s0, [(x, z)], 'L'); put(s1, [(x, z)], 'L')
    rect(s2, 10, 11, 14, 14, 'r')
    put(s0, [(11, 13), (12, 13), (13, 13), (12, 12)], 'h')   # feno = marcador p/ animais (KubeJS)
    put(s1, [(12, 13)], 'h')
    put(s0, [(2, 2), (3, 2)], 'T'); put(s0, [(2, 13)], 'c')
    put(s0, [(5, 5), (9, 4), (4, 10)], 'g')
    put(s1, [(0, 0), (15, 0)], 'l')
    pal = {'f': 'minecraft:spruce_fence', 'E': 'minecraft:spruce_fence_gate[facing=north]', 'L': 'minecraft:stripped_spruce_log[axis=y]',
           'r': 'minecraft:spruce_slab[type=bottom]', 'h': 'minecraft:hay_block[axis=y]', 'T': 'minecraft:water_cauldron[level=3]',
           'c': 'minecraft:composter[level=2]', 'g': 'minecraft:grass', 'l': 'minecraft:lantern'}
    return part('curral', [s0, s1, s2, s3], pal, 'parks')


def pomar():
    s0 = grid()
    rect(s0, 7, 0, 8, 15, 'p'); rect(s0, 0, 7, 15, 8, 'p')
    trees = [(2, 2), (12, 2), (2, 12), (12, 12), (2, 5), (12, 5)]
    for i, (x, z) in enumerate(trees):
        s0[z][x] = 'abc'[i % 3]
    put(s0, [(5, 3), (4, 11), (10, 13), (13, 9), (3, 9), (10, 4)], 'r')
    put(s0, [(5, 12), (11, 10), (4, 4)], 'y')
    put(s0, [(6, 6)], 'h'); put(s0, [(9, 9)], 'k')
    put(s0, [(6, 9)], 'B')
    pal = {'p': 'minecraft:dirt_path', 'a': 'minecraft:oak_sapling', 'b': 'minecraft:birch_sapling', 'c': 'minecraft:cherry_sapling',
           'r': 'minecraft:rose_bush[half=lower]', 'y': 'minecraft:sunflower[half=lower]', 'h': 'minecraft:beehive[facing=south]',
           'k': 'farmersdelight:wooden_basket[facing=up]', 'B': 'furniture:oak_bench[facing=east]'}
    # rose_bush/sunflower sao altos: metade de cima no slice 1
    s1 = grid()
    put(s1, [(5, 3), (4, 11), (10, 13), (13, 9), (3, 9), (10, 4)], 'R')
    put(s1, [(5, 12), (11, 10), (4, 4)], 'Y')
    pal.update({'R': 'minecraft:rose_bush[half=upper]', 'Y': 'minecraft:sunflower[half=upper]'})
    return part('pomar', [s0, s1], pal, 'parks')


def praca():
    s0, s1, s2, s3, s4 = grid(), grid(), grid(), grid(), grid()
    # piso xadrez: centro em slab DUPLA (vira bloco cheio, sem spawn),
    # apenas o anel da borda em slab UNICA (degrau decorativo)
    rect(s0, 1, 1, 14, 14, 'a')
    for z in range(1, 15):
        for x in range(1, 15):
            if (x + z) % 2 == 0: s0[z][x] = 'b'
    for z in range(2, 14):
        for x in range(2, 14):
            s0[z][x] = 'D' if (x + z) % 2 == 0 else 'A'
    rect(s0, 5, 5, 10, 10, 'R', fill=False)          # borda da fonte
    rect(s0, 6, 6, 9, 9, 'w')
    rect(s0, 7, 7, 8, 8, 'P'); rect(s1, 7, 7, 8, 8, 'P'); rect(s2, 7, 7, 8, 8, 'Q')
    put(s3, [(7, 7), (8, 8)], 'l')
    # bancos virados para a fonte
    put(s1, [(6, 3), (7, 3), (8, 3), (9, 3)], 'N'); put(s1, [(6, 12), (7, 12), (8, 12), (9, 12)], 'S')
    put(s1, [(3, 6), (3, 7), (3, 8), (3, 9)], 'W'); put(s1, [(12, 6), (12, 7), (12, 8), (12, 9)], 'E')
    # postes de luz e arvores nos cantos (canto sem piso = grama)
    for x, z in [(2, 2), (13, 2), (2, 13), (13, 13)]:
        put(s1, [(x, z)], 'L')
    for x, z in [(0, 0), (15, 0), (0, 15), (15, 15)]:
        s0[z][x] = 't'
    put(s0, [(0, 7), (0, 8), (15, 7), (15, 8), (7, 0), (8, 0), (7, 15), (8, 15)], 'F')
    put(s1, [(1, 1)], 'm')
    pal = {'a': 'minecraft:stone_brick_slab[type=bottom]', 'b': 'minecraft:smooth_stone_slab[type=bottom]',
           'A': 'minecraft:stone_brick_slab[type=double]', 'D': 'minecraft:smooth_stone_slab[type=double]',
           'R': 'minecraft:stone_bricks', 'w': 'minecraft:water', 'P': 'minecraft:chiseled_stone_bricks',
           'Q': 'minecraft:stone_brick_wall', 'l': 'minecraft:lantern',
           'N': 'furniture:oak_bench[facing=south]', 'S': 'furniture:oak_bench[facing=north]',
           'W': 'furniture:oak_bench[facing=east]', 'E': 'furniture:oak_bench[facing=west]',
           'L': 'furniture:street_lantern[facing=south]', 't': 'minecraft:oak_sapling', 'F': 'minecraft:flowering_azalea',
           'm': 'refurbished_furniture:oak_mail_box[facing=south]'}
    return part('praca', [s0, s1, s2, s3, s4], pal, 'parks')


def feira():
    s0, s1, s2, s3 = grid(), grid(), grid(), grid()
    # piso xadrez 2x2: centro em slab DUPLA (vira bloco cheio, sem spawn),
    # apenas o anel da borda em slab UNICA (degrau decorativo)
    rect(s0, 0, 0, 15, 15, 'a')
    for z in range(16):
        for x in range(16):
            if (x // 2 + z // 2) % 2: s0[z][x] = 'b'
    for z in range(1, 15):
        for x in range(1, 15):
            s0[z][x] = 'D' if (x // 2 + z // 2) % 2 else 'A'
    stalls = [(1, 1, 'NR'), (9, 1, 'NW'), (1, 10, 'SR'), (9, 10, 'SW')]
    goods = ['K', 'T', 'U', 'M', 'Q', 'H', 'X', 'Y']
    for i, (x0, z0, kind) in enumerate(stalls):
        roof = 'r' if kind[1] == 'R' else 'v'
        # balcao de 4 com mercadorias
        front_z = z0 + 3 if kind[0] == 'N' else z0
        for k in range(4):
            put(s1, [(x0 + 1 + k, front_z)], goods[(i * 2 + k) % len(goods)])
        put(s2, [(x0 + 2, front_z)], 'C')
        for x, z in [(x0, z0), (x0 + 5, z0), (x0, z0 + 3), (x0 + 5, z0 + 3)]:
            put(s1, [(x, z)], 'f'); put(s2, [(x, z)], 'f')
        rect(s3, x0, z0, x0 + 5, z0 + 3, roof)
        for x in range(x0, x0 + 6, 2):
            for z in range(z0, z0 + 4):
                s3[z][x] = 'w'
    put(s1, [(7, 7), (8, 8)], 'B'); put(s1, [(8, 7)], 'L'); put(s1, [(7, 8)], 'c')
    pal = {'a': 'minecraft:spruce_slab[type=bottom]', 'b': 'minecraft:stone_brick_slab[type=bottom]',
           'A': 'minecraft:spruce_slab[type=double]', 'D': 'minecraft:stone_brick_slab[type=double]',
           'f': 'minecraft:spruce_fence',
           'r': 'minecraft:red_wool', 'v': 'minecraft:green_wool', 'w': 'minecraft:white_wool',
           'K': 'culturaldelights:eggplant_crate', 'T': 'hearthandharvest:raspberry_crate', 'U': 'vintagedelight:cucumber_crate',
           'M': 'minecraft:melon', 'Q': 'minecraft:pumpkin', 'H': 'minecraft:hay_block[axis=y]', 'X': 'minecraft:barrel[facing=up]',
           'Y': 'vintagedelight:peanut_crate', 'C': 'furniture:cash_register[facing=south]', 'B': 'minecraft:barrel[facing=up]',
           'L': 'furniture:street_lantern[facing=south]', 'c': 'minecraft:composter[level=3]'}
    return part('feira', [s0, s1, s2, s3], pal, 'parks')


def jardim():
    s0, s1 = grid(), grid()
    rect(s0, 7, 0, 8, 15, 'p'); rect(s0, 0, 7, 15, 8, 'p')
    flowers = 'abcdefgh'
    for z in range(1, 15):
        for x in range(1, 15):
            if s0[z][x] == ' ' and (x * 7 + z * 3) % 3 != 0:
                s0[z][x] = flowers[(x + z * 2) % len(flowers)]
    put(s0, [(3, 3), (12, 12)], 'h'); put(s0, [(12, 3), (3, 12)], 't')
    put(s0, [(6, 6)], 'B'); put(s0, [(9, 9)], 'E')
    put(s0, [(6, 9)], 'L')
    pal = {'p': 'minecraft:moss_carpet', 'a': 'minecraft:poppy', 'b': 'minecraft:dandelion', 'c': 'minecraft:cornflower',
           'd': 'minecraft:allium', 'e': 'minecraft:oxeye_daisy', 'f': 'minecraft:pink_tulip', 'g': 'minecraft:azure_bluet',
           'h': 'minecraft:beehive[facing=south]', 't': 'minecraft:flowering_azalea', 'h2': 'minecraft:lily_of_the_valley',
           'B': 'furniture:oak_bench[facing=east]', 'E': 'furniture:oak_bench[facing=west]', 'L': 'furniture:street_lantern[facing=south]'}
    pal.pop('h2')
    return part('jardim', [s0, s1], pal, 'parks')


# ---------------------------------------------------------------- decoracao de rua (slot "fountains")
def fonte():
    s0, s1, s2 = grid(), grid(), grid()
    rect(s0, 5, 5, 10, 10, 'R', fill=False); rect(s0, 6, 6, 9, 9, 'w')
    rect(s0, 7, 7, 8, 8, 'P'); rect(s1, 7, 7, 8, 8, 'Q'); put(s2, [(7, 7), (8, 8)], 'l')
    for x, z in [(5, 5), (10, 5), (5, 10), (10, 10)]:
        put(s1, [(x, z)], 'f')
    pal = {'R': 'minecraft:stone_bricks', 'w': 'minecraft:water', 'P': 'minecraft:chiseled_stone_bricks',
           'Q': 'minecraft:stone_brick_wall', 'l': 'minecraft:lantern', 'f': 'minecraft:flower_pot'}
    return part('fonte', [s0, s1, s2], pal, 'fountains')


def canteiro():
    s0, s1 = grid(), grid()
    rect(s0, 6, 6, 9, 9, 'b', fill=False); rect(s0, 7, 7, 8, 8, 'd')
    put(s1, [(7, 7)], 't'); put(s1, [(8, 8)], 'r'); put(s1, [(8, 7)], 'y'); put(s1, [(7, 8)], 'c')
    pal = {'b': 'minecraft:mud_bricks', 'd': 'minecraft:grass_block', 't': 'minecraft:flowering_azalea',
           'r': 'minecraft:poppy', 'y': 'minecraft:dandelion', 'c': 'minecraft:cornflower'}
    return part('canteiro', [s0, s1], pal, 'fountains')


def poco():
    s0, s1, s2, s3 = grid(), grid(), grid(), grid()
    rect(s0, 6, 6, 9, 9, 'c', fill=False); rect(s0, 7, 7, 8, 8, 'w')
    for x, z in [(6, 6), (9, 6), (6, 9), (9, 9)]:
        put(s1, [(x, z)], 'f'); put(s2, [(x, z)], 'f')
    rect(s3, 6, 6, 9, 9, 's'); put(s2, [(7, 7)], 'L')
    pal = {'c': 'minecraft:cobblestone', 'w': 'minecraft:water', 'f': 'minecraft:spruce_fence',
           's': 'minecraft:spruce_slab[type=bottom]', 'L': 'minecraft:lantern[hanging=true]'}
    return part('poco', [s0, s1, s2, s3], pal, 'fountains')


def postes():
    s0 = grid()
    put(s0, [(7, 7)], 'L'); put(s0, [(8, 8)], 'B')
    pal = {'L': 'furniture:street_lantern[facing=south]', 'B': 'furniture:oak_bench[facing=north]'}
    return part('postes', [s0], pal, 'fountains')


# ---------------------------------------------------------------- mescla de mods (zona rural, docas, praca com waystone)
# Cada parque mistura blocos de varios mods (Farmer's Delight, Let's Do, Kaleidoscope, Legendary Survival,
# Hearth & Harvest, Cultural Delights, Farmer's Respite, Youkai's Homecoming, Crabber's Delight, Supplementaries...).
# Bloco que nao existir no modpack derruba o build (validate), entao tudo aqui foi conferido no registry.json.
HORTA_KINDS = {
    'horta_sobrevivencia': {
        'crops': {'1': 'culturaldelights:eggplants[age=7]', '2': 'kaleidoscope_cookery:chili_crop[age=7]',
                  '3': 'kaleidoscope_cookery:lettuce_crop[age=7]', '4': 'veggiesdelight:turnip_crop[age=5]',
                  '5': 'veggiesdelight:broccoli_crop[age=5]', '6': 'veggiesdelight:garlic_crop[age=5]'},
        'deco': ['farm_and_charm:potato_bag[facing=south]', 'farmersdelight:straw_bale[axis=y]', 'meadow:wheelbarrow[facing=east]',
                 'supplementaries:sack', 'farmersdelight:wooden_basket[facing=up]', 'hearthandharvest:cotton_bale[axis=y]',
                 'farm_and_charm:potato_bag[facing=north]', 'minecraft:composter[level=5]']},
    'horta_graos': {
        # graos de verdade sao sazonais (aveia=verao, cevada=outono/inverno, trigo=verao/outono):
        # aqui vao raizes e verduras do ano todo (beterraba, nabo, alho, batata-doce, couve-flor; batata e cenoura estao em CROP_BLACKLIST)
        'crops': {'1': 'minecraft:beetroots[age=3]', '2': 'veggiesdelight:bellpepper_crop[age=5]', '3': 'veggiesdelight:turnip_crop[age=5]',
                   '4': 'veggiesdelight:garlic_crop[age=5]', '5': 'veggiesdelight:sweet_potato_crop[age=5]',
                   '6': 'veggiesdelight:cauliflower_crop[age=7]'},
        'deco': ['farm_and_charm:flour_bag[facing=south]', 'farmersdelight:rice_bale[facing=up]', 'farm_and_charm:corn_bag[facing=south]',
                 'brewinandchewin:keg[facing=south,vertical=false]', 'farmersdelight:straw_bale[axis=y]', 'farmersdelight:rice_bag',
                 'meadow:wheelbarrow[facing=west]', 'minecraft:composter[level=7]']},
}


def horta_mod(kind):
    spec = HORTA_KINDS[kind]
    s0, s1 = grid(), grid()
    fence_ring(s0)
    rect(s0, 1, 1, 14, 14, 'p')
    crops = list(spec['crops'])
    # NOTE (2026-10-09): idem horta(): talhoes de 4 (hidratacao alcanca 4 do canal).
    for i, (z0, z1) in enumerate([(2, 3), (5, 6), (9, 10), (12, 13)]):
        for side, (x0, x1) in enumerate([(3, 6), (9, 12)]):
            rect(s0, x0, z0, x1, z1, 'F')
            rect(s1, x0, z0, x1, z1, crops[(i * 2 + side) % len(crops)])
    rect(s0, 7, 2, 8, 13, 'w')
    put(s0, [(7, 7), (8, 7), (7, 8), (8, 8)], 'p')
    # mobilia de varios mods nas pontas dos caminhos (nunca nos portoes x=7/8)
    spots = [(1, 1), (2, 1), (13, 1), (14, 1), (1, 14), (2, 14), (13, 14), (14, 14)]
    pal = {'f': 'minecraft:spruce_fence', 'E': 'minecraft:spruce_fence_gate[facing=north]', 'p': 'minecraft:dirt_path',
           'F': 'minecraft:farmland[moisture=7]', 'w': 'minecraft:water', 'S': 'farm_and_charm:scarecrow[facing=south]',
           'L': 'furniture:street_lantern[facing=south]'}
    for i, ((x, z), st) in enumerate(zip(spots, spec['deco'])):
        ch = 'abcdeghi'[i]
        put(s1, [(x, z)], ch); pal[ch] = st
    pal.update(spec['crops'])
    put(s1, [(4, 8)], 'S'); put(s1, [(11, 8)], 'L')
    return part(kind, [s0, s1], pal, 'parks')


def pomar_frutas():
    """pomar de frutinhas: fileiras de arbustos de varios mods + arvores frutiferas, colmeias e banca de colheita"""
    s0, s1, s2 = grid(), grid(), grid()
    rect(s0, 7, 0, 8, 15, 'p'); rect(s0, 0, 7, 15, 8, 'p')
    rows = ['b', 'r', 's', 'e', 'w', 'e']  # blueberry, raspberry, sweet berry, cha baixo e trevo (tudo 1 bloco)
    for i, z in enumerate([1, 3, 5, 10, 12, 14]):
        for x in list(range(1, 6)) + list(range(10, 15)):
            put(s0, [(x, z)], rows[i])
            if rows[i] in 'tk':
                put(s1, [(x, z)], rows[i].upper())
    for x, z in [(3, 2), (12, 2), (3, 13), (12, 13)]:
        put(s0, [(x, z)], 'A' if x < 8 else 'C')  # macieira/cerejeira (muda)
    # banca da colheita no cruzamento
    put(s1, [(6, 6)], 'h'); put(s1, [(9, 6)], 'H')
    put(s1, [(6, 9)], 'c'); put(s1, [(9, 9)], 'd'); put(s1, [(5, 9)], 'q')
    put(s1, [(5, 6)], 'v'); put(s2, [(5, 6)], 'V')
    put(s1, [(10, 9)], 'x'); put(s1, [(10, 6)], 'y'); put(s1, [(6, 10)], 'B'); put(s1, [(9, 10)], 'B')
    put(s1, [(0, 0), (15, 15)], 'l')
    for x, z in [(0, 4), (15, 4), (0, 11), (15, 11), (4, 0), (11, 15)]:
        put(s0, [(x, z)], 'w')
    pal = {'p': 'minecraft:dirt_path',
           'b': 'hearthandharvest:blueberry_bush[age=3]', 'r': 'hearthandharvest:raspberry_bush[age=3]',
           's': 'minecraft:sweet_berry_bush[age=3]', 'e': 'farmersrespite:small_tea_bush',
           't': 'farmersrespite:tea_bush[age=3,half=lower]', 'T': 'farmersrespite:tea_bush[age=3,half=upper]',
           'k': 'farmersrespite:coffee_bush[half=lower]', 'K': 'farmersrespite:coffee_bush[half=upper]',
           'A': 'minecraft:oak_sapling', 'C': 'minecraft:cherry_sapling',
           'h': 'minecraft:beehive[facing=south]', 'H': 'minecraft:bee_nest[facing=south]',
           'c': 'hearthandharvest:apple_crate', 'd': 'hearthandharvest:blueberry_crate', 'q': 'hearthandharvest:raspberry_crate',
           'v': 'vinery:apple_press[facing=south,half=lower]', 'V': 'vinery:apple_press[facing=south,half=upper]',
           'x': 'vinery:apple_bag[facing=south]', 'y': 'kaleidoscope_cookery:fruit_basket[facing=south]',
           'B': 'furniture:oak_bench[facing=north]', 'l': 'furniture:street_lantern[facing=south]',
           'w': 'buzzier_bees:white_clover'}
    return part('pomar_frutas', [s0, s1, s2], pal, 'parks')


def celeiro():
    """galpao aberto de fazenda: telhado em laje sobre toras, estoque de varios mods e cercado de animais"""
    s0, s1, s2, s3, s4 = grid(), grid(), grid(), grid(), grid()
    rect(s0, 1, 1, 9, 14, 'P')                         # piso de tabua do galpao
    for x, z in [(1, 1), (9, 1), (1, 14), (9, 14), (1, 7), (9, 7)]:
        for s in (s1, s2, s3):
            put(s, [(x, z)], 'L')
    rect(s4, 0, 0, 10, 15, 'r')                        # telhado
    rect(s4, 1, 1, 9, 14, 'R')
    # estoque encostado na parede oeste/fundo
    stock = ['h', 'j', 'k', 'm', 'n', 'o', 'q', 'u', 'v', 'x', 'y', 'z']
    for i, z in enumerate(range(2, 14)):
        put(s1, [(2, z)], stock[i % len(stock)])
    for i, x in enumerate(range(3, 9)):
        put(s1, [(x, 2)], stock[(i + 5) % len(stock)])
    put(s1, [(3, 3), (3, 4), (3, 9)], 'h')             # feno no chao (marcador de animais do KubeJS, ground..ground+2)
    put(s1, [(5, 9)], 'T'); put(s1, [(6, 9)], 'b'); put(s2, [(5, 9)], 'B')   # lanterna sobre a mesa, nao sobre o moedor
    put(s1, [(8, 13)], 'w'); put(s1, [(7, 13)], 'c'); put(s1, [(5, 13)], 'K')
    put(s3, [(5, 5), (5, 11)], 'l')
    # cercado ao lado
    rect(s0, 11, 1, 15, 14, 'g')
    rect(s1, 10, 0, 15, 15, 'f', fill=False)
    put(s1, [(10, 7)], 'G')
    put(s1, [(13, 3)], 'W'); put(s1, [(14, 12)], 'h'); put(s1, [(13, 12)], 'h')
    pal = {'P': 'minecraft:spruce_planks', 'L': 'minecraft:stripped_spruce_log[axis=y]',
           'r': 'minecraft:spruce_slab[type=bottom]', 'R': 'minecraft:spruce_slab[type=top]',
           'h': 'minecraft:hay_block[axis=y]', 'j': 'farmersdelight:straw_bale[axis=y]', 'k': 'farmersdelight:rice_bale[facing=up]',
           'm': 'hearthandharvest:cotton_bale[axis=y]', 'n': 'farm_and_charm:potato_bag[facing=east]',
           'o': 'farm_and_charm:carrot_bag[facing=east]', 'q': 'hearthandharvest:egg_crate', 'u': 'hearthandharvest:milk_crate[type=bottom]',
           'v': 'culturaldelights:eggplant_crate', 'x': 'brewinandchewin:keg[facing=east,vertical=false]',
           'y': 'refurbished_furniture:spruce_crate[open=false]', 'z': 'minecraft:barrel[facing=up]',
           'T': 'refurbished_furniture:spruce_table', 'b': 'farm_and_charm:mincer', 'B': 'minecraft:lantern',
           'w': 'minecraft:water_cauldron[level=3]', 'c': 'minecraft:composter[level=6]', 'K': 'meadow:wheelbarrow[facing=north]',
           'l': 'minecraft:lantern[hanging=true]', 'g': 'minecraft:grass', 'f': 'minecraft:spruce_fence',
           'G': 'minecraft:spruce_fence_gate[facing=east]', 'W': 'minecraft:water_cauldron[level=3]'}
    pal.pop('g')
    s0 = [[' ' if c == 'g' else c for c in r] for r in s0]
    return part('celeiro', [s0, s1, s2, s3, s4], pal, 'parks')


def doca():
    """cais de pesca: tanque com deck de madeira, armadilhas de caranguejo, barris de peixe e varal de peixe seco"""
    s0, s1, s2, s3 = grid(), grid(), grid(), grid()
    rect(s0, 0, 0, 15, 15, 'P')
    rect(s0, 2, 5, 13, 13, 'w')                        # tanque
    rect(s0, 6, 5, 9, 11, 'P')                         # pier central
    rect(s0, 7, 12, 8, 13, 'P')
    for x, z in [(6, 5), (9, 5), (6, 8), (9, 8), (6, 11), (9, 11)]:
        put(s1, [(x, z)], 'f')                         # cunhos de amarracao
    put(s2, [(6, 11), (9, 11)], 'l')
    put(s0, [(3, 7), (12, 7), (4, 11), (11, 10)], 'T')  # armadilhas dentro d'agua
    # barris e caixas de peixe na beira norte
    stock = ['a', 'b', 'c', 'd', 'e', 'g', 'h', 'i', 'j', 'k']
    for i, x in enumerate([1, 2, 3, 4, 11, 12, 13, 14]):
        put(s1, [(x, 1)], stock[i % len(stock)])
    put(s1, [(1, 2), (14, 2)], 'k'); put(s1, [(2, 2)], 'j')
    # varal de peixe seco e mesa de limpeza
    put(s1, [(5, 2), (10, 2)], 'R'); put(s1, [(6, 2)], 'D'); put(s1, [(9, 2)], 'D')
    put(s1, [(7, 2)], 'C'); put(s1, [(8, 2)], 'N')
    put(s1, [(1, 14), (14, 14)], 'L'); put(s1, [(0, 4), (15, 4)], 'B')
    put(s1, [(5, 3)], 'r'); put(s1, [(10, 3)], 'r'); put(s2, [(5, 3), (10, 3)], 'l')
    pal = {'P': 'minecraft:spruce_planks', 'w': 'minecraft:water', 'f': 'minecraft:spruce_fence',
           'l': 'minecraft:lantern', 'T': 'crabbersdelight:crab_trap[facing=north,hanging=false,waterlogged=true]',
           'a': 'crabbersdelight:cod_barrel', 'b': 'crabbersdelight:salmon_barrel', 'c': 'crabbersdelight:crab_barrel',
           'd': 'crabbersdelight:shrimp_barrel', 'e': 'crabbersdelight:clam_barrel', 'g': 'crabbersdelight:squid_barrel',
           'h': 'crabbersdelight:tropical_fish_barrel', 'i': 'crabbersdelight:pufferfish_barrel',
           'j': 'supplementaries:sack', 'k': 'minecraft:barrel[facing=up]',
           'R': 'youkaishomecoming:drying_rack[facing=south]', 'D': 'youkaishomecoming:dried_fish[facing=south]',
           'C': 'farmersdelight:cutting_board[facing=south]', 'N': 'farmersdelight:safety_net',
           'L': 'furniture:street_lantern[facing=south]', 'B': 'furniture:spruce_bench[facing=south]',
           'r': 'minecraft:spruce_fence'}
    return part('doca', [s0, s1, s2, s3], pal, 'parks')


def praca_waystone():
    """praca de pedra com uma waystone no meio (a Waystones gera nome e registra sozinha ao carregar o bloco)"""
    s0, s1, s2, s3 = grid(), grid(), grid(), grid()
    rect(s0, 1, 1, 14, 14, 'a')
    for z in range(2, 14):
        for x in range(2, 14):
            s0[z][x] = 'D' if (x + z) % 2 == 0 else 'A'
    rect(s0, 6, 6, 9, 9, 'R')                          # tablado da waystone
    put(s1, [(7, 7)], 'W'); put(s2, [(7, 7)], 'U')
    for x, z in [(6, 6), (9, 6), (6, 9), (9, 9)]:
        put(s1, [(x, z)], 'f')
    put(s1, [(5, 3), (6, 3), (9, 3), (10, 3)], 'N'); put(s1, [(5, 12), (6, 12), (9, 12), (10, 12)], 'S')
    put(s1, [(3, 5), (3, 6), (3, 9), (3, 10)], 'E'); put(s1, [(12, 5), (12, 6), (12, 9), (12, 10)], 'O')
    for x, z in [(2, 2), (13, 2), (2, 13), (13, 13)]:
        put(s1, [(x, z)], 'L')
    put(s1, [(7, 2)], 'n'); put(s1, [(8, 13)], 'm')
    for x, z in [(0, 0), (15, 0), (0, 15), (15, 15)]:
        s0[z][x] = 't'
    pal = {'a': 'minecraft:stone_brick_slab[type=bottom]', 'A': 'minecraft:stone_brick_slab[type=double]',
           'D': 'minecraft:polished_andesite_slab[type=double]', 'R': 'minecraft:chiseled_stone_bricks',
           'W': 'waystones:waystone[facing=south,half=lower]', 'U': 'waystones:waystone[facing=south,half=upper]',
           'f': 'supplementaries:flower_box[facing=south,face=floor]',
           'N': 'another_furniture:oak_bench[facing=south]', 'S': 'another_furniture:oak_bench[facing=north]',
           'E': 'another_furniture:oak_bench[facing=east]', 'O': 'another_furniture:oak_bench[facing=west]',
           'L': 'furniture:street_lantern[facing=south]', 'n': 'supplementaries:notice_board[facing=south,has_book=false]',
           'm': 'refurbished_furniture:oak_mail_box[facing=north]', 't': 'minecraft:flowering_azalea'}
    return part('praca_waystone', [s0, s1, s2, s3], pal, 'parks')


def waystone_rua():
    """decoracao de rua: waystone num canteiro com bancos e poste (slot fountains, aparece em qualquer bairro)"""
    s0, s1, s2 = grid(), grid(), grid()
    rect(s0, 6, 6, 9, 9, 'b')
    rect(s0, 7, 7, 8, 8, 'R')
    put(s1, [(7, 7)], 'W'); put(s2, [(7, 7)], 'U')
    put(s1, [(6, 6), (9, 9)], 'f'); put(s1, [(9, 6), (6, 9)], 'p')
    put(s1, [(5, 7), (5, 8)], 'E'); put(s1, [(10, 7), (10, 8)], 'O')
    put(s1, [(8, 5)], 'L')
    pal = {'b': 'minecraft:moss_block', 'R': 'minecraft:chiseled_stone_bricks',
           'W': 'waystones:waystone[facing=south,half=lower]', 'U': 'waystones:waystone[facing=south,half=upper]',
           'f': 'minecraft:flowering_azalea', 'p': 'minecraft:potted_red_tulip',
           'E': 'another_furniture:oak_bench[facing=east]', 'O': 'another_furniture:oak_bench[facing=west]',
           'L': 'furniture:street_lantern[facing=south]'}
    return part('waystone_rua', [s0, s1, s2], pal, 'fountains')


ALL = [horta, lambda: horta(True), lambda: horta_mod('horta_sobrevivencia'), lambda: horta_mod('horta_graos'),
       curral, pomar, pomar_frutas, celeiro, doca, praca_waystone, praca, feira, jardim, fonte, canteiro, poco, postes, waystone_rua]


def write_all(write):
    for f in ALL:
        name, folder, p, pal = f()
        write(f'data/sunlit/lostcities/parts/{folder}/{name}.json', p)
        write(f'data/sunlit/lostcities/palettes/{folder}/{name}_palette.json', {'palette': pal})
