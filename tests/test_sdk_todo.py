from pathlib import Path

from appsec_triage_assistant.sdk_todo import create_triage_session, load_agent


def test_load_agent_reads_frontmatter_and_instructions() -> None:
    agent = load_agent(Path("agents/triage.agent.md"))

    assert agent["name"] == "triage-agent"
    assert "read" in agent["tools"]
    assert "Do not dismiss alerts" in agent["instructions"]


def test_create_triage_session_sends_bundle_to_agent() -> None:
    session = create_triage_session(
        Path("alerts/dependabot-sample.json"),
        project_root=Path("."),
    )

    assert session["agent"]["name"] == "triage-agent"
    assert session["evidence_bundle"]["alert"]["source"] == "dependabot"
    assert "AlertEvidenceBundle" in session["messages"][1]["content"]
    assert "reachability not established" in session["messages"][1]["content"]
    assert "write/API actions" in session["human_approval_required_for"]
