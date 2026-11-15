# agent-skills

Skills for Claude Code by [Preet Dave](https://iampreetdave.me). Each one came out of real projects where an AI agent kept making the same mistake, and each one is a single `SKILL.md` you can read in a few minutes. One rule runs through all of them: never assume anything.

## Install everything with one command

From your terminal (macOS, Linux, Git Bash, PowerShell 7):

```
claude plugin marketplace add iampreetdave-max/agent-skills && claude plugin install all-skills@preet-skills
```

On Windows PowerShell 5, replace `&&` with `;`. Then restart Claude Code.

## Packs

| Pack | Skills |
|---|---|
| **all-skills** | all ten below |
| **senior-pack** | done-gate, loop-breaker, skill-scout, doc-extraction, make-automation, honest-model-eval, compliance-check |
| **student-pack** | hackathon-sprint, exam-sheet, done-gate, loop-breaker |

## The skills

| Skill | What it does |
|---|---|
| [done-gate](skills/done-gate/SKILL.md) | Stops the agent saying "done" when it isn't. Rebuilds the list of asks from your own words, proves each one with `file:line` evidence, has a fresh subagent audit the work without being told what changed, and runs your project's own checks. A missing item is reported as missing. |
| [loop-breaker](skills/loop-breaker/SKILL.md) | For when the same error keeps coming back. Stops the edits, reproduces the failure by hand, tests every assumption, and proves the root cause with evidence before any fix. If that fails, it writes a handoff for a fresh session on a different model. |
| [compliance-check](skills/compliance-check/SKILL.md) | Catches compliance gaps before a vibe-coded product ships. Reads the code to see what data it touches and who sees it, asks only what the code can't answer (where users are, minors, payments, health or financial data, AI decisions about people), maps India's DPDP Act, GDPR, the EU AI Act, CCPA, COPPA, HIPAA, PCI DSS, accessibility and messaging consent, and pushes a prioritised fix list with `file:line` evidence. Not legal advice. |
| [skill-scout](skills/skill-scout/SKILL.md) | Finds skills that fit your project on GitHub and plugin marketplaces, ranked by fit, then health, then stars, with a summary of their open issues and a read of their code. Counts which of your installed skills you actually use (a script reads your local history) and tells you what to remove. Proposes new skills from the corrections you keep repeating. |
| [doc-extraction](skills/doc-extraction/SKILL.md) | OCR and document extraction whose numbers you can trust. Text layer first, OCR or a vision model only where needed, each page read with context from the one before, deterministic validators (running balance to the cent, checksums, totals) that decide what is correct, one adapter per layout, and human review built in. |
| [make-automation](skills/make-automation/SKILL.md) | Make.com automations: when to use Make, Python or both together, webhooks between them, Microsoft Teams and other painful APIs, multiple accounts, human approval before anything goes out, never acting twice, dry runs and error handling. |
| [honest-model-eval](skills/honest-model-eval/SKILL.md) | Stops vibe-coded ML models from leaking. Audits the data first (a script flags imbalance, ID columns and leak suspects), checks every feature is really available at prediction time, splits by time, compares against the market, and reports calibrated results with their uncertainty. |
| [hackathon-sprint](skills/hackathon-sprint/SKILL.md) | Building to win a hackathon with an AI agent: pick the hard category, mine open source and papers first, scope to one flawless demo path, deploy to a real URL, and a sleek deck with a rehearsed three-minute demo. |
| [android-device-test](skills/android-device-test/SKILL.md) | Tests your app on a real Android phone over adb. Installs the build, taps real UI elements found in the view hierarchy (not guessed pixels), cuts the network, kills the process, and reports pass or fail with screenshots and logcat. |
| [exam-sheet](skills/exam-sheet/SKILL.md) | Turns a syllabus and past papers into one printable revision page. Chapters are ranked by the marks they actually carried, every topic is an exam-ready answer with a hand-drawn diagram, and a verifier catches broken diagrams. Notes for GTU included. |

## Install in Claude Code

```
/plugin marketplace add iampreetdave-max/agent-skills
/plugin install senior-pack@preet-skills
```

Or install single skills, for example `/plugin install loop-breaker@preet-skills`. Install one pack or single skills, not several overlapping ones, or the same skill loads twice.

## Using them

- Each skill loads by itself when your request matches its description: "verify it before you say done", "I'm stuck, same error again", "find skills for this project".
- Or call one by name: type `/`, then the install name and the skill, for example `/all-skills:loop-breaker` or `/loop-breaker:loop-breaker`.
- Get updates with `claude plugin marketplace update preet-skills`. Remove with `claude plugin uninstall <name>@preet-skills`.

## Without the plugin system

The skills use the open `SKILL.md` format. Copy a folder from `skills/` into `~/.claude/skills/` (all projects) or `.claude/skills/` (one project), or into the skills folder of any other agent that reads `SKILL.md`.

## Requirements

- **android-device-test**: `adb` (Android SDK platform-tools) and a phone with USB debugging on, or an emulator.
- **exam-sheet**: Python 3.9+. For the layout checks, `pip install playwright` then `playwright install chromium`; without them the verifier still checks structure and diagrams.
- **honest-model-eval**: Python with pandas (and pyarrow for Parquet) for the audit script.
- **skill-scout**: the GitHub CLI (`gh`), signed in, and Python 3.9+ for the usage script.
- The rest need nothing extra.

## License

MIT
