package com.sunlit.hangdump;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Map;

import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerAboutToStartEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Diagnostic only: when the server thread goes STALL_MS without finishing a tick (stuck loading or
 * generating), writes the stack of every thread to logs/sunlit-hangdump-<time>.txt. The game itself is
 * never touched; a dump is the only side effect.
 */
@Mod("sunlit_hangdump")
public class HangDump {
    private static final Logger LOG = LoggerFactory.getLogger("sunlit_hangdump");
    private static final long STALL_MS = 90_000L;
    private static final long REPEAT_MS = 120_000L;
    private static final int MAX_DUMPS = 5;

    private static volatile boolean active;
    private static volatile long lastBeat;
    private static volatile long lastDump;
    private static volatile int dumps;

    public HangDump() {
        MinecraftForge.EVENT_BUS.addListener(EventPriority.LOWEST, false, ServerAboutToStartEvent.class, e -> {
            lastBeat = System.currentTimeMillis();
            lastDump = 0L;
            dumps = 0;
            active = true;
        });
        MinecraftForge.EVENT_BUS.addListener(EventPriority.LOWEST, false, TickEvent.ServerTickEvent.class, e -> {
            if (e.phase == TickEvent.Phase.END) lastBeat = System.currentTimeMillis();
        });
        MinecraftForge.EVENT_BUS.addListener(EventPriority.LOWEST, false, ServerStoppedEvent.class, e -> active = false);
        Thread watcher = new Thread(HangDump::watch, "Sunlit-HangDump");
        watcher.setDaemon(true);
        watcher.start();
    }

    private static void watch() {
        while (true) {
            try {
                Thread.sleep(5_000L);
                long now = System.currentTimeMillis();
                if (!active || dumps >= MAX_DUMPS || now - lastBeat < STALL_MS) continue;
                if (lastDump != 0L && now - lastDump < REPEAT_MS) continue;
                lastDump = now;
                dumps++;
                write(now - lastBeat);
            } catch (InterruptedException e) {
                return;
            } catch (Throwable t) {
                LOG.warn("hang dump failed", t);
            }
        }
    }

    private static void write(long stalledMs) throws IOException {
        StringBuilder sb = new StringBuilder();
        sb.append("Server thread without a finished tick for ").append(stalledMs / 1000).append(" s\n\n");
        for (Map.Entry<Thread, StackTraceElement[]> en : Thread.getAllStackTraces().entrySet()) {
            Thread t = en.getKey();
            sb.append('"').append(t.getName()).append("\" ").append(t.getState()).append('\n');
            StackTraceElement[] st = en.getValue();
            if (st.length <= 100) {
                for (StackTraceElement e : st) sb.append("    at ").append(e).append('\n');
            } else {
                for (int i = 0; i < 30; i++) sb.append("    at ").append(st[i]).append('\n');
                sb.append("    ... ").append(st.length - 100).append(" frames omitted\n");
                for (int i = st.length - 70; i < st.length; i++) sb.append("    at ").append(st[i]).append('\n');
            }
            sb.append('\n');
        }
        String stamp = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss").format(new Date());
        Path out = FMLPaths.GAMEDIR.get().resolve("logs").resolve("sunlit-hangdump-" + stamp + ".txt");
        Files.writeString(out, sb.toString(), StandardCharsets.UTF_8);
        LOG.warn("server stalled for {} s, thread dump written to {}", stalledMs / 1000, out);
    }
}
