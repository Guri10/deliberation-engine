import json

from engine.config import SYSTEM_CONTEXT
from engine.deliberation import run_deliberation

FEATURE_REQUEST = "Project managers should see the full engagement history before a new mission."


def proposal(round_no: int) -> str:
    return json.dumps({
        "scope_in": [f"Engagement timeline per country (v{round_no})"],
        "scope_out": ["Other teams' confidential meeting notes"],
        "assumptions": [{"id": "A1", "statement": "History means the last 5 years"}],
        "success_criteria": [{"metric": "Time to brief before a mission", "threshold": "under 10 minutes"}],
    })


def critique(verdict: str) -> str:
    return json.dumps({
        "verdict": verdict,
        "challenges": [] if verdict == "SATISFIED" else [
            {"id": "C1", "target": "A1", "text": "Why 5 years? Treaties often span decades."}
        ],
    })


DECISION = json.dumps({
    "scope_in": ["Engagement timeline per country"],
    "scope_out": ["Other teams' confidential meeting notes"],
    "assumptions": [{"statement": "History means the last 5 years", "status": "Challenged-and-held"}],
    "open_questions": ["Who approves access to confidential records?"],
    "success_criteria": [{"metric": "Time to brief before a mission", "threshold": "under 10 minutes"}],
})


class ScriptedClient:
    """Fake model client: returns canned replies in call order and records every call."""

    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.calls: list[dict] = []

    def __call__(self, system, messages, output_model):
        self.calls.append({"system": system, "messages": messages, "output_model": output_model})
        return self.replies.pop(0)


def test_two_round_run_ends_satisfied_and_writes_trace_and_decision_document(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE"),
        proposal(2), critique("SATISFIED"),
        DECISION,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "satisfied"
    assert len(result.rounds) == 2
    assert {p.name for p in result.run_dir.iterdir()} == {
        "trace.md", "decision_document.json", "decision_document.md",
    }
    assert "Who approves access to confidential records?" in (result.run_dir / "decision_document.md").read_text()
    assert all(SYSTEM_CONTEXT in call["system"] for call in client.calls)


def test_satisfied_verdict_in_round_one_does_not_end_the_run(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("SATISFIED"),
        proposal(2), critique("SATISFIED"),
        DECISION,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "satisfied"
    assert len(result.rounds) == 2


def test_run_ends_at_round_cap_when_critic_never_satisfied(tmp_path):
    replies = [reply for n in range(1, 7) for reply in (proposal(n), critique("CONTINUE"))]
    client = ScriptedClient(replies + [DECISION])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "round_cap"
    assert len(result.rounds) == 6
    assert "round_cap" in (result.run_dir / "decision_document.md").read_text()
