import json

import pytest
from pydantic import ValidationError

from engine.config import SYSTEM_CONTEXT
from engine.deliberation import run_deliberation

FEATURE_REQUEST = "Project managers should see the full engagement history before a new mission."


def proposal(round_no: int, responses: list[dict] | None = None) -> str:
    return json.dumps({
        "scope_in": [f"Engagement timeline per country (v{round_no})"],
        "scope_out": ["Other teams' confidential meeting notes"],
        "assumptions": [{"id": "A1", "statement": "History means the last 5 years"}],
        "success_criteria": [{"metric": "Time to brief before a mission", "threshold": "under 10 minutes"}],
        "responses": responses or [],
    })


def challenge(cid: str, text: str = "", target: str = "A1", type_: str = "objection") -> dict:
    return {"id": cid, "target": target, "type": type_, "text": text or f"Challenge {cid} on {target}"}


def state(cid: str, value: str, reason: str = "") -> dict:
    return {"challenge_id": cid, "state": value, "reason": reason}


def critique(verdict: str, new: list[dict] | None = None, states: list[dict] | None = None) -> str:
    return json.dumps({"verdict": verdict, "new_challenges": new or [], "challenge_states": states or []})


def defend(cid: str) -> dict:
    return {"challenge_id": cid, "type": "Defend", "text": "Five years covers every active mission."}


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

    def contents(self, prompt_word: str) -> list[str]:
        """User message text of every call whose system prompt has the given role heading."""
        return [c["messages"][0]["content"] for c in self.calls if f"# Role: {prompt_word}" in c["system"]]


def test_two_round_run_ends_satisfied_and_writes_trace_and_decision_document(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
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
    replies = [proposal(1), critique("CONTINUE", new=[challenge("C1")])]
    for n in range(2, 7):
        replies += [proposal(n, [defend("C1")]), critique("CONTINUE", states=[state("C1", "open", "Still unclear")])]
    client = ScriptedClient(replies + [DECISION])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "round_cap"
    assert len(result.rounds) == 6
    assert "round_cap" in (result.run_dir / "decision_document.md").read_text()


def test_new_challenges_beyond_the_round_limit_are_dropped_and_logged(tmp_path):
    first = [challenge(f"C{i}") for i in range(1, 8)]
    second = [challenge(f"C{i}") for i in range(8, 12)]
    close_first_five = [state(f"C{i}", "closed") for i in range(1, 6)]
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=first),
        proposal(2, [defend(f"C{i}") for i in range(1, 6)]),
        critique("CONTINUE", new=second, states=close_first_five),
        proposal(3, [defend(f"C{i}") for i in range(8, 11)]),
        critique("SATISFIED", states=[state(f"C{i}", "closed") for i in range(8, 11)]),
        DECISION,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert [c.id for c in result.rounds[0].critic_turn.new_challenges] == ["C1", "C2", "C3", "C4", "C5"]
    assert [c.id for c in result.rounds[1].critic_turn.new_challenges] == ["C8", "C9", "C10"]
    assert result.stop_reason == "satisfied"
    trace = (result.run_dir / "trace.md").read_text()
    assert "Dropped 2 new Challenges over the limit of 5: C6, C7" in trace
    assert "Dropped 1 new Challenges over the limit of 3: C11" in trace


def test_challenge_escalated_in_round_two_becomes_an_open_question_and_allows_satisfied(tmp_path):
    sanctions = "Who may see notes on sanctioned contacts? Only legal can decide this."
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1", sanctions, type_="risk")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "escalated")]),
        DECISION,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "satisfied"
    assert [(t.challenge.id, t.state) for t in result.challenges] == [("C1", "escalated")]
    assert any(sanctions in q for q in result.decision.open_questions)
    assert sanctions in (result.run_dir / "decision_document.md").read_text().split("## Open Questions")[1]


