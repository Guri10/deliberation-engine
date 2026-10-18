# Deliberation Engine: Spec

Source: `ai_engineer_assessment.pdf`. Terms are defined in [`GLOSSARY.md`](../GLOSSARY.md). Diagram: [`DIAGRAM.md`](DIAGRAM.md). Question numbers (Q1 to Q30) refer to the design interview that produced this spec.

## Goal

Build a two-agent system (Proposer and Critic, plus a Summarizer) that takes a vague Feature Request for the Government CRM and produces a Decision Document. It must cover every MUST and SHOULD item in the assessment, and both BONUS items.

## Scope of work (Q1)

- Built here: the code, the prompts, `README.md`, a committed sample run, and a `DECISIONS.md` skeleton with headings only.
- Written by the candidate, not generated: the body of `DECISIONS.md`, and the final tuning of the prompts.

## Stack (Q2, Q3, Q4)

- Python 3.13, the `anthropic` SDK, Pydantic. No orchestration framework.
- LangGraph was considered and rejected: the graph has three nodes and one decision point, so the framework would add size and dependencies without adding clarity.
- Model: `claude-haiku-5-5` for all three agents, set in one config value.
- Needs `ANTHROPIC_API_KEY` in the environment.

## Input (Q5, Q8)

- `python main.py --request "..."` or `python main.py --request-file path`.
- Default when neither is given: Example 2, "Project managers should be able to see the full history of engagement with a country before starting a new mission."
- The system context (Government CRM) is fixed text passed to every agent.

## Agents

### What each agent sees (Q21)

| Agent | Sees |
|---|---|
| Proposer | System context, Feature Request, its last proposal, open Challenges |
| Critic | System context, Feature Request, current proposal, all past Challenges with their state |
| Summarizer | Full transcript, both confidence scores |

### Proposer turn (Q10, Q13, Q14, Q17, Q23)

JSON with:
- `scope_in`, `scope_out`: lists.
- `assumptions`: each has `id`, `statement`, `invented` (true or false).
- `success_criteria`: each has `metric` and `threshold`. A criterion without both is not allowed.
- `responses` (from round 2 on): each has `challenge_id`, `type` (`Defend`, `Revise`, or `Concede`), and `text`.

Rules:
- Invented CRM facts are allowed only when needed to reason. Each one is an Assumption with `invented: true`.
- Every `Revise` and `Concede` must quote the Critic argument that changed the Proposer's mind.
- There is no quota on Defend. The trace shows the count of each Response type per round.

### Critic turn (Q15, Q16, Q22, Q30)

JSON with:
- `verdict`: `SATISFIED` or `CONTINUE`.
- `new_challenges`: each has `id`, `target` (an Assumption or Success Criterion id), `type` (`question`, `objection`, or `risk`), and `text`, ranked by importance.
- `challenge_states`: one entry for every Challenge that was open at the start of the turn, with state `open` (plus a reason), `closed`, or `escalated`.

Rules:
- At most 5 new Challenges in round 1, and 3 per round after that. Code drops any extras and logs that it did.
- In every run, the Critic must raise one Challenge on data access and confidentiality (who sees what; how confidential or diplomatic records are handled).
- Escalated means the agents cannot settle it and a human must decide. It becomes an Open Question.

### Summarizer (Q7, Q20)

- Runs once, after the loop ends. Returns the Decision Document as JSON only.
- Code renders the Markdown from that JSON. No LLM is involved in rendering.

## Validation (Q19, Q27)

Two checks run on every agent reply. Each one gets one retry.

1. **Shape check:** the reply must match the Pydantic model. If the retry also fails, the run stops with an error and the trace so far is saved.
2. **Consistency check (Critic only):** these three contradictions count as invalid output:
   - `SATISFIED` while a Challenge is still `open`.
   - `SATISFIED` in round 1.
   - `CONTINUE` with nothing open and no new Challenges.

   The retry message quotes the exact contradiction. If the retry still contradicts itself, a fallback applies: the first two become `CONTINUE`, and the third ends the run with stop reason `critic_exhausted`. The fallback is logged in the trace.

## Termination (Q6, Q22, Q27, Q28, Q29)

Checked after every Critic turn, by one function, in this order:

