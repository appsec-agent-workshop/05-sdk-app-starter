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

The Python code loads sample JSON, builds an evidence bundle, prepares custom-agent configs from `agents/`, registers `skills/`, and can run the triage task through the GitHub Copilot SDK.

The sample JSON is intentional here: it gives the SDK section a deterministic loader and repeatable tests. A live GitHub REST loader is the next production-style loader, not the first workshop bootstrap step.

## Setup

Use `python3` instead of `python` if your system does not provide `python` on `PATH`.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
python -m copilot download-runtime
```

## Smoke test

```bash
python -m appsec_triage_assistant alerts/dependabot-sample.json
python -m appsec_triage_assistant alerts/dependabot-sample.json --triage-session
```

SDK-backed run:

```bash
copilot login
python -m appsec_triage_assistant alerts/dependabot-sample.json --sdk-run
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
Run the GitHub Copilot SDK path with --sdk-run.
Explain how agents/triage.agent.md, the skills directory, and the evidence bundle are passed into the SDK session.
Then choose one next implementation slice, such as adding the challenger/judge turn or replacing the sample JSON loader with read-only GitHub REST calls.
```

Start with `src/appsec_triage_assistant/sdk_todo.py`. The workshop goal is to connect the deterministic loader, Copilot SDK session, custom agents, skills, challenge step, judge gate, and audit artifacts. Live GitHub API loaders are intentionally out of scope for the first SDK slice.

The deterministic triage-session payload already:

- loads `agents/triage.agent.md`
- registers the `skills/` directory
- embeds the `AlertEvidenceBundle`
- records which write/API actions require human approval

The SDK-backed run already:

- creates a `CopilotClient`
- creates a session with `custom_agents`
- registers `skill_directories`
- selects `triage-agent`
- sends the frozen evidence bundle as the user task

The next open-ended engineering step is to add the challenger/judge loop or a read-only GitHub alert loader.

For a follow-up implementation, replace the sample JSON loader with read-only GitHub REST calls equivalent to:

```bash
gh api "repos/OWNER/REPO/code-scanning/alerts?state=open"
gh api "repos/OWNER/REPO/dependabot/alerts?state=open"
```

## Safety boundary

Do not implement automatic dismissal, severity changes, risk acceptance, or campaign creation in the workshop.
