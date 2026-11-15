"""How often each installed Claude Code skill was actually used, from local transcripts.

    python skill_usage.py [--days 30] [--project .]

Counts Skill tool calls (deduped by call id) and /slash invocations in user messages, then lists the
installed skills (user, project, enabled plugins) that went unused. Reads only. Prints skill names and
counts, never transcript text.
"""
import argparse
import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home() / ".claude"
SLASH = re.compile(r"<command-name>/?([\w:.-]+)</command-name>")


def skill_name(md: Path) -> str:
    m = re.search(r"^name:\s*(.+)$", md.read_text(encoding="utf-8", errors="ignore"), re.M)
    return m.group(1).strip() if m else md.parent.name


def installed(project: Path) -> dict:
    found = {}
    for md in (HOME / "skills").glob("*/SKILL.md"):
        found[skill_name(md)] = "user"
    for md in (project / ".claude" / "skills").glob("*/SKILL.md"):
        found[skill_name(md)] = "project"
    for md in (HOME / "commands").glob("*.md"):
        found[md.stem] = "user command"
    try:
        enabled = json.loads((HOME / "settings.json").read_text(encoding="utf-8")).get("enabledPlugins", {})
    except (OSError, ValueError):
        enabled = {}
    for key, on in enabled.items():
        if not on or "@" not in key:
            continue
        plugin, market = key.split("@", 1)
        versions = sorted((HOME / "plugins" / "cache" / market / plugin).glob("*"), key=lambda p: p.stat().st_mtime)
        if versions:  # newest cached version only
            for md in versions[-1].glob("skills/*/SKILL.md"):
                found[f"{plugin}:{skill_name(md)}"] = f"plugin {key}"
    return found


def usage(days: int, have: dict):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    uses, last, seen = Counter(), {}, set()
    for f in (HOME / "projects").glob("*/*.jsonl"):
        for line in f.open(encoding="utf-8", errors="ignore"):
            if '"Skill"' not in line and "<command-name>" not in line:
                continue
            try:
                d = json.loads(line)
                ts = datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))
            except (ValueError, KeyError, TypeError, AttributeError):
                continue
            if ts < since or d.get("type") not in ("assistant", "user"):
                continue
            content = (d.get("message") or {}).get("content")
            hits = []
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Skill":
                        if c.get("id") in seen:
                            continue
                        seen.add(c.get("id"))
                        hits.append(str((c.get("input") or {}).get("skill", "")))
            if d["type"] == "user":  # only installed skills and commands; /clear, /login etc. are CLI built-ins
                hits += [s for s in SLASH.findall(json.dumps(content)) if s in have]
            for h in filter(None, hits):
                uses[h] += 1
                last[h] = max(last.get(h, ts), ts)
    return uses, last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--project", default=".")
    a = ap.parse_args()
    have = installed(Path(a.project).resolve())
    uses, last = usage(a.days, have)

    print(f"# Skill usage, last {a.days} days\n")
    print("| skill | uses | last used | installed as |\n|---|---|---|---|")
    for name, n in uses.most_common():
        print(f"| {name} | {n} | {last[name]:%Y-%m-%d} | {have.get(name, 'built-in, another project, or removed')} |")
    unused = sorted(n for n in have if uses[n] == 0)
    print(f"\n{len(have)} skills installed, {len(have) - len(unused)} used in the last {a.days} days.")
    print(f"\n## Installed but unused in {a.days} days ({len(unused)})")
    print("\n".join(f"- {n} ({have[n]})" for n in unused) or "None.")


if __name__ == "__main__":
    main()
