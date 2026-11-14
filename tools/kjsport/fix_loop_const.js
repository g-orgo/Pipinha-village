#!/usr/bin/env node
// KubeJS 2101 Rhino keeps the FIRST value of a `const` declared inside a loop body
// (for / for-in / for-of / while / do-while) when the loop runs inside a function,
// and throws "redeclaration of var" when the loop is at the top level of a script.
// Proven with the pack's rhino-2101.2.7 jar (2026-11-13): for (const k in o) { const v = o[k]; }
// yields v = first value on every iteration. `let` behaves correctly.
//
// This tool finds every `const` declaration whose nearest enclosing loop sits in the same
// function (loop heads included) and rewrites it to `let`.
// Usage: NODE_PATH=<dir with acorn, acorn-walk> node tools/kjsport/fix_loop_const.js <root> [--write]
const fs = require("fs");
const path = require("path");
const acorn = require("acorn");
const walk = require("acorn-walk");

const LOOPS = new Set(["ForStatement", "ForInStatement", "ForOfStatement", "WhileStatement", "DoWhileStatement"]);
const FUNCS = new Set(["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"]);

const listJs = (dir) =>
  fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) => {
    const p = path.join(dir, d.name);
    if (d.isDirectory()) return listJs(p);
    return d.isFile() && p.endsWith(".js") ? [p] : [];
  });

const root = process.argv[2];
const write = process.argv.includes("--write");
let totalFiles = 0;
let totalDecls = 0;
const failures = [];

for (const file of listJs(root)) {
  const src = fs.readFileSync(file, "utf8");
  let ast;
  try {
    ast = acorn.parse(src, { ecmaVersion: "latest", sourceType: "script", allowReturnOutsideFunction: true });
  } catch (err) {
    failures.push(`${path.relative(root, file)}: ${err.message}`);
    continue;
  }
  const hits = [];
  walk.ancestor(ast, {
    VariableDeclaration(node, ancestors) {
      if (node.kind !== "const") return;
      // ancestors ends with node itself; scan upward until a function boundary.
      for (let i = ancestors.length - 2; i >= 0; i--) {
        const a = ancestors[i];
        if (FUNCS.has(a.type)) return;
        if (LOOPS.has(a.type)) {
          hits.push(node.start);
          return;
        }
      }
    },
  });
  if (hits.length === 0) continue;
  totalFiles++;
  totalDecls += hits.length;
  console.log(`${path.relative(root, file)}: ${hits.length}`);
  if (write) {
    let out = src;
    for (const start of hits.sort((a, b) => b - a)) {
      if (out.slice(start, start + 5) !== "const") throw new Error(`unexpected token at ${file}:${start}`);
      out = out.slice(0, start) + "let" + out.slice(start + 5);
    }
    fs.writeFileSync(file, out);
  }
}
console.log(`files=${totalFiles} decls=${totalDecls} parseFailures=${failures.length} write=${write}`);
failures.slice(0, 20).forEach((f) => console.log(`PARSE FAIL ${f}`));
