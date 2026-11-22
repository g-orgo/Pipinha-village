package com.pipinha.cinematictoms.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.logging.LogUtils;
import com.tom.storagemod.block.AbstractStorageTerminalBlock;
import com.tom.storagemod.menu.CraftingTerminalMenu;
import com.tom.storagemod.menu.StorageTerminalMenu;
import com.tom.storagemod.inventory.StoredItemStack;
import com.tom.storagemod.util.TerminalSyncManager;
import dev.dyslexic.cinematic.api.client.AddonMenuStation;
import dev.dyslexic.cinematic.client.Anim;
import dev.dyslexic.cinematic.client.CameraRig;
import dev.dyslexic.cinematic.client.ItemPlacer;
import dev.dyslexic.cinematic.client.Picking;
import dev.dyslexic.cinematic.client.Scene;
import dev.dyslexic.cinematic.net.StationActionPayload;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.Util;
import org.joml.Matrix3f;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import net.neoforged.neoforge.network.PacketDistributor;
import org.slf4j.Logger;

public final class TerminalStation extends AddonMenuStation<StorageTerminalMenu> {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final int DIAG_INTERVAL = 40;
    private static final double REACH = 0.45;
    private static final double FLY_LENGTH = 0.45;
    private static final double FLASH_LENGTH = 0.25;
    private static final double NEVER = -10.0;
    private static final double SCREEN_DEPTH = 5.0 / 16.0;

    private enum Target {
        NONE,
        SCREEN,
        CELL,
        RESULT
    }

    private Target target = Target.NONE;
    private int hoverCell = -1;
    private Vec3 held;
    private ItemStack flyStack = ItemStack.EMPTY;
    private double flyAt = NEVER;
    private double flashAt = NEVER;
    private boolean arrived = true;
    private final StorageStrip strip = new StorageStrip();
    private int diagTicks;
    private final Direction normalDir;
    // Click-and-drag over the crafting grid, like the vanilla inventory: right button places
    // one item on each cell passed over, left button splits the carried stack evenly on release.
    private int dragButton = -1;
    private int dragStart = -1;
    private final List<Integer> dragCells = new ArrayList<>();
    private ItemStack dragStack = ItemStack.EMPTY;
    private long lastPickupAllClickAt = Long.MIN_VALUE;
    private int lastPickupAllCell = -1;

    public TerminalStation(BlockPos pos, Direction side, Class<StorageTerminalMenu> menuType) {
        super(pos, side, menuType, 0);
        this.normalDir = screenNormal(pos, side);
    }

    private static Direction screenNormal(BlockPos pos, Direction side) {
        // Tom's terminal placed on a floor (pos=down) faces up, on a ceiling (pos=up) faces down.
        BlockState state = Minecraft.getInstance().level == null ? null : Minecraft.getInstance().level.getBlockState(pos);
        if (state == null || !state.hasProperty(AbstractStorageTerminalBlock.TERMINAL_POS)) {
            return side;
        }
        return switch (state.getValue(AbstractStorageTerminalBlock.TERMINAL_POS)) {
            case DOWN -> Direction.UP;
            case UP -> Direction.DOWN;
            default -> side;
        };
    }

    private boolean flat() {
        return this.normalDir.getAxis() == Direction.Axis.Y;
    }

    // Direction the screen faces; equals side() for a wall terminal.
    private Vec3 normal() {
        return Vec3.atLowerCornerOf(this.normalDir.getNormal());
    }

    // Direction of the top edge of the screen. The model's x rotation turns the
    // top edge toward the block's FACING on a floor and away from it on a ceiling.
    private Vec3 screenUp() {
        if (this.normalDir == Direction.UP) {
            return this.side().scale(-1.0);
        }
        if (this.normalDir == Direction.DOWN) {
            return this.side();
        }
        return new Vec3(0.0, 1.0, 0.0);
    }

    // Item orientation lying on the screen: +Z along the normal, +Y along the screen top.
    private Quaternionf facing() {
        Vec3 z = this.normal();
        Vec3 y = this.screenUp();
        Vec3 x = y.cross(z);
        Matrix3f basis = new Matrix3f(new Vector3f((float)x.x, (float)x.y, (float)x.z),
                new Vector3f((float)y.x, (float)y.y, (float)y.z), new Vector3f((float)z.x, (float)z.y, (float)z.z));
        return new Quaternionf().setFromNormalized(basis);
    }

