from pathlib import Path

from appsec_triage_assistant.sdk_todo import (
    build_custom_agent_configs,
    create_triage_session,
    load_agent,
)


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


def test_build_custom_agent_configs_maps_agents_to_skills() -> None:
    configs = build_custom_agent_configs(Path("."))

    by_name = {config["name"]: config for config in configs}
    assert by_name["triage-agent"]["skills"] == ["appsec-alert-triage"]
    assert by_name["triage-agent"]["tools"] == ["view", "grep", "glob"]
    assert by_name["appsec-triage-challenger"]["skills"] == ["challenge-triage-report"]
    assert by_name["appsec-triage-judge"]["skills"] == ["report-quality"]
    assert by_name["appsec-triage-judge"]["tools"] == []
