"""Shapes of every agent reply and of the Decision Document. A reply that doesn't fit is invalid."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

StopReason = Literal["satisfied", "critic_exhausted", "stalled", "round_cap"]
ChallengeStateValue = Literal["open", "closed", "escalated"]


class Assumption(BaseModel):
    id: str
    statement: str


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


class SurfacedAssumption(BaseModel):
    statement: str
    status: Literal["Accepted", "Challenged-and-held", "Revised", "Dropped"]


class DecisionDocument(BaseModel):
    scope_in: list[str]
    scope_out: list[str]
    assumptions: list[SurfacedAssumption]
    open_questions: list[str]
    success_criteria: list[SuccessCriterion]
