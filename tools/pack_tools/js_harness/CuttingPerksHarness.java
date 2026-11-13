import dev.latvian.mods.rhino.Context;
import dev.latvian.mods.rhino.Scriptable;
import java.io.FileReader;
import java.io.Reader;

/**
 * Runs kubejs/startup_scripts/forgeEvents/culinariaSkills.js outside the game, on
 * KubeJS's own Rhino, with a fake cutting board (cuttingPerksTests.js).
 */
public class CuttingPerksHarness {
    public static void main(String[] args) throws Exception {
        Context cx = Context.enter();
        Scriptable scope = cx.initStandardObjects();

        // Stubs and tests share one file; the script under test needs the stubs first.
        String tests = new String(java.nio.file.Files.readAllBytes(java.nio.file.Path.of("/w/cuttingPerksTests.js")));
        int split = tests.indexOf("var RANDOM");
        cx.evaluateString(scope, tests.substring(0, split), "stubs", 1, null);
        try (Reader r = new FileReader("/w/culinariaSkills.js")) {
            cx.evaluateReader(scope, r, "culinariaSkills.js", 1, null);
        }
        cx.evaluateString(scope, tests.substring(split), "tests", 1, null);

        System.out.println(cx.toString(cx.evaluateString(scope, "OUT.join('\\n')", "<out>", 1, null)));
        System.out.println("falhas=" + cx.toString(cx.evaluateString(scope, "RESULT", "<result>", 1, null)));
    }
}
