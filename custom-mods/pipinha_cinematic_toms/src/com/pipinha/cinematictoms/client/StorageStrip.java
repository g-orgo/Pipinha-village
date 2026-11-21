package com.pipinha.cinematictoms.client;

import com.tom.storagemod.menu.StorageTerminalMenu;
import com.tom.storagemod.inventory.sorting.SortingTypes;
import com.tom.storagemod.inventory.TerminalItemStack;
import net.minecraft.core.component.DataComponentPatch;
import dev.dyslexic.cinematic.client.Anim;
import dev.dyslexic.cinematic.client.Picking;
import dev.dyslexic.cinematic.client.Scene;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.regex.Pattern;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.util.Mth;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

final class StorageStrip {
    private static final int COLS = 9;
    private static final int CELL = 18;
    private static final int PAD = 5;
    private static final int BASE_H = 28;
    private static final int CHROME_H = 34;
    private static final int EXPAND_H = CHROME_H + 58;
    private static final int PANEL_W = 172;
    private static final int BOTTOM_GAP = 26;
    private static final int SWAP_GAP = 4;
    private static final int BTN = 16;
    private static final int BTN_GAP = 1;
    private static final int BTN_COUNT = 4;
    private static final int TOOLBAR_Y = 2;
    private static final int FIELD_Y = 20;
    private static final int FIELD_H = 12;
    private static final int FIELD_W = PANEL_W - PAD * 2;
    private static final int MAX_QUERY = 48;
    private static final ResourceLocation ICON_SORT_AMOUNT = icon("sort_amount");
    private static final ResourceLocation ICON_SORT_NAME = icon("sort_name");
    private static final ResourceLocation ICON_SORT_MOD = icon("sort_by_mod");
    private static final ResourceLocation ICON_ASC = icon("sort_asc");
    private static final ResourceLocation ICON_DESC = icon("sort_desc");
    private static final ResourceLocation ICON_SEARCH = icon("search_mode");
    private static final ResourceLocation ICON_SEARCH_KEEP = icon("search_mode_keep");
    private static final ResourceLocation ICON_PIN_OFF = icon("tall_terminal_off");
    private static final ResourceLocation ICON_PIN_ON = icon("tall_terminal_on");

    private static ResourceLocation icon(String name) {
        return ResourceLocation.fromNamespaceAndPath("pipinha_cinematic_toms", "textures/gui/strip/" + name + ".png");
    }

    private static String keptQuery = "";

    private final List<TerminalItemStack> all = new ArrayList<>();
    private final List<TerminalItemStack> items = new ArrayList<>();
    private StorageTerminalMenu menu;
    private boolean stateLoaded;
    private int sortType;
    private boolean reversed;
    private boolean keepSearch;
    private boolean pinned;
    private String query = "";
    private int caret;
    // Other end of the selected text; equal to caret when nothing is selected.
    private int anchor;
    private boolean focused;
    private double caretAt;
    private int row;
    private double expand;
    private double pop;
    private int popIndex = -1;
    private int hoverButton = -1;
    private boolean shown;
    private float scale = 1.0f;
    private int panelX;
    private int panelY;
    private int panelW;
    private int panelH;
    private int panelBottom;
    private boolean swapped;
    private int swapTop;
    private int swapLimit;
    private int localH = BASE_H;

    void refresh(StorageTerminalMenu menu) {
        this.menu = menu;
        this.all.clear();
        for (TerminalItemStack s : menu.sync.getAsList()) {
            if (s.getQuantity() > 0) {
                this.all.add(s);
            }
        }
        if (!this.stateLoaded) {
            this.stateLoaded = true;
            this.readState(menu);
        }
        this.applyFilter();
    }

    // Tom's Simple Storage 2.4.2 protocol (AbstractStorageTerminalScreen.sendUpdate):
    // sorting: bits 0-7 SortingTypes ordinal, bit 8 reverse, bit 9 set when ghost items are off.
    // searchType: bit 0 auto, bit 1 keep search text, bit 2 sync.
    // modes: bits 0-3 control mode, bit 4 tall mode. There is no pinned bit in 2.4.2,
    // so pinned is kept as local client state only.
    private void readState(StorageTerminalMenu menu) {
        int d = menu.sorting;
        this.sortType = (d & 0xFF) % SortingTypes.VALUES.length;
        this.reversed = (d & 0x100) != 0;
        // searchType is -1 until the server has synced it; treat that as "no bits set".
        int st = menu.searchType < 0 ? 0 : menu.searchType;
        this.keepSearch = (st & 2) != 0;
        this.query = this.keepSearch ? keptQuery : "";
        this.caret = this.query.length();
        this.anchor = this.caret;
    }

