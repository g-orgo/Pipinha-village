package com.pipinha.cinematictoms.mixin;

import dev.dyslexic.cinematic.client.SceneScreen;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(value = SceneScreen.class, remap = false)
public interface SceneScreenAccessor {
    @Invoker("hoveredPanelItem")
    ItemStack cinematicToms$hoveredPanelItem();

    @Accessor("panelX")
    int cinematicToms$getPanelX();

    @Accessor("panelW")
    int cinematicToms$getPanelW();

    @Accessor("panelY")
    int cinematicToms$getPanelY();

    @Accessor("panelY")
    void cinematicToms$setPanelY(int y);

    @Accessor("panelH")
    int cinematicToms$getPanelH();

    @Accessor("field")
    EditBox cinematicToms$getField();
}
