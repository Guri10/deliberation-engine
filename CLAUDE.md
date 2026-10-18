# Deliberation Engine

Two-agent system (Proposer + Critic, plus a Summarizer) that turns a vague Government CRM feature request into a structured decision document. Spec: `docs/SPEC.md`. Diagram: `docs/DIAGRAM.md`.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues in Guri10/deliberation-engine (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default labels: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `GLOSSARY.md` + `docs/adr/`. See `docs/agents/domain.md`.
