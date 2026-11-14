#!/usr/bin/env node
// KubeJS 2101 CardinalBlockBuilder: the blockstate points straight at parentModel, but the generated
// block/<id> model (used by the block item) keeps parentModel as parent and overrides the side, front,
// top and particle variables with <ns>:block/<id>(_front) defaults that usually do not exist.
// Cardinal chains must therefore keep .parentModel(X). This tool turns a cardinal chain's
// .modelGenerator((m) => m.parent(X)) back into .parentModel(global.cardinalParent(<id>, X)), which
// records <id> -> X so client_scripts/cardinalModels.js can rewrite block/<id> as a plain {"parent": X}.
// Usage: NODE_PATH=<dir with acorn, acorn-walk> node tools/kjsport/fix_cardinal_model.js <dir> [--write]
const fs = require("fs");
const path = require("path");
const acorn = require("acorn");
const walk = require("acorn-walk");

const listJs = (dir) =>
  fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) => {
    const p = path.join(dir, d.name);
    if (d.isDirectory()) return listJs(p);
    return d.isFile() && p.endsWith(".js") ? [p] : [];
  });

// Returns the X of `(m) => m.parent(X)` or null.
const parentArg = (fn) => {
  if (!fn || fn.type !== "ArrowFunctionExpression" || fn.params.length !== 1) return null;
  const body = fn.body;
  if (body.type !== "CallExpression" || body.callee.type !== "MemberExpression") return null;
  if (body.callee.property.name !== "parent" || body.arguments.length !== 1) return null;
  return body.arguments[0];
};

const root = process.argv[2];
const write = process.argv.includes("--write");
let total = 0;
for (const file of listJs(root)) {
  const src = fs.readFileSync(file, "utf8");
  const ast = acorn.parse(src, { ecmaVersion: "latest", sourceType: "script", allowReturnOutsideFunction: true });
  const edits = [];
  walk.simple(ast, {
    CallExpression(node) {
      const c = node.callee;
      if (c.type !== "MemberExpression" || c.property.name !== "modelGenerator" || node.arguments.length !== 1) return;
      const x = parentArg(node.arguments[0]);
      if (!x) return;
      // Walk down the chain to its create(id, "cardinal") call.
      let n = c.object;
      let create = null;
      while (n && (n.type === "CallExpression" || n.type === "MemberExpression")) {
        if (n.type === "CallExpression" && n.callee.type === "MemberExpression" && n.callee.property.name === "create") {
          create = n;
          break;
        }
        n = n.type === "CallExpression" ? n.callee : n.object;
      }
      if (!create || create.arguments.length !== 2) return;
      const type = create.arguments[1];
      if (type.type !== "Literal" || type.value !== "cardinal") return;
      const idSrc = src.slice(create.arguments[0].start, create.arguments[0].end);
      const xSrc = src.slice(x.start, x.end);
      edits.push({ start: c.property.start, end: node.end, text: `parentModel(global.cardinalParent(${idSrc}, ${xSrc}))` });
    },
  });
  if (!edits.length) continue;
  total += edits.length;
  console.log(`${path.relative(root, file)}: ${edits.length}`);
  if (write) {
    let out = src;
    for (const e of edits.sort((a, b) => b.start - a.start)) out = out.slice(0, e.start) + e.text + out.slice(e.end);
    fs.writeFileSync(file, out);
  }
}
console.log(`rewrites=${total} write=${write}`);
