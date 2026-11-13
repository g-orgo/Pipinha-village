"""Mescla de mods bloco a bloco.

Um char de paleta que vira um destes grupos passa a ser uma lista "blocks" com
pesos "random": o Lost Cities sorteia o bloco em cada posicao, entao a mesma
cozinha sai com fogao do Farmer's Delight ao lado de um do Kaleidoscope, a mesma
horta mistura trigo, alface do Let's Do e berinjela do Cultural Delights etc.

Facing: refurbished_furniture aponta para as COSTAS e o resto para a FRENTE
(ver interior.py), entao ao trocar de familia o facing gira 180 graus.
"""
import re
import mapping as M
from itemcheck import bad_crop

OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}

# (regex no id convertido, [estados alternativos]); o proprio bloco original entra no sorteio
GROUPS = [
    (r'_stove$|^farmersdelight:stove$', [
        'refurbished_furniture:light_stove', 'farmersdelight:stove', 'candlelight:stone_bricks_stove',
        'kaleidoscope_cookery:stove', 'farm_and_charm:stove']),
    (r'cooking_pot$|kaleidoscope_cookery:(pot|stockpot)$', [
        'farmersdelight:cooking_pot', 'kaleidoscope_cookery:pot', 'kaleidoscope_cookery:stockpot[has_lid=true]',
        'candlelight:cooking_pot', 'youkaishomecoming:cooking_stockpot', 'farmersdelight:skillet']),
    (r'cutting_board$|chopping_board$', [
        'farmersdelight:cutting_board', 'kaleidoscope_cookery:chopping_board', 'refurbished_furniture:oak_cutting_board']),
    (r'(cabbage|tomato|cucumber|peanut|apple|blueberry|raspberry|eggplant|avocado)_crate$|_bag$', [
        'culturaldelights:eggplant_crate', 'hearthandharvest:raspberry_crate', 'vintagedelight:cucumber_crate',
        'hearthandharvest:apple_crate', 'hearthandharvest:blueberry_crate', 'culturaldelights:eggplant_crate',
        'youkaishomecoming:cucumber_crate', 'farm_and_charm:potato_bag', 'vinery:apple_bag',
        'farmersrespite:green_tea_leaves_sack', 'farmersdelight:rice_bag']),
    (r'wooden_basket$|fruit_basket$|short_basket$', [
        'farmersdelight:wooden_basket[facing=up]', 'kaleidoscope_cookery:fruit_basket', 'youkaishomecoming:short_basket']),
    # colheitas: so plantas de 1 bloco que crescem em farmland o ANO TODO, ja maduras
    # (regra 2026-10-06: Serene Seasons mostra "Cannot grow" fora de estacao; planta de bioma X
    # so nasceria no bioma X, entao nada com trava de bioma aqui). Batata/cenoura sao sempre
    # ferteis (sem tag sazonal); o resto e Veggies Delight, Kaleidoscope e Cultural Delights.
    (r'^minecraft:(wheat|carrots|potatoes|beetroots)$|^farmersdelight:(cabbages|onions)$|_crop$|^culturaldelights:eggplants$', [
        'veggiesdelight:turnip_crop[age=5]', 'veggiesdelight:broccoli_crop[age=5]',
        'veggiesdelight:cauliflower_crop[age=7]', 'veggiesdelight:garlic_crop[age=5]',
        'veggiesdelight:sweet_potato_crop[age=5]', 'kaleidoscope_cookery:lettuce_crop[age=7]',
        'kaleidoscope_cookery:chili_crop[age=7]', 'culturaldelights:eggplants[age=7]']),
]
GROUPS = [(re.compile(rx), alts) for rx, alts in GROUPS]


def _family_back(bid):
    return bid.startswith('refurbished_furniture:')


def blocks_for(state):
    """estado convertido -> lista [{'random', 'block'}] ou None se nao for de grupo misto."""
    bid, props = M.parse(state)
    for rx, alts in GROUPS:
        if not rx.search(bid):
            continue
        out, seen = [], set()
        for alt in [state] + alts:
            aid, aprops = M.parse(alt)
            if 'onion' in aid:
                continue  # cebola so na loja
            if not M.exists(aid) or aid in seen or bad_crop(aid):
                continue
            seen.add(aid)
            p = dict(aprops)
            f = props.get('facing')
            if f in OPP and 'facing' not in aprops:
                p['facing'] = OPP[f] if _family_back(aid) != _family_back(bid) else f
            for k, v in props.items():
                if k not in p and k != 'facing':
                    p[k] = v
            out.append({'random': 10, 'block': M.fmt(aid, M.clean_props(aid, p))})
        return out if len(out) > 1 else None
    return None
