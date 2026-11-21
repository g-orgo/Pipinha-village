#!/usr/bin/env node
// KubeJS 2101 Rhino throws "TypeError: redeclaration of var X" on the FIRST run of a `const`
// declared inside a nested block (if / try / else / switch case) when the enclosing function
// also holds a closure (any inner function or arrow, debug lambdas included).
// Seen 2026-11-20: global.handleBETick (`const nbtStage` inside the dawn `if`) broke as soon as
// the [artisandebug] arrows were added, and no artisan machine advanced at dawn anymore.
// Nested `let` and `const` at the top of a function body are fine.
//
// This tool lists every `const` inside a nested block. Lines tagged ERROR sit in a function
// with a closure and fail at runtime; lines tagged latent work today but break once a closure
// is added to that function. Exit code 1 when any ERROR is found.
// Fix: declare with `let` at the top of the function and only assign inside the block.
// Usage: NODE_PATH=<dir with acorn, acorn-walk> node tools/kjsport/find_nested_const.js <kubejs dir> [--latent]
const fs = require("fs");
const path = require("path");
const acorn = require("acorn");
const walk = require("acorn-walk");

const FUNCS = new Set(["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"]);

const listJs = (dir) =>
  fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) => {
    const p = path.join(dir, d.name);
    if (d.isDirectory()) return listJs(p);
    return d.isFile() && p.endsWith(".js") ? [p] : [];
  });

const hasInnerFunction = (fn) => {
  let found = false;
  walk.full(fn.body, (n) => {
    if (FUNCS.has(n.type)) found = true;
  });
  return found;
};

const root = process.argv[2];
const showLatent = process.argv.includes("--latent");
let errors = 0;
let latent = 0;

for (const file of listJs(root)) {
  const rel = path.relative(root, file);
  let ast;
  try {
    ast = acorn.parse(fs.readFileSync(file, "utf8"), {
      ecmaVersion: "latest",
      sourceType: "script",
      allowReturnOutsideFunction: true,
      locations: true,
    });
  } catch (err) {
    console.log(`PARSEFAIL ${rel}: ${err.message}`);
    continue;
  }
  walk.ancestor(ast, {
    VariableDeclaration(node, ancestors) {
      if (node.kind !== "const") return;
      const parent = ancestors[ancestors.length - 2];
      let nested = parent.type === "SwitchCase";
      if (parent.type === "BlockStatement") {
        const owner = ancestors[ancestors.length - 3];
        nested = !(owner && FUNCS.has(owner.type) && owner.body === parent);
      }
      if (!nested) return;
      const fn = [...ancestors].reverse().find((a) => FUNCS.has(a.type));
      const names = node.declarations.map((d) => (d.id.type === "Identifier" ? d.id.name : "{...}")).join(", ");
      if (fn && hasInnerFunction(fn)) {
        errors++;
        console.log(`ERROR ${rel}:${node.loc.start.line} const ${names}`);
      } else {
        latent++;
        if (showLatent) console.log(`latent ${rel}:${node.loc.start.line} const ${names}`);
      }
    },
  });
}

console.log(`errors=${errors} latent=${latent}`);
process.exit(errors > 0 ? 1 : 0);
