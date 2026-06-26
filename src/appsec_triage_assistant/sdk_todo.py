"""SDK session helpers for the guided AppSec triage build.

The deterministic payload is the audit boundary. The SDK runner uses that
payload as input to a real Copilot SDK session with custom agents and skills.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .evidence_bundle import build_evidence_bundle

AGENT_SKILLS = {
    "triage-agent": ["appsec-alert-triage"],
    "appsec-triage-challenger": ["challenge-triage-report"],
    "appsec-triage-judge": ["report-quality"],
}

TOOL_ALIASES = {
    "read": "view",
    "search": "grep",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    if not markdown.startswith("---\n"):
        return {}, markdown

    _, frontmatter, body = markdown.split("---\n", 2)
    metadata: dict[str, Any] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            metadata[key.strip()] = [
                item.strip().strip('"').strip("'")
                for item in value.strip("[]").split(",")
                if item.strip()
            ]
        else:
            metadata[key.strip()] = value.strip('"').strip("'")

    return metadata, body.strip()


def load_agent(agent_path: Path) -> dict[str, Any]:
    """Load a markdown custom-agent file into SDK-friendly metadata."""
    metadata, instructions = _split_frontmatter(_read_text(agent_path))
    return {
        "path": str(agent_path),
        "name": metadata.get("name", agent_path.stem),
        "description": metadata.get("description", ""),
        "tools": metadata.get("tools", []),
        "instructions": instructions,
    }


def build_custom_agent_configs(project_root: Path = Path(".")) -> list[dict[str, Any]]:
    """Build Copilot SDK custom-agent configs from the markdown agent files."""
    project_root = project_root.resolve()
    configs: list[dict[str, Any]] = []
    for agent_path in [
        project_root / "agents" / "triage.agent.md",
        project_root / "agents" / "challenger.agent.md",
        project_root / "agents" / "judge.agent.md",
    ]:
        agent = load_agent(agent_path)
        tools = [TOOL_ALIASES.get(tool, tool) for tool in agent["tools"]]
        if "grep" in tools and "glob" not in tools:
            tools.append("glob")
        configs.append(
            {
                "name": agent["name"],
                "description": agent["description"],
                "prompt": agent["instructions"],
                "tools": tools,
                "skills": AGENT_SKILLS.get(agent["name"], []),
            }
        )
    return configs


def create_triage_session(
    alert_path: Path,
    *,
    project_root: Path = Path("."),
    agent_path: Path | None = None,
    skill_dir: Path | None = None,
) -> dict[str, Any]:
    """Create the next-smallest triage session payload.

    The returned object is deterministic and safe to audit. A future production
    runner can submit ``messages`` to the Copilot SDK without changing the
    evidence bundle shape.
    """
    project_root = project_root.resolve()
    agent_path = agent_path or project_root / "agents" / "triage.agent.md"
    skill_dir = skill_dir or project_root / "skills"
    evidence_bundle = build_evidence_bundle(alert_path)
    bundle_json = json.dumps(evidence_bundle, indent=2, sort_keys=True)
    session_seed = f"{agent_path}:{bundle_json}".encode("utf-8")

    return {
        "session": {
            "id": hashlib.sha256(session_seed).hexdigest()[:16],
            "kind": "appsec-triage",
            "status": "draft-ready",
        },
        "agent": load_agent(agent_path),
        "skill_directory": str(skill_dir),
        "evidence_bundle": evidence_bundle,
        "messages": [
            {
                "role": "system",
                "content": "Use the loaded triage agent instructions and registered skills. Keep all write/API actions human-approved.",
            },
            {
                "role": "user",
                "content": (
                    "Draft a human-reviewed AppSec alert triage recommendation "
                    "from this AlertEvidenceBundle. Preserve facts, missing "
                    f"evidence, and confidence ceilings.\n\n```json\n{bundle_json}\n```"
                ),
            },
        ],
        "human_approval_required_for": [
            "security alert dismissal",
            "severity changes",
            "risk acceptance",
            "remediation approval",
            "campaign creation",
            "write/API actions",
            "shell execution",
        ],
    }


async def run_sdk_triage(
    alert_path: Path,
    *,
    project_root: Path = Path("."),
    model: str | None = None,
    timeout: float = 180.0,
) -> str:
    """Run the triage task through a real GitHub Copilot SDK session."""
    from copilot import CopilotClient
    from copilot.rpc import PermissionDecisionApproveOnce, PermissionDecisionReject
    from copilot.session import PermissionRequestResult
    from copilot.session_events import AssistantMessageData
    from copilot.session_events import PermissionRequest

    project_root = project_root.resolve()
    session_payload = create_triage_session(alert_path, project_root=project_root)

    def approve_read_only(
        request: PermissionRequest, invocation: dict[str, str]
    ) -> PermissionRequestResult:
        if request.kind == "read":
            return PermissionDecisionApproveOnce()
        return PermissionDecisionReject()

    session_kwargs: dict[str, Any] = {
        "on_permission_request": approve_read_only,
        "working_directory": str(project_root),
        "skill_directories": [str(project_root / "skills")],
        "custom_agents": build_custom_agent_configs(project_root),
        "agent": session_payload["agent"]["name"],
    }
    if model:
        session_kwargs["model"] = model

    async with CopilotClient() as client:
        async with await client.create_session(**session_kwargs) as sdk_session:
            reply = await sdk_session.send_and_wait(
                session_payload["messages"][1]["content"],
                timeout=timeout,
            )

    if reply is not None and isinstance(reply.data, AssistantMessageData):
        return reply.data.content or ""
    return ""
