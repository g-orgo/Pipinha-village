# PORTING.md: pipinha_cinematic_toms (1.20.1 Forge -> 1.21.1 NeoForge 21.1.265)

Phase 2 state (partial): sources renamed (package com.pipinha.cinematictoms, modid, assets
namespace, mixin config), metadata and build.sh written. Phase 2 has NOT been ported yet:
the Tom's and Forge names in the phase 2 files are still the 1.20.1 ones. Build now fails
with 161 errors (was 260 in phase 1, the drop comes from the fixed classpath, not from ports).
Probe data lives in /tmp/p2 (outside the project).

Phase 2 changes so far: build.sh uses the 0.18.30 jar name (find over /mods, the name has
spaces) and removes /src/out inside the container on exit, so a failed build leaves no
root-owned out/ folder. NeoForge rows are checked against the lib jars (see NeoForge table).

## Build notes

- Libraries are mounted at /opt/libs (not /lib, which breaks the eclipse-temurin image).
- The classpath skips 1.20.1 artifacts (`/minecraftforge/`, `1.20.1` in the path). Several
  of them are broken zips ("zip END header not found") and make javap and javac fail.
- javac runs with -Xmaxerrs 1000 so the full error list is visible.
- Build output stays inside the container (root-owned). Cleanup goes through docker exec.

## Inventory: Cinematic Interactions 0.18.30 (modid cinematic)

Jar in mods/: "Cinematic Interaction-NeoForge-1.21.1-0.18.30.jar" (name has spaces; build.sh
finds it with find). The 1.20.1 pack used Forge 0.18.28. The addon API is back in 0.18.30,
so the 1.20.1 addon design stays. Checked with javap -p (batch in one detached container).

| Old class / member used | In 0.18.30 jar | Signature / note |
|---|---|---|
| api.AddonStations | yes | static register(Definition), byId(ResourceLocation), forBlock(BlockState) |
| api.AddonStations$Definition (record) | yes | ctor (ResourceLocation id, ResourceLocation blockId, Class<? extends AbstractContainerMenu> menuClass, Function<BlockState, List<Direction>> sides); accepts(menu), usableSides(state) |
| api.client.AddonMenuStation<M> | yes | abstract, extends client.MenuStation<M>; protected ctor (BlockPos, Direction, Class<M>, int); final kind() returns station.StationKind |
| api.client.AddonScenes | yes | static register(ResourceLocation, Factory), available(BlockState), create(BlockPos, BlockState, LocalPlayer, Direction) returns ClientStation |
| api.client.AddonScenes$Factory | yes | ClientStation create(BlockPos, BlockState, LocalPlayer, Direction) |
| client.SceneScreen | yes | final, extends Screen; mixin target |
| client.Scene | yes | final; static fields phase, overPanel, consulting (package-private); onScreenOpening(net.neoforged.neoforge.client.event.ScreenEvent$Opening) is public static |
| client.CinematicClient$Events | yes | final class, holds onScreenOpening |
| client.ClientStation, TableStation | yes | TableStation extends ClientStation (abstract) |
| client.Picking, Anim, Fx, CameraRig, ItemPlacer | yes | unchanged names (members checked at port time) |
| client.ClientNet | NO | replaced by client.ClientPayloads (nested AtStation) |
| net.StationActionPayload | yes | record implementing CustomPacketPayload, nested Action enum |

The addon registration gap from 0.18.2 is closed: AddonStations and AddonScenes exist in
0.18.30. The old terminal scene flow must be retargeted to these classes in phase 2.

## Inventory: Tom's Simple Storage 2.4.2 (modid toms_storage)

