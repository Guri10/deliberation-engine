# Decision Document
_Stop reason: satisfied_

## Agreed Scope
**In scope:**
- Read-only executive dashboard showing, per member country in the executive's portfolio, the logged engagement activity (meetings, emails, active missions, project affiliations) recorded by any staff member in that country's relationship records, limited to records the executive's role already permits them to read
- Every dashboard view carries a fixed label reading 'Logged CRM activity only; work outside the CRM is not shown'
- Filtering the dashboard by country, by region, and by date range
- Drill-down from a country summary to the underlying logged engagement records, respecting each record's existing access controls and showing nothing for records the role does not permit
- Executive-role access granted by the CRM's role model, with the executive's country portfolio taken from the role model's assignments
**Out of scope:**
- Editing or creating engagement records from the dashboard
- Individual staff performance metrics or time tracking
- Access to contact records flagged as diplomatically or confidentially sensitive beyond what the executive's role already permits, including any count, date or owner of such records
- Grouping activity by staff team or reporting line (the view is by country, not by team membership)
- Real-time alerts or notifications
- Activity captured outside the CRM (personal email, phone logs, chat tools)
- Predictive analytics or recommendations

## Surfaced Assumptions
- A1: 'Everything their teams are doing' means all logged engagement activity (meetings, emails, mission participation, project affiliation changes) recorded in the CRM for each country in the executive's portfolio, by any staff member, not work conducted outside the CRM. (Revised; raised in round 1)
- A2: 'Executives' means users holding an executive-level role in the CRM. An executive's view is defined by the countries in their assigned portfolio, not by a list of staff; the dashboard does not need to know team membership. (Revised; raised in round 1)
- A3: The CRM has an existing role model with executive-level roles and country or region portfolio assignments that can scope what each executive sees. The Head of Country Engagement must confirm these assignments exist before build starts; if they do not, the feature is blocked and returns to the requester. (Challenged-and-held; raised in round 1)
- A4: Sensitive or confidential contact records keep their existing restrictions. The dashboard computes every count, date and owner only over records the executive's role can already read; for records the role cannot read, nothing about them (including their existence) is shown. (Revised; raised in round 1)
- A5: 'Everything' is interpreted as the most recent 12 months by default, with the option to view a longer history, because full all-time history across roughly 100 countries would not be usable on one screen. (Accepted; raised in round 1)
- A6: Activity is shown as logged metadata (type, date, owner, country, project) rather than full email bodies or meeting notes, to limit exposure of sensitive content and keep the view summary-level. (Accepted; raised in round 1)
- A7: Contact records carry a sensitivity or confidentiality flag that the CRM already enforces in its access controls, and the Data Protection Officer owns the list of flags that trigger restriction. The proposal does not define that list. (Accepted; raised in round 2)
- A8: A country with no assigned executive is not shown on any executive dashboard; it is visible only to users with a cross-portfolio role, and no executive has a portfolio without at least one assigned country. (Accepted; raised in round 2)

## Open Questions
- **Non-blocking:** Does the Head of Country Engagement accept the fixed label wording 'Logged CRM activity only; work outside the CRM is not shown', and the build team settles its exact placement? (answer: Head of Country Engagement; source: deliberation)
- **Non-blocking:** Confirm A2: 'Executives' means users holding an executive-level role in the CRM. An executive's view is defined by the countries in their assigned portfolio, not by a list of staff; the dashboard does not need to know team membership. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A3: The CRM has an existing role model with executive-level roles and country or region portfolio assignments that can scope what each executive sees. The Head of Country Engagement must confirm these assignments exist before build starts; if they do not, the feature is blocked and returns to the requester. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A4: Sensitive or confidential contact records keep their existing restrictions. The dashboard computes every count, date and owner only over records the executive's role can already read; for records the role cannot read, nothing about them (including their existence) is shown. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A7: Contact records carry a sensitivity or confidentiality flag that the CRM already enforces in its access controls, and the Data Protection Officer owns the list of flags that trigger restriction. The proposal does not define that list. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A8: A country with no assigned executive is not shown on any executive dashboard; it is visible only to users with a cross-portfolio role, and no executive has a portfolio without at least one assigned country. (answer: CRM system owner; source: invented fact)

## Invented Facts
- A2: 'Executives' means users holding an executive-level role in the CRM. An executive's view is defined by the countries in their assigned portfolio, not by a list of staff; the dashboard does not need to know team membership.
- A3: The CRM has an existing role model with executive-level roles and country or region portfolio assignments that can scope what each executive sees. The Head of Country Engagement must confirm these assignments exist before build starts; if they do not, the feature is blocked and returns to the requester.
- A4: Sensitive or confidential contact records keep their existing restrictions. The dashboard computes every count, date and owner only over records the executive's role can already read; for records the role cannot read, nothing about them (including their existence) is shown.
- A7: Contact records carry a sensitivity or confidentiality flag that the CRM already enforces in its access controls, and the Data Protection Officer owns the list of flags that trigger restriction. The proposal does not define that list.
- A8: A country with no assigned executive is not shown on any executive dashboard; it is visible only to users with a cross-portfolio role, and no executive has a portfolio without at least one assigned country.

## Success Criteria
- Coverage of an executive's countries: share of records in an independently computed expected set (raw CRM engagement tables, filtered by the executive's permitted records and 12-month window, computed by a separate query not used by the dashboard) that appear on the dashboard, checked on a sample of executives and countries by the QA team at release and quarterly: 100% of sampled expected records appear; zero records outside the executive's portfolio appear
- Time for an executive to find the latest activity for one country: under 1 minute from dashboard open
- Access audit: sensitive records, or counts, dates or owners of sensitive records, visible to users without the required permission, checked by the QA team against the Data Protection Officer's list of flags at release and quarterly: zero

## Deliberation Summary
- Rounds run: 3
- Stop reason: satisfied
- Disagreement per round: R1 4, R2 1 (-3), R3 0 (-1)
- Proposer confidence: 55 (Scope is well bounded, but several load-bearing facts are unconfirmed: the CRM role model's executive and portfolio assignments (A3), the sensitivity flag list owned by the DPO (A7), and the rule for suppressing counts on restricted records, so the build cannot start until those are confirmed.)
- Critic confidence: 66 (All four challenges are closed and the scope is tight, but the build still depends on two unconfirmed facts: that the CRM role model holds executive portfolio assignments (A3, a go/no-go gate) and the Data Protection Officer's list of restriction flags (A7), which the access-audit criterion relies on.)
