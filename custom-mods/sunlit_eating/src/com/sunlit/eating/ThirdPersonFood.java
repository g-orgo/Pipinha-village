package com.sunlit.eating;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import java.io.Reader;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.joml.Vector4f;
import org.toame.food.additions.definiton.FoodDefinition;
import org.toame.food.additions.definiton.FoodDefinitionManager;
import software.bernie.geckolib.cache.GeckoLibCache;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.cache.object.GeoCube;
import software.bernie.geckolib.cache.object.GeoQuad;
import software.bernie.geckolib.cache.object.GeoVertex;
import software.bernie.geckolib.core.state.BoneSnapshot;
import software.bernie.geckolib.util.RenderUtils;

// Draws the Immersive Eating model of a food in the hand while it is eaten in third person. Bites
// follow the item use progress, using the moments the first person animation scales a bone to zero.
final class ThirdPersonFood {
    private static final float FOOD_SIZE = 0.42F;
    private static final float VESSEL_SIZE = 0.38F;
    // Bowls, plates and cups lean over, so what is inside them, and the bites, can be seen.
    private static final float VESSEL_TILT = (float) Math.toRadians(35.0);
    private static final Set<String> NOT_FOOD = Set.of("utensil", "utensil_part", "morsel", "kuaizi", "kuaizi_right",
            "kuazi_left", "K1", "chopsticks", "tableware", "leftArm", "rightArm", "camera", "carmera");
    private static final Map<String, Entry> ENTRIES = new HashMap<>();
    private static final Map<String, FoodDefinition> DEFINITIONS = new HashMap<>();
    private static int definitionCount = -1;

    private ThirdPersonFood() {
    }

    private interface CubeSink {
        void accept(PoseStack pose, GeoCube cube);
    }

    private static final class Entry {
        BakedGeoModel model;
        GeoBone root;
        ResourceLocation texture;
        Set<String> hidden = Set.of();
        // Hand foods built upright for first person (bone "orient"): held at the grip, standing up from the fist.
        boolean upright;
        // Bowl and plate tilt on the root is first person staging; third person keeps its own VESSEL_TILT.
        boolean skipRootRotation;
        final Map<String, Float> vanish = new HashMap<>();
        final float[] min = {Float.MAX_VALUE, Float.MAX_VALUE, Float.MAX_VALUE};
        final float[] max = {-Float.MAX_VALUE, -Float.MAX_VALUE, -Float.MAX_VALUE};
    }

    static boolean render(LivingEntity entity, ItemStack stack, ItemDisplayContext context, PoseStack pose,
            MultiBufferSource buffers, int light) {
        boolean thirdPerson = context == ItemDisplayContext.THIRD_PERSON_LEFT_HAND
                || context == ItemDisplayContext.THIRD_PERSON_RIGHT_HAND;
        if (!thirdPerson || !entity.m_6117_() || entity.m_21120_(entity.m_7655_()) != stack) {
            return false;
        }
        UseAnim animation = stack.m_41780_();
        Entry entry = animation == UseAnim.EAT || animation == UseAnim.DRINK ? entry(stack) : null;
        if (entry == null || entry.root == null) {
            return false;
        }
        float partial = Minecraft.m_91087_().m_91296_();
        float progress = 1.0F - (entity.m_21212_() - partial) / Math.max(1, stack.m_41779_());
        float width = entry.max[0] - entry.min[0];
        float height = entry.max[1] - entry.min[1];
        float depth = entry.max[2] - entry.min[2];
        boolean vessel = height < 1.3F * width && depth >= 0.5F * width;
        float scale = (vessel ? VESSEL_SIZE : FOOD_SIZE) / Math.max(Math.max(width, height), Math.max(depth, 0.01F));
        VertexConsumer buffer = buffers.m_6299_(RenderType.m_110470_(entry.texture));
        pose.m_85836_();
        pose.m_252781_(new Quaternionf().rotationX((float) (Math.PI / 2.0)));
        if (vessel) {
            pose.m_252781_(new Quaternionf().rotationX(VESSEL_TILT));
        }
        pose.m_85841_(scale, scale, scale);
        if (entry.upright) {
            // The root pivot is the hand, where the grip pixel of the food sits.
            pose.m_252880_(-entry.root.getPivotX() / 16.0F, -entry.root.getPivotY() / 16.0F, -entry.root.getPivotZ() / 16.0F);
        } else pose.m_252880_(-(entry.min[0] + entry.max[0]) / 2.0F, -(entry.min[1] + entry.max[1]) / 2.0F,
                -(entry.min[2] + entry.max[2]) / 2.0F);
        walk(entry.root, entry, progress, pose, (matrices, cube) -> emit(matrices, cube, buffer, light));
        pose.m_85849_();
        return true;
    }