    void reset() {
        this.focused = false;
        this.hoverButton = -1;
        this.stateLoaded = false;
        this.menu = null;
        this.row = 0;
        if (!this.keepSearch) {
            this.query = "";
            this.caret = 0;
        }
        this.anchor = this.caret;
    }

    boolean isSearchFocused() {
        return this.focused;
    }

    private void applyFilter() {
        this.items.clear();
        String raw = this.query.trim();
        boolean byMod = raw.startsWith("@");
        boolean byTag = raw.startsWith("#");
        boolean byNbt = !byMod && !byTag && raw.startsWith("$");
        String needle = byMod || byTag || byNbt ? raw.substring(1).toLowerCase(Locale.ROOT) : raw.toLowerCase(Locale.ROOT);
        Pattern pattern = needle.isEmpty() ? null : compile(needle);
        for (TerminalItemStack s : this.all) {
            if (pattern == null || matches(s.getStack(), pattern, byMod, byTag, byNbt)) {
                this.items.add(s);
            }
        }
        this.items.sort(comparator());
        this.clampRow();
    }

    private static Pattern compile(String needle) {
        try {
            return Pattern.compile(needle, Pattern.CASE_INSENSITIVE);
        } catch (Throwable broken) {
            try {
                return Pattern.compile(Pattern.quote(needle), Pattern.CASE_INSENSITIVE);
            } catch (Throwable brokenAgain) {
                return null;
            }
        }
    }

    private static boolean matches(ItemStack stack, Pattern pattern, boolean byMod, boolean byTag, boolean byNbt) {
        if (byMod) {
            return pattern.matcher(BuiltInRegistries.ITEM.getKey(stack.getItem()).getNamespace()).find();
        }
        if (byTag) {
            for (TagKey<Item> tag : stack.getTags().toList()) {
                if (pattern.matcher(tag.location().toString()).find()) {
                    return true;
                }
            }
            return false;
        }
        if (byNbt) {
            DataComponentPatch patch = stack.getComponentsPatch();
            return !patch.isEmpty() && pattern.matcher(patch.toString().toLowerCase(Locale.ROOT)).find();
        }
        if (pattern.matcher(stack.getHoverName().getString().toLowerCase(Locale.ROOT)).find()) {
            return true;
        }
        return pattern.matcher(BuiltInRegistries.ITEM.getKey(stack.getItem()).getPath()).find();
    }

    private Comparator<TerminalItemStack> comparator() {
        int type = Mth.clamp(this.sortType, 0, SortingTypes.VALUES.length - 1);
        return SortingTypes.VALUES[type].create(this.reversed);
    }

    void scroll(double delta) {
        if (delta > 0.0) {
            this.row--;
        } else if (delta < 0.0) {
            this.row++;
        }
        this.clampRow();
    }

    private int totalRows() {
        return (this.items.size() + COLS - 1) / COLS;
    }

    private int visibleRows() {
        return this.expand > 0.5 ? 4 : 1;
    }

    private void clampRow() {
        int max = Math.max(0, this.totalRows() - this.visibleRows());
        this.row = Mth.clamp(this.row, 0, max);
    }

    private void layout(int w, int h) {
        this.scale = Mth.clamp(h * 0.068f / 18.0f, 0.6f, 1.25f);
        this.panelW = Math.round(PANEL_W * this.scale);
        this.localH = BASE_H + (int)Math.round(this.expand * EXPAND_H);
        this.panelH = Math.round(this.localH * this.scale);
        this.panelX = (w - this.panelW) / 2;
        if (this.swapped) {
            // Crafting swap: the strip sits where the inventory panel was, kept clear above the inventory.
            this.panelY = Math.max(0, Math.min(this.swapTop, this.swapLimit - SWAP_GAP - this.panelH));
            this.panelBottom = this.panelY + this.panelH;
            return;
        }
        this.panelBottom = h - BOTTOM_GAP;
        this.panelY = this.panelBottom - this.panelH;
    }

