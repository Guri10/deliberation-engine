import json

import pytest

from engine.agents import AgentReplyError, proposal_changes
from engine.config import SYSTEM_CONTEXT
from engine.deliberation import run_deliberation
from engine.models import ProposalChanges, ProposerTurn

FEATURE_REQUEST = "Project managers should see the full engagement history before a new mission."


A1 = {"id": "A1", "statement": "History means the last 5 years", "invented": False}


def proposal(round_no: int, responses: list[dict] | None = None, assumptions: list[dict] | None = None) -> str:
    return json.dumps({
        "scope_in": [f"Engagement timeline per country (v{round_no})"],
        "scope_out": ["Other teams' confidential meeting notes"],
        "assumptions": assumptions or [A1],
        "success_criteria": [{"metric": "Time to brief before a mission", "threshold": "under 10 minutes"}],
        "responses": responses or [],
    })


def challenge(cid: str, text: str = "", target: str = "A1", type_: str = "objection") -> dict:
    return {
        "id": cid, "target": target, "type": type_, "text": text or f"Challenge {cid} on {target}",
        "who_should_answer": "Data protection officer",
    }


def state(cid: str, value: str, reason: str = "") -> dict:
    return {"challenge_id": cid, "state": value, "reason": reason}


def critique(verdict: str, new: list[dict] | None = None, states: list[dict] | None = None) -> str:
    return json.dumps({"verdict": verdict, "new_challenges": new or [], "challenge_states": states or []})


def defend(cid: str) -> dict:
    return {"challenge_id": cid, "type": "Defend", "text": "Five years covers every active mission."}


DECISION = json.dumps({
    "scope_in": ["Engagement timeline per country"],
    "scope_out": ["Other teams' confidential meeting notes"],
    "assumptions": [{"id": "A1", "statement": "History means the last 5 years", "status": "Challenged-and-held"}],
    "open_questions": [{
        "text": "Who approves access to confidential records?", "blocking": True, "who_should_answer": "Legal",
    }],
    "success_criteria": [{"metric": "Time to brief before a mission", "threshold": "under 10 minutes"}],
})


def confidence(score: int, reason: str) -> str:
    return json.dumps({"score": score, "reason": reason})


PROPOSER_CONFIDENCE = confidence(85, "Scope is tight; retention period still a judgement call.")
CRITIC_CONFIDENCE = confidence(55, "Sanctioned-contact visibility is unresolved.")
CONFIDENCES = [PROPOSER_CONFIDENCE, CRITIC_CONFIDENCE]
ENDING = CONFIDENCES + [DECISION]


def open_questions_section(result) -> str:
    return (result.run_dir / "decision_document.md").read_text().split("## Open Questions")[1].split("##")[0]


OPEN_HEADING = "The Critic's open challenges, with their history:"
SETTLED_HEADING = "Settled challenges (closed or escalated). Keep what settled them; do not undo it:"
CHANGES_HEADING = "Changes since last proposal:"
PAST_HEADING = "Challenges you raised in earlier rounds, with their states (open ones with their history):"


def json_section(message: str, heading: str):
    """The JSON that follows a heading line in an agent's message."""
    return json.loads(message.split(heading + "\n", 1)[1].split("\n\n", 1)[0])


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
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "satisfied"
    assert len(result.rounds) == 2
    assert {p.name for p in result.run_dir.iterdir()} == {
        "trace.md", "decision_document.json", "decision_document.md",
    }
    assert "Who approves access to confidential records?" in (result.run_dir / "decision_document.md").read_text()
    assert all(SYSTEM_CONTEXT in call["system"] for call in client.calls)


