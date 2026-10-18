# Decision Document
_Stop reason: satisfied_

## Agreed Scope
**In scope:**
- Compute a per-country engagement recency signal from logged interactions (meetings, calls, emails, mission visits) recorded in the CRM, using the most recent qualifying interaction date across all counterparts in that country
- Compute the cold flag once per country from unrestricted qualifying interactions only, so the flag value is identical for every viewer; restricted interactions do not affect the flag in the default design pending the Data Protection Officer's decision
- Flag a country as cold when its engagement recency exceeds a threshold set per country tier by the regional coordinator, with a default of 90 days for countries that have no tier assigned
- Send an in-app alert and a daily digest email to the assigned regional coordinator and country project lead when a country becomes cold; alerts and digests show only country name, cold flag status, and last engagement date, with the date taken from the unrestricted signal so the digest, alert, and dashboard show the same flag and date to every recipient
- Show the cold-country list on a dashboard view with the last logged engagement date and the responsible owner, drawn from the same once-computed flag and filtered by the same visibility rules as the digest
- Record each alert and its acknowledgement in the country's alert log, kept separate from the engagement history so it does not feed the recency signal
- Provide a review queue where coordinators can mark a cold flag as confirmed active or confirmed disengaged, with the reviewer and date recorded; the review decision is stored once per country flag and shown identically to all viewers of that flag
**Out of scope:**
- Predicting future disengagement with machine learning or sentiment analysis of email content
- Alerting on individual contacts going cold (contact-level alerts are a separate request)
- Ingesting interactions from external systems such as calendars, mail servers, or ministry portals
- Automatic outreach or drafting of messages to government counterparts
- Changing access controls or the confidentiality handling of contact records
- Creating new country tiers; if no tiering exists, this feature uses the 90-day default only and tiering is a separate request
- Enforcing log completeness through automated penalties or audits of individual staff
- Per-viewer cold flags or per-viewer recency calculations

## Surfaced Assumptions
- A1: 'Relationship' means organizational engagement with a country as a whole, measured by logged interactions with any counterpart in that country, not the strength of any single contact. (Accepted; raised in round 1)
- A2: 'Goes cold' means no qualifying logged engagement for longer than a threshold; the default threshold is 90 days, adjustable per country tier. System-generated records (alerts, acknowledgements, digests, review decisions) are excluded from the signal. (Revised; raised in round 1)
- A3: Engagement is only counted if it is logged in the CRM; unlogged calls or informal contact do not count, so the alert may fire for countries that are in fact still active. The review queue is the mechanism for coordinators to clear false positives without creating log entries. (Revised; raised in round 1)
- A4: Each country has an assigned regional coordinator and a project lead recorded in the CRM, so alerts have a named recipient. (Accepted; raised in round 1)
- A5: Countries are tiered in the CRM for example by strategic priority; where a country has no tier, the 90-day default applies. If the CRM has no tier field, per-tier thresholds are deferred and only the default applies. (Revised; raised in round 1)
- A6: Interactions carry a country link and a date that the signal can query directly, without manual tagging per interaction. (Accepted; raised in round 1)
- A7: Restricted interactions are excluded from the single country-level cold flag and from the date shown in alerts, digests, and dashboard, so the flag is the same for every viewer. A country whose only recent engagement is restricted may show as cold to everyone, a false positive that coordinators clear in the review queue. The Data Protection Officer decides whether restricted interactions should count toward recency at all, and whether any viewer-specific handling is needed. (Revised; raised in round 1)
- A8: Acknowledgement means a coordinator or project lead opening the alert and selecting an explicit action (confirm active or confirm disengaged) in the review queue; opening alone does not count. (Revised; raised in round 2)

## Open Questions
- **Non-blocking:** Who in Country Engagement accepts accountability for log completeness under the existing CRM logging policy, given the Proposer assigned it to the Head of Country Engagement without that role confirming it (answer: Head of Country Engagement; source: deliberation)
- **Non-blocking:** Is the 90-day default cold threshold correct, and who validates it and sets per-tier thresholds once tiers exist; the default was never tested against real engagement patterns (answer: Head of Country Engagement; source: deliberation)
- **Blocking:** A7 limits recency visibility to users who already hold access to confidential interactions, but the alert and the cold-country dashboard show the last logged engagement date for the country. If the only recent interaction is a restricted one, the date itself reveals that a confidential engagement happened, and coordinators or project leads who cannot see that record would still learn of it. The proposal does not say whether the date is masked, whether the dashboard and digest respect the same restriction, or who decides this. (answer: Data protection officer; source: escalated, C1)
- **Non-blocking:** Confirm A4: Each country has an assigned regional coordinator and a project lead recorded in the CRM, so alerts have a named recipient. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A5: Countries are tiered in the CRM for example by strategic priority; where a country has no tier, the 90-day default applies. If the CRM has no tier field, per-tier thresholds are deferred and only the default applies. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A6: Interactions carry a country link and a date that the signal can query directly, without manual tagging per interaction. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A7: Restricted interactions are excluded from the single country-level cold flag and from the date shown in alerts, digests, and dashboard, so the flag is the same for every viewer and reveals nothing about restricted engagement. As a consequence a country whose only recent engagement is restricted may show as cold to everyone, a false positive that coordinators clear in the review queue. The Data Protection Officer decides whether restricted interactions should count toward recency at all, and whether any viewer-specific handling is needed. (answer: CRM system owner; source: invented fact)

## Invented Facts
- A4: Each country has an assigned regional coordinator and a project lead recorded in the CRM, so alerts have a named recipient.
- A5: Countries are tiered in the CRM for example by strategic priority; where a country has no tier, the 90-day default applies. If the CRM has no tier field, per-tier thresholds are deferred and only the default applies.
- A6: Interactions carry a country link and a date that the signal can query directly, without manual tagging per interaction.
- A7: Restricted interactions are excluded from the single country-level cold flag and from the date shown in alerts, digests, and dashboard, so the flag is the same for every viewer and reveals nothing about restricted engagement. As a consequence a country whose only recent engagement is restricted may show as cold to everyone, a false positive that coordinators clear in the review queue. The Data Protection Officer decides whether restricted interactions should count toward recency at all, and whether any viewer-specific handling is needed.

## Success Criteria
- share of cold-country flags marked 'confirmed disengaged' by the coordinator in the review queue, sampled quarterly by the Head of Country Engagement across at least 20 flags: at least 80% confirmed disengaged
- time from a country crossing its cold threshold to the coordinator receiving an alert: within 24 hours
- share of cold-country alerts with an explicit review action (A8) within 7 days: at least 90%

## Deliberation Summary
- Rounds run: 3
- Stop reason: satisfied
- Disagreement per round: R1 5, R2 1 (-4), R3 0 (-1)
- Proposer confidence: 55 (The core signal and flag are now defined, but C1's restriction handling for the displayed date is escalated and unresolved, the DPO has not decided whether restricted interactions count toward recency, and A4 and A6 remain unverified invented facts that the CRM owner must confirm.)
- Critic confidence: 62 (The scope is buildable with a defined default, but the restricted-interaction handling (C1, escalated to the Data Protection Officer) is unresolved, and key assumptions A4 to A6 (named coordinators, country tiers, direct country links on interactions) are invented and unverified.)
