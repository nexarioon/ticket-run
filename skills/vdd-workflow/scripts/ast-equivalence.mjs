#!/usr/bin/env node
/**
 * Prove that a change touched only comments, not code.
 *
 * Compares the AST of every changed TS/TSX/JS/MJS file between a git base
 * revision and the working tree. TypeScript's printer drops comments, so if
 * the printed AST is identical the diff cannot have changed code, strings,
 * identifiers or formatting-sensitive syntax.
 *
 *   node ast-equivalence.mjs            # base = HEAD
 *   node ast-equivalence.mjs origin/main
 *
 * Exit 0 = only comments changed. Exit 1 = AST differs (list printed).
 * Requires `typescript` in the repo (any workspace) or on NODE_PATH.
 */
import { execSync } from "node:child_process"
import { readFileSync, existsSync } from "node:fs"
import { createRequire } from "node:module"
import { resolve } from "node:path"

const base = process.argv[2] || "HEAD"

function loadTypeScript() {
  const candidates = [
    resolve(process.cwd(), "node_modules/typescript"),
    resolve(process.cwd(), "apps/api/node_modules/typescript"),
    resolve(process.cwd(), "apps/web/node_modules/typescript"),
    "typescript",
  ]

  for (const c of candidates) {
    if (c !== "typescript" && !existsSync(c)) continue
    try {
      return createRequire(resolve(process.cwd(), "package.json"))(c)
    } catch {
      /* try next */
    }
  }

  console.error("typescript not found: install it or set NODE_PATH")
  process.exit(2)
}

const ts = loadTypeScript()

const files = execSync(`git diff --name-only ${base} -- .`, { encoding: "utf8" })
  .split("\n")
  .filter((f) => f && /\.(ts|tsx|mjs|cjs|js|jsx)$/.test(f))

const scriptKind = (f) =>
  f.endsWith(".tsx") ? ts.ScriptKind.TSX
  : f.endsWith(".ts") ? ts.ScriptKind.TS
  : ts.ScriptKind.JS

const print = (src, f) =>
  ts.createPrinter({ removeComments: true }).printFile(
    ts.createSourceFile(f, src, ts.ScriptTarget.Latest, true, scriptKind(f)),
  )

const differ = []
let checked = 0

for (const f of files) {
  let before
  try {
    before = execSync(`git show ${base}:${f}`, { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 })
  } catch {
    continue // new file: nothing to compare
  }

  checked++
  if (print(before, f) !== print(readFileSync(f, "utf8"), f)) differ.push(f)
}

console.log(`checked ${checked} file(s) against ${base}`)
if (differ.length) {
  console.log("AST DIFFERS (code changed):")
  for (const f of differ) console.log("  -", f)
  process.exit(1)
}

console.log("OK: AST identical, only comments changed")
