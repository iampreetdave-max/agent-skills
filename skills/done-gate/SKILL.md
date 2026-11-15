---
name: done-gate
description: Verification gate to run before reporting any implementation work as done. Rebuilds the list of asks from the user's own words, proves each one with file:line evidence, has a fresh subagent audit the work blind, and runs the project's own build and type checks. Use after finishing a set of code changes and before telling the user anything is finished, or when the user asks "is it really done?", "did you do everything?" or "verify it".
---

# Done gate

Kills the most common agent failure: reporting "done" when 3 of the 10 asks are missing. Nothing is done until it passes all five stages. Small changes get no shortcut; small changes are where items get dropped.

## Stage 1: Rebuild the ledger from the source

Re-read the user's original messages, not your summary of them. List every distinct ask as a numbered item, in the user's words. Include asks made mid-task and corrections ("also...", "actually make it..."). An ask you never acted on is a dropped item: implement it before going on.

## Stage 2: Prove each item with evidence

For each ledger item:

1. Re-read the file as it is on disk now. Do not trust your memory of the edit.
2. Record `file:line` evidence.
3. If the change has to land in more than one place (API and client, schema and migration, web and mobile, a renamed function and every caller), check every place. Grep for the old name too.

No evidence means not done. Implement it now or report it as not done.

## Stage 3: Fresh-eyes audit

Spawn one read-only subagent (the Explore agent in Claude Code). Give it only the numbered ledger and the repo path. Do not tell it what you changed, which files you edited, or your evidence; it has to find the implementation on its own. Instruct it:

> For each numbered requirement, search the codebase and decide whether it is actually implemented. Return DONE (with file:line proof), PARTIAL (what exists, what is missing) or NOT DONE for each. Be skeptical: a function existing is not proof that it is wired up and called. Trace the call path.

Fix anything PARTIAL or NOT DONE, then re-audit only those items.

## Stage 4: Run the project's own checks

Run the checks the project already has, for every layer you touched. Find them instead of inventing them: `package.json` scripts, `Makefile`, `pyproject.toml`, CI workflow files, the README.

| Stack | Typical checks |
|---|---|
| TypeScript / JavaScript | `npx tsc --noEmit`, `npm run lint`, `npm test`, `npm run build` |
| Python | `ruff check .`, `mypy .` or `pyright`, `pytest` |
| Go | `go vet ./...`, `go test ./...` |
| Rust | `cargo check`, `cargo test` |
| Flutter / Dart | `flutter analyze`, `flutter test` |
| A single JS file | `node --check <file>` |

A passing build does not prove the types are clean when the config skips type errors (Next.js `ignoreBuildErrors`, for example), so run the type checker directly. A failing check means not done: fix it and re-run. If a check cannot run here (a missing service, no credentials), say so; never report it as passed.

## Stage 5: Report in this format, and only this format

| # | Ask (user's words) | Status | Evidence | Audit | Checks |
|---|---|---|---|---|---|
| 1 | ... | DONE | `src/api.ts:48` | DONE | pass |
| 2 | ... | NOT DONE: why | | | |

- Items the audit failed are reported NOT DONE or PARTIAL. Never "mostly done".
- Anything skipped or deferred on purpose is listed, with the reason.
- "9 of 10 done, item 7 is not, because X. Want me to do it now?" is a good report. A false "all done" is the one unforgivable failure.

If the change is user-visible and the app can be run, check it running as well: a browser, a device, the CLI. Running behaviour beats static evidence. For Android apps, the `android-device-test` skill does this.
