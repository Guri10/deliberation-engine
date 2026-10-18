# The Critic closes Challenges explicitly; termination reads those states

Each Critic turn must mark every open Challenge as open, closed, or escalated. Termination is decided from those states, not only from the Critic's verdict. A Satisfied verdict counts only when nothing is left open, and escalated Challenges become Open Questions. This gives the Critic a third choice besides "satisfied too early" and "loop until the cap": hand the issue to a human. That choice is where the real Open Questions come from.

## Considered Options

- **Verdict alone:** the Critic says Satisfied and the run stops. Rejected: the Critic could end the run with issues still unresolved, and nothing would show them.
- **Code overrides contradictory verdicts silently:** rejected, because the code would be deciding completion instead of the Critic. The assessment requires the Critic to signal completion. A contradiction is sent back to the Critic once, quoting the exact problem. Code falls back only if the retry also contradicts itself.
