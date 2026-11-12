import dev.latvian.mods.rhino.Context;

import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

// Compiles every .js file under a root with Rhino (no execution).
// Args: <root> <outFile>. Writes one line per file: OK<TAB>rel  or  FAIL<TAB>rel<TAB>line<TAB>message.
public class SyntaxCheck {
    public static void main(String[] args) throws Exception {
        Path root = Path.of(args[0]);
        List<Path> files;
        try (var s = Files.walk(root)) {
            files = s.filter(p -> p.toString().endsWith(".js") && Files.isRegularFile(p))
                    .sorted().toList();
        }
        int ok = 0, fail = 0;
        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(Path.of(args[1])))) {
            for (Path p : files) {
                String rel = root.relativize(p).toString().replace(File.separatorChar, '/');
                String err = compile(p);
                if (err == null) {
                    out.println("OK\t" + rel);
                    ok++;
                } else {
                    out.println("FAIL\t" + rel + "\t" + err);
                    fail++;
                }
            }
        }
        System.out.println("files=" + files.size() + " ok=" + ok + " fail=" + fail);
    }

    // Rhino 2001 (OLD) has a static Context.enter(); Rhino 2101 (NEW) enters through ContextFactory.
    static Context enter() throws Exception {
        java.lang.reflect.Method m = null;
        try {
            m = Context.class.getMethod("enter");
        } catch (NoSuchMethodException e) {
            // Rhino 2101: no public static enter on Context
        }
        if (m != null && java.lang.reflect.Modifier.isStatic(m.getModifiers())) {
            return (Context) m.invoke(null);
        }
        Object factory = Class.forName("dev.latvian.mods.rhino.ContextFactory")
                .getConstructor().newInstance();
        return (Context) factory.getClass().getMethod("enter").invoke(factory);
    }

    static String compile(Path p) {
        try (FileReader r = new FileReader(p.toFile())) {
            enter().compileReader(r, p.getFileName().toString(), 1, null);
            return null;
        } catch (Throwable t) {
            String msg = String.valueOf(t.getMessage()).replace('\t', ' ').replace('\n', ' ');
            int line = 0;
            java.util.regex.Matcher m = java.util.regex.Pattern.compile("#(\\d+)").matcher(msg);
            if (m.find()) line = Integer.parseInt(m.group(1));
            return line + "\t" + msg;
        }
    }
}