| Old class / member used | In 2.4.2 jar | 1.21 replacement / note |
|---|---|---|
| gui.StorageTerminalMenu | NO | menu.StorageTerminalMenu (extends RecipeBookMenu) |
| gui.CraftingTerminalMenu (+ SlotCrafting) | NO | menu.CraftingTerminalMenu extends StorageTerminalMenu; menu.CraftingTerminalMenu$SlotCrafting extends Slot |
| gui.AbstractStorageTerminalScreen | NO | screen.AbstractStorageTerminalScreen<T extends StorageTerminalMenu> (extends PlatformContainerScreen) |
| util.StoredItemStack | NO | inventory.StoredItemStack |
| util.IDataReceiver | yes | util.IDataReceiver (interface), implemented by CraftingTerminalMenu |
| block.AbstractStorageTerminalBlock | yes | not re-checked in phase 2 (verify with javap when porting) |
| network.NetworkHandler.handleData(DataPacket, Supplier) | NO | handleDataServer(DataPacket, IPayloadContext) and handleDataClient(DataPacket, IPayloadContext), both public static; also sendDataToServer(CompoundTag), sendTo(ServerPlayer, CompoundTag) |
| network.DataPacket | yes | public final record, implements CustomPacketPayload, static ID; the tag field is private (no direct access) |
| menu.sendMessage | yes | public void sendMessage(CompoundTag) on StorageTerminalMenu |
| sorting | yes | public int sorting field on StorageTerminalMenu; screen keeps sortingType (SortingTypes), sortComp (Comparator<StoredItemStack>), buttonSortingType |

## Inventory: EMI (modid emi)

| Old class / member used | In 1.21.1 jar | 1.21 replacement / note |
|---|---|---|
| api.EmiPlugin, api.EmiEntrypoint, api.EmiRegistry, api.EmiApi | yes | unchanged |
| api.stack.EmiStack, EmiStackInteraction | yes | unchanged |
| api.widget.Bounds | yes | unchanged |
| runtime.EmiDrawContext | yes | unchanged (check draw signatures) |
| EmiPort | yes | unchanged |
| screen.EmiScreenManager.craftInteraction (private static, mixin target) | yes | signature: (EmiIngredient, Supplier<EmiRecipe>, EmiStackInteraction ...) |
| screen.RecipeScreen, screen.BoMScreen | yes | unchanged |

Note: the EMI jar also ships remi-neoforge (not used by the old code).

## Inventory: JEI (modid jei)

The old code does not import JEI classes directly. JEI is an optional dependency only.
Check in phase 4 whether any JEI reference exists in the sources (grep: none in phase 1).

## Inventory: TrashSlot 21.1.11 (modid trashslot) and Balm

| Old class / member used | In 1.21.1 jar | 1.21 replacement / note |
|---|---|---|
| network.MessageTrashSlotClick | yes (dump OK) | used as a client payload; verify constructor in phase 4 |
| config.TrashSlotConfig | yes | unchanged |
| client.TrashSlotGuiHandler | yes | unchanged |
| Balm (net.blay09.mods.balm.api.Balm) | yes | Balm is not a 1.21 dependency in the pack list: check that the jar exists before using it |

## Inventory: NeoForge / Minecraft (1.21.1 names)

| Old (Forge 1.20.1) import | 1.21.1 name | In dump |
|---|---|---|
| net.minecraftforge.fml.common.Mod | net.neoforged.fml.common.Mod | MISSING in probe (lib path check needed) |
| net.minecraftforge.eventbus.api.SubscribeEvent | net.neoforged.bus.api.SubscribeEvent | MISSING in probe (lib path check needed) |
| net.minecraftforge.eventbus.api.EventPriority | net.neoforged.bus.api.EventPriority | MISSING in probe |
| net.minecraftforge.api.distmarker.Dist | net.neoforged.api.distmarker.Dist | MISSING in probe |
| net.minecraftforge.fml.ModList | net.neoforged.fml.ModList | MISSING in probe |
| net.minecraftforge.fml.loading.FMLPaths | net.neoforged.fml.loading.FMLPaths | MISSING in probe |
| net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext | removed: use ModContainer injected into the constructor | not in any lib jar |
| net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent / FMLClientSetupEvent | net.neoforged.fml.event.lifecycle.* | MISSING in probe |
| net.minecraftforge.client.event.ScreenEvent | net.neoforged.neoforge.client.event.ScreenEvent | OK |
| net.minecraftforge.common.MinecraftForge | net.neoforged.neoforge.common.NeoForge | OK |
| net.minecraftforge.registries.ForgeRegistries | net.minecraft.core.registries.BuiltInRegistries | OK |
| net.minecraftforge.network.NetworkEvent / NetworkDirection / SimpleChannel | removed: payloads (net.neoforged.neoforge.network.*) | not used by 1.21 |
| net.minecraft.* (GuiGraphics, Rect2i, RenderType, KeyMapping, CompoundTag, ResourceLocation, ...) | same names (Mojang) | OK in srg jar |
| com.mojang.logging.LogUtils, org.slf4j.Logger | same | OK |

