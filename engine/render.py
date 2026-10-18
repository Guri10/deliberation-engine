"""Turns Rounds and the Decision Document into Markdown, and writes a run folder."""

from datetime import datetime
from pathlib import Path

from engine.models import DecisionDocument, Response, Round, StopReason, SuccessCriterion


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- (none)"


def _criteria(criteria: list[SuccessCriterion]) -> str:
    return _bullets([f"{s.metric}: {s.threshold}" for s in criteria])


def _scope(scope_in: list[str], scope_out: list[str]) -> str:
    return f"**In scope:**\n{_bullets(scope_in)}\n**Out of scope:**\n{_bullets(scope_out)}"


def _response(r: Response) -> str:
    quote = f' (quoting "{r.quote}")' if r.quote else ""
    return f"{r.challenge_id} {r.type}{quote}: {r.text}"


def format_round(round_: Round) -> str:
    proposal, critic_turn = round_.proposal, round_.critic_turn
    return "\n".join([
        f"## Round {round_.number}",
        "",
        "### Proposer",
        _scope(proposal.scope_in, proposal.scope_out),
        f"**Assumptions:**\n{_bullets([f'{a.id}: {a.statement}' for a in proposal.assumptions])}",
        f"**Success criteria:**\n{_criteria(proposal.success_criteria)}",
        f"**Responses:**\n{_bullets([_response(r) for r in proposal.responses])}",
        "",
        f"### Critic: {critic_turn.verdict}",
        "**Challenge states:**",
        _bullets([
            f"{s.challenge_id}: {s.state}" + (f" ({s.reason})" if s.reason else "")
            for s in critic_turn.challenge_states
        ]),
        "**New challenges:**",
        _bullets([f"{c.id} [{c.type}] on {c.target}: {c.text}" for c in critic_turn.new_challenges]),
        *([f"**Notes:**\n{_bullets(round_.notes)}"] if round_.notes else []),
        "",
    ])


def render_decision(decision: DecisionDocument, stop_reason: StopReason, rounds_run: int) -> str:
    return "\n".join([
        "# Decision Document",
        f"_Stop reason: {stop_reason}_",
        "",
        "## Agreed Scope",
        _scope(decision.scope_in, decision.scope_out),
        "",
        "## Surfaced Assumptions",
        _bullets([f"{a.statement} ({a.status})" for a in decision.assumptions]),
        "",
        "## Open Questions",
        _bullets(decision.open_questions),
        "",
        "## Success Criteria",
        _criteria(decision.success_criteria),
        "",
        "## Deliberation Summary",
        f"- Rounds run: {rounds_run}",
        f"- Stop reason: {stop_reason}",
        "",
    ])


def write_run(
    runs_dir: Path,
    feature_request: str,
    rounds: list[Round],
    stop_reason: StopReason,
    decision: DecisionDocument,
) -> Path:
    run_dir = runs_dir / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    run_dir.mkdir(parents=True)
    trace = [f"# Deliberation trace\n\n**Feature request:** {feature_request}\n"]
    trace += [format_round(r) for r in rounds]
    trace.append(f"**Stop reason:** {stop_reason}\n")
    (run_dir / "trace.md").write_text("\n".join(trace))
    (run_dir / "decision_document.json").write_text(decision.model_dump_json(indent=2))
    (run_dir / "decision_document.md").write_text(render_decision(decision, stop_reason, len(rounds)))
    return run_dir
