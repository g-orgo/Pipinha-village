package com.pipinha.eating;

import java.util.Locale;

// Picks the third person pose of a food from data alone, so it covers every food of the pack,
// including items added later, without a per item table. Has no Minecraft dependency on purpose:
// pipinha_tools runs it over the item inventory.
public enum FoodPose {
    HAND, PLATE, BOWL, SKEWER, SLICE, BOTTLE, CUP;

    private static final String[] BOTTLES = {"bottle", "wine", "sake", "champagne", "vodka", "whisky", "whiskey"};
    private static final String[] PLATES = {"plate", "platter", "saucer", "small_iron_pot", "feast", "dish", "sashimi"};
    // No "chili" here: raw peppers (red_chili, green_chili) share the word, and every chili dish
    // already gets BOWL from its bowl remainder.
    private static final String[] BOWLS = {"bowl", "soup", "stew", "porridge", "congee", "curry", "ramen",
            "noodle", "salad", "broth", "pudding", "gruel"};
    private static final String[] SKEWERS = {"skewer", "kebab", "kabob", "popsicle", "on_a_stick", "lollipop", "candy_apple",
            "corn_dog", "_stick", "barbecue"};
    private static final String[] SLICES = {"slice", "wedge", "piece", "cookie", "cracker", "biscuit", "wafer", "sliced"};

    // path: item path without namespace. remainder: id of the item left behind, or empty.
    public static FoodPose classify(String path, String remainder, boolean drink, boolean bowlClass) {
        String p = path.toLowerCase(Locale.ROOT);
        String r = remainder == null ? "" : remainder.toLowerCase(Locale.ROOT);
        if (drink) {
            return r.contains("bottle") || has(p, BOTTLES) ? BOTTLE : CUP;
        }
        if (has(r, PLATES)) {
            return PLATE;
        }
        if (r.contains("stick") || r.contains("bamboo")) {
            return SKEWER;
        }
        if (bowlClass || r.contains("bowl") || r.contains("cup") || r.contains("jar") || r.contains("can")
                || r.contains("bucket") || r.contains("tankard") || r.contains("shell") || r.contains("bottle")) {
            return BOWL;
        }
        if (has(p, SKEWERS)) {
            return SKEWER;
        }
        if (has(p, SLICES)) {
            return SLICE;
        }
        if (has(p, PLATES)) {
            return PLATE;
        }
        if (has(p, BOWLS)) {
            return BOWL;
        }
        return HAND;
    }

    public boolean isDrink() {
        return this == BOTTLE || this == CUP;
    }

    public String animationName() {
        return name().toLowerCase(Locale.ROOT);
    }

    private static boolean has(String text, String[] needles) {
        for (String needle : needles) {
            if (text.contains(needle)) {
                return true;
            }
        }
        return false;
    }
}
