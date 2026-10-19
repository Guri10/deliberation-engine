# Decisions

## How I designed the agent prompts and why

### The tension I wanted to keep

A scoping meeting has two pulls: a small scope that can be built, and a safe, complete one (in this CRM, mostly who can see what). If the Proposer always gives in, scope grows until it can't be built; if the Critic does, gaps stay hidden. Each prompt holds one side. Points neither agent should decide, such as legal or policy calls, go to a person as Open Questions.

### Proposer

Its job is to be wrong in ways the Critic can see: assumptions with fixed ids, measurable success criteria, and every invented CRM fact marked, because a guess presented as fact is the worst output this system could give.

The hard part was holding a position, because Haiku's default is to agree. So the Proposer must first decide whether a challenge is right. It may Revise only when its position causes harm, breaks a system rule, or leaves out who uses the feature, what it shows, or who can see it. That is the scope boundary. Anything else is a builder's choice, so it should Defend. Every Revise or Concede must quote the Critic's words that changed its mind, so giving in leaves a trail.

### Critic

It must name its target, because "this is too vague" can't be answered or closed. It must raise one challenge about who sees what, the system's biggest risk. It challenges scope, not build detail, or runs fill up with screen-layout questions. New challenges are capped (5, then 3 per Round) to stay on the main points, and a checkable Defend is enough to close one.

### Summarizer

Separate because it took no side in the debate. It must keep unsettled points as Open Questions.

### What I rejected

- **Persona prompts:** they set tone, not behaviour.
- **Free-text replies:** code couldn't track states or decide when to stop, so replies are Pydantic-checked JSON.
- **Agents rating their own disagreement:** the numbers just sounded right; code counts open challenges.
- **A required number of Defends:** it would produce fake ones; a real gap deserves a Revise.

### What tuning taught me (`docs/prompt-tuning-notes.md`)

- **Rules interact.** "Be concrete enough that someone could disagree with each item" made the Proposer add features and perfect thresholds, then give them up. Proposing only what the request needs raised Defends from 2% to 13% of responses, all closed by the Critic.
- **Overlapping rules make the model pick the safe one.** A build detail that fitted both Defend and Revise got a Revise.
- **Some prompt problems were code problems:** the Proposer never saw why a challenge stayed open, so it answered the old question.

### What each agent remembers

Only what code puts in the message: Challenge History for each open challenge (both agents), Settled Challenges (Proposer, so it doesn't undo fixes), and Proposal Changes (Critic, to check a claimed Revise; information only, ADR-0001). Per-challenge history beat a full transcript: fewer tokens, and less pull toward repeating old positions.

## How termination works and what alternatives I considered

Each Round the Critic marks every open challenge `open`, `closed`, or `escalated` and gives a verdict. Code then checks, in order:

1. **satisfied:** the verdict is SATISFIED, it is Round 2 or later, and nothing is open.
2. **critic_exhausted:** CONTINUE with nothing open or new, twice.
3. **stalled:** two Rounds with nothing closed or escalated and no Revise or Concede.
4. **round_cap:** 9 Rounds, a backstop only.

**Against agreeing too early:** no Satisfied in Round 1, Satisfied needs zero open challenges, and giving in costs a quote. **Against looping:** escalation hands a point to a person, the stall rule catches repetition, and critic_exhausted catches a Critic with nothing left to say.

Alternatives I rejected:
- **Verdict alone:** a run could stop with challenges open and unrecorded (ADR-0001).
- **Code overrules a contradictory verdict:** the Critic decides when it is done, so the problem goes back to it once (ADR-0001).
- **Stall means Disagreement didn't fall:** two closed and two deeper new challenges leave the count flat, but that is progress (ADR-0002).

## Why no LangGraph or LangChain

The flow is Proposer, Critic, stop check: a plain Python loop on the `anthropic` SDK and Pydantic (ADR-0003). LangGraph's strengths (branching, parallel steps, pause and resume) would go unused, and the stop rule stays one readable function instead of edge conditions. LangChain would wrap what `messages.parse` already gives (Pydantic-checked replies) and put a template layer over prompts that are plain Markdown. One small `ModelClient` interface lets tests swap in a scripted client.

## One thing I would do differently with more time

**Bring a human into the loop during the run.** An escalated challenge already names who should answer it, such as the Data protection officer, but it just waits until the end. Many are quick policy calls. The run would pause, ask that person, and carry the answer into the next Round as a fact both agents must respect, so the Decision Document holds more decisions and fewer questions. The trade-off: runs no longer finish unattended and must save and resume state, which is where LangGraph would earn its place.

## Future scope

- **Stale escalated Open Questions:** use the Critic's last reason instead of the original challenge text, and drop escalations the final scope no longer needs.
- **Read-only CRM tools** (data model, permission rules, record counts): the Proposer could check facts instead of inventing them, and the Critic could test claims, such as how many records lack a project reference. Tools must obey the same confidentiality rules.

## Interpretations

- **Escalated is not open:** a run can end satisfied with escalations, since both agents agree a person must decide them.
- **A Round** is one Proposer turn, then one Critic turn, so "2 rounds" means the Critic judged at least one answer.
- **Disagreement delta:** the Critic has no position, so code counts open challenges per Round, e.g. `5, 1 (-4), 0 (-1)`.
- **"Challenged or accepted"** becomes four statuses: Accepted, Challenged-and-held, Revised, Dropped.
