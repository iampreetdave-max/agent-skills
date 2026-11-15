"""Daily install-signal snapshot for this repo, kept beyond GitHub's 14-day traffic window.

Every `/plugin marketplace add` (and every marketplace update) clones this repo, so unique
cloners per day is the closest public signal to installs. It also counts updates, CI and bots.
Run from a checkout of the `stats` branch; writes traffic.json and README.md there.

    TRAFFIC_TOKEN=<token with Administration: read> GITHUB_REPOSITORY=owner/repo python traffic.py
"""
import datetime
import json
import os
import urllib.request

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ.get("TRAFFIC_TOKEN")
if not TOKEN:
    raise SystemExit("TRAFFIC_TOKEN is not set: add a fine-grained token with Administration (read) "
                     "on this repo as the repository secret TRAFFIC_TOKEN.")


def get(path: str):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}{path}", headers={
        "Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


data = json.load(open("traffic.json")) if os.path.exists("traffic.json") else {"days": {}, "snapshots": {}}
clones, views = get("/traffic/clones"), get("/traffic/views")
for kind, payload in (("clones", clones), ("views", views)):
    for d in payload[kind]:  # GitHub revises recent days, so the last 14 are rewritten each run
        data["days"].setdefault(d["timestamp"][:10], {})[kind] = {"count": d["count"], "uniques": d["uniques"]}
repo = get("")
today = datetime.date.today().isoformat()
data["snapshots"][today] = {"stars": repo["stargazers_count"], "forks": repo["forks_count"],
                            "unique_cloners_14d": clones["uniques"], "unique_visitors_14d": views["uniques"]}
with open("traffic.json", "w") as f:
    json.dump(data, f, indent=1, sort_keys=True)

days = sorted(data["days"].items())
cell = lambda v, kind, key: v.get(kind, {}).get(key, 0)
rows = "\n".join(f"| {day} | {cell(v, 'clones', 'uniques')} | {cell(v, 'clones', 'count')} | "
                 f"{cell(v, 'views', 'uniques')} | {cell(v, 'views', 'count')} |" for day, v in reversed(days[-30:]))
first = days[0][0] if days else today
snap = data["snapshots"][today]
with open("README.md", "w") as f:
    f.write(f"""# Install signal for iampreetdave-skills

Every `/plugin marketplace add` or update clones this repo, so **unique cloners** is the closest
public signal to installs. It also counts updates, CI and bots, and GitHub reports it a day late.

- Unique cloners, last 14 days: **{snap['unique_cloners_14d']}**
- Sum of daily unique cloners since {first}: **{sum(cell(v, 'clones', 'uniques') for _, v in days)}**
- Clones since {first}: {sum(cell(v, 'clones', 'count') for _, v in days)}; page views: {sum(cell(v, 'views', 'count') for _, v in days)}
- Stars: {snap['stars']} · Forks: {snap['forks']}

Updated {today} by `.github/workflows/traffic.yml`.

| Day | Unique cloners | Clones | Unique visitors | Views |
|---|---|---|---|---|
{rows}
""")
print(f"{len(days)} days recorded; unique cloners in the last 14 days: {snap['unique_cloners_14d']}")
