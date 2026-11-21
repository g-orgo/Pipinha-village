package com.pipinha.cinematictoms;

import com.tom.storagemod.block.AbstractStorageTerminalBlock;
import com.tom.storagemod.menu.CraftingTerminalMenu;
import com.tom.storagemod.menu.StorageTerminalMenu;
import dev.dyslexic.cinematic.api.AddonStations;
import java.util.List;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;

@Mod(CinematicToms.MOD_ID)
public final class CinematicToms {
    public static final String MOD_ID = "pipinha_cinematic_toms";

    public static final ResourceLocation STORAGE_TERMINAL = ResourceLocation.fromNamespaceAndPath(MOD_ID, "storage_terminal");
    public static final ResourceLocation CRAFTING_TERMINAL = ResourceLocation.fromNamespaceAndPath(MOD_ID, "crafting_terminal");

    public CinematicToms(IEventBus modBus) {
        modBus.addListener(this::commonSetup);
    }

    private void commonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            AddonStations.register(new AddonStations.Definition(
                    STORAGE_TERMINAL,
                    ResourceLocation.fromNamespaceAndPath("toms_storage", "storage_terminal"),
                    StorageTerminalMenu.class,
                    state -> List.of(state.getValue(AbstractStorageTerminalBlock.FACING).getOpposite())));
            AddonStations.register(new AddonStations.Definition(
                    CRAFTING_TERMINAL,
                    ResourceLocation.fromNamespaceAndPath("toms_storage", "crafting_terminal"),
                    CraftingTerminalMenu.class,
                    state -> List.of(state.getValue(AbstractStorageTerminalBlock.FACING).getOpposite())));
        });
    }
}
