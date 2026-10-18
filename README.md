# Deliberation Engine

Turns a vague Government CRM feature request into a structured Decision Document. A **Proposer** puts forward a scope, a **Critic** challenges it over several Rounds, and a **Summarizer** writes up the result: agreed scope, assumptions, open questions, success criteria, and how the deliberation went.

- Spec: [`docs/SPEC.md`](docs/SPEC.md)
- Flow diagram: [`docs/DIAGRAM.md`](docs/DIAGRAM.md)
- Design records: [`docs/adr/`](docs/adr/)
- Terms: [`GLOSSARY.md`](GLOSSARY.md)
- Design reasoning: [`DECISIONS.md`](DECISIONS.md)
- Agent prompts: [`prompts/`](prompts/)

## Setup

You need Python 3.13 and an Anthropic API key.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

Instead of exporting the key, you can copy `.env.example` to `.env` and paste the key there. The engine loads `.env` on startup.

`requirements.txt` has only what the engine needs. `requirements-dev.txt` adds pytest and mypy.

## Run

With no arguments, the engine uses the default Feature Request: *"Project managers should be able to see the full history of engagement with a country before starting a new mission."*

```bash
python main.py
```

To pass your own request as text:

```bash
python main.py --request "The CRM should alert us when our relationship with a country goes cold."
```

To read the request from a file:

```bash
python main.py --request-file my_request.txt
```

Each Round is printed to the console as it runs. The run ends with its Stop Reason and the folder it saved to.

The model is set once, in `engine/config.py` (`MODEL`). The round cap and Challenge limits are set there too.

## Output

Each run writes a new timestamped folder under `runs/`, for example `runs/20261017-142301-123456/`:

| File | Contents |
| --- | --- |
| `trace.md` | Every Round: the Proposer's turn, the Critic's turn, retries, dropped Challenges, and the Stop Reason |
| `decision_document.json` | The Decision Document as JSON, for other tools to read |
| `decision_document.md` | The same Decision Document as Markdown, rendered from the JSON by code |

If an agent's output is still invalid after one retry, the run stops and still saves `trace.md` with everything up to that point.

A full live run of *"The CRM should alert us when our relationship with a country goes cold."*, made with `claude-haiku-5-5`, is committed in [`runs/sample/`](runs/sample/). Other run folders are git-ignored.

## Tests

```bash
pytest
```

The tests use a scripted fake model, so they need no API key and no network.

To typecheck:

```bash
mypy
```

## Layout

```
main.py              CLI entry point
engine/config.py     model name, round cap, Challenge limits, default Feature Request
engine/models.py     shapes of each agent's output and of the Decision Document
engine/agents.py     one function per agent, Confidence rating, and the Anthropic client
engine/deliberation.py  Round loop, Challenge bookkeeping, stop rule
engine/decision.py   builds the Decision Document
engine/render.py     Markdown rendering and run folder output
prompts/             one prompt per agent, plus the shared system context
tests/               behaviour tests through the public entry point
```
