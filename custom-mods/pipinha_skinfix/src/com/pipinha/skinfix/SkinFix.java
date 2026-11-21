package com.pipinha.skinfix;

import java.util.UUID;

import com.mojang.authlib.minecraft.MinecraftSessionService;
import com.mojang.authlib.yggdrasil.ProfileResult;
import com.mojang.logging.LogUtils;
import net.neoforged.fml.common.Mod;
import org.slf4j.Logger;

/**
 * Vanilla 1.21.1 fetches the local player's profile (the one carrying the skin "textures" property) exactly
 * once, at startup, into Minecraft.profileFuture. When the session server answers with an error (Mojang
 * "Service unavailable" pages were seen in the logs), authlib returns null and the whole session runs with a
 * profile without textures, so the player is drawn with a default skin until the game is restarted.
 * This retries that single startup request a few times with backoff. It runs on the background IO pool and
 * the result is only awaited when the initial screens are built, after resource loading, so the retries do
 * not delay the loading screen.
 */
@Mod("pipinha_skinfix")
public class SkinFix {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final long[] RETRY_DELAYS_MS = {2_000L, 4_000L, 8_000L, 15_000L, 15_000L};

    public static ProfileResult fetchWithRetry(MinecraftSessionService service, UUID id, boolean requireSecure) {
        ProfileResult result = service.fetchProfile(id, requireSecure);
        for (int attempt = 0; result == null && attempt < RETRY_DELAYS_MS.length; attempt++) {
            LOGGER.info("[pipinha_skinfix] Player profile lookup failed, retrying in {} ms (attempt {}/{})",
                    RETRY_DELAYS_MS[attempt], attempt + 1, RETRY_DELAYS_MS.length);
            try {
                Thread.sleep(RETRY_DELAYS_MS[attempt]);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return null;
            }
            result = service.fetchProfile(id, requireSecure);
            if (result != null) {
                LOGGER.info("[pipinha_skinfix] Player profile loaded on retry {}, skin will be shown", attempt + 1);
            }
        }
        if (result == null) {
            LOGGER.warn("[pipinha_skinfix] Player profile still unavailable after {} retries, using the default skin this session",
                    RETRY_DELAYS_MS.length);
        }
        return result;
    }
}
