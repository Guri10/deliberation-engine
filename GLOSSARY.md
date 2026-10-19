# Deliberation Engine

A two-agent dialogue that turns a vague feature request for a Government CRM into a structured decision document, by having one agent propose a scope and the other challenge it.

## Participants

**Proposer**:
The agent that interprets the feature request and puts forward a scope, assumptions, and success criteria it is willing to defend.
_Avoid_: Planner, author, agent 1

**Critic**:
The agent that challenges the Proposer's position to make it more robust, and decides when deliberation is complete.
_Avoid_: Reviewer, skeptic, agent 2

**Summarizer**:
The agent that reads the whole deliberation once it has ended and writes the Decision Document.
_Avoid_: Reporter, synthesizer

## Deliberation

**Feature Request**:
The vague, stakeholder-written request that starts a deliberation.
_Avoid_: Prompt, input, ticket

**Round**:
One Proposer turn followed by one Critic turn.
_Avoid_: Turn, iteration, exchange

**Assumption**:
A claim the Proposer makes about what the Feature Request means or about how the CRM works.
_Avoid_: Premise, hypothesis

**Invented Fact**:
An Assumption about the CRM itself (a field, role, or rule) that the system context does not state and the Proposer supplied in order to reason.
_Avoid_: Guess, placeholder

**Success Criterion**:
A measurable condition, with a metric and a threshold, that tells whether the feature worked.
_Avoid_: Goal, KPI, acceptance criterion

**Challenge**:
A specific question, objection, or risk the Critic raises against an Assumption or Success Criterion.
_Avoid_: Critique, pushback, comment

**Challenge State**:
Where a Challenge stands after the Critic reviews a Response: open (not yet convinced), closed (convinced), or escalated (the agents cannot settle it and a human must decide).
_Avoid_: Resolved, done, pending

**Response**:
The Proposer's answer to one Challenge: Defend (keep the position), Revise (change it), or Concede (drop it).
_Avoid_: Reply, rebuttal

**Challenge History**:
Every Response to one Challenge and every Challenge State the Critic gave it, Round by Round.
_Avoid_: Thread, log, timeline

**Settled Challenge**:
A Challenge whose state is closed or escalated.
_Avoid_: Resolved, done, finished

**Proposal Changes**:
What differs between the previous and current proposal (Assumptions, scope items, Success Criteria added, removed, or changed), worked out by code.
_Avoid_: Diff, delta, edits

**Verdict**:
The Critic's signal at the end of each Round: Satisfied or Continue.
_Avoid_: Decision, approval

**Stall**:
Two Rounds in a row in which nothing moved: no Challenge closed or escalated, and no Response revised or conceded.
_Avoid_: Deadlock, loop, stuck

**Stop Reason**:
Why a deliberation ended: satisfied (the Critic signaled completion), stalled, round cap, or critic exhausted (the Critic had nothing left to raise but would not say so).
_Avoid_: Exit code, end state

## Outcome

**Decision Document**:
The structured record of a finished deliberation: agreed scope, surfaced assumptions, open questions, success criteria, and how the deliberation went.
_Avoid_: Report, summary, decisions file

**Assumption Status**:
Where an Assumption ended up: Accepted (never challenged), Challenged-and-held, Revised, or Dropped.
_Avoid_: State, outcome

**Open Question**:
Something the agents could not settle that needs a human answer, marked blocking or non-blocking.
_Avoid_: Unknown, TBD, gap

**Disagreement**:
The number of Challenges still open at the end of a Round.
_Avoid_: Tension score, conflict level

**Confidence**:
An agent's own rating, from 0 to 100, of how ready the final agreed scope is.
_Avoid_: Certainty, score
