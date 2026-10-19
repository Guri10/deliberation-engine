# Prompt tuning notes (issue #8)

Raw notes from tuning the prompts, for the candidate to draw on when writing `DECISIONS.md`. Not part of the submission text.

## Baseline: 5 live runs before tuning

Requests: the default ("full history of engagement"), "goes cold", partner organizations, minister changes, promises to countries.

| Run | Rounds | Stop reason | Round 2 responses |
| --- | --- | --- | --- |
| Full history (old sample) | 5 | satisfied | Revise 5 of 5 |
| Goes cold | 6 | round cap | Revise 5 of 5 |
| Partner organizations | 4 | satisfied | Revise 5 of 5 |
| Minister changes | 2 | satisfied | Defend 1, Revise 3, Concede 1 |
| Promises | 3 | satisfied | Revise 5 of 5 |

What went wrong:

1. **The Proposer almost never defended.** In 4 of 5 runs it revised every challenge in Round 2. Only 3 Defends across all 20 Rounds.
2. **"Goes cold" hit the round cap while one challenge kept moving.** C5 stayed open for 3 Rounds. Each Round the Critic's open reason named a new gap (snooze caps, then re-firing after acknowledgement), and the Proposer kept re-arguing the original text ("Snooze limits and audit trail were not missing").
3. **The Critic drifted into build detail** in later Rounds: how often recency is checked, a 14-day re-alert holdoff. A team could settle these while building.
4. **The Summarizer repeated escalated challenges** as its own Open Questions (old sample: PDF exports repeats C3, paging repeats C4, completeness counts repeats C6).

## Root cause of problem 2: a code bug, not a prompt

The Proposer was sent only each open challenge's original text, not the Critic's reason for keeping it open (`engine/deliberation.py` passed `t.challenge`). So the Proposer kept answering the old question while the Critic waited for an answer to the new one. Fixed: the Proposer now gets the reason too. Test: `test_proposer_sees_why_the_critic_kept_each_challenge_open`.

## Iteration 1: prompt changes

- **Proposer:** answer the Critic's `reason`, not the original text. Decide whether a challenge is right before answering. Defend when it misreads the proposal, goes beyond the request, or asks for build detail. Revise or Concede only when the position would cause harm, break a system-context rule, or fail its own success criterion. A Defend needs a checkable reason.
- **Critic:** challenge scope, not build detail. From Round 2, only raise challenges that change scope or block building. An open reason must stay on the gap the challenge first named; a new gap becomes a new challenge. A sound Defend is enough to close a challenge.
- **Summarizer:** do not reword escalated or open challenges or invented facts into new questions. Drop questions the final scope made moot.

Result: overcorrected. Default run ended in 2 Rounds, "goes cold" in 3, both satisfied. The default run had one Defend (C3), which the Critic closed. But in "goes cold" the Summarizer found a blocking gap the Critic never raised: the engagement score behind "cold" was never defined. The Critic was being too lenient.

## Iteration 2: prompt changes

- **Critic:** a definition the feature depends on is scope, not detail (for example, how "cold" is scored). Before SATISFIED, re-read the whole proposal, especially what changed this Round, because a fix often opens a new gap. A gap that would block building is never ready to act on.

Result: "goes cold" ran 3 Rounds, the Critic challenged the definition of "cold" directly (C2), caught a gap created by a revision (C6), and accepted one Defend (C3). Default ran 4 Rounds, caught a gap created by a revision (C6), escalated one challenge (C2), but had no Defend: all 4 Round 2 challenges were real gaps.

## Still worth noticing

- Escalated challenges are added to Open Questions by code, so the Summarizer cannot remove one the final scope made moot (old sample C7, name matching). Fixing that would need the Critic to close or the code to drop moot escalations.
- The Critic rarely uses `objection`; most challenges are `question` or `risk`. Questions about real gaps are hard to Defend honestly, which caps how many Defends to expect.

## Iteration 3: variance check, no prompt changes

Two more default-request runs on the final prompts. Both ended satisfied in Round 2 with no Defend. In one, the Critic escalated 3 of 4 challenges. Reading them, the escalations were fair: the Proposer gave concrete defaults but rightly left policy calls (DPO access tiers, cross-project visibility) to their owners.

So across 3 default runs on the final prompts, every Round 2 challenge pointed to a real gap, and the Proposer had nothing honest to Defend. Pushing it harder would have produced fake Defends.

## Iteration 4: review fix

- **Proposer:** the "only Revise or Concede when..." list was closed, so a missing central definition (which the Critic is now told to challenge) fit none of its cases and pushed the Proposer toward a fake Defend. Added a fourth case: the position leaves out something the feature cannot be built without.

Two "goes cold" runs on these final prompts:

- Run A: Revise 5 of 5 in Round 2, then satisfied in Round 2 with 2 escalations. No Defend.
- Run B: Defend 1, Revise 4 in Round 2; one new challenge (C6) in Round 2, revised in Round 3; satisfied in Round 3.

## Committed sample

`runs/sample/` is run B above, on the final prompts. Against the #8 checks:

- **Defend survives a later Round:** C5 Defend in Round 2 (log-completeness risk). It points to what the proposal already covers and declines staff audits as beyond the request. The Critic closed it, and Round 3's proposal still lists staff audits as out of scope.
- **Specific challenges:** C1 to C6 each name an assumption or success criterion and a concrete concern.
- **Escalated / blocking:** C1 is escalated and becomes a blocking Open Question (the last engagement date shown in alerts can reveal restricted interactions).
- **Tension kept:** the Summarizer raised who accepts accountability for log completeness, because the Proposer's Defend assigned it to the Head of Country Engagement without that role confirming.

The sample uses Example 3 ("goes cold"), not the default request: no default-request run on the tuned prompts had a Defend.

## Samples after #9 (agent memory)

After #9 the agents get each open Challenge's history, Settled Challenges, and Proposal Changes, all as JSON. The sample was regenerated on that code with `ROUND_CAP = 9`. Defends stayed rare: over 12 runs of 4 requests, 1 run had a Defend (old code: 2 of 12). No single run met all three #8 checks, so `runs/sample/` now holds two runs:

- `defend/` (Executives request): C2 Defend in Round 3 answers the Critic's earlier reason and points to A2 and A3; the Critic closed it. No escalation.
- `escalation/` (two teams, same ministry): C1 escalated to the Data protection officer, with blocking Open Questions. No Defend.

Known flaw in `escalation/`: one blocking Open Question repeats C1's original text, which the Proposer's Revise had already answered. Code builds escalated Open Questions from the Challenge text, not from what is still open.
