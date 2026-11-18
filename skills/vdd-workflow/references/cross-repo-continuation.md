# Continuing a ticket across repos without disturbing the checkout

For the remainder-work case: a ticket spans a backend and a frontend repo, the user deferred commit/deploy, and the ticket branch is behind `main`.

## 1. Decide whether the branch is still the right place

```bash
git -C <repo> rev-list --count HEAD..origin/main      # how far behind
git -C <repo> rev-list --count origin/main..HEAD      # what it adds
git -C <repo> merge-tree --write-tree origin/main <branch>   # non-zero exit + CONFLICT lines
```

If the file you need is absent from the branch, the branch cannot hold the fix without merging main first:

```bash
git -C <repo> ls-tree -r --name-only origin/main | grep <file>
```

## 2. Put the change on main's code in a detached worktree

```bash
git -C <repo> worktree add <parent>/<repo>-wip --detach origin/main
cd <parent>/<repo>-wip
ln -s <repo>/node_modules node_modules     # reuse installed deps, do not reinstall
```

- `--detach` leaves the user's current branch and working tree untouched — required when their checkout holds unrelated in-progress work.
- A symlinked `node_modules` is enough for `vitest` and `tsc` to resolve packages.
- Uncommitted work in a detached worktree is easy to lose: after the last edit run `git diff > <parent>/<repo>-wip.patch`, and name that backup path in the summary.

## 3. Run the checks the repo does not run

```bash
# Python tests without the project venv or its missing local deps
uv run --no-project --with pytest --with fastapi --with motor --with redis \
  --with pydantic-settings pytest tests/unit -q

# TS file outside the tsconfig include list (edge handlers, workers, scripts)
npx tsc --noEmit --strict --target es2022 --module esnext \
  --moduleResolution bundler --skipLibCheck functions/<handler>.ts

# focused test first, whole unit dir after
npx vitest run src/utils/<file>.test.ts
```

`--no-project` installs only what you list, so add the imports the test module actually touches. Run the focused file first for fast feedback, then the wider directory — shared fixtures are where a signature change breaks other tests.

## 4. Cross-repo deploy-order pattern

The frontend keeps the call shape that works today and adds the new one as a retry:

```ts
let lookup = await fetchPreview(api, articleId ?? segment);   // shape that works in prod now
if (lookup.status === 'not_found' && articleId && segment !== articleId) {
  lookup = await fetchPreview(api, segment);                  // new shape, enabled by the backend fix
}
```

Without this, a frontend deployed before the backend turns every detail URL into a hard 404 — for an indexing/SEO ticket that is a worse regression than the bug being fixed.

## 5. What the summary must contain when deploy is deferred

- nothing committed or pushed, stated plainly
- changed files per repo, and which worktree/directory holds them when it is not the user's checkout
- review command per repo: `git -C <repo> diff`
- what is deliberately not done (console/credential work, dead-path decisions) and why
- verification actually run, with counts (`254 passed`, `23 passed`, `tsc clean`, `git diff --check` clean)
