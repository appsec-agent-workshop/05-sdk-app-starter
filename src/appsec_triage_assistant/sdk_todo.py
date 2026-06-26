"""Small, deterministic triage-session builder for the guided SDK build.

This module deliberately stops before live model/API orchestration. It creates
the session payload a Copilot SDK runner would send to the triage agent while
preserving the normalized JSON evidence bundle and the human-approval boundary.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .evidence_bundle import build_evidence_bundle


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
