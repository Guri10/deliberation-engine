"""Shapes of every agent reply and of the Decision Document. A reply that doesn't fit is invalid."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

StopReason = Literal["satisfied", "critic_exhausted", "stalled", "round_cap"]
ChallengeStateValue = Literal["open", "closed", "escalated"]
OpenQuestionSource = Literal["escalated", "invented fact", "stalled", "round cap", "deliberation"]


class Assumption(BaseModel):
    id: str
    statement: str
    invented: bool = Field(
        description="True if this is a fact about the CRM itself (a field, role, or rule) that the system context "
        "does not state, and you supplied it in order to reason."
    )


class SuccessCriterion(BaseModel):
    metric: str
    threshold: str


class Response(BaseModel):
    challenge_id: str
    type: Literal["Defend", "Revise", "Concede"]
    text: str
    quote: str = Field("", description="The Critic's words that changed your mind. Required for Revise and Concede.")

    @model_validator(mode="after")
    def _revise_and_concede_quote_the_critic(self) -> "Response":
        if self.type != "Defend" and not self.quote.strip():
            raise ValueError(f"{self.type} on {self.challenge_id} must quote the Critic argument that changed your mind")
        return self


class ProposerTurn(BaseModel):
    scope_in: list[str]
    scope_out: list[str]
    assumptions: list[Assumption]
    success_criteria: list[SuccessCriterion] = Field(min_length=1)
    responses: list[Response] = []


class Challenge(BaseModel):
    id: str
    target: str
    type: Literal["question", "objection", "risk"]
    text: str
    who_should_answer: str = Field(description="Who would have to decide this if the agents cannot, e.g. 'Legal'.")


class ChallengeState(BaseModel):
    challenge_id: str
    state: ChallengeStateValue
    reason: str = Field("", description="What is still missing. Required when the state is open.")

    @model_validator(mode="after")
    def _open_gives_a_reason(self) -> "ChallengeState":
        if self.state == "open" and not self.reason.strip():
            raise ValueError(f"open state on {self.challenge_id} must give a reason")
        return self


class CriticTurn(BaseModel):
    verdict: Literal["SATISFIED", "CONTINUE"]
    new_challenges: list[Challenge]
    challenge_states: list[ChallengeState]


class TrackedChallenge(BaseModel):
    """A Challenge with where it stands now and the Round it was raised in."""

    challenge: Challenge
    state: ChallengeStateValue = "open"
    reason: str = ""
    raised_in_round: int


class Round(BaseModel):
    number: int
    proposal: ProposerTurn
    critic_turn: CriticTurn
    notes: list[str] = []
    disagreement: int = Field(description="Challenges still open at the end of this Round, counted by code.")
    disagreement_change: int | None = Field(description="Change from the previous Round; None in Round 1.")


class Confidence(BaseModel):
    score: int = Field(ge=0, le=100)
    reason: str


AssumptionStatus = Literal["Accepted", "Challenged-and-held", "Revised", "Dropped"]


class SummarizedAssumption(BaseModel):
    id: str
    statement: str
    status: AssumptionStatus


class SummarizedOpenQuestion(BaseModel):
    text: str
    blocking: bool
    who_should_answer: str


class SummarizerTurn(BaseModel):
    """What the Summarizer writes. Code adds the rest of the Decision Document."""

    scope_in: list[str]
    scope_out: list[str]
    assumptions: list[SummarizedAssumption]
    open_questions: list[SummarizedOpenQuestion]
    success_criteria: list[SuccessCriterion]


class SurfacedAssumption(SummarizedAssumption):
    round_raised: int | None


class OpenQuestion(SummarizedOpenQuestion):
    source: OpenQuestionSource
    challenge_id: str | None = None


class DisagreementPoint(BaseModel):
    round: int
    open: int
    change: int | None


class DeliberationSummary(BaseModel):
    rounds_run: int
    disagreement: list[DisagreementPoint]
    proposer_confidence: Confidence
    critic_confidence: Confidence


class DecisionDocument(BaseModel):
    stop_reason: StopReason
    scope_in: list[str]
    scope_out: list[str]
    assumptions: list[SurfacedAssumption]
    open_questions: list[OpenQuestion]
    invented_facts: list[Assumption]
    success_criteria: list[SuccessCriterion]
    summary: DeliberationSummary
