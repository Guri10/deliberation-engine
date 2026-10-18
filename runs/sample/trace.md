# Deliberation trace

**Feature request:** The CRM should alert us when our relationship with a country goes cold.

## Round 1

### Proposer
**In scope:**
- Compute a per-country engagement recency signal from logged interactions (meetings, calls, emails, mission visits) recorded in the CRM
- Flag a country as cold when its engagement recency exceeds a configurable threshold, with the threshold set per country tier by the regional coordinator
- Send an in-app alert and a daily digest email to the assigned regional coordinator and country project lead when a country becomes cold
- Show the cold-country list on a dashboard view with the last logged engagement date and the responsible owner
- Record each alert and its acknowledgement in the country's engagement history
**Out of scope:**
- Predicting future disengagement with machine learning or sentiment analysis of email content
- Alerting on individual contacts going cold (contact-level alerts are a separate request)
- Ingesting interactions from external systems such as calendars, mail servers, or ministry portals
- Automatic outreach or drafting of messages to government counterparts
- Changing access controls or the confidentiality handling of contact records
**Assumptions:**
- A1: 'Relationship' means organizational engagement with a country as a whole, measured by logged interactions with any counterpart in that country, not the strength of any single contact.
- A2: 'Goes cold' means no logged engagement of any type for longer than a threshold; the default threshold is 90 days, adjustable per country tier.
- A3: Engagement is only counted if it is logged in the CRM; unlogged calls or informal contact do not count, so the alert may fire for countries that are in fact still active.
- A4: Each country has an assigned regional coordinator and a project lead recorded in the CRM, so alerts have a named recipient.
- A5: Countries are already tiered (for example by strategic priority) in the CRM, so per-tier thresholds can be applied without new tiering data.
- A6: Interactions carry a country link and a date that the signal can query directly, without manual tagging per interaction.
- A7: Confidential or diplomatically sensitive interactions are visible in the recency calculation only to users who already have access to them; the alert shows only the date and country, not the content.
**Success criteria:**
- share of countries flagged cold that coordinators confirm as genuinely disengaged: at least 80% confirmed in a quarterly review
- time from a country crossing its cold threshold to the coordinator receiving an alert: within 24 hours
- share of cold-country alerts acknowledged within 7 days: at least 90%
**Responses:**
- (none)
**Response counts:** Defend 0, Revise 0, Concede 0

### Critic: CONTINUE
**Challenge states:**
- (none)
**New challenges:**
- C1 [risk] on A7: A7 limits recency visibility to users who already hold access to confidential interactions, but the alert and the cold-country dashboard show the last logged engagement date for the country. If the only recent interaction is a restricted one, the date itself reveals that a confidential engagement happened, and coordinators or project leads who cannot see that record would still learn of it. The proposal does not say whether the date is masked, whether the dashboard and digest respect the same restriction, or who decides this.
- C2 [question] on A2 and A5: A2 sets the cold threshold per country tier, and A5 assumes tiers already exist in the CRM. The proposal does not say how a country's engagement recency is computed when it has several counterparts and mission visits, or how 'cold' is determined when a country has no tier assigned. Without these definitions the core signal cannot be built, and if tiers do not exist, creating them would add scope.
- C3 [question] on A3 and scope_in alert history: Scope_in records each alert and its acknowledgement in the country's engagement history. If alerts or acknowledgements are logged as interactions, they would reset the recency signal and the country would never go cold. The proposal must state that system-generated records are excluded from the engagement signal, and what counts as an acknowledgement.
- C4 [question] on Success criteria 1 and 3: Success criteria 1 and 3 cannot be measured as written. 'Confirmed as genuinely disengaged' has no defined review process, owner, or sample, and 'acknowledged within 7 days' does not say what counts as acknowledgement (opening the alert, clicking a button, or a logged action). Without these definitions the criteria cannot be checked after launch.
- C5 [risk] on A3: A3 accepts that unlogged engagement is ignored, so the alert will fire for countries that are still active but poorly logged. Once alerts go to coordinators, staff may back-date or create low-value log entries to clear them, which would corrupt the engagement history the signal depends on. The proposal does not address this incentive or who is accountable for log completeness.
**Disagreement:** 5 open (first round)

## Round 2

