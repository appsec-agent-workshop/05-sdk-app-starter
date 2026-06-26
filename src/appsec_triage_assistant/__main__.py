from __future__ import annotations

import json
from argparse import ArgumentParser
from pathlib import Path

from .evidence_bundle import build_evidence_bundle
from .sdk_todo import create_triage_session


def main() -> int:
    parser = ArgumentParser(description="Build AppSec alert evidence bundles.")
    parser.add_argument("alert_json", help="Path to a workshop alert JSON file.")
    parser.add_argument(
        "--triage-session",
        action="store_true",
        help="Emit the deterministic triage-session payload for agents/triage.agent.md.",
    )
    args = parser.parse_args()

    alert_path = Path(args.alert_json)
    payload = (
        create_triage_session(alert_path, project_root=Path("."))
        if args.triage_session
        else build_evidence_bundle(alert_path)
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