| Stop reason | Condition |
|---|---|
| `satisfied` | Round ≥ 2, verdict `SATISFIED`, zero open Challenges (escalated ones are allowed) |
| `critic_exhausted` | Consistency fallback from case 3 above |
| `stalled` | Two Rounds in a row with no movement: no Challenge closed or escalated, and no `Revise` or `Concede` |
| `round_cap` | Round 6 finished. Safety net only. |

When the run ends by `stalled` or `round_cap`, every Challenge still open becomes a **blocking** Open Question, tagged with the stop reason.

A flat Disagreement count does not mean a stall. If two Challenges close and two new ones open in the same Round, real work happened.

## Scores (Q7, Q18)

- **Disagreement:** counted by code, not by an agent. It is the number of open Challenges at the end of each Round, plus the change from the previous Round.
- **Confidence:** each agent reports it once, at the end, from 0 to 100, using fixed anchor points in the prompt (90 to 100: would ship as is; 50: major gaps remain), with a one-line reason.

## Output (Q8, Q11, Q12, Q14, Q20, Q29)

Each run writes `runs/<timestamp>/`:
- `trace.md`: every Round, also printed to the console.
- `decision_document.json`: from the Summarizer.
- `decision_document.md`: rendered from the JSON.

Decision Document sections, in order:
1. **Agreed Scope:** in-scope items, out-of-scope items.
2. **Surfaced Assumptions:** statement, Assumption Status (Accepted, Challenged-and-held, Revised, or Dropped), round raised.
3. **Open Questions:** text, blocking or non-blocking, who should answer, source (escalated, invented fact, stalled, round cap).
4. **Invented Facts:** the `invented: true` Assumptions, each also listed as a non-blocking Open Question.
5. **Success Criteria:** metric and threshold.
6. **Deliberation Summary:** rounds run, stop reason, Disagreement per round, both Confidence scores with their reasons.

## Repo layout (Q24, Q25, Q26)

```
prompts/          system_context.md, proposer.md, critic.md, summarizer.md
engine/
  config.py       model name, round cap, default Feature Request
  models.py       Pydantic shapes
  agents.py       one function per agent: load prompt, call Claude, check output
  deliberation.py round loop, consistency check, stop rule
  render.py       Decision Document JSON → Markdown; trace writer
main.py           CLI entry point
tests/            pytest, no API calls
runs/sample/      one committed run of Example 2
README.md  DECISIONS.md (skeleton)  GLOSSARY.md  requirements.txt
```

`runs/*` is git-ignored except `runs/sample/`.

## Tests (Q24, revised at /to-spec)

One seam: the **model client**, a function that takes an agent's system prompt, messages, and expected reply shape, and returns its raw reply text. The real one wraps the `anthropic` SDK. Tests pass a scripted fake that returns canned replies in order. The whole deliberation runs for real, and tests check only what comes out (Stop Reason, Rounds, Challenge States, Open Questions, Disagreement, retries in the transcript, rendered Markdown). They never call internal functions directly. No API calls.

Covered:
- Each stop reason, including "flat count is not a stall."
- The consistency check, its retry, and its fallback.
- Shape failure twice → error, trace saved.
- Challenge limit drops extras and logs it.
- Leftovers become blocking Open Questions; escalated Challenges and Invented Facts become Open Questions.
- The Disagreement count and delta.
- Markdown rendering of the Decision Document (six sections, in order).

## Defaults chosen without a question

- Temperature: not set. Haiku 5.5 rejects non-default sampling values (400), so the planned per-agent temperatures were dropped (found while building #2).
- Structured output: the real client uses `messages.parse` with each agent's Pydantic model, so replies follow the shape. The seam still returns raw text, so tests can feed malformed replies.
- A per-call `max_tokens` limit (16000).
- The API key is read from `.env` (git-ignored; `.env.example` is committed) or the environment.
- Plain `print` for console logging.

## Build order

1. `engine/models.py` and the stop rule in `engine/deliberation.py`, test-first.
2. `engine/agents.py` and the three prompts.
3. `engine/render.py`, `main.py`, and the README.
4. A live run of Example 2, committed to `runs/sample/`.
5. The `DECISIONS.md` skeleton.
