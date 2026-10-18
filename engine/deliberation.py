"""The Round loop and the stop rule."""

from dataclasses import dataclass
from pathlib import Path

from engine.agents import ModelClient, criticize, propose, summarize
from engine.config import ROUND_CAP
from engine.models import CriticTurn, DecisionDocument, Round, StopReason
from engine.render import format_round, write_run


@dataclass
class RunResult:
    stop_reason: StopReason
    rounds: list[Round]
    decision: DecisionDocument
    run_dir: Path


def stop_reason(round_number: int, critic_turn: CriticTurn, round_cap: int) -> StopReason | None:
    """Why the deliberation should end after this Round, or None to continue."""
    if critic_turn.verdict == "SATISFIED" and round_number >= 2:
        return "satisfied"
    if round_number >= round_cap:
        return "round_cap"
    return None


def run_deliberation(
    feature_request: str,
    client: ModelClient,
    runs_dir: Path = Path("runs"),
    round_cap: int = ROUND_CAP,
) -> RunResult:
    rounds: list[Round] = []
    reason: StopReason | None = None

    while reason is None:
        round_number = len(rounds) + 1
        last = rounds[-1] if rounds else None
        proposal = propose(
            client,
            feature_request,
            last.proposal if last else None,
            last.critic_turn.challenges if last else [],
        )
        past_challenges = [c for r in rounds for c in r.critic_turn.challenges]
        critic_turn = criticize(client, feature_request, round_number, proposal, past_challenges)
        rounds.append(Round(number=round_number, proposal=proposal, critic_turn=critic_turn))
        print(format_round(rounds[-1]))
        reason = stop_reason(round_number, critic_turn, round_cap)

    decision = summarize(client, feature_request, rounds)
    run_dir = write_run(runs_dir, feature_request, rounds, reason, decision)
    return RunResult(stop_reason=reason, rounds=rounds, decision=decision, run_dir=run_dir)
