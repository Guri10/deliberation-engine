"""The Round loop, the Challenge ledger, and the stop rule."""

from dataclasses import dataclass
from pathlib import Path

from engine.agents import ModelClient, criticize, propose, summarize
from engine.config import FIRST_ROUND_CHALLENGE_LIMIT, LATER_ROUND_CHALLENGE_LIMIT, ROUND_CAP
from engine.models import CriticTurn, DecisionDocument, Round, StopReason, TrackedChallenge
from engine.render import format_round, write_run


@dataclass
class RunResult:
    stop_reason: StopReason
    rounds: list[Round]
    challenges: list[TrackedChallenge]
    decision: DecisionDocument
    run_dir: Path


def stop_reason(round_number: int, critic_turn: CriticTurn, open_count: int, round_cap: int) -> StopReason | None:
    """Why the deliberation should end after this Round, or None to continue."""
    if critic_turn.verdict == "SATISFIED" and round_number >= 2 and open_count == 0:
        return "satisfied"
    if round_number >= round_cap:
        return "round_cap"
    return None


def apply_critic_turn(
    ledger: dict[str, TrackedChallenge], critic_turn: CriticTurn, round_number: int
) -> tuple[CriticTurn, list[str]]:
    """Record the Critic's Challenge States and new Challenges in the ledger.

    Returns the turn with any Challenges over the limit removed, and notes for the trace.
    """
    open_ids = {cid for cid, t in ledger.items() if t.state == "open"}
    stated_ids = {s.challenge_id for s in critic_turn.challenge_states}
    if stated_ids != open_ids:
        raise ValueError(
            f"Round {round_number}: the Critic must give a state for exactly the open Challenges "
            f"{sorted(open_ids)}, but gave states for {sorted(stated_ids)}"
        )
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

    while reason is None:
        round_number = len(rounds) + 1
        open_challenges = [t.challenge for t in ledger.values() if t.state == "open"]
        proposal = propose(
            client,
            feature_request,
            rounds[-1].proposal if rounds else None,
            open_challenges,
        )
        critic_turn = criticize(client, feature_request, round_number, proposal, list(ledger.values()))
        critic_turn, notes = apply_critic_turn(ledger, critic_turn, round_number)
        rounds.append(Round(number=round_number, proposal=proposal, critic_turn=critic_turn, notes=notes))
        print(format_round(rounds[-1]))
        open_count = sum(t.state == "open" for t in ledger.values())
        reason = stop_reason(round_number, critic_turn, open_count, round_cap)

    challenges = list(ledger.values())
    decision = summarize(client, feature_request, rounds, challenges)
    escalated = [
        f"{t.challenge.text} (escalated {t.challenge.id})" for t in challenges if t.state == "escalated"
    ]
    decision = decision.model_copy(update={"open_questions": decision.open_questions + escalated})
    run_dir = write_run(runs_dir, feature_request, rounds, reason, decision)
    return RunResult(stop_reason=reason, rounds=rounds, challenges=challenges, decision=decision, run_dir=run_dir)