def test_satisfied_in_round_one_is_retried_then_treated_as_continue_if_repeated(tmp_path):
    first_round_satisfied = critique("SATISFIED", new=[challenge("C1")])
    client = ScriptedClient([
        proposal(1), first_round_satisfied, first_round_satisfied,
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert "round 1" in client.calls[2]["messages"][-1]["content"]
    assert result.rounds[0].critic_turn.verdict == "CONTINUE"
    assert result.stop_reason == "satisfied"
    assert len(result.rounds) == 2
    round_one = (result.run_dir / "trace.md").read_text().split("## Round 2")[0]
    assert "fallback: treated as CONTINUE" in round_one


def two_close_two_open_every_round(rounds: int) -> list[str]:
    """Each Round closes the 2 open Challenges and opens 2 new ones, so Disagreement stays at 2."""
    replies = [proposal(1), critique("CONTINUE", new=[challenge("C1"), challenge("C2")])]
    for n in range(2, rounds + 1):
        old = [f"C{2 * n - 3}", f"C{2 * n - 2}"]
        new = [challenge(f"C{2 * n - 1}"), challenge(f"C{2 * n}")]
        replies += [
            proposal(n, [defend(cid) for cid in old]),
            critique("CONTINUE", new=new, states=[state(cid, "closed") for cid in old]),
        ]
    return replies


def test_closing_two_and_opening_two_each_round_is_not_a_stall_and_runs_to_the_round_cap(tmp_path):
    client = ScriptedClient(two_close_two_open_every_round(6) + ENDING)

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path, round_cap=6)

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
        *ENDING,
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
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "satisfied"
    assert [(t.challenge.id, t.state) for t in result.challenges] == [("C1", "escalated")]
    assert f"**Blocking:** {sanctions} (answer: Data protection officer; source: escalated, C1)" in (
        open_questions_section(result)
    )


def test_proposer_sees_open_challenges_with_their_history_and_settled_ones_in_their_own_section(tmp_path):
    closed_text = "Why 5 years? Treaties often span decades."
    open_text = "How is 'time to brief' measured?"
    escalated_text = "Can regional coordinators see ministry-level notes?"
    silent_text = "Who may export a country history?"
    revise = {
        "challenge_id": "C1", "type": "Revise", "text": "History now covers 20 years.", "quote": "Treaties often span decades",
    }
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[
            challenge("C1", closed_text),
            challenge("C2", open_text, target="time to brief"),
            challenge("C3", escalated_text, type_="risk"),
            challenge("C4", silent_text, type_="question"),
        ]),
        proposal(2, [revise, defend("C2"), defend("C3"), defend("C4")]),
        critique("CONTINUE", states=[
            state("C1", "closed"), state("C2", "open", "No baseline"),
            state("C3", "escalated", "Ministry policy call"), state("C4", "escalated"),
        ]),
        proposal(3, [defend("C2")]), critique("SATISFIED", states=[state("C2", "closed")]),
        *ENDING,
    ])

    run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    round_three_proposer = client.contents("Proposer")[2]
    open_challenges = json_section(round_three_proposer, OPEN_HEADING)
    assert [c["challenge"]["id"] for c in open_challenges] == ["C2"]
    assert open_challenges[0]["history"] == [{
        "round": 2, "response_type": "Defend", "response_text": "Five years covers every active mission.",
        "critic_state": "open", "critic_reason": "No baseline",
    }]
    assert json_section(round_three_proposer, SETTLED_HEADING) == [
        {"id": "C1", "state": "closed", "settled_in_round": 2, "text": closed_text,
         "response_type": "Revise", "response_text": "History now covers 20 years."},
        {"id": "C3", "state": "escalated", "settled_in_round": 2, "text": escalated_text,
         "critic_reason": "Ministry policy call", "who_should_answer": "Data protection officer"},
        {"id": "C4", "state": "escalated", "settled_in_round": 2, "text": silent_text,
         "who_should_answer": "Data protection officer"},
    ]
    round_three_critic = client.contents("Critic")[2]
    assert [c["challenge"]["id"] for c in json_section(round_three_critic, PAST_HEADING)] == ["C1", "C2", "C3", "C4"]


