package com.pipinha.cinematictoms.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.tom.storagemod.menu.CraftingTerminalMenu;
import com.tom.storagemod.menu.CraftingTerminalMenu.SlotCrafting;
import dev.dyslexic.cinematic.client.Fx;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;

final class TerminalGrid {
    static final int SIZE = 3;
    static final double CELL = 0.125;
    static final double GRID_X = -0.047;
    static final double GRID_Y = 0.03;
    static final double RESULT_X = 0.23;
    static final double RESULT_Y = GRID_Y;
    static final double LIFT = 0.02;
    static final double ITEM_SIZE = 0.1;
    static final double BLOCK_SIZE = 0.08;
    static final double RESULT_SCALE = 1.25;

    private TerminalGrid() {
    }

    static List<Slot> grid(CraftingTerminalMenu menu) {
        List<Slot> out = new ArrayList<>();
        for (Slot s : menu.slots) {
            if (s instanceof SlotCrafting) {
                out.add(s);
            }
        }
        return out;
    }

    static int cellAt(double u, double v) {
        double gx = (u - GRID_X) / CELL + 1.5;
        double gy = (GRID_Y - v) / CELL + 1.5;
        int c = (int)Math.floor(gx);
        int r = (int)Math.floor(gy);
        if (c < 0 || c >= SIZE || r < 0 || r >= SIZE) {
            return -1;
        }
        return r * SIZE + c;
    }

    static double cellU(int i) {
        return GRID_X + (i % SIZE - 1) * CELL;
    }

    static double cellV(int i) {
        return GRID_Y - (i / SIZE - 1) * CELL;
    }

    static boolean resultAt(double u, double v) {
        return Math.abs(u - RESULT_X) <= CELL * 0.6 && Math.abs(v - RESULT_Y) <= CELL * 0.6;
    }

    static Vec3 point(Vec3 face, Vec3 right, Vec3 up, double x, double y) {
        return face.add(right.scale(x)).add(up.scale(y));
    }

    static void highlight(PoseStack pose, MultiBufferSource buffers, Vec3 right, Vec3 up, double x, double y, double half) {
        Matrix4f m = pose.last().pose();
        VertexConsumer quads = buffers.getBuffer(Fx.HIGHLIGHT);
        fill(quads, m, right, up, x - half, y - half, x + half, y + half, 255, 244, 214, 47);
        double w = 0.004;
        fill(quads, m, right, up, x - half, y + half - w, x + half, y + half, 255, 235, 185, 150);
        fill(quads, m, right, up, x - half, y - half, x + half, y - half + w, 255, 235, 185, 150);
        fill(quads, m, right, up, x - half, y - half, x - half + w, y + half, 255, 235, 185, 150);
        fill(quads, m, right, up, x + half - w, y - half, x + half, y + half, 255, 235, 185, 150);
    }

    private static void fill(VertexConsumer quads, Matrix4f m, Vec3 right, Vec3 up, double x0, double y0, double x1, double y1, int r, int g, int b, int a) {
        vertex(quads, m, right, up, x0, y0, r, g, b, a);
        vertex(quads, m, right, up, x0, y1, r, g, b, a);
        vertex(quads, m, right, up, x1, y1, r, g, b, a);
        vertex(quads, m, right, up, x1, y0, r, g, b, a);
    }

    private static void vertex(VertexConsumer quads, Matrix4f m, Vec3 right, Vec3 up, double x, double y, int r, int g, int b, int a) {
        Vec3 p = right.scale(x).add(up.scale(y));
        quads.addVertex(m, (float)p.x, (float)p.y, (float)p.z).setColor(r, g, b, a);
    }
}
