"""Builds the Decision Document from the Summarizer's turn plus what code knows about the run."""

from engine.models import (
    Confidence,
    DecisionDocument,
    DeliberationSummary,
    DisagreementPoint,
    OpenQuestion,
    OpenQuestionSource,
    Round,
    StopReason,
    SummarizerTurn,
    SurfacedAssumption,
    TrackedChallenge,
)

INVENTED_FACT_OWNER = "CRM system owner"


def challenge_open_questions(challenges: list[TrackedChallenge], reason: StopReason) -> list[OpenQuestion]:
    """Open Questions that come from Challenges, added by code so they never depend on the Summarizer.

    Escalated Challenges always become blocking Open Questions, since a human must decide them.
    When the run stalled or ran out of Rounds, every Challenge still open becomes a blocking one too,
    tagged with the Stop Reason.
    """
    sources: dict[str, OpenQuestionSource] = {"escalated": "escalated"}
    if reason == "stalled":
        sources["open"] = "stalled"
    elif reason == "round_cap":
        sources["open"] = "round cap"
    return [
        OpenQuestion(
            text=t.challenge.text,
            blocking=True,
            who_should_answer=t.challenge.who_should_answer,
            source=sources[t.state],
            challenge_id=t.challenge.id,
        )
        for t in challenges
        if t.state in sources
    ]


def _round_raised(rounds: list[Round], assumption_id: str) -> int | None:
    return next((r.number for r in rounds if any(a.id == assumption_id for a in r.proposal.assumptions)), None)


def build_decision_document(
    turn: SummarizerTurn,
    rounds: list[Round],
    challenges: list[TrackedChallenge],
    reason: StopReason,
    proposer_confidence: Confidence,
    critic_confidence: Confidence,
) -> DecisionDocument:
    invented_facts = [a for a in rounds[-1].proposal.assumptions if a.invented]
    open_questions = [OpenQuestion(**q.model_dump(), source="deliberation") for q in turn.open_questions]
    open_questions += challenge_open_questions(challenges, reason)
    open_questions += [
        OpenQuestion(
            text=f"Confirm {a.id}: {a.statement}",
            blocking=False,
            who_should_answer=INVENTED_FACT_OWNER,
            source="invented fact",
        )
        for a in invented_facts
    ]
    return DecisionDocument(
        stop_reason=reason,
        scope_in=turn.scope_in,
        scope_out=turn.scope_out,
        assumptions=[
            SurfacedAssumption(**a.model_dump(), round_raised=_round_raised(rounds, a.id)) for a in turn.assumptions
        ],
        open_questions=open_questions,
        invented_facts=invented_facts,
        success_criteria=turn.success_criteria,
        summary=DeliberationSummary(
            rounds_run=len(rounds),
            disagreement=[
                DisagreementPoint(round=r.number, open=r.disagreement, change=r.disagreement_change) for r in rounds
            ],
            proposer_confidence=proposer_confidence,
            critic_confidence=critic_confidence,
        ),
    )
