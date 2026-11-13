import dev.latvian.mods.rhino.Context;
import dev.latvian.mods.rhino.Scriptable;
import java.io.FileReader;
import java.io.Reader;

/**
 * Runs the hostile spawn toggle scripts outside the game, in KubeJS's own Rhino.
 * Evaluates every file given as argument in order (stubs, scripts, tests) and
 * prints OUT plus the failure count kept in RESULT.
 */
public class HostileToggleHarness {
    public static void main(String[] args) throws Exception {
        Context cx = Context.enter();
        Scriptable scope = cx.initStandardObjects();
        for (String path : args) {
            try (Reader r = new FileReader(path)) {
                cx.evaluateReader(scope, r, path, 1, null);
            }
        }
        System.out.println(cx.toString(cx.evaluateString(scope, "OUT.join('\\n')", "<out>", 1, null)));
        System.out.println("failures=" + cx.toString(cx.evaluateString(scope, "RESULT", "<result>", 1, null)));
    }
}
