# 05 - Copilot SDK app starter

Use this repository during the workshop section:
**Copilot SDK app for the alert triage use case**.

## Goal

Start a controlled AppSec triage app without spending workshop time on project bootstrap.

The app shape is:

```text
Alert loader
  -> AlertEvidenceBundle
  -> triage agent
  -> challenger / report validator
  -> judge or approve/rework gate
  -> human action draft
```

## What is already scaffolded

```text
alerts/
agents/
skills/
prompts/
src/appsec_triage_assistant/
tests/
output/
```

The Python code currently loads sample JSON, builds an evidence bundle, and emits the next-smallest deterministic triage-session payload. Live model/API orchestration is intentionally left as a follow-up step.

The sample JSON is intentional here: it gives the SDK section a deterministic loader and repeatable tests. A live GitHub REST loader is the next production-style loader, not the first workshop bootstrap step.

## Setup

Use `python3` instead of `python` if your system does not provide `python` on `PATH`.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Smoke test

```bash
python -m appsec_triage_assistant alerts/dependabot-sample.json
python -m appsec_triage_assistant alerts/dependabot-sample.json --triage-session
```

Optional test run:

```bash
pip install -e ".[dev]"
pytest
```

## Exercise

Ask Copilot:

```text
Use the README and scaffold files to inspect the deterministic triage-session payload.
Explain how agents/triage.agent.md, the skills directory, and the evidence bundle would map to a future Copilot SDK runner.
Then choose one next implementation slice, such as adding the challenger/judge step or replacing the sample JSON loader with read-only GitHub REST calls.
```

Start with `src/appsec_triage_assistant/sdk_todo.py`. The workshop goal is to understand the deterministic loader, agents, skills, challenge step, judge gate, and audit artifacts. Live GitHub API loaders and production credentials are intentionally out of scope for the first SDK slice.

The deterministic triage-session payload already:

- loads `agents/triage.agent.md`
- registers the `skills/` directory
- embeds the `AlertEvidenceBundle`
- marks write/API actions as human-approved

A live model call is optional or facilitator-led unless an SDK package and credentials are provided.

For a follow-up implementation, replace the sample JSON loader with read-only GitHub REST calls equivalent to:

```bash
gh api "repos/OWNER/REPO/code-scanning/alerts?state=open"
gh api "repos/OWNER/REPO/dependabot/alerts?state=open"
```

## Safety boundary

Do not implement automatic dismissal, severity changes, risk acceptance, or campaign creation in the workshop.