    // Crafting only: top edge wanted for the strip, and the top edge of the inventory panel it must stay above.
    void swapTo(int top, int inventoryTop) {
        this.swapped = true;
        this.swapTop = top;
        this.swapLimit = inventoryTop;
    }

    void resetSwap() {
        this.swapped = false;
    }

    boolean over(double mx, double my) {
        if (!this.shown) {
            return false;
        }
        Minecraft mc = Minecraft.getInstance();
        this.layout(mc.getWindow().getGuiScaledWidth(), mc.getWindow().getGuiScaledHeight());
        return mx >= this.panelX - 4 && mx <= this.panelX + this.panelW + 4
                && my >= this.panelY - 4 && my <= this.panelBottom + 4;
    }

    void render(GuiGraphics g, Font font, float alpha) {
        Minecraft mc = Minecraft.getInstance();
        double[] m = Picking.mouseGui();
        boolean hover = this.over(m[0], m[1]);
        boolean open = hover || this.pinned || this.focused;
        this.expand = Anim.approach(this.expand, open ? 1.0 : 0.0, 13.0, Scene.frameDt);
        this.shown = alpha > 0.05f && Scene.phase == Scene.Phase.ACTIVE;
        this.clampRow();
        if (!this.shown) {
            this.hoverButton = -1;
            return;
        }
        int w = mc.getWindow().getGuiScaledWidth();
        int h = mc.getWindow().getGuiScaledHeight();
        this.layout(w, h);

        this.hoverButton = this.expand > 0.9 && hover ? this.buttonAt(m[0], m[1]) : -1;
        int hovIdx = hover && this.hoverButton < 0 && !this.overField(m[0], m[1]) ? this.cellIndex(m[0], m[1]) : -1;
        if (hovIdx != this.popIndex) {
            this.popIndex = hovIdx;
            this.pop = 0.0;
        }
        this.pop = Anim.approach(this.pop, hovIdx >= 0 ? 1.0 : 0.0, 16.0, Scene.frameDt);

        int bg = argb(0.46f * alpha, 12, 12, 16);
        int edge = argb(0.2f * alpha, 255, 255, 255);
        g.fill(this.panelX, this.panelY, this.panelX + this.panelW, this.panelY + this.panelH, bg);
        g.fill(this.panelX, this.panelY, this.panelX + this.panelW, this.panelY + 1, edge);
        g.fill(this.panelX, this.panelY + 1, this.panelX + 1, this.panelY + this.panelH, argb(0.08f * alpha, 255, 255, 255));
        g.fill(this.panelX + this.panelW - 1, this.panelY + 1, this.panelX + this.panelW, this.panelY + this.panelH, argb(0.08f * alpha, 255, 255, 255));

        g.enableScissor(this.panelX, Math.max(0, this.panelY), this.panelX + this.panelW, this.panelY + this.panelH);
        g.pose().pushPose();
        g.pose().translate((float)this.panelX, (float)this.panelY, 0.0f);
        g.pose().scale(this.scale, this.scale, 1.0f);

        int rowBase = this.localH - PAD - CELL;
        int gridTop = rowBase - 3 * CELL;
        if (this.expand > 0.02) {
            this.drawChrome(g, font, alpha);
        }
        int firstRowY = this.rowY(0, rowBase, gridTop);
        this.drawRow(g, font, 0, firstRowY, hovIdx, alpha);
        if (this.expand > 0.02) {
            float rows = (float)Anim.smoother(this.expand);
            int dividerY = firstRowY - 3;
            g.fill(7, dividerY, 165, dividerY + 1, argb(0.12f * alpha * rows, 255, 255, 255));
            for (int r = 1; r <= 3; ++r) {
                this.drawRow(g, font, r, this.rowY(r, rowBase, gridTop), hovIdx, alpha * rows);
            }
        } else {
            int gx = PANEL_W / 2;
            g.fill(gx - 9, firstRowY - 3, gx + 9, firstRowY - 2, argb(0.35f * alpha, 255, 255, 255));
        }

        if (this.items.isEmpty()) {
            Component empty = Component.translatable(this.all.isEmpty() ? "pipinha_cinematic_toms.strip.empty" : "pipinha_cinematic_toms.strip.no_match");
            g.drawString(font, empty, PANEL_W / 2 - font.width(empty) / 2, firstRowY + 5, argb(alpha, 216, 216, 216), false);
        }

        int totalRows = this.totalRows();
        int visible = this.visibleRows();
        if (totalRows > visible) {
            int trackTop = visible > 1 ? gridTop : rowBase;
            int trackH = rowBase + CELL - trackTop;
            g.fill(167, trackTop, 169, trackTop + trackH, argb(0.1f * alpha, 255, 255, 255));
            int thumbH = Math.max(6, trackH * visible / totalRows);
            double frac = (double)this.row / (double)(totalRows - visible);
            int thumbY = trackTop + (int)Math.round((trackH - thumbH) * frac);
            g.fill(167, thumbY, 169, thumbY + thumbH, argb(0.35f * alpha, 255, 255, 255));
        }

        g.pose().popPose();
        g.disableScissor();
    }

