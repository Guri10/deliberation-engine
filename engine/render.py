"""Turns Rounds and the Decision Document into Markdown, and writes a run folder."""

from datetime import datetime
from pathlib import Path

from engine.models import DecisionDocument, OpenQuestion, Response, Round, SuccessCriterion, SurfacedAssumption


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- (none)"


def _criteria(criteria: list[SuccessCriterion]) -> str:
    return _bullets([f"{s.metric}: {s.threshold}" for s in criteria])


def _scope(scope_in: list[str], scope_out: list[str]) -> str:
    return f"**In scope:**\n{_bullets(scope_in)}\n**Out of scope:**\n{_bullets(scope_out)}"


def notes_block(notes: list[str]) -> str:
    return f"**Notes:**\n{_bullets(notes)}"


def _response(r: Response) -> str:
    quote = f' (quoting "{r.quote}")' if r.quote else ""
    return f"{r.challenge_id} {r.type}{quote}: {r.text}"


def _response_counts(responses: list[Response]) -> str:
    types = [r.type for r in responses]
    return ", ".join(f"{t} {types.count(t)}" for t in ("Defend", "Revise", "Concede"))


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
        f"**Response counts:** {_response_counts(proposal.responses)}",
        "",
        f"### Critic: {critic_turn.verdict}",
        "**Challenge states:**",
        _bullets([
            f"{s.challenge_id}: {s.state}" + (f" ({s.reason})" if s.reason else "")
            for s in critic_turn.challenge_states
        ]),
        "**New challenges:**",
        _bullets([f"{c.id} [{c.type}] on {c.target}: {c.text}" for c in critic_turn.new_challenges]),
        f"**Disagreement:** {round_.disagreement} open ({_change(round_.disagreement_change, 'first round')})",
        *([notes_block(round_.notes)] if round_.notes else []),
        "",
    ])


def _change(change: int | None, if_none: str) -> str:
    return if_none if change is None else f"{change:+d}"


def _open_question(q: OpenQuestion) -> str:
    kind = "Blocking" if q.blocking else "Non-blocking"
    source = q.source + (f", {q.challenge_id}" if q.challenge_id else "")
    return f"**{kind}:** {q.text} (answer: {q.who_should_answer}; source: {source})"


def _assumption(a: SurfacedAssumption) -> str:
    raised = f"raised in round {a.round_raised}" if a.round_raised is not None else "round raised unknown"
    return f"{a.id}: {a.statement} ({a.status}; {raised})"


def render_decision(decision: DecisionDocument) -> str:
    summary = decision.summary
    disagreement = ", ".join(
        f"R{d.round} {d.open}" + ("" if d.change is None else f" ({_change(d.change, '')})")
        for d in summary.disagreement
    )
    confidence = [
        f"- {agent} confidence: {c.score} ({c.reason})"
        for agent, c in (("Proposer", summary.proposer_confidence), ("Critic", summary.critic_confidence))
    ]
    return "\n".join([
        "# Decision Document",
        f"_Stop reason: {decision.stop_reason}_",
        "",
        "## Agreed Scope",
        _scope(decision.scope_in, decision.scope_out),
        "",
        "## Surfaced Assumptions",
        _bullets([_assumption(a) for a in decision.assumptions]),
        "",
        "## Open Questions",
        _bullets([_open_question(q) for q in decision.open_questions]),
        "",
        "## Invented Facts",
        _bullets([f"{a.id}: {a.statement}" for a in decision.invented_facts]),
        "",
        "## Success Criteria",
        _criteria(decision.success_criteria),
        "",
        "## Deliberation Summary",
        f"- Rounds run: {summary.rounds_run}",
        f"- Stop reason: {decision.stop_reason}",
        f"- Disagreement per round: {disagreement}",
        *confidence,
        "",
    ])


def new_run_dir(runs_dir: Path) -> Path:
    run_dir = runs_dir / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    run_dir.mkdir(parents=True)
    return run_dir


def write_trace(run_dir: Path, feature_request: str, rounds: list[Round], footer: list[str]) -> None:
    """Write every finished Round, then run-level lines such as the stop reason or an error."""
    trace = [f"# Deliberation trace\n\n**Feature request:** {feature_request}\n"]
    trace += [format_round(r) for r in rounds]
    trace += [f"{line}\n" for line in footer]
    (run_dir / "trace.md").write_text("\n".join(trace))


def write_decision(run_dir: Path, decision: DecisionDocument) -> None:
    (run_dir / "decision_document.json").write_text(decision.model_dump_json(indent=2))
    (run_dir / "decision_document.md").write_text(render_decision(decision))
