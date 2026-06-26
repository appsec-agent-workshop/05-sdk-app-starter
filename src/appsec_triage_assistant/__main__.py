from __future__ import annotations

import json
import asyncio
from argparse import ArgumentParser
from pathlib import Path

from .evidence_bundle import build_evidence_bundle
from .sdk_todo import create_triage_session, run_sdk_triage


def main() -> int:
    parser = ArgumentParser(description="Build AppSec alert evidence bundles.")
    parser.add_argument("alert_json", help="Path to a workshop alert JSON file.")
    parser.add_argument(
        "--triage-session",
        action="store_true",
        help="Emit the deterministic triage-session payload for agents/triage.agent.md.",
    )
    parser.add_argument(
        "--sdk-run",
        action="store_true",
        help="Run the triage task through a real GitHub Copilot SDK session.",
    )
    parser.add_argument("--model", help="Optional Copilot model identifier for --sdk-run.")
    args = parser.parse_args()

    alert_path = Path(args.alert_json)
    if args.sdk_run:
        print(asyncio.run(run_sdk_triage(alert_path, project_root=Path("."), model=args.model)))
        return 0

    payload = (
        create_triage_session(alert_path, project_root=Path("."))
        if args.triage_session
        else build_evidence_bundle(alert_path)
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