def test_proposer_sees_why_the_critic_kept_each_challenge_open(tmp_path):
    reason = "No baseline: how long does a briefing take today?"
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("CONTINUE", states=[state("C1", "open", reason)]),
        proposal(3, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *ENDING,
    ])

    run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert reason in client.contents("Proposer")[2]


def test_revise_and_concede_carry_the_quoted_critic_argument(tmp_path):
    argument = "Treaties often span decades"
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1", f"Why 5 years? {argument}."), challenge("C2")]),
        proposal(2, [
            {"challenge_id": "C1", "type": "Revise", "text": "History now covers 20 years.", "quote": argument},
            {"challenge_id": "C2", "type": "Concede", "text": "Dropped.", "quote": "Challenge C2 on A1"},
        ]),
        critique("SATISFIED", states=[state("C1", "closed"), state("C2", "closed")]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert [(r.type, r.quote) for r in result.rounds[1].proposal.responses] == [
        ("Revise", argument), ("Concede", "Challenge C2 on A1"),
    ]
    assert f'"{argument}"' in (result.run_dir / "trace.md").read_text()


def invalid_twice(client: ScriptedClient, tmp_path) -> AgentReplyError:
    with pytest.raises(AgentReplyError) as raised:
        run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)
    return raised.value


def test_two_malformed_replies_stop_the_run_with_an_error_and_save_the_trace(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        "not json", '{"scope_in": []}',
    ])

    error = invalid_twice(client, tmp_path)

    assert "Proposer reply was invalid twice" in str(error)
    assert error.run_dir is not None
    trace = (error.run_dir / "trace.md").read_text()
    assert "## Round 1" in trace
    assert "**Run stopped with an error:** Proposer reply was invalid twice" in trace
    assert not (error.run_dir / "decision_document.md").exists()


@pytest.mark.parametrize("response_type", ["Revise", "Concede"])
def test_revise_or_concede_without_a_quote_is_invalid(tmp_path, response_type):
    unquoted = proposal(2, [{"challenge_id": "C1", "type": response_type, "text": "Fine, changed."}])
    client = ScriptedClient([proposal(1), critique("CONTINUE", new=[challenge("C1")]), unquoted, unquoted])

    assert "must quote the Critic argument" in str(invalid_twice(client, tmp_path))


def test_critic_must_give_a_state_for_every_open_challenge(tmp_path):
    missing_c2 = critique("CONTINUE", states=[state("C1", "closed")])
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1"), challenge("C2")]),
        proposal(2, [defend("C1"), defend("C2")]), missing_c2, missing_c2,
    ])

    assert "C2" in str(invalid_twice(client, tmp_path))


def test_open_challenge_state_without_a_reason_is_invalid(tmp_path):
    no_reason = critique("CONTINUE", states=[state("C1", "open")])
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), no_reason, no_reason,
    ])

    assert "must give a reason" in str(invalid_twice(client, tmp_path))


def test_critic_prompt_requires_a_data_access_and_confidentiality_challenge(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *ENDING,
    ])

    run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    critic_system = next(c["system"] for c in client.calls if "# Role: Critic" in c["system"])
    assert "In every run, raise at least one challenge on data access and confidentiality" in critic_system