### Proposer
**In scope:**
- Compute a per-country engagement recency signal from logged interactions (meetings, calls, emails, mission visits) recorded in the CRM, using the most recent qualifying interaction date across all counterparts in that country
- Flag a country as cold when its engagement recency exceeds a threshold set per country tier by the regional coordinator, with a default of 90 days for countries that have no tier assigned
- Send an in-app alert and a daily digest email to the assigned regional coordinator and country project lead when a country becomes cold; alerts and digests show only country name, cold threshold status, and last engagement date, with the date masked where the last engagement was restricted
- Show the cold-country list on a dashboard view with the last logged engagement date and the responsible owner, filtered by the same visibility rules as the digest
- Record each alert and its acknowledgement in the country's alert log, kept separate from the engagement history so it does not feed the recency signal
- Provide a review queue where coordinators can mark a cold flag as confirmed active or confirmed disengaged, with the reviewer and date recorded
**Out of scope:**
- Predicting future disengagement with machine learning or sentiment analysis of email content
- Alerting on individual contacts going cold (contact-level alerts are a separate request)
- Ingesting interactions from external systems such as calendars, mail servers, or ministry portals
- Automatic outreach or drafting of messages to government counterparts
- Changing access controls or the confidentiality handling of contact records
- Creating new country tiers; if no tiering exists, this feature uses the 90-day default only and tiering is a separate request
- Enforcing log completeness through automated penalties or audits of individual staff
**Assumptions:**
- A1: 'Relationship' means organizational engagement with a country as a whole, measured by logged interactions with any counterpart in that country, not the strength of any single contact.
- A2: 'Goes cold' means no qualifying logged engagement for longer than a threshold; the default threshold is 90 days, adjustable per country tier. A qualifying engagement is a meeting, call, email, or mission visit logged against the country by a user; system-generated records (alerts, acknowledgements, digests, review decisions) are excluded from the signal.
- A3: Engagement is only counted if it is logged in the CRM; unlogged calls or informal contact do not count, so the alert may fire for countries that are in fact still active. The review queue (scope_in) is the mechanism for coordinators to clear false positives without creating log entries.
- A4: Each country has an assigned regional coordinator and a project lead recorded in the CRM, so alerts have a named recipient.
- A5: Countries are tiered in the CRM for example by strategic priority; where a country has no tier, the 90-day default applies. If the CRM has no tier field, per-tier thresholds are deferred and only the default applies.
- A6: Interactions carry a country link and a date that the signal can query directly, without manual tagging per interaction.
- A7: Restricted interactions count toward recency only for users who may see them. For users who cannot, the country's last engagement date is shown as the most recent unrestricted date, so the existence of a restricted engagement is not revealed. The Data Protection Officer decides the exact masking rule and whether restricted interactions should count toward recency at all.
- A8: Acknowledgement means a coordinator or project lead opening the alert and selecting an explicit action (confirm active or confirm disengaged) in the review queue; opening alone does not count.
**Success criteria:**
- share of cold-country flags marked 'confirmed disengaged' by the coordinator in the review queue, sampled quarterly by the Head of Country Engagement across at least 20 flags: at least 80% confirmed disengaged
- time from a country crossing its cold threshold to the coordinator receiving an alert: within 24 hours
- share of cold-country alerts with an explicit review action (A8) within 7 days: at least 90%
**Responses:**
- C1 Revise (quoting "the date itself reveals that a confidential engagement happened, and coordinators or project leads who cannot see that record would still learn of it"): The dashboard and digest will use the same visibility rule as the recency calculation. For users who cannot see a restricted interaction, the last engagement date shown is the latest unrestricted date, so the restricted engagement is not revealed. The Data Protection Officer owns the masking rule and decides whether restricted interactions count toward recency at all, as recorded in A7.
- C2 Revise (quoting "how 'cold' is determined when a country has no tier assigned"): Recency is the latest qualifying interaction across all counterparts and mission visits for the country. Countries with no tier use the 90-day default. Creating tiers is out of scope; if the CRM has no tier field, only the default applies, as stated in A5.
- C3 Revise (quoting "The proposal must state that system-generated records are excluded from the engagement signal, and what counts as an acknowledgement."): System-generated records (alerts, acknowledgements, digests, review decisions) are excluded from the recency signal, as stated in A2. Alerts go to a separate alert log, not the engagement history. Acknowledgement is defined in A8 as an explicit review action.
- C4 Revise (quoting "'Confirmed as genuinely disengaged' has no defined review process, owner, or sample"): Success criterion 1 now uses the coordinator's review-queue decision, sampled quarterly by the Head of Country Engagement across at least 20 flags. Criterion 3 uses the explicit review action defined in A8, not opening the alert.
- C5 Defend: Back-dating and low-value logging is a real risk, but the proposal addresses it in part: system-generated records are excluded and the review queue lets coordinators clear false positives without creating log entries (A3, scope_in). Log completeness accountability sits with the Head of Country Engagement under existing CRM logging policy, which this feature does not change. Adding staff-level audits would go beyond the request, so it is listed in scope_out. The review queue's recorded reviewer and date make back-dating visible in audit.
**Response counts:** Defend 1, Revise 4, Concede 0

