package com.pipinha.cinematictoms.client.emi;

import com.tom.storagemod.menu.StorageTerminalMenu;
import dev.dyslexic.cinematic.client.Scene;
import dev.dyslexic.cinematic.client.SceneScreen;
import dev.emi.emi.EmiPort;
import dev.emi.emi.api.EmiApi;
import dev.emi.emi.api.EmiEntrypoint;
import dev.emi.emi.api.EmiPlugin;
import dev.emi.emi.api.EmiRegistry;
import dev.emi.emi.api.stack.EmiStack;
import dev.emi.emi.api.stack.EmiStackInteraction;
import dev.emi.emi.api.widget.Bounds;
import dev.emi.emi.runtime.EmiDrawContext;
import dev.emi.emi.screen.BoMScreen;
import dev.emi.emi.screen.EmiScreenManager;
import dev.emi.emi.screen.RecipeScreen;
import com.pipinha.cinematictoms.mixin.SceneAccessor;
import java.util.function.BooleanSupplier;
import javax.annotation.Nullable;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.Rect2i;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.event.ScreenEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.bus.api.EventPriority;

// Shows EMI's own sidebar (item index, search, favorites) during a Cinematic scene, as on the inventory screen.
// EMI only wires itself into container screens, so the scene screen gets the same calls from here.
@EmiEntrypoint
public final class SceneEmiPlugin implements EmiPlugin {
    private static boolean listening;
    // True while EMI handles input on the scene, so the screens it opens count as a consultation.
    private static boolean routing;
    // The window EMI last laid its widgets out for.
    @Nullable
    private static Rect2i placed;

    @Override
    public void register(EmiRegistry registry) {
        registry.addScreenBoundsProvider(SceneScreen.class, screen -> {
            Rect2i area = SceneEmi.area(screen.width, screen.height);
            return area == null ? Bounds.EMPTY : bounds(area);
        });
        registry.addExclusionArea(SceneScreen.class, (screen, consumer) -> {
            for (Rect2i area : SceneEmi.extraAreas()) {
                consumer.accept(bounds(area));
            }
        });
        // R and U over an item in the scene's inventory drawer, as over a slot on the inventory screen.
        // Not clickable: EMI turns a click on a clickable stack into "show recipe", which ate the click
        // that belonged to the drawer slot. Lookups stay on the R/U keys.
        registry.addStackProvider(SceneScreen.class, (screen, x, y) -> {
            ItemStack stack = SceneEmi.hoveredPanelItem();
            return stack == null ? EmiStackInteraction.EMPTY
                    : new EmiStackInteraction(EmiStack.of(stack), null, false);
        });
        SceneEmi.setActive(true);
        if (!listening) {
            listening = true;
            NeoForge.EVENT_BUS.addListener(EventPriority.HIGH, SceneEmiPlugin::onScreenOpening);
            NeoForge.EVENT_BUS.addListener(SceneEmiPlugin::onScreenInit);
            NeoForge.EVENT_BUS.addListener(SceneEmiPlugin::onScreenRendered);
            NeoForge.EVENT_BUS.addListener(EventPriority.HIGH, SceneEmiPlugin::onMousePressed);
            NeoForge.EVENT_BUS.addListener(EventPriority.HIGH, SceneEmiPlugin::onMouseReleased);
            NeoForge.EVENT_BUS.addListener(EventPriority.HIGH, SceneEmiPlugin::onMouseDragged);
            NeoForge.EVENT_BUS.addListener(EventPriority.HIGH, SceneEmiPlugin::onMouseScrolled);
            NeoForge.EVENT_BUS.addListener(EventPriority.HIGH, SceneEmiPlugin::onKeyPressed);
            NeoForge.EVENT_BUS.addListener(EventPriority.HIGH, SceneEmiPlugin::onCharTyped);
        }
    }

    private static Bounds bounds(Rect2i area) {
        return new Bounds(area.getX(), area.getY(), area.getWidth(), area.getHeight());
    }

    private static boolean shown(Screen screen) {
        return screen instanceof SceneScreen && SceneEmi.inScene() && !EmiScreenManager.isDisabled()
                && SceneEmi.area(screen.width, screen.height) != null;
    }

    private static boolean route(BooleanSupplier input) {
        routing = true;
        try {
            return input.getAsBoolean();
        } finally {
            routing = false;
        }
    }

    // A recipe page opened from the sidebar is a consultation: the scene holds and comes back when it closes.
    // EMI opens it over an inventory screen, which the scene would refuse, so a stand-in takes that place.
    private static void onScreenOpening(ScreenEvent.Opening event) {
        Screen next = event.getNewScreen();
        if (next == null) {
            return;
        }
        if (next instanceof SceneLookupScreen) {
            event.setNewScreen(Scene.phase == Scene.Phase.ACTIVE ? new SceneScreen() : null);
            return;
        }
        Screen current = event.getCurrentScreen();
        if (Scene.phase != Scene.Phase.ACTIVE || !(current instanceof SceneScreen || current instanceof SceneLookupScreen)) {
            return;
        }
        LocalPlayer player = Minecraft.getInstance().player;
        if (routing) {
            SceneAccessor.cinematicToms$setConsulting(true);
        }
        if (routing && player != null && next instanceof InventoryScreen) {
            event.setNewScreen(lookupScreen(player));
            return;
        }
        // EMI keeps the window it was opened from as the parent of its recipe and use pages, and fills
        // the recipe into that window's menu. Opened from a scene it would keep a plain inventory screen,
        // whose only source is the player's own items; the terminal's menu makes the fill count the
        // storage and places the ingredients in the scene's crafting grid.
        StorageTerminalMenu menu = SceneEmi.terminalMenu();
        if (menu == null || player == null) {
            return;
        }
        if (next instanceof RecipeScreen recipe) {
            recipe.old = new SceneLookupScreen(menu, player);
        } else if (next instanceof BoMScreen uses) {
            uses.old = new SceneLookupScreen(menu, player);
        }
    }

