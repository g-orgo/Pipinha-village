import com.sunlit.eating.FoodPose;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

// Prints the pose FoodPose picks for each line of sunlit_tools/eating/foods_dump.txt.
// Run with the source of FoodPose on the classpath; it has no Minecraft dependency.
public class PoseDump {
    public static void main(String[] args) throws Exception {
        List<String> out = new ArrayList<>();
        for (String line : Files.readAllLines(Path.of(args[0]))) {
            String[] f = line.split("\\|", -1);
            String id = f[0];
            String cls = f[6].substring(f[6].lastIndexOf('.') + 1);
            FoodPose pose = FoodPose.classify(id.substring(id.indexOf(':') + 1), f[7], f[2].equals("DRINK"), cls.startsWith("BowlFood"));
            out.add(id + "|" + pose.animationName());
        }
        Files.write(Path.of(args[1]), out);
    }
}