### Critic: CONTINUE
**Challenge states:**
- C1: escalated
- C2: closed
- C3: closed
- C4: closed
- C5: closed
**New challenges:**
- C6 [risk] on A7 and scope_in cold flag: A7 says restricted interactions count toward recency only for users who may see them. If the cold flag itself is computed per viewer, a country can show as cold to a coordinator who cannot see a restricted interaction and as active to one who can. The alert or dashboard then reveals the restricted engagement through the flag's presence or absence, even if the date is masked. The proposal must say whether the flag is computed once on unrestricted data or per viewer, and how the digest, alert, and dashboard stay consistent.
**Disagreement:** 1 open (-4)

## Round 3

### Proposer
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
**Assumptions:**
- A1: 'Relationship' means organizational engagement with a country as a whole, measured by logged interactions with any counterpart in that country, not the strength of any single contact.
- A2: 'Goes cold' means no qualifying logged engagement for longer than a threshold; the default threshold is 90 days, adjustable per country tier. A qualifying engagement is a meeting, call, email, or mission visit logged against the country by a user; system-generated records (alerts, acknowledgements, digests, review decisions) are excluded from the signal.
- A3: Engagement is only counted if it is logged in the CRM; unlogged calls or informal contact do not count, so the alert may fire for countries that are in fact still active. The review queue (scope_in) is the mechanism for coordinators to clear false positives without creating log entries.
- A4: Each country has an assigned regional coordinator and a project lead recorded in the CRM, so alerts have a named recipient.
- A5: Countries are tiered in the CRM for example by strategic priority; where a country has no tier, the 90-day default applies. If the CRM has no tier field, per-tier thresholds are deferred and only the default applies.
- A6: Interactions carry a country link and a date that the signal can query directly, without manual tagging per interaction.
- A7: Restricted interactions are excluded from the single country-level cold flag and from the date shown in alerts, digests, and dashboard, so the flag is the same for every viewer and reveals nothing about restricted engagement. As a consequence a country whose only recent engagement is restricted may show as cold to everyone, a false positive that coordinators clear in the review queue. The Data Protection Officer decides whether restricted interactions should count toward recency at all, and whether any viewer-specific handling is needed.
- A8: Acknowledgement means a coordinator or project lead opening the alert and selecting an explicit action (confirm active or confirm disengaged) in the review queue; opening alone does not count.
**Success criteria:**
- share of cold-country flags marked 'confirmed disengaged' by the coordinator in the review queue, sampled quarterly by the Head of Country Engagement across at least 20 flags: at least 80% confirmed disengaged
- time from a country crossing its cold threshold to the coordinator receiving an alert: within 24 hours
- share of cold-country alerts with an explicit review action (A8) within 7 days: at least 90%
**Responses:**
- C6 Revise (quoting "The proposal must say whether the flag is computed once on unrestricted data or per viewer, and how the digest, alert, and dashboard stay consistent."): The cold flag is computed once per country from unrestricted qualifying interactions only, not per viewer. The digest, alert, dashboard, and review queue all read that single flag and its unrestricted last-engagement date, so every viewer sees the same status and nothing about a restricted interaction can appear through the flag's presence or absence. The trade-off is a possible false positive where restricted engagement is the only recent activity; the review queue handles this. Whether restricted interactions should count toward recency at all is left to the Data Protection Officer, as recorded in A7.
**Response counts:** Defend 0, Revise 1, Concede 0

### Critic: SATISFIED
**Challenge states:**
- C6: closed
**New challenges:**
- (none)
**Disagreement:** 0 open (-1)

**Stop reason:** satisfied