    private static SceneLookupScreen lookupScreen(LocalPlayer player) {
        StorageTerminalMenu menu = SceneEmi.terminalMenu();
        return new SceneLookupScreen(menu == null ? player.inventoryMenu : menu, player);
    }

    private static void onScreenInit(ScreenEvent.Init.Post event) {
        if (event.getScreen() instanceof SceneScreen) {
            placed = null;
        }
    }

    private static void onScreenRendered(ScreenEvent.Render.Post event) {
        Screen screen = event.getScreen();
        if (!shown(screen)) {
            return;
        }
        // The side columns belong to EMI, so the cursor there does not aim at the work.
        if (ownsCursor(event.getMouseX(), event.getMouseY())) {
            Scene.overPanel = true;
        }
        Rect2i area = SceneEmi.area(screen.width, screen.height);
        if (area != placed) {
            placed = area;
            EmiScreenManager.addWidgets(screen);
        }
        int mouseX = event.getMouseX();
        int mouseY = event.getMouseY();
        float delta = event.getPartialTick();
        EmiDrawContext context = EmiDrawContext.wrap(event.getGuiGraphics());
        context.push();
        EmiScreenManager.drawBackground(context, mouseX, mouseY, delta);
        EmiScreenManager.render(context, mouseX, mouseY, delta);
        EmiPort.setPositionTexShader();
        EmiScreenManager.drawForeground(context, mouseX, mouseY, delta);
        context.pop();
    }

    // The drawer and the work sit in the middle: clicks there belong to the scene (pick up, craft, place).
    // EMI gets the clicks in its side columns (index, favorites, page buttons) and on its own widgets,
    // which the centered search bar puts below the middle.
    private static boolean ownsCursor(double x, double y) {
        return SceneEmi.overSides(x) || over(EmiScreenManager.search, x, y)
                || over(EmiScreenManager.emi, x, y) || over(EmiScreenManager.tree, x, y);
    }

    private static boolean over(@Nullable AbstractWidget widget, double x, double y) {
        return widget != null && widget.isMouseOver(x, y);
    }

    private static void onMousePressed(ScreenEvent.MouseButtonPressed.Pre event) {
        if (!shown(event.getScreen())) {
            return;
        }
        // A click on the work leaves the search, so typing goes back to the scene's keys.
        if (!ownsCursor(event.getMouseX(), event.getMouseY())) {
            if (EmiScreenManager.search != null && EmiScreenManager.search.isFocused()) {
                EmiScreenManager.search.setFocused(false);
            }
            return;
        }
        if (!fillGesture(event.getButton())
                && route(() -> EmiScreenManager.mouseClicked(event.getMouseX(), event.getMouseY(), event.getButton()))) {
            event.setCanceled(true);
        }
    }

    private static void onMouseReleased(ScreenEvent.MouseButtonReleased.Pre event) {
        if (shown(event.getScreen()) && ownsCursor(event.getMouseX(), event.getMouseY())
                && !fillGesture(event.getButton())
                && route(() -> EmiScreenManager.mouseReleased(event.getMouseX(), event.getMouseY(), event.getButton()))) {
            event.setCanceled(true);
        }
    }

    // Shift + left click asks EMI to fill a recipe into the container window the sidebar is drawn over.
    // A scene has no container window and EMI dereferences it, which crashed the game (2026-10-30).
    // Only that gesture is kept from EMI: plain clicks still open recipes and uses from the sidebar,
    // and the fill is done from the recipe page, whose stand-in window carries the terminal's menu.
    private static boolean fillGesture(int button) {
        return button == 0 && Screen.hasShiftDown() && EmiApi.getHandledScreen() == null;
    }

    private static void onMouseDragged(ScreenEvent.MouseDragged.Pre event) {
        if (shown(event.getScreen()) && ownsCursor(event.getMouseX(), event.getMouseY())
                && route(() -> EmiScreenManager.mouseDragged(event.getMouseX(), event.getMouseY(),
                event.getMouseButton(), event.getDragX(), event.getDragY()))) {
            event.setCanceled(true);
        }
    }

    private static void onMouseScrolled(ScreenEvent.MouseScrolled.Pre event) {
        if (shown(event.getScreen())
                && route(() -> EmiScreenManager.mouseScrolled(event.getMouseX(), event.getMouseY(), event.getScrollDeltaY()))) {
            event.setCanceled(true);
        }
    }

    private static void onKeyPressed(ScreenEvent.KeyPressed.Pre event) {
        if (shown(event.getScreen())
                && route(() -> EmiScreenManager.keyPressed(event.getKeyCode(), event.getScanCode(), event.getModifiers()))) {
            event.setCanceled(true);
        }
    }

    private static void onCharTyped(ScreenEvent.CharacterTyped.Pre event) {
        if (shown(event.getScreen()) && EmiScreenManager.search != null
                && EmiScreenManager.search.charTyped(event.getCodePoint(), event.getModifiers())) {
            event.setCanceled(true);
        }
    }
}
