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

The Python code currently loads sample JSON and builds an evidence bundle. The Copilot SDK orchestration is intentionally left as TODOs for the guided build.

The sample JSON is intentional here: it gives the SDK section a deterministic loader and repeatable tests. A live GitHub REST loader is the next production-style loader, not the first workshop bootstrap step.

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Smoke test

```bash
python -m appsec_triage_assistant alerts/dependabot-sample.json
```

Optional test run:

```bash
pip install -e ".[dev]"
pytest
```

## Exercise

Ask Copilot:

```text
Use the README and scaffold files to implement the next smallest SDK step:
create a triage session that sends the evidence bundle to agents/triage.agent.md.
Keep write/API actions human-approved and preserve the JSON evidence bundle.
```

Start with `src/appsec_triage_assistant/sdk_todo.py`. The workshop goal is to map the deterministic loader, agents, skills, challenge step, judge gate, and audit artifacts. Live GitHub API loaders and production credentials are intentionally out of scope for the first SDK slice.

For a follow-up implementation, replace the sample JSON loader with read-only GitHub REST calls equivalent to:

```bash
gh api repos/OWNER/REPO/code-scanning/alerts?state=open
gh api repos/OWNER/REPO/dependabot/alerts?state=open
```

## Safety boundary

Do not implement automatic dismissal, severity changes, risk acceptance, or campaign creation in the workshop.

Treat stale, missing, or timed-out CodeQL as missing evidence that caps confidence. Do not interpret absent analysis as proof of low risk.
