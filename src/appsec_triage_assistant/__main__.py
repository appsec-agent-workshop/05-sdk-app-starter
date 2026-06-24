from __future__ import annotations

import json
import sys
from pathlib import Path

from .evidence_bundle import build_evidence_bundle


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python -m appsec_triage_assistant <alert-json>", file=sys.stderr)
        return 2

    alert_path = Path(sys.argv[1])
    bundle = build_evidence_bundle(alert_path)
    print(json.dumps(bundle, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
