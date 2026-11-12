# REPORT server-05y (tag scripts)

Files: kubejs/server_scripts/tags/handleItemBlockFluidTags.js, kubejs/server_scripts/tags/canonicalItemTags.js (NEW root). Worked directly, no opencode.

Dropped mods removed (farmlife, splendid_slimes; botania had only society:botania_seeds, kept):
- handle: farmlife c:cheeses pair (duplicate) removed; splendid_slimes adds removed (slime_vac_fireable x5, animal_spawn_eggs forEach block, sellable/farmer_product plort and slime_heart x4).
- canonical: duplicate "c:cheeses" entry removed.

forge -> c mapping (verified in mods/*.jar data/c/tags/item/):
- handle: forge:vegetables/eggplant -> c:crops/eggplant; forge:grain/corn -> c:grains/corn; forge:rope -> c:ropes; forge:cobblestone -> c:cobblestones.
- handle: forge:food/cheese and forge:food/pastas aliases removed (they only forwarded to c:foods/cheese and forge:foods/pastas; mapping them would self-reference).
- canonical: cobblestone, cooked_eggs, cooked_rice, cucumber, flour/wheat, food/cheese, food/pastas, grain/corn, rope, tea_leaves, vegetables/eggplant mapped to c:cobblestones, c:foods/cooked_eggs, c:foods/cooked_rice, c:crops/cucumber, c:flours/wheat, c:foods/cheese, c:foods/pasta, c:grains/corn, c:ropes, c:crops/tea_leaves, c:crops/eggplant.
- canonical: forge:cabbage, corn, foods/pastas, oat, onion, peanut, tomato, vegetables/onion removed (the c equivalent already in the list).
- Kept forge: food/raw_pasta, pasta/raw_pasta, plates/lead, plates/silver, raw_crab, salad_ingredients, shears, relocation_not_supported, is_snowy (no c equivalent).

society:* ids unchanged.

Syntax: Rhino check in detached container kjs-syntax-server-05y on both files: files=4 ok=4 fail=0 (2 files, staged twice).

Not verified: in-game behavior (owner test). Other kubejs files still reference dropped mods (out of scope, not touched).