    StorageStrip strip() {
        return this.strip;
    }

    // The menu the scene has open at this terminal, or null while it is not open.
    public StorageTerminalMenu sceneMenu() {
        return this.menu();
    }

    private Vec3 blockFront() {
        return Vec3.atCenterOf(this.pos).add(this.normal().scale(0.5));
    }

    private Vec3 faceCenter() {
        // Tom's terminal model is a 6px panel on the wall; its screen sits 5px out from the back.
        return Vec3.atCenterOf(this.pos).add(this.normal().scale(SCREEN_DEPTH - 0.5));
    }

    private boolean flying() {
        return Scene.clock() - this.flyAt < FLY_LENGTH;
    }

    private void startFly(ItemStack stack) {
        this.flyStack = stack;
        this.flyAt = Scene.clock();
        this.arrived = false;
    }

    @Override
    public Component hint() {
        return Component.translatable(this.strip.isSearchFocused()
                ? "pipinha_cinematic_toms.hint.terminal.search"
                : "pipinha_cinematic_toms.hint.terminal");
    }

    // Crafting terminals swap the inventory panel and the contents strip; storage terminals keep the default layout.
    boolean crafting() {
        return this.menu() instanceof CraftingTerminalMenu;
    }

    @Override
    public boolean showsInventory() {
        return true;
    }

    @Override
    public boolean busy() {
        return super.busy() || this.flying();
    }

    @Override
    public Vec3 workPoint() {
        return this.faceCenter();
    }

    @Override
    public List<Vec3> approach(LocalPlayer player) {
        Vec3 center = Vec3.atCenterOf(this.pos).add(this.side().scale(0.95));
        Vec3 stand = new Vec3(center.x, player.getY(), center.z);
        boolean walk = Math.hypot(stand.x - player.getX(), stand.z - player.getZ()) > 0.06;
        return walk ? List.of(stand) : List.of();
    }

    @Override
    public boolean crouches() {
        return false;
    }

    @Override
    public boolean workOnTop() {
        return false;
    }

    @Override
    public CameraRig.Pose lean() {
        if (this.flat()) {
            // Flat screen: hover over it from the player's side and look down (or up) onto it.
            Vec3 eye = this.faceCenter().add(this.normal().scale(0.8)).add(this.side().scale(0.3));
            Vec3 look = this.faceCenter().subtract(eye);
            float pitch = (float)(-Math.toDegrees(Math.atan2(look.y, Math.hypot(look.x, look.z))));
            return new CameraRig.Pose(eye, this.side.getOpposite().toYRot(), pitch, 0.0f);
        }
        // The terminal screen is a vertical wall face: stand in front of it at screen height.
        Vec3 eye = this.blockFront().add(this.side().scale(0.85)).add(0.0, 0.08, 0.0);
        Vec3 look = this.blockFront().subtract(eye);
        float pitch = (float)(-Math.toDegrees(Math.atan2(look.y, Math.hypot(look.x, look.z))));
        return new CameraRig.Pose(eye, this.side.getOpposite().toYRot(), pitch, 0.0f);
    }

    @Override
    public Vec3 rest(boolean right) {
        if (this.flat()) {
            return this.faceCenter().add(this.right().scale(right ? 0.3 : -0.3)).add(this.side().scale(0.35)).add(this.normal().scale(0.12));
        }
        return this.blockFront().add(this.right().scale(right ? 0.3 : -0.3)).add(this.side().scale(0.3)).add(0.0, -0.25, 0.0);
    }

    @Override
    protected Vec3 restPoint(int slot) {
        return this.rest(true).add(this.right().scale(this.denyShake()));
    }

