"""One function per agent: build its context, call the model client, check the reply's shape."""

import json
from typing import Protocol, TypeVar

import anthropic
from anthropic.types import MessageParam
from pydantic import BaseModel

from engine.config import MAX_TOKENS, MODEL, PROMPTS_DIR, SYSTEM_CONTEXT
from engine.models import Challenge, CriticTurn, DecisionDocument, ProposerTurn, Round

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


def _ask(client: ModelClient, agent: str, content: str, output_model: type[T]) -> T:
    system = f"{SYSTEM_CONTEXT}\n\n{(PROMPTS_DIR / f'{agent}.md').read_text()}"
    raw = client(system, [{"role": "user", "content": content}], output_model)
    return output_model.model_validate_json(raw)


def _challenges_json(challenges: list[Challenge]) -> str:
    return json.dumps([c.model_dump() for c in challenges], indent=2)


def propose(
    client: ModelClient,
    feature_request: str,
    last_proposal: ProposerTurn | None,
    challenges: list[Challenge],
) -> ProposerTurn:
    content = f"Feature request:\n{feature_request}"
    if last_proposal is not None:
        content += (
            f"\n\nYour last proposal:\n{last_proposal.model_dump_json(indent=2)}"
            f"\n\nThe Critic's challenges:\n{_challenges_json(challenges)}"
            "\n\nWrite your updated proposal."
        )
    return _ask(client, "proposer", content, ProposerTurn)


def criticize(
    client: ModelClient,
    feature_request: str,
    round_number: int,
    proposal: ProposerTurn,
    past_challenges: list[Challenge],
) -> CriticTurn:
    content = (
        f"Feature request:\n{feature_request}"
        f"\n\nThis is round {round_number}."
        f"\n\nCurrent proposal:\n{proposal.model_dump_json(indent=2)}"
        f"\n\nChallenges you raised in earlier rounds:\n{_challenges_json(past_challenges)}"
    )
    return _ask(client, "critic", content, CriticTurn)


def summarize(client: ModelClient, feature_request: str, rounds: list[Round]) -> DecisionDocument:
    transcript = json.dumps([r.model_dump() for r in rounds], indent=2)
    content = f"Feature request:\n{feature_request}\n\nFull deliberation transcript:\n{transcript}"
    return _ask(client, "summarizer", content, DecisionDocument)
