# agent-skills

Skills for Claude Code by [Preet Dave](https://iampreetdave.me). Each one came out of a real project where the agent kept making the same mistake, and each one is a single `SKILL.md` you can read in two minutes.

| Skill | What it does |
|---|---|
| [done-gate](skills/done-gate/SKILL.md) | Stops the agent saying "done" when it isn't. Rebuilds the list of asks from your own words, proves each one with `file:line` evidence, has a fresh subagent audit the work without being told what changed, and runs your project's own checks. The report is a table where a missing item is shown as missing. |
| [android-device-test](skills/android-device-test/SKILL.md) | Tests your app on a real Android phone over adb. Installs the build, taps real UI elements found in the view hierarchy (not guessed pixels), cuts the network, kills the process, rotates the screen, and reports pass or fail with screenshots and logcat. |
| [exam-sheet](skills/exam-sheet/SKILL.md) | Turns a syllabus and past papers into one printable revision page. Chapters are ranked by the marks they actually carried, every topic is an exam-ready answer with a hand-drawn diagram, and a verifier catches broken diagrams before you see them. Notes for GTU included. |

## Install in Claude Code

```
/plugin marketplace add iampreetdave-max/agent-skills
/plugin install done-gate@preet-skills
/plugin install android-device-test@preet-skills
/plugin install exam-sheet@preet-skills
```

Install only the ones you want. Each skill loads when your request matches its description, or call it directly, for example `/done-gate`.

## Without the plugin system

The skills use the open `SKILL.md` format. Copy a folder from `skills/` into `~/.claude/skills/` (all projects) or `.claude/skills/` (one project), or into the skills folder of any other agent that reads `SKILL.md`.

## Requirements

- **done-gate**: nothing extra.
- **android-device-test**: `adb` (Android SDK platform-tools) and a phone with USB debugging on, or an emulator.
- **exam-sheet**: Python 3.9+. For the layout checks, `pip install playwright` then `playwright install chromium`; without them the verifier still checks structure and diagrams.

## License

MIT