    @Override
    public void updateCursor(boolean overPanel) {
        this.clearCursor();
        double[] m = Picking.mouseGui();
        if (this.strip.over(m[0], m[1])) {
            return;
        }
        if (overPanel || this.menu() == null) {
            return;
        }
        Vec3 center = this.faceCenter();
        Vec3 hit = Picking.cursorOnPlane(center, this.normal());
        if (hit == null) {
            return;
        }
        if (this.menu() instanceof CraftingTerminalMenu crafting) {
            Vec3 right = this.right();
            Vec3 up = this.screenUp();
            Vec3 local = hit.subtract(center);
            double u = local.dot(right);
            double v = local.dot(up);
            int cell = TerminalGrid.cellAt(u, v);
            if (cell >= 0) {
                this.target = Target.CELL;
                this.hoverCell = cell;
                this.aim = TerminalGrid.point(center, right, up, TerminalGrid.cellU(cell), TerminalGrid.cellV(cell)).add(this.normal().scale(TerminalGrid.LIFT));
                return;
            }
            if (TerminalGrid.resultAt(u, v) && !crafting.getCraftingResultSlot().getItem().isEmpty()) {
                this.target = Target.RESULT;
                this.aim = TerminalGrid.point(center, right, up, TerminalGrid.RESULT_X, TerminalGrid.RESULT_Y).add(this.normal().scale(TerminalGrid.LIFT));
                return;
            }
        }
        if (hit.distanceTo(center) > REACH) {
            return;
        }
        this.target = Target.SCREEN;
        this.aim = center;
    }

    @Override
    public void clearCursor() {
        super.clearCursor();
        this.target = Target.NONE;
        this.hoverCell = -1;
    }

    @Override
    public List<Component> tooltip(ItemStack carried) {
        StorageTerminalMenu menu = this.menu();
        if (!(menu instanceof CraftingTerminalMenu crafting)) {
            return null;
        }
        ItemStack stack = ItemStack.EMPTY;
        if (this.target == Target.CELL) {
            List<Slot> grid = TerminalGrid.grid(crafting);
            if (this.hoverCell < grid.size()) {
                stack = grid.get(this.hoverCell).getItem();
            }
        } else if (this.target == Target.RESULT) {
            stack = crafting.getCraftingResultSlot().getItem();
        }
        return stack.isEmpty() ? null : Screen.getTooltipFromItem(Minecraft.getInstance(), stack);
    }

    @Override
    public Vec3 handTarget(Vec3 aim, Vec3 shoulder, boolean carrying, double tap) {
        Vec3 at = this.flying() ? this.faceCenter() : aim;
        Vec3 reach = at.subtract(shoulder).normalize();
        double hover = carrying ? 0.11 : 0.075;
        return at.add(this.normal().scale(hover - 0.18 * tap)).subtract(reach.scale(0.07)).add(0.0, 0.035, 0.0);
    }

    @Override
    public Vec3 heldItemPoint(Vec3 hand, Vec3 shoulder) {
        Vec3 reach = hand.subtract(shoulder).normalize();
        this.held = hand.add(reach.scale(0.07)).add(0.0, -0.045, 0.0);
        return this.held;
    }

    @Override
    public void click(int button, boolean shift) {
        StorageTerminalMenu menu = this.menu();
        if (button == 0 && !shift && this.target == Target.CELL && this.hoverCell >= 0
                && menu instanceof CraftingTerminalMenu crafting && !this.moving()) {
            long now = Util.getMillis();
            if (this.lastPickupAllCell == this.hoverCell && now - this.lastPickupAllClickAt <= 250L) {
                this.lastPickupAllClickAt = Long.MIN_VALUE;
                this.lastPickupAllCell = -1;
                List<Slot> grid = TerminalGrid.grid(crafting);
                if (this.hoverCell < grid.size()) {
                    Minecraft mc = Minecraft.getInstance();
                    if (mc.gameMode != null && mc.player != null) {
                        mc.gameMode.handleInventoryMouseClick(crafting.containerId, grid.get(this.hoverCell).index,
                                0, ClickType.PICKUP_ALL, mc.player);
                        this.playPull();
                    }
                }
                return;
            }
            this.lastPickupAllClickAt = now;
            this.lastPickupAllCell = this.hoverCell;
        } else {
            this.lastPickupAllClickAt = Long.MIN_VALUE;
            this.lastPickupAllCell = -1;
        }
        if (!shift && (button == 0 || button == 1) && this.target == Target.CELL && this.hoverCell >= 0
                && !this.moving() && menu instanceof CraftingTerminalMenu && !menu.getCarried().isEmpty()) {
            this.dragButton = button;
            this.dragStart = this.hoverCell;
            this.dragCells.clear();
            this.dragStack = menu.getCarried().copy();
            if (button == 1) {
                // Right button acts at once, the same as a single right click.
                this.dragCells.add(this.hoverCell);
                super.click(button, false);
            } else if (this.spreadable(this.hoverCell, this.dragStack)) {
                this.dragCells.add(this.hoverCell);
            }
            return;
        }
        super.click(button, shift);
    }

