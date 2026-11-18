# Behaviour-preserving refactor

Use when the request is "clean this up / tidy the repo / rapihkan" with the constraint that the
system must keep behaving exactly the same. The deliverable is a smaller diff with identical
output, plus evidence that the output is identical.

## 1. Measure before touching anything

```bash
# file size ranking (ignore generated files such as *.d.ts)
find apps/web/src apps/api/src -name '*.ts' -o -name '*.tsx' | xargs wc -l | sort -rn | head -15

# duplicate helper definitions: same name in several files
grep -rhno "function [a-zA-Z]*" apps/web/src | sed 's/.*function //' | sort | uniq -c | sort -rn | awk '$1>1'

# type escape hatches
grep -rc ': any\|as any\|<any>' apps/web/src apps/api/src | grep -v ':0'

# decorative comment banners
grep -rn '─\{3,\}\|-\{4,\}' apps/web/src apps/api/src --include='*.ts*' | wc -l
```

Turn the numbers into numbered findings (`F-01…`) with the rule they violate and the measured
evidence. A cleanup ticket has no acceptance criteria in the tracker, so the findings list *is*
the specification; get it approved before editing.

## 2. Test plan for a refactor is artifact identity, not "tests pass"

Green tests only prove the paths they cover. Add at least one identity check:

| Artifact | Check |
|---|---|
| Moved code | `sha256` of the block before and after the move must match |
| Generated file (docx/pdf/xlsx) | hash of the unpacked XML, or a byte diff of two runs |
| API response | snapshot JSON for every endpoint touched, compared before/after |
| Bundle | build succeeds and the chunk size does not jump (e.g. < 5%) |

Run the snapshot/hash capture **before** the first edit; after the edit there is nothing to
compare against.

## 3. Move, do not rewrite

Cut the whole block to the new module, add only `export` keywords, and leave the body untouched.
Then prove it:

```bash
python3 - <<'PY'
import hashlib, subprocess
old = subprocess.run(['git','show','HEAD:src/Big.tsx'], capture_output=True, text=True).stdout
new = open('src/Big.tsx').read()
def blok(s):
    return s[s.index('function alpha('):s.index('export function Page(')].rstrip() + '\n'
print(hashlib.sha256(blok(old).encode()).hexdigest() == hashlib.sha256(blok(new).encode()).hexdigest())
PY
```

Locate blocks by **marker text**, never by remembered line numbers: removing helpers above shifts
every index and a hard-coded range silently compares the wrong lines.

## 4. Deleting N duplicate definitions safely

1. Extract the canonical implementation into the shared module first.
2. Delete each local copy with an exact-block script, then insert the import.
3. Re-run the duplicate scan: the count must land on exactly 1.
4. Let the compiler find the misses (`tsc`/`vite build`), not review by eye.

```python
pat = re.compile(r'\n[ \t]*(?:export )?function formatRupiah\([^)]*\)\s*\{\n(?:[^\n]*\n)*?[ \t]*\}\n', re.M)
```

The leading `[ \t]*` matters: helpers declared **inside** a component are indented, and a
line-anchored pattern leaves them behind while the count looks plausible.

## 5. When not to merge

Same name does not mean same behaviour. Diff the bodies first:

```python
print(hashlib.sha256(a.encode()).hexdigest() == hashlib.sha256(b.encode()).hexdigest())
```

A variant that abbreviates money (`Rp 1,2 JT`) or spells a word differently is a *different*
function: give it its own honest name in the shared module (`formatRupiahShort`) and keep the
call sites pointing at the behaviour they had.

## 6. Typing is part of the cleanup

Replacing a parameter typed `any` with the real type (for example
`type Docx = typeof import("docx")`) is free at runtime and finds latent bugs. Expect one or two:
an enum member that does not exist, a property that was always `undefined`. Fix them, and list
each as an **intentional behaviour change** in the report with the reason. Do not revert the type
just to keep the diff uniform.

## 7. Closing gate

```bash
npm run test -w @pkg/api          # whole suite
cd apps/web && npx playwright test # whole E2E dir
npm run typecheck && npm run build
git diff --stat                    # only the files the plan named
git diff --check                   # no whitespace noise
```

Report: before/after line counts, duplicate counts, the identity hash result, the intentional
changes, and what was left out of scope.