    private int chromeTop() {
        return this.localH - PAD - CELL - 58 - 4 - CHROME_H;
    }

    // Item 1 no topo esquerdo: as linhas são numeradas de cima para baixo.
    // Fechado sobra só a primeira linha, ancorada embaixo; ao abrir, as linhas
    // deslizam para cima até a posição final (gridTop + r * CELL).
    private int rowY(int r, int rowBase, int gridTop) {
        return rowBase + Math.round((gridTop - rowBase + r * CELL) * (float)this.expand);
    }

    private void drawChrome(GuiGraphics g, Font font, float alpha) {
        int top = this.chromeTop();
        int barY = top + TOOLBAR_Y;
        int plateX0 = PAD - 2;
        int plateX1 = PANEL_W - PAD + 2;
        g.fill(plateX0, barY - 2, plateX1, barY + BTN + 2, argb(0.9f * alpha, 51, 38, 33));
        g.fill(plateX0, barY - 2, plateX1, barY - 1, argb(0.9f * alpha, 92, 70, 58));
        g.fill(plateX0, barY + BTN + 1, plateX1, barY + BTN + 2, argb(0.9f * alpha, 30, 22, 19));
        for (int i = 0; i < BTN_COUNT; ++i) {
            int x = PAD + i * (BTN + BTN_GAP);
            if (i == this.hoverButton) {
                g.fill(x, barY, x + BTN, barY + BTN, argb(0.22f * alpha, 255, 255, 255));
            }
            this.drawButton(g, x, barY, i, alpha);
        }

        int fx = PAD;
        int fy = top + FIELD_Y;
        int border = this.focused ? argb(alpha, 235, 235, 235) : argb(alpha, 160, 160, 160);
        g.fill(fx - 1, fy - 1, fx + FIELD_W + 1, fy + FIELD_H + 1, border);
        g.fill(fx, fy, fx + FIELD_W, fy + FIELD_H, argb(alpha, 0, 0, 0));
        String text = this.query;
        boolean empty = text.isEmpty();
        int avail = FIELD_W - 8;
        if (empty && !this.focused) {
            Component hint = Component.translatable("pipinha_cinematic_toms.strip.search");
            g.drawString(font, hint, fx + 4, fy + 2, argb(0.55f * alpha, 255, 255, 255), false);
        } else {
            int caret = Mth.clamp(this.caret, 0, text.length());
            int start = 0;
            while (start < caret && font.width(text.substring(start, caret)) > avail) {
                start++;
            }
            String shown = font.plainSubstrByWidth(text.substring(start), avail);
            g.drawString(font, shown, fx + 4, fy + 2, argb(alpha, 255, 255, 255), false);
            int from = Mth.clamp(this.selStart(), start, start + shown.length());
            int to = Mth.clamp(this.selEnd(), start, start + shown.length());
            if (this.focused && from < to && alpha > 0.5f) {
                // Same inverted highlight as vanilla text fields.
                int x0 = fx + 4 + font.width(text.substring(start, from));
                int x1 = fx + 4 + font.width(text.substring(start, to));
                g.fill(RenderType.guiTextHighlight(), x0, fy + 1, x1, fy + FIELD_H - 1, 0xFF0000FF);
            }
            if (this.focused && this.blink()) {
                int before = Math.min(avail, font.width(text.substring(start, caret)));
                g.fill(fx + 4 + before, fy + 2, fx + 5 + before, fy + 10, argb(alpha, 220, 220, 220));
            }
        }
        int lineY = fy + FIELD_H + 3;
        g.fill(PAD, lineY, PANEL_W - PAD, lineY + 1, argb(0.10f * alpha, 255, 255, 255));
    }

