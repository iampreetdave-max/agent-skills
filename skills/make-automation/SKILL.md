---
name: make-automation
description: Design, build and debug automations on Make.com (formerly Integromat), and decide when Make, Python, or both together are the right tool. Covers checking Make's current docs first, connections and multiple accounts, webhooks between Python and Make, Microsoft Teams and other painful APIs, human approval before anything goes out, never acting twice, dry runs and error handling. Use when the user mentions Make, Make.com, Integromat or a scenario, or wants a scheduled or event-driven automation across SaaS tools.
---

# Make.com automations

Make is the best tool for automations that must run every day, be easy to track, and connect to many accounts. Python is the best tool for heavy logic. The strongest setups use both.

## 0. Check the current docs first, and never assume anything

Make changes often: modules get new versions, fields get renamed, limits and pricing move. Before designing anything, read the current docs for the apps and modules involved at help.make.com, and at developers.make.com for the API and custom apps. Don't build from memory. Never assume a module field means what its name suggests: run the module once and read the real output bundle.

## 1. Make, Python, or both

- **Make** when the automation must run reliably every day, be visible and trackable (execution history, per-run logs, alerts), be maintained by non-developers, or reach apps whose APIs are painful. Microsoft Teams is the classic case: the Graph API needs an app registration, permissions and admin consent, while Make's Teams connection handles that sign-in for you.
- **Python** when the logic is heavy (parsing, ML, big data, complex branching), needs libraries, or must be unit-tested. Make's modules mostly wrap the same public APIs, so anything Make does, Python can do through the API, an SDK or an MCP server.
- **Both** (often the best): Python does the hard thinking and Make does the delivery. Python posts a JSON payload to a Make custom webhook, and the scenario sends the Teams message, updates the CRM or writes the row. Make can call Python back with its HTTP module.
- If a step can't be built cleanly in Make within a few hours, move that step to Python. Don't fight the tool.

## 2. Connections

- Create each connection once and reuse it. Make can hold several connections for the same app (two Gmail inboxes, two Teams tenants), so name them clearly, for example "Teams, support tenant".
- Credentials live in connections, never pasted into HTTP module headers or text fields.
- Prefer Make's official apps. Community-built apps are often unmaintained and break silently, so avoid them. If no official module covers the action, call the service's API directly with the HTTP module.

## 3. Scenario design

- **Trigger:** instant (webhook or instant trigger) when it must react now; scheduled when polling is fine. Every run and every module consumes your plan's operations or credits, so check current pricing before choosing a one-minute schedule.
- **One scenario, one job.** Chain scenarios through webhooks rather than building one 60-module monster.
- Put filters straight after the trigger to drop what you don't need early. It is cheaper and clearer.
- Use routers for branches, and iterators and aggregators for lists. Set each aggregator's source module carefully: aggregating at the wrong level is the classic bug.
- Export the blueprint (JSON) after every meaningful change and keep it in git, so you have history and a restore point.

## 4. Webhooks between Python and Make

- A custom webhook gives you a URL. Define its data structure from a real sample payload.
- The URL is a secret: anyone who has it can trigger the scenario. Send a shared secret from Python and make the first filter check it.
- Send an idempotency key with every payload, for example a hash of the source record id.
- When Python needs an answer (a status, a created id), end the scenario with a Webhook response module, and set a timeout on the Python side.

```python
import hashlib, os, requests

payload = {
    "secret": os.environ["MAKE_HOOK_SECRET"],
    "key": hashlib.sha256(record_id.encode()).hexdigest(),
    "message": text,
}
r = requests.post(os.environ["MAKE_HOOK_URL"], json=payload, timeout=30)
r.raise_for_status()
```

## 5. A human approves before anything goes out

For automations that post publicly or message clients, the AI or script drafts and a person approves.

- The draft goes to an approval channel (Slack, Teams or email) with Approve and Reject links. Each link is a webhook URL carrying the item id, the action and a secret.
- A second scenario receives the click, checks that the item is still pending, then publishes it and marks it done.
- Nothing publishes without an approval record. Log who approved what, and when.
- Remove or blur names and personal details before anything is posted publicly.

## 6. Never act twice, and stay safe while testing

- **Dedupe:** store the idempotency key in a Make data store (or your database) when an action succeeds, and check it before acting. Retries and reruns then do no harm.
- **Dry-run mode:** a variable at the top of the scenario, or a `mode` field sent from Python, routes output to a log or test channel instead of the real destination. Keep it on while building: no live writes to client channels during development.
- Test with "Run once" on real sample data, read every module's output bundle, and only then switch on the schedule.

## 7. When it fails

- Add error handlers to every module that talks to the outside world: Resume with a fallback value, Ignore for optional steps, Break to retry later, and Rollback or Commit around data store work.
- Turn on storing incomplete executions, so failed runs can be fixed and resumed instead of lost.
- Alert a person on errors, by email or a Teams or Slack message naming the scenario and the error.
- Watch rate limits and pagination: set a maximum on search modules and handle further pages.

## 8. Handoff

Document every scenario: its trigger, what it reads, what it writes, the connections it uses (by name, never secrets), the schedule, operations per run, the owner, and how to pause it. Keep the blueprint export next to the document.