def test_satisfied_verdict_with_a_challenge_still_open_does_not_end_the_run(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "open", "Five years is arbitrary")]),
        proposal(3, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        DECISION,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "satisfied"
    assert len(result.rounds) == 3


def test_proposer_sees_only_open_challenges(tmp_path):
    closed_text = "Why 5 years? Treaties often span decades."
    open_text = "How is 'time to brief' measured?"
    escalated_text = "Can regional coordinators see ministry-level notes?"
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[
            challenge("C1", closed_text),
            challenge("C2", open_text, target="time to brief"),
            challenge("C3", escalated_text, type_="risk"),
        ]),
        proposal(2, [defend("C1"), defend("C2"), defend("C3")]),
        critique("CONTINUE", states=[state("C1", "closed"), state("C2", "open", "No baseline"), state("C3", "escalated")]),
        proposal(3, [defend("C2")]), critique("SATISFIED", states=[state("C2", "closed")]),
        DECISION,
    ])

    run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    round_three_proposer = client.contents("Proposer")[2]
    assert open_text in round_three_proposer
    assert closed_text not in round_three_proposer
    assert escalated_text not in round_three_proposer
    round_three_critic = client.contents("Critic")[2]
    assert all(text in round_three_critic for text in (closed_text, open_text, escalated_text))


def test_revise_and_concede_carry_the_quoted_critic_argument(tmp_path):
    argument = "Treaties often span decades"
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1", f"Why 5 years? {argument}."), challenge("C2")]),
        proposal(2, [
            {"challenge_id": "C1", "type": "Revise", "text": "History now covers 20 years.", "quote": argument},
            {"challenge_id": "C2", "type": "Concede", "text": "Dropped.", "quote": "Challenge C2 on A1"},
        ]),
        critique("SATISFIED", states=[state("C1", "closed"), state("C2", "closed")]),
        DECISION,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert [(r.type, r.quote) for r in result.rounds[1].proposal.responses] == [
        ("Revise", argument), ("Concede", "Challenge C2 on A1"),
    ]
    assert f'"{argument}"' in (result.run_dir / "trace.md").read_text()


@pytest.mark.parametrize("response_type", ["Revise", "Concede"])
def test_revise_or_concede_without_a_quote_is_rejected(tmp_path, response_type):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [{"challenge_id": "C1", "type": response_type, "text": "Fine, changed."}]),
    ])

    with pytest.raises(ValidationError, match="quote"):
        run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)


def test_critic_must_give_a_state_for_every_open_challenge(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1"), challenge("C2")]),
        proposal(2, [defend("C1"), defend("C2")]), critique("CONTINUE", states=[state("C1", "closed")]),
    ])

    with pytest.raises(ValueError, match="C2"):
        run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)


def test_critic_prompt_requires_a_data_access_and_confidentiality_challenge(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("SATISFIED"),
        proposal(2), critique("SATISFIED"),
        DECISION,
    ])

    run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    critic_system = next(c["system"] for c in client.calls if "# Role: Critic" in c["system"])
    assert "In every run, raise at least one challenge on data access and confidentiality" in critic_system


def test_open_challenge_state_without_a_reason_is_rejected(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("CONTINUE", states=[state("C1", "open")]),
    ])

    with pytest.raises(ValidationError, match="reason"):
        run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)


def test_new_challenge_reusing_an_id_is_ignored_and_does_not_use_up_the_limit(tmp_path):
    later = [challenge("C1", "A different point"), challenge("C2"), challenge("C3"), challenge("C4")]
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("CONTINUE", new=later, states=[state("C1", "closed")]),
        proposal(3, [defend(f"C{i}") for i in (2, 3, 4)]),
        critique("SATISFIED", states=[state(f"C{i}", "closed") for i in (2, 3, 4)]),
        DECISION,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert [c.id for c in result.rounds[1].critic_turn.new_challenges] == ["C2", "C3", "C4"]
    assert "Ignored new Challenges that reuse an existing id: C1" in (result.run_dir / "trace.md").read_text()