Re-check done in phase 2 (zip listing of the lib jars under net/neoforged): all 12 NeoForge
classes used by the port are present. The MISSING marks were a probe classpath problem:
- fml.common.Mod -> loader-4.0.45.jar; bus.api.SubscribeEvent, EventPriority -> bus-8.0.5.jar
- api.distmarker.Dist -> mergetool-2.0.0-api.jar; fml.ModList, fml.loading.FMLPaths,
  fml.event.lifecycle.FMLCommonSetupEvent / FMLClientSetupEvent -> loader-4.0.45.jar
- neoforge.common.NeoForge, neoforge.network.event.RegisterPayloadHandlersEvent,
  neoforge.network.handling.IPayloadContext, neoforge.client.event.ScreenEvent -> neoforge-21.1.265-universal.jar

## Mixin targets (remap = false, Mojang names, no refmap)

| Mixin | Target | Member | Status |
|---|---|---|---|
| NetworkHandlerMixin | com.tom.storagemod.network.NetworkHandler | handleData(DataPacket, Supplier)V | target GONE: retarget to handleDataServer or handleDataClient (DataPacket, IPayloadContext); the mixin body uses NetworkEvent, which is also gone (rewrite, phase 4) |
| CinematicEventsMixin | dev.dyslexic.cinematic.client.CinematicClient$Events | onScreenOpening | present, event type is NeoForge ScreenEvent$Opening |
| SceneScreenMixin | dev.dyslexic.cinematic.client.SceneScreen | guideShown()Z | present in 0.18.30 (private boolean guideShown()) |
| SceneScreenMixin | SceneScreen | layout()V | present (private void layout()) |
| SceneScreenMixin | SceneScreen | overPanel(DD)Z | present (private boolean overPanel(double,double)) |
| SceneScreenAccessor | SceneScreen | hoveredPanelItem (invoker) | present in 0.18.30 (private ItemStack hoveredPanelItem()) |
| SceneScreenAccessor | SceneScreen | panelX, panelY, panelW, panelH | present (private int fields) |
| SceneScreenAccessor | SceneScreen | field (EditBox) | present (private EditBox field) |
| SceneAccessor | dev.dyslexic.cinematic.client.Scene | consulting | present in 0.18.30 (static boolean consulting, package-private: the mixin must sit in the same package or use an accessor with the right access) |
| EmiScreenManagerMixin | dev.emi.emi.screen.EmiScreenManager | craftInteraction (private static, 5+ params) | present |

The three gaps from 0.18.2 (guideShown, hoveredPanelItem, Scene.consulting) are closed in
0.18.30. Open point for the mixin port: Scene.consulting is package-private, so the
accessor target must be checked against the mixin package rules (phase 4).

## Source files: error count after phase 2 build (javac, 161 errors in 14 files)

Counts are from the last build.sh run (phase 2 not ported yet, so these are the 1.20.1 names).