def test_new_challenge_reusing_an_id_is_ignored_and_does_not_use_up_the_limit(tmp_path):
    later = [challenge("C1", "A different point"), challenge("C2"), challenge("C3"), challenge("C4")]
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("CONTINUE", new=later, states=[state("C1", "closed")]),
        proposal(3, [defend(f"C{i}") for i in (2, 3, 4)]),
        critique("SATISFIED", states=[state(f"C{i}", "closed") for i in (2, 3, 4)]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert [c.id for c in result.rounds[1].critic_turn.new_challenges] == ["C2", "C3", "C4"]
    assert "Ignored new Challenges that reuse an existing id: C1" in (result.run_dir / "trace.md").read_text()


def test_one_malformed_reply_is_retried_and_the_retry_shows_in_the_trace(tmp_path):
    client = ScriptedClient([
        "not json at all", proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "satisfied"
    retry_messages = client.calls[1]["messages"]
    assert retry_messages[1] == {"role": "assistant", "content": "not json at all"}
    assert "invalid" in retry_messages[2]["content"]
    assert "Proposer reply was invalid, retried" in (result.run_dir / "trace.md").read_text().split("## Round 2")[0]


def three_challenges_then(*round_two_critiques: str) -> list[str]:
    return [
        proposal(1), critique("CONTINUE", new=[challenge("C1"), challenge("C2"), challenge("C3")]),
        proposal(2, [defend("C1"), defend("C2"), defend("C3")]), *round_two_critiques,
    ]


ALL_CLOSED = [state("C1", "closed"), state("C2", "closed"), state("C3", "closed")]
C3_STILL_OPEN = [state("C1", "closed"), state("C2", "closed"), state("C3", "open", "No retention rule")]


def test_satisfied_with_a_challenge_open_is_retried_quoting_it_and_a_corrected_reply_is_accepted(tmp_path):
    client = ScriptedClient(three_challenges_then(
        critique("SATISFIED", states=C3_STILL_OPEN), critique("SATISFIED", states=ALL_CLOSED),
    ) + ENDING)

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "satisfied"
    assert len(result.rounds) == 2
    retry_message = client.calls[4]["messages"][-1]["content"]
    assert "SATISFIED" in retry_message and "C3" in retry_message
    assert "Critic contradicted itself, retried" in (result.run_dir / "trace.md").read_text()


def test_satisfied_with_a_challenge_open_twice_is_treated_as_continue_and_logged(tmp_path):
    client = ScriptedClient(three_challenges_then(
        critique("SATISFIED", states=C3_STILL_OPEN), critique("SATISFIED", states=C3_STILL_OPEN),
        proposal(3, [defend("C3")]), critique("SATISFIED", states=[state("C3", "closed")]),
    ) + ENDING)

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.rounds[1].critic_turn.verdict == "CONTINUE"
    assert result.stop_reason == "satisfied"
    assert len(result.rounds) == 3
    round_two = (result.run_dir / "trace.md").read_text().split("## Round 2")[1].split("## Round 3")[0]
    assert "Critic contradicted itself again; fallback: treated as CONTINUE" in round_two


def test_continue_with_nothing_open_and_nothing_new_twice_ends_the_run_as_critic_exhausted(tmp_path):
    nothing_left = critique("CONTINUE", states=ALL_CLOSED)
    client = ScriptedClient(three_challenges_then(nothing_left, nothing_left) + ENDING)

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert "CONTINUE" in client.calls[4]["messages"][-1]["content"]
    assert result.stop_reason == "critic_exhausted"
    assert len(result.rounds) == 2
    assert "fallback: run ends as critic_exhausted" in (result.run_dir / "trace.md").read_text()
    assert "critic_exhausted" in (result.run_dir / "decision_document.md").read_text()


def test_continue_whose_only_new_challenge_reuses_an_id_counts_as_nothing_new(tmp_path):
    reused_only = critique("CONTINUE", new=[challenge("C1", "Same id again")], states=ALL_CLOSED)
    client = ScriptedClient(three_challenges_then(reused_only, reused_only) + ENDING)

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "critic_exhausted"


def test_failed_run_trace_keeps_the_unfinished_rounds_notes(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        "first bad reply", "second bad reply",
    ])

    error = invalid_twice(client, tmp_path)

    assert error.run_dir is not None
    trace = (error.run_dir / "trace.md").read_text()
    assert "Proposer reply was invalid, retried" in trace


def test_summarizer_failure_trace_keeps_the_stop_reason(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *CONFIDENCES, "bad decision", "bad decision",
    ])

    error = invalid_twice(client, tmp_path)

    assert error.run_dir is not None
    trace = (error.run_dir / "trace.md").read_text()
    assert "**Stop reason:** satisfied" in trace
    assert "Summarizer reply was invalid twice" in trace


def test_summarizer_retry_shows_in_the_trace(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *CONFIDENCES, "bad decision", DECISION,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert "Summarizer reply was invalid, retried" in (result.run_dir / "trace.md").read_text()


def still_open(cid: str) -> dict:
    return state(cid, "open", "Not convinced yet")


def test_two_rounds_in_a_row_with_no_movement_end_the_run_as_stalled(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("CONTINUE", states=[still_open("C1")]),
        proposal(3, [defend("C1")]), critique("CONTINUE", states=[still_open("C1")]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "stalled"
    assert len(result.rounds) == 3


def test_at_a_stall_each_open_challenge_becomes_a_blocking_open_question_tagged_stalled(tmp_path):
    retention = "How long may mission notes be kept?"
    sanctions = "Who sees notes on sanctioned contacts?"
    settled = "Is five years enough?"
    stuck = [still_open("C1"), still_open("C2")]
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[
            challenge("C1", retention), challenge("C2", sanctions, type_="risk"), challenge("C3", settled),
        ]),
        proposal(2, [defend("C1"), defend("C2"), defend("C3")]),
        critique("CONTINUE", states=stuck + [state("C3", "closed")]),
        proposal(3, [defend("C1"), defend("C2")]), critique("CONTINUE", states=stuck),
        proposal(4, [defend("C1"), defend("C2")]), critique("CONTINUE", states=stuck),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "stalled"
    section = open_questions_section(result)
    assert f"**Blocking:** {retention} (answer: Data protection officer; source: stalled, C1)" in section
    assert f"**Blocking:** {sanctions} (answer: Data protection officer; source: stalled, C2)" in section
    assert settled not in section


def test_at_the_round_cap_each_open_challenge_becomes_a_blocking_open_question_tagged_round_cap(tmp_path):
    client = ScriptedClient(two_close_two_open_every_round(6) + ENDING)

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path, round_cap=6)

    section = open_questions_section(result)
    assert "**Blocking:** Challenge C11 on A1 (answer: Data protection officer; source: round cap, C11)" in section
    assert "**Blocking:** Challenge C12 on A1 (answer: Data protection officer; source: round cap, C12)" in section
    assert "C10" not in section


@pytest.mark.parametrize("round_three_response, round_three_state", [
    ({"challenge_id": "C1", "type": "Revise", "text": "Now 20 years.", "quote": "Challenge C1"}, still_open("C1")),
    ({"challenge_id": "C1", "type": "Concede", "text": "Dropped.", "quote": "Challenge C1"}, still_open("C1")),
    (defend("C1"), state("C1", "escalated")),
])
def test_a_revise_concede_or_escalation_alone_counts_as_movement(tmp_path, round_three_response, round_three_state):
    still_open_after_three = ["C1", "C2"] if round_three_state["state"] == "open" else ["C2"]
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1"), challenge("C2")]),
        proposal(2, [defend("C1"), defend("C2")]), critique("CONTINUE", states=[still_open("C1"), still_open("C2")]),
        proposal(3, [round_three_response, defend("C2")]),
        critique("CONTINUE", states=[round_three_state, still_open("C2")]),
        proposal(4, [defend(cid) for cid in still_open_after_three]),
        critique("SATISFIED", states=[state(cid, "closed") for cid in still_open_after_three]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert result.stop_reason == "satisfied"
    assert len(result.rounds) == 4


def test_proposer_must_respond_to_exactly_the_open_challenges(tmp_path):
    answers_closed_one = proposal(3, [
        {"challenge_id": "C1", "type": "Revise", "text": "Changed.", "quote": "Challenge C1"}, defend("C2"),
    ])
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1"), challenge("C2")]),
        proposal(2, [defend("C1"), defend("C2")]), critique("CONTINUE", states=[state("C1", "closed"), still_open("C2")]),
        answers_closed_one, answers_closed_one,
    ])

    error = invalid_twice(client, tmp_path)

    assert "C1" in str(error) and "C2" in str(error)


def test_disagreement_and_its_change_per_round_appear_in_trace_and_summary(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1"), challenge("C2"), challenge("C3")]),
        proposal(2, [defend("C1"), defend("C2"), defend("C3")]),
        critique("CONTINUE", new=[challenge("C4")], states=[state("C1", "closed"), state("C2", "closed"), still_open("C3")]),
        proposal(3, [defend("C3"), defend("C4")]),
        critique("SATISFIED", states=[state("C3", "closed"), state("C4", "closed")]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    trace = (result.run_dir / "trace.md").read_text()
    rounds = trace.split("## Round ")[1:]
    assert "**Disagreement:** 3 open (first round)" in rounds[0]
    assert "**Disagreement:** 2 open (-1)" in rounds[1]
    assert "**Disagreement:** 0 open (-2)" in rounds[2]
    summary = (result.run_dir / "decision_document.md").read_text().split("## Deliberation Summary")[1]
    assert "- Disagreement per round: R1 3, R2 2 (-1), R3 0 (-2)" in summary


def test_trace_shows_response_type_counts_per_round(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge(f"C{i}") for i in range(1, 5)]),
        proposal(2, [
            defend("C1"), defend("C2"),
            {"challenge_id": "C3", "type": "Revise", "text": "Changed.", "quote": "Challenge C3"},
            {"challenge_id": "C4", "type": "Concede", "text": "Dropped.", "quote": "Challenge C4"},
        ]),
        critique("SATISFIED", states=[state(f"C{i}", "closed") for i in range(1, 5)]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    rounds = (result.run_dir / "trace.md").read_text().split("## Round ")[1:]
    assert "**Response counts:** Defend 0, Revise 0, Concede 0" in rounds[0]
    assert "**Response counts:** Defend 2, Revise 1, Concede 1" in rounds[1]


def test_both_agents_confidence_and_reasons_appear_in_the_summary_and_reach_the_summarizer(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    summary = (result.run_dir / "decision_document.md").read_text().split("## Deliberation Summary")[1]
    assert "- Proposer confidence: 85 (Scope is tight; retention period still a judgement call.)" in summary
    assert "- Critic confidence: 55 (Sanctioned-contact visibility is unresolved.)" in summary
    confidence_calls = client.calls[4:6]
    assert all("90 to 100: would ship as is" in c["messages"][0]["content"] for c in confidence_calls)
    assert all("50: major gaps remain" in c["messages"][0]["content"] for c in confidence_calls)
    summarizer_input = client.contents("Summarizer")[0]
    assert "Sanctioned-contact visibility is unresolved." in summarizer_input


def test_every_assumption_shows_its_final_status_and_the_round_it_was_raised(tmp_path):
    a2 = {"id": "A2", "statement": "Only logged meetings count as engagement", "invented": False}
    decision = json.dumps({**json.loads(DECISION), "assumptions": [
        {"id": "A1", "statement": "History means the last 20 years", "status": "Revised"},
        {"id": "A2", "statement": "Only logged meetings count as engagement", "status": "Accepted"},
    ]})
    revise = {"challenge_id": "C1", "type": "Revise", "text": "Now 20 years.", "quote": "Challenge C1"}
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [revise], [A1, a2]), critique("SATISFIED", states=[state("C1", "closed")]),
        *CONFIDENCES, decision,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    section = (result.run_dir / "decision_document.md").read_text().split("## Surfaced Assumptions")[1].split("##")[0]
    assert "- A1: History means the last 20 years (Revised; raised in round 1)" in section
    assert "- A2: Only logged meetings count as engagement (Accepted; raised in round 2)" in section


def test_invented_facts_get_their_own_section_and_are_each_a_non_blocking_open_question(tmp_path):
    invented = {"id": "A2", "statement": "Each contact record has a confidentiality level field", "invented": True}
    client = ScriptedClient([
        proposal(1, assumptions=[A1, invented]), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")], [A1, invented]), critique("SATISFIED", states=[state("C1", "closed")]),
        *CONFIDENCES, json.dumps({**json.loads(DECISION), "assumptions": [
            {"id": "A1", "statement": A1["statement"], "status": "Challenged-and-held"},
            {"id": "A2", "statement": invented["statement"], "status": "Accepted"},
        ]}),
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    markdown = (result.run_dir / "decision_document.md").read_text()
    invented_section = markdown.split("## Invented Facts")[1].split("##")[0]
    assert "- A2: Each contact record has a confidentiality level field" in invented_section
    assert "A1" not in invented_section
    assert (
        "**Non-blocking:** Confirm A2: Each contact record has a confidentiality level field "
        "(answer: CRM system owner; source: invented fact)"
    ) in open_questions_section(result)


def test_decision_document_has_six_sections_in_order_with_the_stop_reason_in_the_header(tmp_path):
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *ENDING,
    ])

    result = run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    markdown = (result.run_dir / "decision_document.md").read_text()
    header, *_ = markdown.split("## ")
    assert "satisfied" in header
    sections = [line.removeprefix("## ") for line in markdown.splitlines() if line.startswith("## ")]
    assert sections == [
        "Agreed Scope", "Surfaced Assumptions", "Open Questions",
        "Invented Facts", "Success Criteria", "Deliberation Summary",
    ]
    assert (
        "**Blocking:** Who approves access to confidential records? (answer: Legal; source: deliberation)"
    ) in open_questions_section(result)


def test_summarizer_must_give_a_status_for_every_assumption_raised(tmp_path):
    a2 = {"id": "A2", "statement": "Only logged meetings count", "invented": False}
    client = ScriptedClient([
        proposal(1, assumptions=[A1, a2]), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *CONFIDENCES, DECISION, DECISION,
    ])

    error = invalid_twice(client, tmp_path)

    assert "Summarizer reply was invalid twice" in str(error) and "A2" in str(error)


def turn(scope_in=None, scope_out=None, assumptions=None, criteria=None):
    return ProposerTurn.model_validate({
        "scope_in": scope_in or [],
        "scope_out": scope_out or [],
        "assumptions": assumptions or [],
        "success_criteria": criteria or [{"metric": "Time to brief", "threshold": "under 10 minutes"}],
    })


def test_proposal_changes_list_assumptions_added_removed_and_changed():
    a1 = {"id": "A1", "statement": "History means 5 years", "invented": False}
    a4 = {"id": "A4", "statement": "mission heads approve visibility per contact", "invented": True}
    before = turn(assumptions=[a1, {"id": "A2", "statement": "all coordinators", "invented": False}])
    after = turn(assumptions=[{"id": "A2", "statement": "coordinators in that country", "invented": False}, a4])

    assert proposal_changes(before, after).model_dump(exclude_defaults=True) == {
        "assumptions_added": [a4],
        "assumptions_removed": [a1],
        "assumptions_changed": [{"id": "A2", "before": "all coordinators", "after": "coordinators in that country"}],
    }


def test_proposal_changes_list_scope_items_added_and_removed():
    before = turn(scope_in=["Timeline per country"], scope_out=["bulk export", "Other teams' notes"])
    after = turn(scope_in=["Timeline per country", "Filter by project"], scope_out=["Other teams' notes"])

    assert proposal_changes(before, after).model_dump(exclude_defaults=True) == {
        "scope_in_added": ["Filter by project"],
        "scope_out_removed": ["bulk export"],
    }


def test_proposal_changes_list_success_criteria_added_removed_and_threshold_changed():
    before = turn(criteria=[
        {"metric": "Time to brief", "threshold": "under 10 minutes"},
        {"metric": "Notes found", "threshold": "95%"},
    ])
    after = turn(criteria=[
        {"metric": "Time to brief", "threshold": "under 15 minutes"},
        {"metric": "Wrong-country notes shown", "threshold": "zero"},
    ])

    assert proposal_changes(before, after).model_dump(exclude_defaults=True) == {
        "criteria_added": [{"metric": "Wrong-country notes shown", "threshold": "zero"}],
        "criteria_removed": [{"metric": "Notes found", "threshold": "95%"}],
        "criteria_threshold_changed": [
            {"metric": "Time to brief", "before": "under 10 minutes", "after": "under 15 minutes"},
        ],
    }


def test_proposal_changes_are_empty_when_nothing_changed():
    same = turn(scope_in=["Timeline"], assumptions=[A1])

    assert proposal_changes(same, same) == ProposalChanges()


def test_critic_sees_proposal_changes_from_round_two_and_none_in_round_one(tmp_path):
    a1_revised = {**A1, "statement": "History means the last 20 years"}
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1")]),
        proposal(2, [defend("C1")], assumptions=[a1_revised]),
        critique("CONTINUE", states=[state("C1", "open", "Still no rule for absent heads")]),
        proposal(3, [defend("C1")], assumptions=[a1_revised]), critique("SATISFIED", states=[state("C1", "closed")]),
        *ENDING,
    ])

    run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    round_one, round_two, round_three = client.contents("Critic")[:3]
    assert CHANGES_HEADING not in round_one
    assert json_section(round_two, CHANGES_HEADING) == {
        "assumptions_changed": [
            {"id": "A1", "before": "History means the last 5 years", "after": "History means the last 20 years"},
        ],
        "scope_in_added": ["Engagement timeline per country (v2)"],
        "scope_in_removed": ["Engagement timeline per country (v1)"],
    }
    assert json_section(round_three, CHANGES_HEADING) == {
        "scope_in_added": ["Engagement timeline per country (v3)"],
        "scope_in_removed": ["Engagement timeline per country (v2)"],
    }


def test_both_agents_see_the_full_challenge_history_of_each_open_challenge(tmp_path):
    revise = {
        "challenge_id": "C1", "type": "Revise", "text": "Mission heads approve per contact.",
        "quote": "restricted notes",
    }
    client = ScriptedClient([
        proposal(1), critique("CONTINUE", new=[challenge("C1", "Who decides visibility of restricted notes?", type_="risk")]),
        proposal(2, [defend("C1")]), critique("CONTINUE", states=[state("C1", "open", "Sanctioned contacts not covered")]),
        proposal(3, [revise]), critique("CONTINUE", states=[state("C1", "open", "No rule when mission head is absent")]),
        proposal(4, [defend("C1")]), critique("SATISFIED", states=[state("C1", "closed")]),
        *ENDING,
    ])

    run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    history = [
        {"round": 2, "response_type": "Defend", "response_text": "Five years covers every active mission.",
         "critic_state": "open", "critic_reason": "Sanctioned contacts not covered"},
        {"round": 3, "response_type": "Revise", "response_text": "Mission heads approve per contact.",
         "critic_state": "open", "critic_reason": "No rule when mission head is absent"},
    ]
    [proposer_c1] = json_section(client.contents("Proposer")[3], OPEN_HEADING)
    assert proposer_c1["history"] == history
    assert proposer_c1["challenge"]["who_should_answer"] == "Data protection officer"
    [critic_c1] = json_section(client.contents("Critic")[3], PAST_HEADING)
    assert critic_c1["history"] == history


def test_critic_is_told_in_one_line_when_the_proposal_did_not_change(tmp_path):
    unchanged = json.loads(proposal(1))
    client = ScriptedClient([
        json.dumps(unchanged), critique("CONTINUE", new=[challenge("C1")]),
        json.dumps({**unchanged, "responses": [defend("C1")]}), critique("SATISFIED", states=[state("C1", "closed")]),
        *ENDING,
    ])

    run_deliberation(FEATURE_REQUEST, client, runs_dir=tmp_path)

    assert f"{CHANGES_HEADING} none\n" in client.contents("Critic")[1]