    private static Entry entry(ItemStack stack) {
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.m_41720_());
        if (id == null) {
            return null;
        }
        List<FoodDefinition> list = FoodDefinitionManager.list;
        if (definitionCount != list.size()) {
            DEFINITIONS.clear();
            list.forEach(definition -> DEFINITIONS.put(definition.getItem(), definition));
            definitionCount = list.size();
        }
        String key = id.toString();
        FoodDefinition definition = DEFINITIONS.get(key);
        if (definition == null) {
            return null;
        }
        Map<ResourceLocation, BakedGeoModel> models = GeckoLibCache.getBakedModels();
        String stem = id.m_135815_() + "__" + id.m_135827_();
        BakedGeoModel model = models.get(new ResourceLocation("food", "geo/" + stem + ".geo.json"));
        if (model == null) {
            stem = id.m_135815_();
            model = models.get(new ResourceLocation("food", "geo/" + stem + ".geo.json"));
        }
        Entry cached = ENTRIES.get(key);
        if (cached != null && cached.model == model) {
            return cached;
        }
        Entry entry = build(model, stem, definition);
        ENTRIES.put(key, entry);
        return entry;
    }

    private static Entry build(BakedGeoModel model, String stem, FoodDefinition definition) {
        Entry entry = new Entry();
        entry.model = model;
        if (model == null) {
            return entry;
        }
        entry.root = model.getBone("food").or(() -> model.getBone("golden_salad")).orElse(null);
        entry.upright = entry.root != null && model.getBone("orient").isPresent();
        entry.skipRootRotation = entry.root != null && model.getBone("vessel").isPresent()
                && entry.root.getInitialSnapshot() != null
                && Math.abs(entry.root.getInitialSnapshot().getRotX()) < Math.toRadians(45.0);
        entry.texture = new ResourceLocation("food", "textures/item/" + stem + ".png");
        if (definition.getInvisible() != null) {
            entry.hidden = Set.copyOf(definition.getInvisible());
        }
        readVanish(entry, new ResourceLocation("food", "animations/" + stem + ".animation.json"));
        if (entry.root != null) {
            walk(entry.root, entry, -1.0F, new PoseStack(), (pose, cube) -> grow(entry, pose, cube));
        }
        return entry;
    }

    private static void readVanish(Entry entry, ResourceLocation location) {
        try (Reader reader = Minecraft.m_91087_().m_91098_().m_215597_(location)) {
            JsonObject animations = JsonParser.parseReader(reader).getAsJsonObject().getAsJsonObject("animations");
            JsonObject animation = animations.has("eat") ? animations.getAsJsonObject("eat")
                    : animations.entrySet().iterator().next().getValue().getAsJsonObject();
            float length = animation.get("animation_length").getAsFloat();
            for (Map.Entry<String, JsonElement> bone : animation.getAsJsonObject("bones").entrySet()) {
                JsonElement scale = bone.getValue().getAsJsonObject().get("scale");
                if (scale != null && scale.isJsonObject()) {
                    Float time = vanishTime(scale.getAsJsonObject());
                    if (time != null && length > 0.0F) {
                        entry.vanish.put(bone.getKey(), time / length);
                    }
                }
            }
        } catch (Exception ignored) {
            // A model without a readable animation is still drawn, just without bites.
        }
    }

    // Start of the trailing run of zero keyframes, if the bone was visible before it.
    private static Float vanishTime(JsonObject keyframes) {
        TreeMap<Float, Boolean> zeros = new TreeMap<>();
        for (Map.Entry<String, JsonElement> keyframe : keyframes.entrySet()) {
            try {
                zeros.put(Float.parseFloat(keyframe.getKey()), isZero(keyframe.getValue()));
            } catch (NumberFormatException notKeyframed) {
                return null;
            }
        }
        Float start = null;
        for (Map.Entry<Float, Boolean> keyframe : zeros.entrySet()) {
            start = !keyframe.getValue() ? null : start == null ? keyframe.getKey() : start;
        }
        return start == null || start.equals(zeros.firstKey()) ? null : start;
    }

    private static boolean isZero(JsonElement value) {
        if (value.isJsonArray()) {
            for (JsonElement component : value.getAsJsonArray()) {
                if (!isZero(component)) {
                    return false;
                }
            }
            return true;
        }
        if (value.isJsonObject()) {
            JsonObject object = value.getAsJsonObject();
            JsonElement inner = object.has("post") ? object.get("post") : object.get("vector");
            return inner != null && isZero(inner);
        }
        return value.isJsonPrimitive() && value.getAsJsonPrimitive().isNumber() && Math.abs(value.getAsFloat()) < 0.01F;
    }

    private static void walk(GeoBone bone, Entry entry, float progress, PoseStack pose, CubeSink sink) {
        String name = bone.getName();
        Float vanish = entry.vanish.get(name);
        if (NOT_FOOD.contains(name) || entry.hidden.contains(name) || (vanish != null && vanish <= progress)) {
            return;
        }
        // Baked bones are shared with the first person renderer, which leaves its pose on them.
        BoneSnapshot rest = bone.getInitialSnapshot();
        pose.m_85836_();
        RenderUtils.translateToPivotPoint(pose, bone);
        if (!(bone == entry.root && entry.skipRootRotation)) {
            pose.m_252781_(new Quaternionf().rotationZYX(rest != null ? rest.getRotZ() : bone.getRotZ(),
                    rest != null ? rest.getRotY() : bone.getRotY(), rest != null ? rest.getRotX() : bone.getRotX()));
        }
        if (entry.upright && "orient".equals(name)) {
            // In the third person item pose the first person "up" of these foods points down: turn it in its own plane.
            pose.m_252781_(new Quaternionf().rotationZ((float) Math.PI));
        }
        RenderUtils.translateAwayFromPivotPoint(pose, bone);
        for (GeoCube cube : bone.getCubes()) {
            pose.m_85836_();
            RenderUtils.translateToPivotPoint(pose, cube);
            RenderUtils.rotateMatrixAroundCube(pose, cube);
            RenderUtils.translateAwayFromPivotPoint(pose, cube);
            sink.accept(pose, cube);
            pose.m_85849_();
        }
        for (GeoBone child : bone.getChildBones()) {
            walk(child, entry, progress, pose, sink);
        }
        pose.m_85849_();
    }

    private static void grow(Entry entry, PoseStack pose, GeoCube cube) {
        Matrix4f matrix = pose.m_85850_().m_252922_();
        for (GeoQuad quad : cube.quads()) {
            if (quad == null) {
                continue;
            }
            for (GeoVertex vertex : quad.vertices()) {
                Vector4f point = matrix.transform(new Vector4f(vertex.position(), 1.0F));
                float[] coordinates = {point.x(), point.y(), point.z()};
                for (int axis = 0; axis < 3; axis++) {
                    entry.min[axis] = Math.min(entry.min[axis], coordinates[axis]);
                    entry.max[axis] = Math.max(entry.max[axis], coordinates[axis]);
                }
            }
        }
    }

    private static void emit(PoseStack pose, GeoCube cube, VertexConsumer buffer, int light) {
        Matrix3f normals = pose.m_85850_().m_252943_();
        Matrix4f matrix = pose.m_85850_().m_252922_();
        for (GeoQuad quad : cube.quads()) {
            if (quad == null) {
                continue;
            }
            Vector3f normal = normals.transform(new Vector3f(quad.normal()));
            RenderUtils.fixInvertedFlatCube(cube, normal);
            for (GeoVertex vertex : quad.vertices()) {
                Vector4f point = matrix.transform(new Vector4f(vertex.position(), 1.0F));
                buffer.m_5954_(point.x(), point.y(), point.z(), 1.0F, 1.0F, 1.0F, 1.0F, vertex.texU(), vertex.texV(),
                        OverlayTexture.f_118083_, light, normal.x(), normal.y(), normal.z());
            }
        }
    }
}
