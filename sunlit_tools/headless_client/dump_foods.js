// Temporary inventory dump: copy into kubejs/startup_scripts of the scratch copy only.
// Lines go to logs/kubejs/startup.log; strip the prefix and save as sunlit_tools/eating/foods_dump.txt.
StartupEvents.postInit(() => {
  var reg = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
  var it = reg.ITEMS.getEntries().iterator()
  while (it.hasNext()) {
    var e = it.next()
    var item = e.getValue()
    var st = item.getDefaultInstance()
    var ua = String(st.getUseAnimation())
    if (item.isEdible() || ua == 'DRINK' || ua == 'EAT') {
      var food = item.getFoodProperties()
      var rem = item.getCraftingRemainingItem()
      console.log('FOODDUMP|' + e.getKey().location() + '|' + item.isEdible() + '|' + ua + '|' + st.getUseDuration() + '|' + (food ? food.getNutrition() : -1) + '|' + (food ? food.isFastFood() : false) + '|' + item.getClass().getName() + '|' + (rem ? String(reg.ITEMS.getKey(rem)) : ''))
    }
  }
})
