---
name: loop-breaker
description: Get out of a debugging or build loop. Use when the same error keeps coming back, fixes keep failing, two or three attempts have been made without proof of the cause, or the user says "still broken", "same error", "we're going in circles", "you're stuck" or "start over". Stops the edits, reproduces the failure by hand, lists and tests every assumption, proves the root cause with evidence before any fix, and, if that fails, hands off cleanly to a fresh session.
---

# Loop breaker

When an agent loops, it is usually fixing a cause it assumed instead of one it proved. More edits make it worse. This is the way out.

## 1. Stop, and say so

- Stop editing. Say plainly: "I'm in a loop. I tried A, B and C, and none of them fixed it."
- List every change made during the loop (`git status`, `git diff`). Unproven changes are suspects too. Offer to stash or revert them (`git stash`) back to the last known state, and do it only with the user's yes.

## 2. Reproduce it yourself, from scratch

- Find the smallest command that shows the failure, and run it yourself. Capture the exact output, not a summary of it.
- Reproduce from a clean state: a fresh build, cleared caches, a restarted server. "It works after a restart" is a finding.
- If you can't reproduce it, that is the first problem to solve. Ask the user for the exact steps and the exact error.

## 3. List the assumptions, then test every one

Write down what the fixes so far took for granted, and mark each one VERIFIED or ASSUMED:

- The code that runs is the code you edited: right file, saved, rebuilt, not a stale bundle or a cached module.
- Config and environment values are what you think. Print them.
- Versions are what you think. Check `--version` and the lockfile.
- The input data is what you think. Print a real sample.
- The error message points at the real cause. It often doesn't.

Verify every ASSUMED item with a command. From here on, assume nothing until it is proven.

## 4. Prove the root cause before fixing

- Narrow it down mechanically: `git bisect`, commenting out halves, one log line at each boundary, checking the input and output of each step.
- Read the real source or docs of the library involved instead of guessing its behaviour, and search its issue tracker for the exact error text.
- The root cause is proven when you can say what happens, where (`file:line`) and why, and show the evidence: a log line, a failing assertion, or a value printed at the moment it goes wrong.
- Then fix that cause, once, and re-run the reproduction from step 2 to show it is gone.

## 5. Start fresh when the context is the problem

If steps 1 to 4 don't crack it, or the conversation is long and full of dead theories, the context itself is now in the way. Write a handoff and start a new chat, ideally with a different model:

```
## Handoff: <one-line symptom>
Repro: <exact command> -> <exact error>
Expected: <what should happen>
Ruled out, with evidence: <assumption: how it was verified>
Changes made and reverted: <list>
Open hypotheses (unproven): <list>
Files involved: <paths>
```

Save it as `HANDOFF.md` (or hand it to the user) and say: open a new session, paste the handoff, and start from the reproduction, not from the old theories. A different model brings fresh eyes.

## Never

- Apply a fix you can't explain.
- Stack a new fix on an unproven one. Revert first.
- Call it fixed without re-running the original reproduction.