| File | Lines | Errors | Phase |
|---|---|---|---|
| client/TerminalStation.java | 622 | 30 | 2 |
| client/StorageStrip.java | 743 | 19 | 3 |
| client/TerminalGrid.java | 89 | 5 | 2 |
| client/TerminalStripEvents.java | 92 | 19 | 3 |
| client/TerminalClientSetup.java | 25 | 12 | 2 |
| client/TomsPacketRouter.java | 36 | 2 | 2 |
| client/CraftingPanelSwap.java | 47 | 0 | 2 |
| client/TrashSlotEvents.java | 131 | 15 | 4 |
| client/TrashSlotBridge.java | 70 | 3 | 4 |
| client/TrashSlotToggle.java | 56 | 2 | 4 |
| client/emi/SceneEmiPlugin.java | 243 | 31 | 4 |
| client/emi/SceneEmi.java | 152 | 2 | 4 |
| client/emi/SceneLookupScreen.java | 26 | 0 | 4 |
| CinematicToms.java | 38 | 14 | 2 (mod class, payload registration) |
| mixin/NetworkHandlerMixin.java | 27 | 5 | 4 |
| mixin/CinematicEventsMixin.java | 21 | 2 | 4 |
| mixin/SceneScreenMixin.java | 38 | 0 | 4 |
| mixin/SceneScreenAccessor.java | 32 | 0 | 4 |
| mixin/SceneAccessor.java | 14 | 0 | 4 |
| mixin/EmiScreenManagerMixin.java | 22 | 0 | 4 |

Zero counts can hide errors: javac may skip a file once an earlier import fails. Recount
after the first changes.

## Phases

- Phase 2 (about 820 lines): client/TerminalStation.java (crafting grid, vanilla drag),
  client/TerminalGrid.java, client/CraftingPanelSwap.java, client/TerminalClientSetup.java,
  client/TomsPacketRouter.java. Needs the Tom's menu and payload API and the new event bus.
- Phase 3 (about 835 lines): client/StorageStrip.java (item panel, sort, search, Ctrl+A),
  client/TerminalStripEvents.java. Needs the menu sorting API and GuiGraphics changes.
- Phase 4 (about 880 lines): client/TrashSlotEvents.java, client/TrashSlotBridge.java,
  client/TrashSlotToggle.java, client/emi/SceneEmiPlugin.java, client/emi/SceneEmi.java,
  client/emi/SceneLookupScreen.java, CinematicToms.java, all six mixin files. Ends with a
  full build and the acceptance checks (mixscan, ranges, unzip path check).

## Phase 2 status (not finished)

- Done: Cinematic 0.18.30 API checked (javap), build.sh jar name and cleanup, NeoForge rows
  re-checked, Tom's 2.4.2 API inventory (menus, screen, NetworkHandler, DataPacket, sorting).
- Pending, all in client/TerminalStation.java (30 errors), client/TerminalGrid.java (5),
  client/TerminalClientSetup.java (12), client/TomsPacketRouter.java (2),
  CinematicToms.java (14): Tom's imports gui.* -> menu.* / screen.*, Forge imports ->
  neoforged, payload registration (RegisterPayloadHandlersEvent) replacing SimpleChannel,
  ResourceLocation.fromNamespaceAndPath instead of the private constructor, GuiGraphics and
  vertex API (TerminalGrid line 87 uses the 1.20.1 vertex chain), IPayloadContext in the
  packet router. CraftingPanelSwap shows 0 errors, but javac may skip it: recount after.
- Not started in phase 2: none of the code bodies were rewritten yet. The brain should
  split this (TerminalStation alone is 622 lines) into an operator unit.

## Phase 3 plan (remaining per-file work)

- client/StorageStrip.java (743 lines, 19 errors): menu sorting API (sorting field and
  sortComp), GuiGraphics 1.21 calls, inventory.StoredItemStack.
- client/TerminalStripEvents.java (92 lines, 19 errors): event bus rename, ScreenEvent
  Opening/Render calls, menu sorting.
