#!/usr/bin/env node
// KubeJS 2101: a builder with .parentModel(X) still writes the default texture map into the
// generated model, and a block builder with .box(...) also gets cube elements textured with the
// default `<ns>:block/<path>` texture. When that texture does not exist the item/block shows a
// purple-black cube (e.g. the adv_* plushies). .modelGenerator((m) => m.parent(X)) returns before
// that code runs, so the model is exactly "parent X".
//
// This tool rewrites .parentModel(X) to .modelGenerator((m) => m.parent(X)) unless the same builder
// chain (or the same item callback body) also sets textures, which then must be kept.
// Usage: NODE_PATH=<dir with acorn, acorn-walk> node tools/kjsport/fix_parent_model.js <dir> [--write]
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

const TEXTURE_METHODS = new Set(["texture", "textures"]);
const root = process.argv[2];
const write = process.argv.includes("--write");
let total = 0;
let skipped = 0;

for (const file of listJs(root)) {
  const src = fs.readFileSync(file, "utf8");
  const ast = acorn.parse(src, { ecmaVersion: "latest", sourceType: "script", allowReturnOutsideFunction: true });
  const edits = [];
  walk.ancestor(ast, {
    CallExpression(node, ancestors) {
      const callee = node.callee;
      if (callee.type !== "MemberExpression" || callee.property.name !== "parentModel" || node.arguments.length !== 1) return;
      // Outermost expression of this method chain.
      let top = node;
      for (let i = ancestors.length - 2; i >= 0; i--) {
        const a = ancestors[i];
        if ((a.type === "MemberExpression" && a.object === top) || (a.type === "CallExpression" && a.callee === top)) top = a;
        else break;
      }
      // The enclosing function body counts too (item callbacks call item.texture separately).
      let scope = top;
      for (let i = ancestors.length - 1; i >= 0; i--) {
        if (/Function/.test(ancestors[i].type)) {
          scope = ancestors[i];
          break;
        }
      }
      // Method names called directly on this chain (nested callbacks are not part of it).
      const chainMethods = new Set();
      for (let n = top; n; ) {
        if (n.type === "CallExpression") n = n.callee;
        else if (n.type === "MemberExpression") {
          if (n.property.type === "Identifier") chainMethods.add(n.property.name);
          n = n.object;
        } else break;
      }
      const scopeText = scope === top ? "" : src.slice(scope.start, scope.end);
      const ownChainSetsTexture = [...TEXTURE_METHODS].some((m) => chainMethods.has(m));
      const itemCallbackSetsTexture =
        callee.object.type === "Identifier" && [...TEXTURE_METHODS].some((m) => scopeText.includes(`${callee.object.name}.${m}(`));
      if (ownChainSetsTexture || itemCallbackSetsTexture) {
        skipped++;
        console.log(`SKIP ${path.relative(root, file)}:${src.slice(0, node.start).split("\n").length}`);
        return;
      }
      const arg = src.slice(node.arguments[0].start, node.arguments[0].end);
      edits.push({ start: callee.property.start, end: node.end, text: `modelGenerator((m) => m.parent(${arg}))` });
    },
  });
  if (edits.length === 0) continue;
  total += edits.length;
  console.log(`${path.relative(root, file)}: ${edits.length}`);
  if (write) {
    let out = src;
    for (const e of edits.sort((a, b) => b.start - a.start)) out = out.slice(0, e.start) + e.text + out.slice(e.end);
    fs.writeFileSync(file, out);
  }
}
console.log(`rewrites=${total} skipped=${skipped} write=${write}`);
