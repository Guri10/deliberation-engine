# Plain Python loop instead of LangGraph

The orchestration is a plain `while` loop using the `anthropic` SDK and Pydantic. We considered LangGraph, which fits state-machine workflows well. The graph here has only three nodes and one decision point, and its strengths (branching, parallel nodes, pausing for a human, saving and resuming state) would go unused. Staying plain keeps the codebase small, keeps the stop rule as ordinary code a reviewer can read, and avoids the extra dependencies.
