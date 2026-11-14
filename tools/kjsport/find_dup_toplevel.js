#!/usr/bin/env node
// KubeJS 2101 runs every script of one type (startup_scripts, server_scripts, client_scripts)
// in a single shared top-level scope. A top-level `const`/`let`/`class` whose name is also
// declared at the top level of another script of the same type makes the later script fail
// with "redeclaration of const X" and none of it runs.
//
// This tool lists those collisions per script type, with each declaration's kind and whether
// the initializer source is identical across files.
// With --fix-identical it rewrites collisions whose initializers are all identical
// (e.g. the same Java.loadClass) to `var` in every file, which Rhino allows to redeclare.
// Usage: NODE_PATH=<dir with acorn> node tools/kjsport/find_dup_toplevel.js <kubejs dir> [--fix-identical]
const fs = require("fs");
const path = require("path");
const acorn = require("acorn");

const listJs = (dir) =>
  fs.existsSync(dir)
    ? fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) => {
        const p = path.join(dir, d.name);
        if (d.isDirectory()) return listJs(p);
        return d.isFile() && p.endsWith(".js") ? [p] : [];
      })
    : [];

const root = process.argv[2];
const fixIdentical = process.argv.includes("--fix-identical");

for (const type of ["startup_scripts", "server_scripts", "client_scripts"]) {
  const decls = new Map(); // name -> [{file, kind, init, start}]
  for (const file of listJs(path.join(root, type))) {
    const src = fs.readFileSync(file, "utf8");
    let ast;
    try {
      ast = acorn.parse(src, { ecmaVersion: "latest", sourceType: "script", allowReturnOutsideFunction: true });
    } catch (err) {
      console.log(`PARSE FAIL ${file}: ${err.message}`);
      continue;
    }
    const add = (name, entry) => {
      if (!decls.has(name)) decls.set(name, []);
      decls.get(name).push(entry);
    };
    for (const node of ast.body) {
      if (node.type === "VariableDeclaration") {
        for (const d of node.declarations) {
          if (d.id.type !== "Identifier") continue;
          const init = d.init ? src.slice(d.init.start, d.init.end).replace(/\s+/g, " ") : "";
          add(d.id.name, { file, kind: node.kind, init, start: node.start, single: node.declarations.length === 1 });
        }
      } else if (node.type === "FunctionDeclaration" && node.id) {
        add(node.id.name, { file, kind: "function", init: src.slice(node.start, node.end).replace(/\s+/g, " "), start: node.start });
      } else if (node.type === "ClassDeclaration" && node.id) {
        add(node.id.name, { file, kind: "class", init: "", start: node.start });
      }
    }
  }
  const edits = new Map(); // file -> [start]
  for (const [name, list] of decls) {
    if (list.length < 2) continue;
    // Only block-scoped kinds collide; var/function redeclarations are legal (last one wins).
    if (!list.some((e) => e.kind === "const" || e.kind === "let" || e.kind === "class")) continue;
    const identical = list.every((e) => e.init === list[0].init);
    console.log(`${type} ${name} identical=${identical}`);
    list.forEach((e) => console.log(`  ${e.kind} ${path.relative(root, e.file)} = ${e.init.slice(0, 90)}`));
    if (fixIdentical && identical) {
      for (const e of list) {
        if (e.kind !== "const" && e.kind !== "let") continue;
        if (!e.single) {
          console.log(`  SKIP multi-declarator in ${path.relative(root, e.file)}`);
          continue;
        }
        if (!edits.has(e.file)) edits.set(e.file, []);
        edits.get(e.file).push({ start: e.start, len: e.kind.length });
      }
    }
  }
  for (const [file, list] of edits) {
    let out = fs.readFileSync(file, "utf8");
    for (const { start, len } of list.sort((a, b) => b.start - a.start)) {
      out = out.slice(0, start) + "var" + out.slice(start + len);
    }
    fs.writeFileSync(file, out);
  }
}
