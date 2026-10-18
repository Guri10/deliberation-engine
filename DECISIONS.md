# Decisions

## How I designed the agent prompts and why

All agents share one short system context, and each has its own prompt in `prompts/`. Every reply must be JSON in a fixed shape, checked with Pydantic; a broken reply gets one more try. I used JSON so that code, not the model, keeps track of each challenge's state, the challenge limits, the Disagreement count, and when to stop.

- **Proposer** must turn the request into things the Critic can argue with: a clear list of what is in and out of scope, assumptions with fixed ids, and success criteria with a metric and a threshold. Every Revise or Concede must quote the Critic's words that changed its mind, so you can see why it changed.
- **Critic** must name the assumption or criterion it is challenging. Vague comments like "consider edge cases" are not allowed. It must raise at least one challenge about who can see what, because that is the biggest risk in this system. It should question scope, not small build details. New challenges are ranked and limited (5 in Round 1, 3 after that), so later Rounds stay on the most important points.
- **Summarizer** is a separate agent because it was not part of the debate, so it has no side to defend. It must keep unsettled points as Open Questions.

For scoring, code counts Disagreement (see Interpretations). If you ask an agent to rate its own disagreement, it tends to give a number that just sounds right. Confidence is rated by each agent once at the end, using fixed reference points (90+ means ready to ship, 50 means big gaps remain).

What changed the prompts most during tuning (notes in `docs/prompt-tuning-notes.md`):
- Before tuning, the Proposer gave in on every challenge in Round 2 in 4 of 5 runs. I added a rule: first decide if the challenge is right. Defend when the Critic misread the proposal, asks for more than the request, or asks about a build detail.
- Then the Critic became too easy to satisfy (one run never defined "cold"). So missing definitions now count as scope, and the Critic re-reads what changed before saying Satisfied.
- The biggest fix was in the code, not a prompt. The Proposer was never shown the Critic's reason for keeping a challenge open, so it kept answering the old question. That is why the "goes cold" run hit the round cap.

## How termination works and what alternatives I considered

Each Round, the Critic marks every open challenge as `open`, `closed`, or `escalated`, and gives a verdict. After each Round, code checks these in order:

1. **satisfied:** the verdict is SATISFIED, it is Round 2 or later, and no challenge is open.
2. **critic_exhausted:** the Critic said CONTINUE with nothing open and nothing new, and said it again after being told about the problem once.
3. **stalled:** two Rounds in a row where no challenge was closed or escalated, and the Proposer made no Revise or Concede.
4. **round_cap:** 6 Rounds.

Each rule protects against one of the two problems the brief names:
- **Agreeing too early:** the Critic cannot be satisfied in Round 1. Satisfied needs zero open challenges, not just the verdict. Every Revise or Concede must quote the Critic, and the Proposer must decide if a challenge is right before giving in.
- **Looping forever:** escalation gives the Critic a third choice besides "agree too early" and "keep arguing": pass the point to a person. The stall rule stops the same arguments repeating. critic_exhausted stops a Critic with nothing left to say. The round cap is only a backstop.

Alternatives I considered:
- **Verdict alone** (the Critic says Satisfied and the run stops). Rejected: the run could stop with challenges still open, and nothing would record them. (ADR-0001)
- **Code quietly overrules a verdict that does not match the states.** Rejected: the brief says the Critic decides when it is done. Instead, the problem is sent back once, and code only steps in if it happens again. (ADR-0001)
- **Stall means the Disagreement count did not go down.** Rejected: if two challenges close and two new, deeper ones open, the count stays the same, but the run is still making progress. (ADR-0002)
- **LangGraph.** Rejected in favour of a plain loop: three steps and one decision do not need a framework, and the stop rule stays as plain code a reviewer can read. (ADR-0003)

## One thing I would do differently with more time

Let the Critic, or the code, remove escalated challenges that the final scope no longer needs. Right now code always adds escalated challenges to Open Questions, so the Decision Document can list a question that no longer matters (for example, name matching, C7 in an early sample).

## Interpretations

- **Escalated is not open.** A run can end satisfied with escalated challenges, because both agents agree a person must decide them. Escalated and leftover open challenges become Open Questions.
- **A Round** is one Proposer turn and then one Critic turn. So "a minimum of 2 rounds" means the Critic has judged at least one answer from the Proposer before the run can end.
- **No data model is given.** The system context names the users and records but not the fields or rules, so the agents have to guess some. The Proposer marks each guess as `invented`, and each one becomes a non-blocking Open Question for the CRM owner.
- **Disagreement delta.** The brief does not say how to measure the gap between two positions, and the Critic has no position of its own. So I count the open challenges at the end of each Round and show the change, for example `5, 1 (-4), 0 (-1)`.
- **"Challenged or accepted"** becomes four statuses: Accepted, Challenged-and-held, Revised, Dropped. "Challenged" alone does not say whether the assumption survived.
