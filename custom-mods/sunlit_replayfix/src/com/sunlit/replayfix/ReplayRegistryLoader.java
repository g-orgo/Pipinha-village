package com.sunlit.replayfix;

import com.google.common.collect.Multimap;
import com.replaymod.replaystudio.replay.ReplayFile;
import com.replaymod.replaystudio.replay.ReplayMetaData;
import java.io.File;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.registries.ForgeRegistry;
import net.minecraftforge.registries.GameData;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

// Every world stores its own numeric registry IDs in level.dat, and Forge only sends them
// over the network to remote clients. A recording made in singleplayer therefore has no IDs
// inside it, and the replay used to decode its packets with the default IDs of the game,
// turning blocks and entities into other ones. This loads the IDs from the recorded world,
// the same way Forge does when that world is opened. The save is only read, never written.
public final class ReplayRegistryLoader {
    private static final Logger LOGGER = LogManager.getLogger("sunlit_replayfix");

    private static boolean loaded;

    private ReplayRegistryLoader() {
    }

    public static void loadFor(ReplayFile replayFile) {
        try {
            ReplayMetaData metaData = replayFile.getMetaData();
            if (!metaData.isSingleplayer()) {
                return;
            }
            String worldName = metaData.getServerName();
            File levelDat = findLevelDat(worldName);
            if (levelDat == null) {
                LOGGER.warn("World '{}' of this replay was not found in saves, keeping default IDs", worldName);
                return;
            }
            CompoundTag registries = NbtIo.m_128937_(levelDat).m_128469_("fml").m_128469_("Registries");
            if (registries.m_128431_().isEmpty()) {
                LOGGER.warn("{} has no registry data, keeping default IDs", levelDat);
                return;
            }
            Map<ResourceLocation, ForgeRegistry.Snapshot> snapshot = new HashMap<>();
            for (String key : registries.m_128431_()) {
                snapshot.put(new ResourceLocation(key), ForgeRegistry.Snapshot.read(registries.m_128469_(key)));
            }
            Multimap<ResourceLocation, ResourceLocation> failed = GameData.injectSnapshot(snapshot, true, true);
            loaded = true;
            LOGGER.info("Loaded {} registries from {} ({} entries failed)", snapshot.size(), levelDat, failed.size());
        } catch (Exception exception) {
            LOGGER.error("Could not load the world registries for this replay", exception);
        }
    }

    public static void restore() {
        if (loaded) {
            loaded = false;
            GameData.revertToFrozen();
            LOGGER.info("Registries restored after closing the replay");
        }
    }

    // The recording stores the level name, which is usually also the folder name.
    private static File findLevelDat(String worldName) {
        File saves = new File(Minecraft.m_91087_().f_91069_, "saves");
        File direct = new File(new File(saves, worldName), "level.dat");
        if (direct.isFile()) {
            return direct;
        }
        File newest = null;
        File[] folders = saves.listFiles(File::isDirectory);
        if (folders == null) {
            return null;
        }
        for (File folder : folders) {
            File candidate = new File(folder, "level.dat");
            if (candidate.isFile() && worldName.equals(readLevelName(candidate))
                    && (newest == null || candidate.lastModified() > newest.lastModified())) {
                newest = candidate;
            }
        }
        return newest;
    }

    private static String readLevelName(File levelDat) {
        try {
            return NbtIo.m_128937_(levelDat).m_128469_("Data").m_128461_("LevelName");
        } catch (Exception exception) {
            return null;
        }
    }
}