    @Override
    public void drag(int button) {
        if (button != this.dragButton) {
            return;
        }
        Scene.updateCursor();
        if (this.target != Target.CELL || this.hoverCell < 0 || this.dragCells.contains(this.hoverCell)) {
            return;
        }
        StorageTerminalMenu menu = this.menu();
        if (!(menu instanceof CraftingTerminalMenu crafting)) {
            return;
        }
        if (button == 1) {
            ItemStack carried = menu.getCarried();
            if (carried.isEmpty() || !this.spreadable(this.hoverCell, carried)) {
                return;
            }
            List<Slot> grid = TerminalGrid.grid(crafting);
            if (this.hoverCell >= grid.size()) {
                return;
            }
            this.dragCells.add(this.hoverCell);
            this.slotClick(grid.get(this.hoverCell).index, 1, false);
            this.playPull();
        } else if (this.dragStack.getCount() > this.dragCells.size() && this.spreadable(this.hoverCell, this.dragStack)) {
            this.dragCells.add(this.hoverCell);
            this.playMark();
        }
    }

    @Override
    public void release(int button) {
        if (button != this.dragButton) {
            return;
        }
        int start = this.dragStart;
        List<Integer> cells = new ArrayList<>(this.dragCells);
        this.dragButton = -1;
        this.dragStart = -1;
        this.dragCells.clear();
        this.dragStack = ItemStack.EMPTY;
        if (button != 0 || !(this.menu() instanceof CraftingTerminalMenu crafting)) {
            return;
        }
        List<Slot> grid = TerminalGrid.grid(crafting);
        if (cells.size() > 1) {
            this.spreadEvenly(crafting, grid, cells);
        } else if (start >= 0 && start < grid.size()) {
            this.slotClick(grid.get(start).index, 0, false);
        }
        this.playPull();
    }

