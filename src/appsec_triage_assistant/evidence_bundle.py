from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_evidence_bundle(alert_path: Path) -> dict[str, Any]:
    """Load a sample alert and normalize it into a workshop evidence bundle."""
    alert = json.loads(alert_path.read_text())

    return {
        "alert": {
            "source": alert.get("source"),
            "repository": alert.get("repository"),
            "alert_number": alert.get("alert_number"),
            "state": alert.get("state"),
            "severity": alert.get("severity"),
            "package_or_rule": alert.get("package_or_rule"),
            "manifest_or_location": alert.get("manifest_or_location"),
            "fixed_version_or_autofix": alert.get("fixed_version_or_autofix"),
        },
        "repository_context": {
            "owner": alert.get("owner"),
            "tests": alert.get("tests"),
            "codeql_status": alert.get("codeql_status"),
            "runtime_exposure": alert.get("runtime_exposure"),
        },
        "missing_evidence": alert.get("missing_evidence", []),
    }
