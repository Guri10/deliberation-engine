# System Diagram

```
                      ┌─────────────────────────────────────────┐
  CLI (main.py)       │ --request "..." | --request-file path   │
                      │ default: Example 2 + system context     │
                      └───────────────────┬─────────────────────┘
                                          │
  prompts/ ──────────────┐                ▼
  proposer.md            │  ┌──────────── ROUND LOOP (engine/deliberation.py) ────────────┐
  critic.md              ├─▶│                                                             │
  summarizer.md          │  │   ┌──────────────┐  proposal (scope, assumptions,           │
                         │  │   │   PROPOSER   │  criteria, responses)                    │
  engine/models.py ──────┤  │   │  Haiku 5.5   │──────────────┐                           │
  (Pydantic shapes:      │  │   └──────▲───────┘              ▼                           │
   check every reply,    │  │          │               ┌──────────────┐                   │
   retry once if bad)    │  │   open challenges        │    CRITIC    │                   │
                         │  │          │               │  Haiku 5.5   │                   │
                         │  │          │               └──────┬───────┘                   │
                         │  │          │   verdict + new challenges (≤5, then ≤3)         │
                         │  │          │   + state of each old one: open/closed/escalated │
                         │  │          │                      ▼                           │
                         │  │          │        ┌───────────────────────────┐             │
                         │  │          │        │ consistency check         │ contradiction│
                         │  │          │        │ (verdict vs. challenges)  │──▶ retry once│
                         │  │          │        └─────────────┬─────────────┘   (fallback) │
                         │  │          │                      ▼                           │
                         │  │          │        ┌───────────────────────────┐             │
                         │  │          │        │ STOP RULE                 │             │
                         │  │          └────────│  continue?                │             │
                         │  │        CONTINUE   │                           │             │
                         │  │                   │  satisfied  (round ≥2,    │             │
                         │  │                   │             0 open)       │             │
                         │  │                   │  stalled    (2 rounds,    │             │
                         │  │                   │             no movement)  │             │
                         │  │                   │  round_cap  (6)           │             │
                         │  │                   │  critic_exhausted         │             │
                         │  │                   └─────────────┬─────────────┘             │
                         │  └─────────────────────────────────┼───────────────────────────┘
                         │        each round → trace.md       │ STOP
                         │        (+ console, disagreement    │ leftovers → blocking
                         │         count & delta)             │ Open Questions
                         │                                    ▼
                         │                          ┌──────────────────┐
                         └─────────────────────────▶│    SUMMARIZER    │ reads full transcript,
                                                    │    Haiku 5.5     │ + both agents' confidence
                                                    └────────┬─────────┘
                                                             │ JSON
                                                             ▼
                                                    ┌──────────────────┐
                                                    │ engine/render.py │ JSON → Markdown (no LLM)
                                                    └────────┬─────────┘
                                                             ▼
                                  runs/<timestamp>/  trace.md
                                                     decision_document.json
                                                     decision_document.md
```

## How to read it

- **Loop:** the Proposer proposes, the Critic challenges, then code checks the Critic's reply and applies the stop rule. On Continue, the Proposer gets back only the open challenges.
- **Two checks:** the shape check (Pydantic, `engine/models.py`) catches malformed JSON. The consistency check catches a Critic whose verdict contradicts its own challenge states. Each one retries once.
- **Stop rule:** one function in `engine/deliberation.py` owns all four stop reasons.
- **Summarizer:** the only agent that sees the whole transcript. Code, not the LLM, writes the Markdown.
