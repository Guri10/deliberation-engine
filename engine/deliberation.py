"""The Round loop, the Challenge ledger, the Critic consistency check, and the stop rule."""

from dataclasses import dataclass
from pathlib import Path

from engine.agents import AgentReplyError, ModelClient, criticize, propose, summarize
from engine.config import FIRST_ROUND_CHALLENGE_LIMIT, LATER_ROUND_CHALLENGE_LIMIT, ROUND_CAP
from engine.models import CriticTurn, DecisionDocument, ProposerTurn, Round, StopReason, TrackedChallenge
from engine.render import format_round, new_run_dir, notes_block, write_decision, write_trace


@dataclass
class RunResult:
    stop_reason: StopReason
    rounds: list[Round]
    challenges: list[TrackedChallenge]
    decision: DecisionDocument
    run_dir: Path


def stop_reason(
    round_number: int, critic_turn: CriticTurn, open_count: int, critic_exhausted: bool, round_cap: int
) -> StopReason | None:
    """Why the deliberation should end after this Round, or None to continue."""
    if critic_turn.verdict == "SATISFIED" and round_number >= 2 and open_count == 0:
        return "satisfied"
    if critic_exhausted:
        return "critic_exhausted"
    if round_number >= round_cap:
        return "round_cap"
    return None


def find_contradiction(critic_turn: CriticTurn, round_number: int, known_ids: set[str]) -> str | None:
    """The way the Critic's Verdict contradicts its own Challenge States, or None if it doesn't.

    New Challenges that reuse a known id don't count: they are ignored when the turn is applied.
    """
    still_open = [s.challenge_id for s in critic_turn.challenge_states if s.state == "open"]
    still_open += [c.id for c in critic_turn.new_challenges if c.id not in known_ids]
    if critic_turn.verdict == "SATISFIED" and round_number == 1:
        return "you said SATISFIED in round 1, but you may not be satisfied in the first round"
    if critic_turn.verdict == "SATISFIED" and still_open:
        return f"you said SATISFIED, but these challenges are still open: {', '.join(still_open)}"
    if critic_turn.verdict == "CONTINUE" and not still_open:
        return "you said CONTINUE, but no challenge is open and you raised no new challenges"
    return None


def apply_critic_turn(
    ledger: dict[str, TrackedChallenge], critic_turn: CriticTurn, round_number: int
) -> tuple[CriticTurn, list[str]]:
    """Record the Critic's Challenge States (already checked to cover the open ones) and new Challenges.

    Returns the turn with any Challenges over the limit removed, and notes for the trace.
    """
    for s in critic_turn.challenge_states:
        ledger[s.challenge_id].state = s.state
        ledger[s.challenge_id].reason = s.reason

    notes: list[str] = []
    reused = [c.id for c in critic_turn.new_challenges if c.id in ledger]
    if reused:
        notes.append(f"Ignored new Challenges that reuse an existing id: {', '.join(reused)}")
    fresh = [c for c in critic_turn.new_challenges if c.id not in ledger]
    limit = FIRST_ROUND_CHALLENGE_LIMIT if round_number == 1 else LATER_ROUND_CHALLENGE_LIMIT
    kept, dropped = fresh[:limit], fresh[limit:]
    if dropped:
        ids = ", ".join(c.id for c in dropped)
        notes.append(f"Dropped {len(dropped)} new Challenges over the limit of {limit}: {ids}")
    for c in kept:
        ledger[c.id] = TrackedChallenge(challenge=c, raised_in_round=round_number)

    return critic_turn.model_copy(update={"new_challenges": kept}), notes


