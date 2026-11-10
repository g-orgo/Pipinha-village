"""Itens que nao podem sair em bau: guias/manuais, itens removidos ou escondidos pelo modpack e itens com icone
quebrado (modelo de item ou textura ausente = quadriculado rosa e preto no inventario).

Indexa os assets de todos os jars de mods + jar vanilla + kubejs/assets uma vez e guarda o veredito por item em
item_icons.json (refeito quando a lista de jars muda).
"""
import glob, json, os, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
INST = os.path.dirname(os.path.dirname(HERE))
MODS = os.path.join(INST, 'mods')
VANILLA = os.path.join(os.path.dirname(os.path.dirname(INST)), 'Install', 'versions', '1.20.1', '1.20.1.jar')
KJS_ASSETS = os.path.join(INST, 'kubejs', 'assets')
CACHE = os.path.join(HERE, 'item_icons.json')

# guides, manuals and lore books: never loot (vanilla books stay allowed)
GUIDE_RX = re.compile(r'guide|manual|lexicon|handbook|codex|almanac|journal|patchouli|tome|_book$|book_of')
# Quark disables whole modules by config and the items stay registered: treat the namespace as unsafe
SKIP_NS = {'quark', 'zeta'}


def _removed_ids():
    """ids literais de global.removedItems/hiddenItems (os gerados em laco o KubeJS filtra em jogo)"""
    src = os.path.join(INST, 'kubejs', 'startup_scripts', 'globalRemovedItems.js')
    return set(re.findall(r'["\']([a-z0-9_.-]+:[a-z0-9_./-]+)["\']', open(src, encoding='utf-8').read())) if os.path.exists(src) else set()


def _strip_ids():
    """stripTags de handleItemBlockFluidTags.js: itens com a cadeia quebrada/desligada pelo modpack
    (semente sem planta, caixote sem receita, wild removido...). Nao sao plantaveis nem saem em bau."""
    src = os.path.join(INST, 'kubejs', 'server_scripts', 'tags', 'handleItemBlockFluidTags.js')
    if not os.path.exists(src):
        return set()
    m = re.search(r'(const|let|var)\s+stripTags\s*=\s*\[(.*?)\];', open(src, encoding='utf-8').read(), re.S)
    return set(re.findall(r'["\']([a-z0-9_.-]+:[a-z0-9_./-]+)["\']', m.group(2))) if m else set()


REMOVED = _removed_ids()
ITEM_STRIP = _strip_ids()

# variavel global de tudo que e proibido em quesito de crops (e de loot): removido, escondido
# (REMOVED ja inclui os hiddenItems, que estao no mesmo arquivo) e cadeia quebrada (ITEM_STRIP).
# (deniedCrops de havestHandling.js NAO entra: la so bloqueia o XP de colheita, a planta cresce.)
# CROP_BLACKLIST: crops and fruits banned in the game and in the generated map (docs/blacklist.md).
# Explicit ids grouped by source; crop and seed items also list their crop/sapling/crate blocks.
CROP_BLACKLIST = {
    # globalRemovedItems.js: removedItems and hiddenItems (crops, crates, seeds, saplings)
    'atmospheric:golden_dragon_fruit', 'atmospheric:golden_dragon_fruit_crate',
    'windswept:ginger_root_crate',
    'farmersdelight:carrot_crate', 'farmersdelight:potato_crate', 'farmersdelight:onion_crate',
    'farmersdelight:beetroot_crate', 'farmersdelight:onion', 'farmersdelight:wild_beetroots',
    'farmersdelight:wild_cabbages', 'farmersdelight:wild_potatoes', 'farmersdelight:wild_carrots',
    'farmersdelight:wild_rice', 'farmersdelight:wild_onions',
    'farm_and_charm:tomato_seeds', 'farm_and_charm:rotten_tomato', 'farm_and_charm:tomato',
    'farm_and_charm:tomato_bag',
    'vintagedelight:oat_seeds',
    'pamhc2trees:gooseberry_sapling', 'pamhc2trees:chestnut_sapling', 'pamhc2trees:avocado_sapling',
    'pamhc2trees:candlenut_sapling', 'pamhc2trees:acorn_sapling', 'pamhc2trees:soursop_sapling',
    'pamhc2trees:spiderweb_sapling', 'pamhc2trees:walnut_sapling', 'pamhc2trees:pear_sapling',
    'pamhc2trees:nutmeg_sapling',
    # handleItemBlockFluidTags.js: stripTags (broken seed, crate and wild chains)
    'vintagedelight:oat', 'vintagedelight:wild_oats', 'vintagedelight:raw_oats',
    'farmersdelight:cabbage_crate', 'farmersdelight:tomato_crate', 'farmersdelight:tomato_seeds',
    'farmersdelight:wild_onions',
    'brewery:hops_seeds', 'farm_and_charm:strawberry_seed', 'farm_and_charm:strawberry',
    'farm_and_charm:lettuce', 'farm_and_charm:corn', 'society:eggplant',
    'pamhc2trees:grapefruit_sapling', 'pamhc2trees:pomegranate_sapling', 'pamhc2trees:guava_sapling',
    'pamhc2trees:jackfruit_sapling', 'pamhc2trees:tamarind_sapling', 'pamhc2trees:papaya_sapling',
    'pamhc2trees:durian_sapling', 'pamhc2trees:rambutan_sapling', 'pamhc2trees:lime_sapling',
    'pamhc2trees:fig_sapling', 'pamhc2trees:date_sapling', 'pamhc2trees:coconut_sapling',
    'pamhc2trees:apricot_sapling', 'pamhc2trees:almond_sapling', 'pamhc2trees:cashew_sapling',
    'pamhc2trees:persimmon_sapling', 'pamhc2trees:pistachio_sapling', 'pamhc2trees:breadfruit_sapling',
    'pamhc2trees:vanillabean_sapling', 'pamhc2trees:peppercorn_sapling', 'pamhc2trees:olive_sapling',
    'pamhc2trees:pecan_sapling', 'pamhc2trees:pinenut_sapling', 'pamhc2trees:paperbark_sapling',
    'pamhc2trees:maple_sapling', 'pamhc2trees:spiderweb_sapling',
    # configs: quark-common.toml disables Potato Crate and Carrot Crate (no registry id, covered by the edition rule)
    # edition decision: potato and carrot leave gardens and loot (vanilla, no seasonal tag)
    'minecraft:potato', 'minecraft:carrot', 'minecraft:potatoes', 'minecraft:carrots',
}

