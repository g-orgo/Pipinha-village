# Unit client-c2b report

Files ported (KubeJS 6 to 7): `kubejs/client_scripts/tooltips/addPriceTooltips.js`, `kubejs/client_scripts/tooltips/addAdvancedTooltips.js`, `kubejs/startup_scripts/globalShippingBinHandlers.js`.

- Tooltips: `addAdvanced` replaced by `tooltip.add(item, text.dynamic(id))` plus `ItemEvents.dynamicTooltips`. Coin, longwing and price tooltips each use one dynamic id. Price data is kept in `priceSources` keyed by item id.
- NBT reads moved to `stack.customData` (`getDouble`, `getString`, `getByte`, `contains`). Quality read via `global.getQualityLevel(stack)`.
- `global.getVariationMultiplier(nbt, stack)` takes the stack as second argument (quality check).
- Splendid removed: `splendid_slimes:plort` and `splendid_slimes:slime_heart` tooltip blocks, Splendid entries in `isSellable`, slime/plort NBT branches in the sales loop, and `block.splendid_slimes.slime_feeder` in the magnifying glass list.
- Caveat: `addAdvancedTooltips.js` quality block was dead code in 1.20.1 (`getCompound` always truthy); the port follows the intent (`if (quality)`).
- Caveat: `priceSources` dedupes by item id; an item priced under two attributes or lists keeps only the first registration.
- Syntax: Rhino check in detached container `kjs-syntax-c2b`, 3 files, 3 OK, 0 FAIL (container removed).
- Acceptance grep `grep -nE '\.nbt\b|getNbt\(|addAdvanced\(|splendid'` on the three files: no hits (exit 1).
- Not verified in game: owner to check price, coin and longwing tooltips (normal and Shift) and the shipping bin sale values.
- Remaining: none in scope.
- Bom senso: removed the dead magnifying-glass Splendid entry (mod absent from `mods/`), not only the listed blocks.