    private boolean blink() {
        return (Scene.clock() - this.caretAt) % 1.0 < 0.5;
    }

    private void drawButton(GuiGraphics g, int x, int y, int id, float alpha) {
        ResourceLocation tex = switch (id) {
            case 0 -> switch (Mth.clamp(this.sortType, 0, 2)) {
                case 1 -> ICON_SORT_NAME;
                case 2 -> ICON_SORT_MOD;
                default -> ICON_SORT_AMOUNT;
            };
            case 1 -> this.reversed ? ICON_DESC : ICON_ASC;
            case 2 -> ICON_SEARCH;
            default -> this.pinned ? ICON_PIN_ON : ICON_PIN_OFF;
        };
        g.setColor(1.0f, 1.0f, 1.0f, alpha);
        g.blit(tex, x, y, 0, 0, BTN, BTN, BTN, BTN);
        if (id == 2 && this.keepSearch) {
            g.blit(ICON_SEARCH_KEEP, x + 1, y + 1, 0, 0, BTN - 2, BTN - 2, BTN - 2, BTN - 2);
        }
        g.setColor(1.0f, 1.0f, 1.0f, 1.0f);
    }

    private int buttonAt(double mx, double my) {
        if (this.expand < 0.9) {
            return -1;
        }
        double lx = (mx - this.panelX) / this.scale;
        double ly = (my - this.panelY) / this.scale;
        int barY = this.chromeTop() + TOOLBAR_Y;
        if (ly < barY || ly >= barY + BTN) {
            return -1;
        }
        for (int i = 0; i < BTN_COUNT; ++i) {
            int x = PAD + i * (BTN + BTN_GAP);
            if (lx >= x && lx < x + BTN) {
                return i;
            }
        }
        return -1;
    }

    private boolean overField(double mx, double my) {
        if (this.expand < 0.9) {
            return false;
        }
        double lx = (mx - this.panelX) / this.scale;
        double ly = (my - this.panelY) / this.scale;
        int fy = this.chromeTop() + FIELD_Y;
        return lx >= PAD && lx < PAD + FIELD_W && ly >= fy && ly < fy + FIELD_H;
    }

    boolean click(double mx, double my, int button, boolean shift) {
        if (!this.over(mx, my)) {
            return false;
        }
        if (this.expand < 0.9) {
            return true;
        }
        int id = this.buttonAt(mx, my);
        if (id >= 0) {
            if (button == 0) {
                this.press(id);
            }
            return true;
        }
        if (this.overField(mx, my)) {
            this.focused = true;
            this.caretAt = Scene.clock();
            if (button == 1) {
                this.setQuery("");
            } else {
                this.caret = this.caretIndexAt(mx);
                this.anchor = this.caret;
            }
            return true;
        }
        this.focused = false;
        return false;
    }

    void unfocus() {
        this.focused = false;
    }

    private int caretIndexAt(double mx) {
        double lx = (mx - this.panelX) / this.scale;
        Font font = Minecraft.getInstance().font;
        int start = PAD + 4;
        int best = this.query.length();
        double bestDistance = Double.MAX_VALUE;
        for (int i = 0; i <= this.query.length(); ++i) {
            double at = start + font.width(this.query.substring(0, i));
            double distance = Math.abs(at - lx);
            if (distance < bestDistance) {
                bestDistance = distance;
                best = i;
            }
        }
        return best;
    }

    private void press(int id) {
        switch (id) {
            case 0 -> this.sortType = (this.sortType + 1) % SortingTypes.VALUES.length;
            case 1 -> this.reversed = !this.reversed;
            case 2 -> this.keepSearch = !this.keepSearch;
            default -> this.pinned = !this.pinned;
        }
        if (id == 2) {
            keptQuery = this.keepSearch ? this.query : "";
        } else if (id != 3) {
            this.pushState();
        }
        this.applyFilter();
    }