- Phase 4 (unchanged): TrashSlot* (unit with Balm check), client/emi/* (EMI and JEI
  check), mixins (NetworkHandlerMixin needs a rewrite to the payload handler, the other
  mixins have 0 or 2 errors), and the full acceptance checks.

## Done in phase 1

- Sources copied to src/com/pipinha/cinematictoms (20 files). Resources in res/.
- res/META-INF/neoforge.mods.toml and res/pipinha_cinematic_toms.mixins.json written.
- build.sh written; run once, failing with 260 errors as listed above.
- Grep for "sunlit" in src and res: empty.

## Phase 2 status (TerminalStation, TerminalGrid)

- TerminalGrid.java and TerminalStation.java ported: 0 javac errors in both files (build total 126, all in other files).
- Tom's: gui -> menu package, StoredItemStack -> inventory, SlotAction -> util.TerminalSyncManager.SlotAction.
- Cinematic: ClientNet.sendToServer -> net.neoforged.neoforge.network.PacketDistributor.sendToServer (runtime send not verified in game).
- VertexConsumer: addVertex(Matrix4f, x, y, z).setColor(...), endVertex removed.

- Phase 4 (CinematicToms, TomsPacketRouter, TerminalClientSetup): 0 javac errors in the three files. Mod class uses IEventBus and neoforged FML; client setup uses @EventBusSubscriber(Dist.CLIENT); router takes CompoundTag and Tom DataPacket.tag() is public (no accessor mixin needed).

## Phase 3 status (StorageStrip, TerminalStripEvents)

- Build (build.sh, javac against NeoForge 21.1.265, Cinematic 0.18.30, Tom's Simple Storage 2.4.2): 0 errors in both files. Project total went from 63 to 55; the remaining errors are in other files (SceneEmiPlugin, TrashSlotEvents, TrashSlotBridge, CinematicEventsMixin, TrashSlotToggle, SceneEmi).
- API facts used: `SortingTypes.VALUES` and `create(boolean)` under `inventory.sorting`; `TerminalItemStack` extends `StoredItemStack`; `ResourceLocation.fromNamespaceAndPath`; `ItemStack.getComponentsPatch()` replaces the 1.20.1 NBT for `$nbt` search; event API uses `ScreenEvent.Init.Post`, `MouseButtonPressed.Pre`, `MouseScrolled.Pre`, `CharacterTyped.Pre`, `Render.Post` with `EventBusSubscriber.Bus.GAME`.
- Protocol bits not verified: sorting is read from `menu.sorting` (sort index = `& 0xFF`, reverse = `& 0x100`), keep-search (`& 0xE0` group) and pinned (`0x400`) are read from `menu.modes`, and the base for pushState is `menu.modes`. The "c"/"d" message packing is kept from the 1.20.1 code and the server handler in Tom's 2.4.2 was not confirmed.
- To check in game (owner): sort and reverse buttons, pin, keep-search, search bar with @mod/#tag/$nbt, Ctrl+A, hover magnify and click pulls.

## Status: port of remaining files (NeoForge 21.1.265)

- Build: `OUT_DIR=out_p4 sh build.sh` exit 0, 0 javac errors. Baseline was 60 errors in my files (63 total, 3 in StorageStrip, not mine).
- Ported: NetworkHandlerMixin (handleData to handleDataClient with IPayloadContext), CinematicEventsMixin (ScreenEvent import), TrashSlotToggle (FMLPaths), TrashSlotEvents (NeoForge EventBusSubscriber, Bus.GAME, Dist.CLIENT), TrashSlotBridge (BuiltInRegistries, ResourceLocation.fromNamespaceAndPath), SceneEmi and SceneEmiPlugin (StorageTerminalMenu, NeoForge.EVENT_BUS, EventPriority; scroll uses getScrollDeltaY()).
- Mixin targets verified with javap: SceneScreen guideShown()Z, layout()V, overPanel(DD)Z (private, matches), SceneScreen panelX/panelY/panelW/panelH/field and hoveredPanelItem(), Scene consulting (static), EmiScreenManager craftInteraction (private static, 4-arg descriptor), CinematicClient$Events onScreenOpening(ScreenEvent$Opening)V.
- Duplicate @Accessor("panelY") in SceneScreenAccessor is a getter plus a setter with distinct method names; valid for Mixin.
- Gaps: no optional-mod guard yet. EMI and TrashSlot mixins are in the required client list, so a missing optional mod fails at load. Fix needs an IMixinConfigPlugin (new file, not in scope) and a separate config.
- Not verified in game (owner to check): SceneAccessor static accessor on interface, scroll direction in EMI, TrashSlot click and render, Scene field guide hidden, crafting panel swap.
