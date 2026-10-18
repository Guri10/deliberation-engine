"""Shapes of every agent reply and of the Decision Document. A reply that doesn't fit is invalid."""

from typing import Literal

from pydantic import BaseModel, Field

StopReason = Literal["satisfied", "round_cap"]


class Assumption(BaseModel):
    id: str
    statement: str


class SuccessCriterion(BaseModel):
    metric: str
    threshold: str


class ProposerTurn(BaseModel):
    scope_in: list[str]
    scope_out: list[str]
    assumptions: list[Assumption]
    success_criteria: list[SuccessCriterion] = Field(min_length=1)


class Challenge(BaseModel):
    id: str
    target: str
    text: str


class CriticTurn(BaseModel):
    verdict: Literal["SATISFIED", "CONTINUE"]
    challenges: list[Challenge]


class Round(BaseModel):
    number: int
    proposal: ProposerTurn
    critic_turn: CriticTurn


class SurfacedAssumption(BaseModel):
    statement: str
    status: Literal["Accepted", "Challenged-and-held", "Revised", "Dropped"]


class DecisionDocument(BaseModel):
    scope_in: list[str]
    scope_out: list[str]
    assumptions: list[SurfacedAssumption]
    open_questions: list[str]
    success_criteria: list[SuccessCriterion]