    // Vanilla even split: QUICK_CRAFT start, one add per cell, end. The server runs the same sequence.
    private void spreadEvenly(CraftingTerminalMenu crafting, List<Slot> grid, List<Integer> cells) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.gameMode == null || mc.player == null) {
            return;
        }
        int id = crafting.containerId;
        mc.gameMode.handleInventoryMouseClick(id, -999, AbstractContainerMenu.getQuickcraftMask(0, 0), ClickType.QUICK_CRAFT, mc.player);
        for (int cell : cells) {
            if (cell < grid.size()) {
                mc.gameMode.handleInventoryMouseClick(id, grid.get(cell).index, AbstractContainerMenu.getQuickcraftMask(1, 0), ClickType.QUICK_CRAFT, mc.player);
            }
        }
        mc.gameMode.handleInventoryMouseClick(id, -999, AbstractContainerMenu.getQuickcraftMask(2, 0), ClickType.QUICK_CRAFT, mc.player);
    }

    private boolean spreadable(int cell, ItemStack stack) {
        if (stack.isEmpty() || !(this.menu() instanceof CraftingTerminalMenu crafting)) {
            return false;
        }
        List<Slot> grid = TerminalGrid.grid(crafting);
        if (cell < 0 || cell >= grid.size()) {
            return false;
        }
        Slot slot = grid.get(cell);
        return slot.mayPlace(stack) && AbstractContainerMenu.canItemQuickReplace(slot, stack, true);
    }

    private void playMark() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level != null) {
            Vec3 at = this.soundPoint();
            float pitch = 1.6f + 0.05f * this.dragCells.size();
            mc.level.playLocalSound(at.x, at.y, at.z, SoundEvents.ITEM_PICKUP, SoundSource.PLAYERS, 0.12f, pitch, false);
        }
    }

    @Override
    protected void act(int button, boolean shift) {
        StorageTerminalMenu menu = this.menu();
        if (menu == null) {
            return;
        }
        if (this.target == Target.CELL && menu instanceof CraftingTerminalMenu crafting) {
            List<Slot> grid = TerminalGrid.grid(crafting);
            if (this.hoverCell < grid.size()) {
                this.slotClick(grid.get(this.hoverCell).index, button, shift);
                this.playPull();
            }
            return;
        }
        if (this.target == Target.RESULT && menu instanceof CraftingTerminalMenu crafting) {
            this.slotClick(crafting.getCraftingResultSlot().index, 0, shift);
            this.playPull();
            return;
        }
        if (this.target != Target.SCREEN) {
            return;
        }
        ItemStack carried = menu.getCarried();
        if (carried.isEmpty()) {
            this.deny();
            return;
        }
        menu.sync.sendInteract(null, TerminalSyncManager.SlotAction.PULL_OR_PUSH_STACK, false);
        this.startFly(carried.copy());
    }

    void stripClick(int button, boolean shift) {
        double[] m = Picking.mouseGui();
        if (this.strip.click(m[0], m[1], button, shift)) {
            return;
        }
        StorageTerminalMenu menu = this.menu();
        if (menu == null || this.busy()) {
            return;
        }
        StoredItemStack hit = this.strip.hit(m[0], m[1]);
        ItemStack carried = menu.getCarried();
        if (button == 0) {
            if (!carried.isEmpty()) {
                menu.sync.sendInteract(null, TerminalSyncManager.SlotAction.PULL_OR_PUSH_STACK, false);
                this.startFly(carried.copy());
            } else if (hit != null) {
                menu.sync.sendInteract(hit, shift ? TerminalSyncManager.SlotAction.SHIFT_PULL : TerminalSyncManager.SlotAction.PULL_OR_PUSH_STACK, false);
                this.playPull();
            }
        } else if (button == 1 && hit != null) {
            menu.sync.sendInteract(hit, TerminalSyncManager.SlotAction.PULL_ONE, false);
            this.playPull();
        }
    }

    private void playPull() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level != null) {
            Vec3 at = this.soundPoint();
            mc.level.playLocalSound(at.x, at.y, at.z, SoundEvents.ITEM_PICKUP, SoundSource.PLAYERS, 0.3f, 1.7f, false);
        }
    }

    @Override
    public void renderScreen(GuiGraphics graphics, Font font, float alpha) {
        this.strip.render(graphics, font, alpha);
    }

    @Override
    public void quickMove(int inventorySlot, int menuSlot) {
        LocalPlayer player = Minecraft.getInstance().player;
        ItemStack stack = player != null ? player.getInventory().getItem(inventorySlot).copy() : ItemStack.EMPTY;
        if (this.busy() || menuSlot < 0 || stack.isEmpty()) {
            return;
        }
        // Cinematic's QUICK action rolls the player slot back when no station slot changed, but Tom's
        // quickMoveStack pushes into the network instead of a slot; the vanilla click reaches it directly.
        this.slotClick(menuSlot, 0, true);
        this.startFly(stack);
    }

    @Override
    public void tick() {
        super.tick();
        if (this.menu() != null) {
            this.menu().onPacket = null;
            this.strip.refresh(this.menu());
        }
        if (this.diagTicks++ % DIAG_INTERVAL == 0) {
            Minecraft mc = Minecraft.getInstance();
            LOGGER.info("[CinematicToms] scene tick: menu={} items={} screen={}",
                    this.menu() == null ? "-" : this.menu().getClass().getSimpleName(),
                    this.menu() == null ? 0 : this.menu().sync.getAsList().size(),
                    mc.screen == null ? "-" : mc.screen.getClass().getSimpleName());
        }
        if (!this.arrived && !this.flying()) {
            this.arrived = true;
            this.flashAt = Scene.clock();
            Minecraft mc = Minecraft.getInstance();
            if (mc.level != null) {
                Vec3 at = this.soundPoint();
                mc.level.playLocalSound(at.x, at.y, at.z, SoundEvents.ITEM_PICKUP, SoundSource.PLAYERS, 0.4f, 1.4f, false);
            }
        }
    }

    @Override
    public void onEnd() {
        super.onEnd();
        this.flyAt = NEVER;
        this.arrived = true;
        this.strip.reset();
    }

    @Override
    public double flash() {
        double t = Scene.clock() - this.flashAt;
        return t >= 0.0 && t < FLASH_LENGTH ? 0.35 * (1.0 - t / FLASH_LENGTH) : 0.0;
    }

    @Override
    public int flashColor() {
        return 0x66E6FF;
    }

    @Override
    public void renderScene(PoseStack pose, MultiBufferSource buffers, Camera camera, int light) {
        if (!this.flying()) {
            return;
        }
        double k = Anim.inOutCubic(Math.min(1.0, (Scene.clock() - this.flyAt) / FLY_LENGTH));
        Vec3 from = this.held != null ? this.held : this.rest(true);
        Vec3 at = Anim.lerp(from, this.faceCenter().add(this.normal().scale(0.02)), k);
        float size = (float)((ItemPlacer.isBlock(this.flyStack) ? 0.16 : 0.24) * (1.0 - k));
        // Upright, facing out of the screen, sinking into the face as it shrinks.
        ItemPlacer.drawOriented(pose, buffers, camera.getPosition(), this.flyStack, at,
                this.facing(), size, light);
    }

    @Override
    public void renderWorld(PoseStack pose, MultiBufferSource buffers, Vec3 camera, int light) {
        if (!(this.menu() instanceof CraftingTerminalMenu crafting)) {
            return;
        }
        Vec3 center = this.faceCenter();
        Vec3 right = this.right();
        Vec3 up = this.screenUp();
        Quaternionf facing = this.facing();
        List<Slot> grid = TerminalGrid.grid(crafting);
        for (int i = 0; i < grid.size(); i++) {
            ItemStack stack = grid.get(i).getItem();
            if (stack.isEmpty()) {
                continue;
            }
            Vec3 at = TerminalGrid.point(center, right, up, TerminalGrid.cellU(i), TerminalGrid.cellV(i)).add(this.normal().scale(TerminalGrid.LIFT * 2.0));
            ItemPlacer.drawOriented(pose, buffers, camera, stack, at, facing, (float)size(stack), light);
        }
        ItemStack result = crafting.getCraftingResultSlot().getItem();
        if (!result.isEmpty()) {
            double bob = Math.sin(Scene.clock() * 2.1) * 0.01;
            Vec3 at = TerminalGrid.point(center, right, up, TerminalGrid.RESULT_X, TerminalGrid.RESULT_Y + bob).add(this.normal().scale(TerminalGrid.LIFT * 3.0));
            ItemPlacer.drawOriented(pose, buffers, camera, result, at, facing, (float)(size(result) * TerminalGrid.RESULT_SCALE), light);
        }
        if (this.dragButton == 0) {
            for (int cell : this.dragCells) {
                if (cell != this.hoverCell) {
                    this.drawHighlight(pose, buffers, camera, TerminalGrid.cellU(cell), TerminalGrid.cellV(cell), TerminalGrid.CELL * 0.5);
                }
            }
        }
        if (this.target == Target.CELL && this.hoverCell >= 0) {
            this.drawHighlight(pose, buffers, camera, TerminalGrid.cellU(this.hoverCell), TerminalGrid.cellV(this.hoverCell), TerminalGrid.CELL * 0.5);
        } else if (this.target == Target.RESULT) {
            this.drawHighlight(pose, buffers, camera, TerminalGrid.RESULT_X, TerminalGrid.RESULT_Y, TerminalGrid.CELL * 0.5);
        }
    }

    private static double size(ItemStack stack) {
        return ItemPlacer.isBlock(stack) ? TerminalGrid.BLOCK_SIZE : TerminalGrid.ITEM_SIZE;
    }

    private void drawHighlight(PoseStack pose, MultiBufferSource buffers, Vec3 camera, double x, double y, double half) {
        Vec3 origin = this.faceCenter().add(this.normal().scale(TerminalGrid.LIFT * 0.5));
        pose.pushPose();
        pose.translate(origin.x - camera.x, origin.y - camera.y, origin.z - camera.z);
        TerminalGrid.highlight(pose, buffers, this.right(), this.screenUp(), x, y, half);
        pose.popPose();
    }

    @Override
    public boolean keyPressed(int key) {
        if (this.strip.keyPressed(key)) {
            return true;
        }
        if (key == Minecraft.getInstance().options.keyInventory.getKey().getValue()) {
            Scene.drop();
            LOGGER.info("[CinematicToms] E pressed, requesting window");
            PacketDistributor.sendToServer(new StationActionPayload(this.pos, this.kind(), StationActionPayload.Action.WINDOW, 0, 0, false, 0));
            return true;
        }
        return super.keyPressed(key);
    }
}