BANNED = REMOVED | ITEM_STRIP | CROP_BLACKLIST


class _Assets:
    def __init__(self):
        self.where = {}  # 'assets/ns/...' -> (zip path or None for loose file, member name or file path)
        self._zips = {}
        srcs = ([VANILLA] if os.path.exists(VANILLA) else []) + sorted(glob.glob(os.path.join(MODS, '*.jar')))
        for j in srcs:
            try:
                z = zipfile.ZipFile(j)
            except (zipfile.BadZipFile, OSError):
                continue
            for n in z.namelist():
                if n.startswith('assets/') and (n.endswith('.json') or n.endswith('.png')) and ('/models/' in n or '/textures/' in n):
                    self.where.setdefault(n, (j, n))
        for f in glob.glob(os.path.join(KJS_ASSETS, '**', '*'), recursive=True):
            if os.path.isfile(f):
                self.where.setdefault('assets/' + os.path.relpath(f, KJS_ASSETS).replace(os.sep, '/'), (None, f))

    def has(self, path):
        return path in self.where

    def json(self, path):
        src, member = self.where[path]
        try:
            if src is None:
                return json.load(open(member, encoding='utf-8'))
            if src not in self._zips:
                self._zips[src] = zipfile.ZipFile(src)
            return json.loads(self._zips[src].read(member).decode('utf-8', 'replace'))
        except ValueError:
            return None


def _split(ref, default_dir):
    ns, _, p = ref.partition(':') if ':' in ref else ('minecraft', '', ref)
    return ns, p if '/' in p or not default_dir else f'{default_dir}/{p}'


def _model_ok(a, ns, path, depth=0):
    """modelo existe, os pais existem e toda textura citada existe"""
    if depth > 12:
        return True
    if (ns, path) in (('minecraft', 'builtin/generated'), ('minecraft', 'builtin/entity'), ('minecraft', 'builtin/missing')):
        return path != 'builtin/missing'
    mp = f'assets/{ns}/models/{path}.json'
    if not a.has(mp):
        return False
    m = a.json(mp)
    if m is None:
        return False
    if 'loader' in m:
        return True  # custom model loader (obj, composite, geckolib...): textures resolved by code
    for v in (m.get('textures') or {}).values():
        if not isinstance(v, str) or v.startswith('#'):
            continue
        tns, tp = _split(v, '')
        if not a.has(f'assets/{tns}/textures/{tp}.png'):
            return False
    par = m.get('parent')
    if par:
        pns, pp = _split(par, '')
        return _model_ok(a, pns, pp, depth + 1)
    return True


def _stamp():
    return [os.path.basename(j) for j in sorted(glob.glob(os.path.join(MODS, '*.jar')))]


_verdict = None
_assets = None


def icon_ok(iid):
    """False quando o icone do item renderiza como textura ausente"""
    global _verdict, _assets
    if _verdict is None:
        _verdict = {}
        if os.path.exists(CACHE):
            d = json.load(open(CACHE))
            if d.get('jars') == _stamp():
                _verdict = d['items']
    if iid not in _verdict:
        if _assets is None:
            _assets = _Assets()
        ns, path = iid.split(':', 1)
        _verdict[iid] = _model_ok(_assets, ns, f'item/{path}')
    return _verdict[iid]


def save_cache():
    if _verdict is not None:
        json.dump({'jars': _stamp(), 'items': _verdict}, open(CACHE, 'w'), sort_keys=True)


def bad_item(iid):
    """motivo para nao sortear o item em bau, ou None"""
    if iid.split(':')[0] in SKIP_NS:
        return 'namespace desligavel'
    if iid in REMOVED:
        return 'removido pelo modpack'
    if iid in ITEM_STRIP:
        return 'cadeia quebrada (stripTags)'
    if not iid.startswith('minecraft:') and GUIDE_RX.search(iid.split(':', 1)[1]):
        return 'guia/manual'
    if not icon_ok(iid):
        return 'icone quebrado'
    return None


def bad_crop(bid, extra=()):
    """motivo para nao plantar o bloco nas cidades, ou None. Checa o bloco + ids relacionados
    (semente, produto) passados em extra: comparacao EXATA, sem substring (ex. o ban de
    farmersdelight:wild_potatoes nao pode barrar minecraft:potatoes)."""
    for i in (bid,) + tuple(extra):
        if i in BANNED:
            return 'proibido pelo modpack'
    return None