def run_deliberation(
    feature_request: str,
    client: ModelClient,
    runs_dir: Path = Path("runs"),
    round_cap: int = ROUND_CAP,
) -> RunResult:
    rounds: list[Round] = []
    ledger: dict[str, TrackedChallenge] = {}
    reason: StopReason | None = None
    summarizer_notes: list[str] = []
    try:
        reason = _run_rounds(feature_request, client, rounds, ledger, round_cap)
        challenges = list(ledger.values())
        decision = summarize(client, feature_request, rounds, challenges, summarizer_notes)
    except AgentReplyError as error:
        footer = [notes_block(error.notes)] if error.notes else []
        footer += [f"**Stop reason:** {reason}"] if reason else []
        footer.append(f"**Run stopped with an error:** {error}")
        error.run_dir = new_run_dir(runs_dir)
        write_trace(error.run_dir, feature_request, rounds, footer)
        raise

    escalated = [
        f"{t.challenge.text} (escalated {t.challenge.id})" for t in challenges if t.state == "escalated"
    ]
    decision = decision.model_copy(update={"open_questions": decision.open_questions + escalated})
    run_dir = new_run_dir(runs_dir)
    footer = [notes_block(summarizer_notes)] if summarizer_notes else []
    write_trace(run_dir, feature_request, rounds, footer + [f"**Stop reason:** {reason}"])
    write_decision(run_dir, decision, reason, len(rounds))
    return RunResult(stop_reason=reason, rounds=rounds, challenges=challenges, decision=decision, run_dir=run_dir)


def _run_rounds(
    feature_request: str,
    client: ModelClient,
    rounds: list[Round],
    ledger: dict[str, TrackedChallenge],
    round_cap: int,
) -> StopReason:
    """Run Rounds until a stop reason applies. Appends to `rounds` and `ledger` as it goes."""
    reason: StopReason | None = None
    while reason is None:
        round_number = len(rounds) + 1
        notes: list[str] = []
        open_challenges = [t.challenge for t in ledger.values() if t.state == "open"]
        proposal = propose(
            client,
            feature_request,
            rounds[-1].proposal if rounds else None,
            open_challenges,
            notes,
        )
        critic_turn, critic_exhausted = _consistent_critic_turn(
            client, feature_request, round_number, proposal, list(ledger.values()), notes
        )
        critic_turn, ledger_notes = apply_critic_turn(ledger, critic_turn, round_number)
        notes += ledger_notes
        rounds.append(Round(number=round_number, proposal=proposal, critic_turn=critic_turn, notes=notes))
        print(format_round(rounds[-1]))
        open_count = sum(t.state == "open" for t in ledger.values())
        reason = stop_reason(round_number, critic_turn, open_count, critic_exhausted, round_cap)
    return reason


def _consistent_critic_turn(
    client: ModelClient,
    feature_request: str,
    round_number: int,
    proposal: ProposerTurn,
    past: list[TrackedChallenge],
    notes: list[str],
) -> tuple[CriticTurn, bool]:
    """Get a Critic turn whose Verdict fits its Challenge States, retrying once (ADR-0001).

    If the retry still contradicts itself, a Satisfied Verdict becomes Continue, and a Continue
    with nothing left to discuss ends the run. Returns the turn and whether the Critic is exhausted.
    """
    known_ids = {t.challenge.id for t in past}
    critic_turn = criticize(client, feature_request, round_number, proposal, past, notes)
    problem = find_contradiction(critic_turn, round_number, known_ids)
    if problem is None:
        return critic_turn, False
    notes.append(f"Critic contradicted itself, retried: {problem}")
    critic_turn = criticize(client, feature_request, round_number, proposal, past, notes, (critic_turn, problem))
    problem = find_contradiction(critic_turn, round_number, known_ids)
    if problem is None:
        return critic_turn, False
    if critic_turn.verdict == "CONTINUE":
        notes.append(f"Critic contradicted itself again; fallback: run ends as critic_exhausted ({problem})")
        return critic_turn, True
    notes.append(f"Critic contradicted itself again; fallback: treated as CONTINUE ({problem})")
    return critic_turn.model_copy(update={"verdict": "CONTINUE"}), False
