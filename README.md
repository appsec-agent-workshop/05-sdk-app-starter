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

## Exercise

Ask Copilot:

```text
Use the README and scaffold files to implement the next smallest SDK step:
create a triage session that sends the evidence bundle to agents/triage.agent.md.
Keep write/API actions human-approved and preserve the JSON evidence bundle.
```

## Safety boundary

Do not implement automatic dismissal, severity changes, risk acceptance, or campaign creation in the workshop.