    private void pushState() {
        if (this.menu == null) {
            return;
        }
        // Same layout as AbstractStorageTerminalScreen.sendUpdate: only the bits this strip
        // owns change, every other bit (ghost items, auto/sync search, control and tall mode)
        // is copied from the menu's current values.
        int sorting = (this.menu.sorting & ~0x1FF) | (this.sortType & 0xFF) | (this.reversed ? 0x100 : 0);
        int base = this.menu.searchType < 0 ? 0 : this.menu.searchType;
        int searchType = (base & ~2) | (this.keepSearch ? 2 : 0);
        CompoundTag data = new CompoundTag();
        data.putInt("s", sorting);
        data.putInt("st", searchType);
        data.putInt("m", this.menu.modes);
        CompoundTag msg = new CompoundTag();
        msg.put("c", data);
        this.menu.sendMessage(msg);
    }

    private void setQuery(String text) {
        this.query = text;
        this.caret = text.length();
        this.anchor = this.caret;
        this.caretAt = Scene.clock();
        if (this.keepSearch) {
            keptQuery = text;
        }
        this.row = 0;
        this.applyFilter();
    }

    boolean charTyped(char c, int modifiers) {
        if (!this.focused || (modifiers & 2) != 0) {
            return false;
        }
        int from = this.selStart();
        int to = this.selEnd();
        if (c < 32 || c == 127 || this.query.length() - (to - from) >= MAX_QUERY) {
            return false;
        }
        this.query = this.query.substring(0, from) + c + this.query.substring(to);
        this.caret = from + 1;
        this.anchor = this.caret;
        this.caretAt = Scene.clock();
        if (this.keepSearch) {
            keptQuery = this.query;
        }
        this.row = 0;
        this.applyFilter();
        return true;
    }

    boolean keyPressed(int key) {
        if (!this.focused) {
            return false;
        }
        int len = this.query.length();
        int at = Mth.clamp(this.caret, 0, len);
        int from = this.selStart();
        int to = this.selEnd();
        if (Screen.isSelectAll(key)) {
            this.anchor = 0;
            this.caret = len;
        } else {
            switch (key) {
                case 256, 257, 335 -> this.focused = false;
                case 259 -> {
                    if (from < to) {
                        this.edit(this.query.substring(0, from) + this.query.substring(to), from);
                    } else if (at > 0) {
                        this.edit(this.query.substring(0, at - 1) + this.query.substring(at), at - 1);
                    }
                }
                case 261 -> {
                    if (from < to) {
                        this.edit(this.query.substring(0, from) + this.query.substring(to), from);
                    } else if (at < len) {
                        this.edit(this.query.substring(0, at) + this.query.substring(at + 1), at);
                    }
                }
                case 263 -> this.moveCaret(from < to ? from : Math.max(0, at - 1));
                case 262 -> this.moveCaret(from < to ? to : Math.min(len, at + 1));
                case 268 -> this.moveCaret(0);
                case 269 -> this.moveCaret(len);
                default -> {
                }
            }
        }
        this.caretAt = Scene.clock();
        return true;
    }

    private int selStart() {
        return Mth.clamp(Math.min(this.anchor, this.caret), 0, this.query.length());
    }

    private int selEnd() {
        return Mth.clamp(Math.max(this.anchor, this.caret), 0, this.query.length());
    }

    private void moveCaret(int at) {
        this.caret = at;
        this.anchor = at;
    }

    private void edit(String text, int at) {
        this.setQuery(text);
        this.moveCaret(at);
    }

    private void drawRow(GuiGraphics g, Font font, int r, int y, int hovIdx, float alpha) {
        for (int col = 0; col < COLS; ++col) {
            int x = PAD + col * CELL;
            int index = (this.row + r) * COLS + col;
            this.drawCell(g, font, index, x, y, hovIdx == index, alpha);
        }
    }

