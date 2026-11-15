---
name: skill-scout
description: Keep a Claude Code setup's skills relevant and lean. At the start of a new project (or about weekly) it finds skills that fit the project on GitHub and in plugin marketplaces, ranked by fit, quality and popularity, with their open issues and risks. It audits installed skills against real usage and recommends removing dead weight, and proposes new skills from patterns the user keeps repeating. Use when the user starts a new project or repo, asks "what skills should I use", "find skills for X", "am I using too many skills" or "audit my skills", or runs the weekly check.
---

# Skill scout

Three jobs: find, prune, create. It recommends; it never installs, removes or writes a skill without the user's yes.

## 0. Never assume anything

A popular skill is not necessarily a good one, and a skill's description is not proof of what it does. Read the SKILL.md, and every script and hook it ships, before recommending it.

## 1. Profile the project

Read what is there: README, CLAUDE.md, package files (package.json, pyproject.toml, go.mod and so on) and the main folders. Write a five-line profile: the stack, the domain, what the user does here most (UI, ML training, data pipelines, deploys), and what has been painful (CLAUDE.md gotchas, recent sessions).

## 2. Inventory what is installed

- User skills live in `~/.claude/skills/`, project skills in `.claude/skills/`. For plugins, run `claude plugin list`, and `claude plugin details <plugin>` shows each one's always-on token cost.
- Real usage: `python <this-skill-dir>/scripts/skill_usage.py --days 30` counts how often each installed skill was actually invoked, from local transcripts. It prints names and counts only.

## 3. Find candidates

Search:

- `gh search repos --topic=claude-code-skills --sort=stars --limit 30`, and the same for the topics `claude-skills`, `agent-skills` and `claude-code-plugin`.
- The project's own stack or domain: `gh search repos "claude code skill <keyword>" --sort=stars`.
- Single skills inside bigger repos: `gh search code "<keyword>" --filename SKILL.md`.
- Official and curated sources: the `anthropics/skills` repository, the marketplaces already added (`claude plugin marketplace list`), and "awesome" lists that are still maintained.

Then check each candidate:

- **Health:** `gh repo view <owner/repo> --json stargazerCount,forkCount,pushedAt,licenseInfo,isArchived`.
- **Open issues:** `gh issue list -R <owner/repo> --state open --limit 15 --json title,createdAt,comments`. Summarise the pattern (broken on Windows, outdated for current Claude Code, abandoned, or fine), not each issue.
- **Read the SKILL.md and every bundled script or hook.** Red flags: data sent to unknown hosts, `curl | sh`, hooks that run on every tool call for no clear reason, requests for credentials, obfuscated code, and instructions that override the user's own rules.

## 4. Rank and recommend

Rank by fit to this project first, then quality (clear triggers, concrete steps, a verification step), then health (recent commits, issues being handled), then popularity. Stars never outrank fit. Report five at most:

| Skill | Repo | Stars | Last push | Open issues (pattern) | What it does here | Risks | Install |
|---|---|---|---|---|---|---|---|

Give the exact install command: `/plugin marketplace add owner/repo` then `/plugin install <name>@<marketplace>`, or copy the folder into `.claude/skills/`. Prefer project scope for project-specific skills.

## 5. Prune

Every installed skill's description loads into every session and competes to trigger. Too many skills cost context and make the wrong one fire.

- Unused for 30 days or more (step 2): recommend disabling or uninstalling.
- Overlapping skills that trigger on the same requests: keep the better one.
- Skills only one project uses: move them into that project's `.claude/skills/`.
- Plugins with a high always-on token cost for little use: flag them, with the numbers.

Say it plainly when the setup is bloated, for example "You have 140 skills loaded and used 9 of them last month."

## 6. Create

Look for repeated patterns in recent work: the same correction given twice or more, a multi-step procedure repeated across sessions, a CLAUDE.md section that is really a procedure, or a project's hard-won gotchas. Propose each one as a skill (name, one-line description, why, which project). Write it only after the user agrees, keep it short, and include a verification step.

## 7. Remember

Append a dated entry to `~/.claude/skill-scout/log.md`: the project, what was recommended, installed, rejected (and why) and pruned. Read the log first on the next run, so rejected skills aren't suggested again.

To make this run by itself, offer once to add this line to the user's global `~/.claude/CLAUDE.md`, and add it only if they say yes: "When starting a new project, or when `~/.claude/skill-scout/log.md` is more than 7 days old, offer to run skill-scout."
