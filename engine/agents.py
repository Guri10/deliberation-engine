"""One function per agent: build its context, call the model client, check the reply's shape."""

import json
from pathlib import Path
from collections.abc import Callable
from typing import Literal, Protocol, TypeVar

import anthropic
from anthropic.types import MessageParam
from pydantic import BaseModel, ValidationError

from engine.config import MAX_TOKENS, MODEL, PROMPTS_DIR, SYSTEM_CONTEXT
from engine.models import (
    Challenge,
    Confidence,
    CriticTurn,
    ProposerTurn,
    Round,
    SummarizerTurn,
    TrackedChallenge,
)

T = TypeVar("T", bound=BaseModel)


class ModelClient(Protocol):
    """The seam between the engine and Claude: takes a system prompt and messages, returns raw reply text."""

    def __call__(self, system: str, messages: list[MessageParam], output_model: type[BaseModel]) -> str: ...


class AnthropicClient:
    """Calls Claude with structured output so the reply follows the agent's shape."""

    def __init__(self, model: str = MODEL, max_tokens: int = MAX_TOKENS):
        self._client = anthropic.Anthropic()
        self._model = model
        self._max_tokens = max_tokens

    def __call__(self, system: str, messages: list[MessageParam], output_model: type[BaseModel]) -> str:
        response = self._client.messages.parse(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=messages,
            output_format=output_model,
        )
        return next(block.text for block in response.content if block.type == "text")


class AgentReplyError(Exception):
    """An agent's reply was still invalid after its one retry.

    `notes` are the trace notes of the unfinished Round. `run_dir` is set once the trace is saved.
    """

    def __init__(self, message: str, notes: list[str]):
        super().__init__(message)
        self.notes = notes
        self.run_dir: Path | None = None


def _send_back(messages: list[MessageParam], reply: str, problem: str) -> list[MessageParam]:
    """The conversation so far, plus the agent's reply and what is wrong with it."""
    return messages + [
        {"role": "assistant", "content": reply or "(empty reply)"},
        {"role": "user", "content": f"{problem}\nReply again with the whole turn."},
    ]


def _ask(
    client: ModelClient,
    agent: str,
    messages: list[MessageParam],
    output_model: type[T],
    notes: list[str],
    check: Callable[[T], str | None] = lambda _: None,
) -> T:
    """Call the agent and check its reply's shape. An invalid reply is sent back once with the problem."""
    system = f"{SYSTEM_CONTEXT}\n\n{(PROMPTS_DIR / f'{agent}.md').read_text()}"
    for attempt in (1, 2):
        raw = client(system, messages, output_model)
        try:
            reply = output_model.model_validate_json(raw)
            problem = check(reply)
        except ValidationError as error:
            problem = " ".join(str(error).split())
        if problem is None:
            return reply
        if attempt == 1:
            notes.append(f"{agent.capitalize()} reply was invalid, retried: {problem}")
            messages = _send_back(messages, raw, f"Your reply was invalid: {problem}")
    raise AgentReplyError(f"{agent.capitalize()} reply was invalid twice: {problem}", list(notes))


def _user(content: str) -> list[MessageParam]:
    return [{"role": "user", "content": content}]


def _json(items: list[Challenge] | list[TrackedChallenge] | list[Round]) -> str:
    return json.dumps([item.model_dump() for item in items], indent=2)


def propose(
    client: ModelClient,
    feature_request: str,
    last_proposal: ProposerTurn | None,
    open_challenges: list[Challenge],
    notes: list[str],
) -> ProposerTurn:
    content = f"Feature request:\n{feature_request}"
    if last_proposal is not None:
        content += (
            f"\n\nYour last proposal:\n{last_proposal.model_dump_json(indent=2)}"
            f"\n\nThe Critic's open challenges:\n{_json(open_challenges)}"
            "\n\nWrite your updated proposal, with one response for each open challenge."
        )
    open_ids = sorted(c.id for c in open_challenges)

    def responds_to_open_challenges(turn: ProposerTurn) -> str | None:
        answered = sorted(r.challenge_id for r in turn.responses)
        if answered == open_ids:
            return None
        return f"give one response for exactly the open challenges {open_ids}, not {answered}"

    return _ask(client, "proposer", _user(content), ProposerTurn, notes, responds_to_open_challenges)


def criticize(
    client: ModelClient,
    feature_request: str,
    round_number: int,
    proposal: ProposerTurn,
    past_challenges: list[TrackedChallenge],
    notes: list[str],
    contradiction: tuple[CriticTurn, str] | None = None,
) -> CriticTurn:
    """Ask the Critic for its turn. With `contradiction`, send back its last turn and the problem to fix."""
    open_ids = [t.challenge.id for t in past_challenges if t.state == "open"]
    content = (
        f"Feature request:\n{feature_request}"
        f"\n\nThis is round {round_number}."
        f"\n\nCurrent proposal, with the Proposer's responses:\n{proposal.model_dump_json(indent=2)}"
        f"\n\nChallenges you raised in earlier rounds, with their states:\n{_json(past_challenges)}"
        f"\n\nGive a challenge state for each of these open challenges: {', '.join(open_ids) or '(none)'}."
    )

    def states_cover_open_challenges(turn: CriticTurn) -> str | None:
        stated = sorted(s.challenge_id for s in turn.challenge_states)
        if stated == sorted(open_ids):
            return None
        return f"give a state for exactly the open challenges {sorted(open_ids)}, not {stated}"

    messages = _user(content)
    if contradiction is not None:
        last_turn, problem = contradiction
        messages = _send_back(
            messages, last_turn.model_dump_json(), f"Your verdict contradicts your own turn: {problem}"
        )
    return _ask(client, "critic", messages, CriticTurn, notes, states_cover_open_challenges)


def rate_confidence(
    client: ModelClient,
    agent: Literal["proposer", "critic"],
    feature_request: str,
    final_proposal: ProposerTurn,
    challenges: list[TrackedChallenge],
    notes: list[str],
) -> Confidence:
    """Ask the Proposer or the Critic, once the deliberation has ended, how ready the final scope is."""
    content = (
        f"{(PROMPTS_DIR / 'confidence.md').read_text()}"
        f"\n\nFeature request:\n{feature_request}"
        f"\n\nFinal proposal:\n{final_proposal.model_dump_json(indent=2)}"
        f"\n\nEvery challenge with its final state:\n{_json(challenges)}"
    )
    return _ask(client, agent, _user(content), Confidence, notes)


def summarize(
    client: ModelClient,
    feature_request: str,
    rounds: list[Round],
    challenges: list[TrackedChallenge],
    proposer_confidence: Confidence,
    critic_confidence: Confidence,
    notes: list[str],
) -> SummarizerTurn:
    scores = "\n".join(
        f"{agent}: {c.score} ({c.reason})"
        for agent, c in (("Proposer", proposer_confidence), ("Critic", critic_confidence))
    )
    content = (
        f"Feature request:\n{feature_request}"
        f"\n\nFull deliberation transcript:\n{_json(rounds)}"
        f"\n\nEvery challenge with its final state:\n{_json(challenges)}"
        f"\n\nConfidence scores:\n{scores}"
    )
    raised_ids = sorted({a.id for r in rounds for a in r.proposal.assumptions})

    def covers_every_assumption(turn: SummarizerTurn) -> str | None:
        given = sorted(a.id for a in turn.assumptions)
        if given == raised_ids:
            return None
        return f"give one status for exactly the assumptions raised {raised_ids}, not {given}"

    return _ask(client, "summarizer", _user(content), SummarizerTurn, notes, covers_every_assumption)
