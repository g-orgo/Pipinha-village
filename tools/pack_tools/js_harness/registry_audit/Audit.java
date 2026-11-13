import dev.latvian.mods.rhino.Context;
import dev.latvian.mods.rhino.Scriptable;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class Audit {
    public static void main(String[] args) throws Exception {
        Context cx = Context.enter();
        Scriptable shared = cx.initStandardObjects();
        cx.evaluateString(shared, new String(Files.readAllBytes(Paths.get("/w/stubs.js"))), "stubs", 1, null);
        for (String f : Files.readAllLines(Paths.get("/w/order.txt"))) {
            if (f.trim().isEmpty()) continue;
            Scriptable local = cx.newObject(shared);
            local.setPrototype(shared);
            try (Reader r = new FileReader("/w/s/" + f)) {
                cx.evaluateReader(local, r, f, 1, null);
                System.out.println("OK   " + f);
            } catch (Throwable t) {
                String m = String.valueOf(t.getMessage());
                System.out.println("FAIL " + f + " :: " + m.substring(0, Math.min(200, m.length())));
            }
        }
        Object out = cx.evaluateString(shared, new String(Files.readAllBytes(Paths.get("/w/dump.js"))), "dump", 1, null);
        Files.write(Paths.get("/w/dump.json"), String.valueOf(out).getBytes("UTF-8"));
    }
}