    private void drawCell(GuiGraphics g, Font font, int index, int x, int y, boolean hovered, float alpha) {
        g.fill(x + 1, y + 1, x + CELL - 1, y + CELL - 1, argb(0.13f * alpha, 255, 255, 255));
        if (hovered) {
            g.fill(x + 1, y + 1, x + CELL - 1, y + CELL - 1, argb(0.35f * alpha, 255, 255, 255));
        }
        if (index < 0 || index >= this.items.size() || alpha <= 0.35f) {
            return;
        }
        TerminalItemStack s = this.items.get(index);
        ItemStack stack = s.getStack();
        float cx = x + 9.0f;
        float cy = y + 9.0f;
        g.pose().pushPose();
        if (hovered) {
            float k = 1.0f + 0.25f * (float)Anim.smoother(this.pop);
            g.pose().translate(cx, cy, 50.0f);
            g.pose().scale(k, k, 1.0f);
            g.pose().translate(-cx, -cy, 0.0f);
        }
        g.renderItem(stack, x + 1, y + 1);
        g.renderItemDecorations(font, stack, x + 1, y + 1, "");
        g.pose().popPose();

        long q = s.getQuantity();
        if (q != 1) {
            String text = compact(q);
            int w = font.width(text);
            float f = w > 16 ? 0.7f : 1.0f;
            g.pose().pushPose();
            g.pose().translate(x + 17.0f, y + 9.0f, 200.0f);
            g.pose().scale(f, f, 1.0f);
            g.drawString(font, text, -w, 0, argb(alpha, 255, 255, 255), true);
            g.pose().popPose();
        }
    }

    private int cellIndex(double mx, double my) {
        if (this.expand < 0.9) {
            return -1;
        }
        double lx = (mx - this.panelX) / this.scale;
        double ly = (my - this.panelY) / this.scale;
        int rowBase = this.localH - PAD - CELL;
        int gridTop = rowBase - 3 * CELL;
        int col = (int)Math.floor((lx - PAD) / CELL);
        if (lx < PAD || col < 0 || col >= COLS) {
            return -1;
        }
        int visible = this.expand > 0.9 ? 4 : 1;
        for (int r = 0; r < visible; ++r) {
            int y = this.rowY(r, rowBase, gridTop);
            if (ly >= y && ly < y + CELL) {
                int index = (this.row + r) * COLS + col;
                return index < this.items.size() ? index : -1;
            }
        }
        return -1;
    }

    TerminalItemStack hit(double mx, double my) {
        if (!this.over(mx, my)) {
            return null;
        }
        int index = this.cellIndex(mx, my);
        return index < 0 ? null : this.items.get(index);
    }

    void renderTooltip(GuiGraphics g, Font font, int mx, int my, ItemStack carried) {
        int id = this.buttonAt(mx, my);
        if (id >= 0) {
            g.renderComponentTooltip(font, List.of(this.buttonTooltip(id)), mx, my);
            return;
        }
        if (!carried.isEmpty()) {
            return;
        }
        TerminalItemStack s = this.hit(mx, my);
        if (s == null) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        List<Component> lines = new ArrayList<>(Screen.getTooltipFromItem(mc, s.getStack()));
        lines.add(Component.translatable("pipinha_cinematic_toms.strip.count", String.format("%,d", s.getQuantity()))
                .withStyle(ChatFormatting.GRAY));
        g.renderComponentTooltip(font, lines, mx, my);
    }

    private Component buttonTooltip(int id) {
        return switch (id) {
            case 0 -> Component.translatable("pipinha_cinematic_toms.strip.sort_" + Mth.clamp(this.sortType, 0, 2));
            case 1 -> Component.translatable(this.reversed ? "pipinha_cinematic_toms.strip.order_desc" : "pipinha_cinematic_toms.strip.order_asc");
            case 2 -> Component.translatable(this.keepSearch ? "pipinha_cinematic_toms.strip.search_keep" : "pipinha_cinematic_toms.strip.search_plain");
            default -> Component.translatable(this.pinned ? "pipinha_cinematic_toms.strip.pin_on" : "pipinha_cinematic_toms.strip.pin_off");
        };
    }

    private static String compact(long q) {
        if (q < 1000) {
            return Long.toString(q);
        }
        String[] units = {"", "k", "M", "B"};
        double v = q;
        int u = 0;
        while (v >= 1000.0 && u < 3) {
            v /= 1000.0;
            u++;
        }
        String num;
        if (v >= 10.0) {
            num = Long.toString(Math.round(v));
        } else {
            num = String.format(Locale.ROOT, "%.1f", v);
            if (num.endsWith(".0")) {
                num = num.substring(0, num.length() - 2);
            }
        }
        return num + units[u];
    }

    private static int argb(float a, int r, int g, int b) {
        int alpha = Mth.clamp(Math.round(a * 255.0f), 0, 255);
        return alpha << 24 | r << 16 | g << 8 | b;
    }
}
