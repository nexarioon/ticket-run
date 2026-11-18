# Behaviour-preserving refactor / cleanup

For tickets that say "clean this up", "rapikan", "refactor", "move this",
"translate comments", "don't change behaviour". Two things must be true at the
end: the measured mess is smaller, and there is proof that behaviour did not
move. Green tests alone are not that proof — they only cover what they cover.

## 1. Measure before touching anything

A cleanup ticket has no acceptance criteria, so the measurement *is* the spec.
Collect, per candidate: file/line counts (`wc -l`), duplicate definitions
(`grep -h 'function NAME' ... | uniq -c`), `any` count, decorative comments,
inline generators (docx/PDF builders inside a page component). Write them into
a numbered findings list with a rule citation and a priority, and get the scope
approved before editing. Without the before-numbers the final report cannot
say what improved.

## 2. Never unify duplicates you have not diffed

Same name does not mean same output. Extract every body and compare:

```bash
# group identical implementations, show the differing ones separately
python3 - <<'PY'
import re, glob, collections
pat = re.compile(r'function formatRupiah\([^)]*\)\s*\{(.*?)\n\}', re.S)
seen = collections.defaultdict(list)
for f in glob.glob('src/**/*.ts*', recursive=True):
    for m in pat.finditer(open(f).read()):
        seen[' '.join(m.group(1).split())].append(f)
for body, files in seen.items():
    print(len(files), body[:120])
PY
```

In one real repo 15 of 17 `formatRupiah` copies were byte-identical while one
used a `1,2 JT` / `3,4 M` shorthand. Unifying all 17 would have silently
changed a dashboard's numbers. Rule: identical bodies merge into the shared
module; a variant keeps its behaviour under a distinct name
(`formatRupiahShort`) and is imported from the same module.

## 3. Prove a move is a move

When functions move file-to-file, hash the block before and after:

```python
# extract by markers so line shifts cannot fool the comparison
blok = src[src.index('function nameA('):src.index('export function Page(')]
print(sha256(blok.encode()).hexdigest())
```

Equal hash = the body was relocated verbatim, indentation included. Only the
wrapper (`export`, imports) may differ. Do this per moved block; it catches a
"move" that quietly rewrote a condition.

## 4. Prove the whole diff is comments-only

For comment-only work (translation, banner removal) an AST comparison is the
proof. `scripts/ast-equivalence.mjs` prints the AST of every changed file with
`removeComments` and diffs it against the git base. Identical output means no
code, string, identifier or JSX text changed — which also proves you did not
translate a UI string, a test title or a data literal by accident.

Do NOT hand-roll a regex comment stripper for this: `//` inside a URL, a
regex literal containing a quote, or a template literal desyncs a naive state
machine and reports false "code changed" on files that are fine. If a quick
stripper is unavoidable, treat its failures as suspects and confirm with the
AST before acting.

## 5. Parallelise the mechanical half, verify centrally

Comment translation or import rewiring across dozens of files is mechanical and
splits cleanly across subagents. Give each child: the exact file list, "comments
only — never strings, JSX text, test titles, or identifiers", and "do not run
build/test/commit". Then verify yourself with the AST check plus one full build
and test run; a child's `git diff` self-report is not evidence.

## 6. Replace `any` with real types — expect latent bugs

Typing an `any` parameter with the library's own type is the cheapest bug hunt
there is. It surfaced `docx.VerticalAlign.MIDDLE`, a member that does not exist
(only `TOP`/`CENTER`/`BOTTOM`), so the value had been `undefined` at runtime.
When a type widening finds one of these, fix it deliberately, say so in the
report as the single intended behaviour change, and do not bury it in a
"refactor, no functional change" claim.

## Report shape

| Metrik | Sebelum | Sesudah |
|---|---|---|
| lines per file / duplicates / `any` / decorative comments | measured | measured |

Then: the identity evidence (hash / AST / snapshot), the test counts actually
printed by the runner, the one intended change if any, and the findings left
undone.
