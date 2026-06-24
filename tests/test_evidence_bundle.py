from pathlib import Path

from appsec_triage_assistant.evidence_bundle import build_evidence_bundle


def test_build_evidence_bundle() -> None:
    bundle = build_evidence_bundle(Path("alerts/dependabot-sample.json"))

    assert bundle["alert"]["source"] == "dependabot"
    assert bundle["alert"]["severity"] == "high"
    assert "reachability not established" in bundle["missing_evidence"]
