import dev.latvian.mods.rhino.Context;
import dev.latvian.mods.rhino.Scriptable;
import java.io.FileReader;
import java.io.Reader;

/**
 * Roda kubejs/startup_scripts/replayViewerButton.js fora do jogo, no Rhino do proprio
 * KubeJS, com uma tela inicial falsa (replayStubs.js) e os cenarios de teste
 * (replayButtonTests.js).
 */
public class ReplayButtonHarness {
    public static void main(String[] args) throws Exception {
        Context cx = Context.enter();
        Scriptable scope = cx.initStandardObjects();

        evalFile(cx, scope, "/w/replayStubs.js");
        evalFile(cx, scope, "/w/replayViewerButton.js");
        System.out.println("OK   replayViewerButton.js (carregou)");
        evalFile(cx, scope, "/w/replayButtonTests.js");

        System.out.println(cx.toString(cx.evaluateString(scope, "OUT.join('\\n')", "<out>", 1, null)));
        Object result = cx.evaluateString(scope, "RESULT", "<result>", 1, null);
        System.out.println("falhas=" + cx.toString(result));
    }

    static void evalFile(Context cx, Scriptable scope, String path) throws Exception {
        try (Reader r = new FileReader(path)) {
            cx.evaluateReader(scope, r, path, 1, null);
        }
    }
}
