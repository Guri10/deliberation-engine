# Deliberation trace

**Feature request:** Executives should be able to see everything their teams are doing with each country.

## Round 1

### Proposer
**In scope:**
- Read-only executive dashboard showing, per member country, the engagement activity logged by staff in that country's relationship records (meetings, emails, active missions, project affiliations)
- Filtering the dashboard by country, by team or region, and by date range
- Drill-down from a country summary to the underlying logged engagement records, respecting each record's existing access controls
- Executive-role access that is granted by the CRM's role model, applied to the dashboard
**Out of scope:**
- Editing or creating engagement records from the dashboard
- Individual staff performance metrics or time tracking
- Access to contact records flagged as diplomatically or confidentially sensitive beyond what the executive's role already permits
- Real-time alerts or notifications
- Activity captured outside the CRM (personal email, phone logs, chat tools)
- Predictive analytics or recommendations
**Assumptions:**
- A1: 'Everything their teams are doing' means all logged engagement activity (meetings, emails, mission participation, project affiliation changes) recorded in the CRM for each country, not work conducted outside the CRM.
- A2: 'Executives' means users holding an executive-level role in the CRM, and 'their teams' means staff whose reporting line or region the executive is assigned to; an executive sees activity only for countries within their assigned portfolio.
- A3: The CRM has an existing role model with executive-level roles and region or portfolio assignments that can scope what each executive sees.
- A4: Sensitive or confidential contact records keep their existing restrictions; the dashboard shows only that a sensitive record exists and its activity count where the executive's role permits, not the content.
- A5: 'Everything' is interpreted as the most recent 12 months by default, with the option to view a longer history, because full all-time history across roughly 100 countries would not be usable on one screen.
- A6: Activity is shown as logged metadata (type, date, owner, country, project) rather than full email bodies or meeting notes, to limit exposure of sensitive content and keep the view summary-level.
**Success criteria:**
- Share of an executive's countries for which the dashboard shows all logged engagement activity in the last 12 months, checked against a sample of records: 100% of sampled records appear; zero records outside the executive's portfolio appear
- Time for an executive to find the latest activity for one country: under 1 minute from dashboard open
- Access audit: sensitive records visible to users without the required permission: zero
**Responses:**
- (none)
**Response counts:** Defend 0, Revise 0, Concede 0

### Critic: CONTINUE
**Challenge states:**
- (none)
**New challenges:**
- C1 [risk] on A4 and the drill-down scope item: the proposal says sensitive records keep their restrictions, yet it shows an activity count and the existence of a sensitive record where the role permits. For a diplomatically sensitive contact, even a count or a record's existence in a country can be a disclosure. The proposal does not say which record flags are sensitive, whether counts are suppressed for them, or whether the drill-down can reveal a restricted record's type, date or owner.: Who decides whether the dashboard may show even a count, date or owner for a sensitive or confidential contact record, and which flags trigger suppression? Without that rule, the dashboard could expose a restricted relationship to an executive whose role does not cover it, and the access-audit criterion (zero) cannot be checked.
- C2 [question] on A2 and A3: 'their teams' and 'assigned portfolio' are assumed to be stored in the CRM's role model, but the proposal does not show that they are. Staff reporting lines and region assignments may be held in HR systems or may be missing for some executives or staff.: What is the authoritative source for which staff count as an executive's 'teams' and which countries form an executive's portfolio? What happens when an executive has no portfolio assignment, when a staff member changes team mid-period, or when a country has no assigned executive? Without an answer, the scope of 'everything their teams are doing' cannot be defined.
- C3 [question] on Success criterion 1 (share of sampled records appearing, zero records outside portfolio) and criterion 3 (zero sensitive records visible without permission): the proposal does not say how the sample is drawn, how the expected record set is known independently of the dashboard, or who performs the check.: How will the team compute the 'expected' set of engagement records for an executive's countries so that 100% coverage can be measured? Who draws the sample, and how often is the check repeated? A success criterion that depends on the same query the dashboard uses cannot show that the dashboard is complete.
- C4 [risk] on A1 and scope_out item 'Activity captured outside the CRM': the dashboard is described as showing 'everything their teams are doing', but only logged CRM activity is included, and the proposal does not say how the dashboard will tell executives that the view is partial.: If executives read the dashboard as a complete picture of their teams' work, they may make decisions on incomplete data, for example believing a country has no activity when the work happened in personal email or phone calls. Is the dashboard to be labelled as 'logged CRM activity only', and who decides how that limitation is presented to executives?
**Disagreement:** 4 open (first round)

## Round 2

### Proposer
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
**Assumptions:**
- A1: 'Everything their teams are doing' means all logged engagement activity (meetings, emails, mission participation, project affiliation changes) recorded in the CRM for each country in the executive's portfolio, by any staff member, not work conducted outside the CRM.
- A2: 'Executives' means users holding an executive-level role in the CRM. An executive's view is defined by the countries in their assigned portfolio, not by a list of staff; the dashboard does not need to know team membership.
- A3: The CRM has an existing role model with executive-level roles and country or region portfolio assignments that can scope what each executive sees.
- A4: Sensitive or confidential contact records keep their existing restrictions. The dashboard computes every count, date and owner only over records the executive's role can already read; for records the role cannot read, nothing about them (including their existence) is shown.
- A5: 'Everything' is interpreted as the most recent 12 months by default, with the option to view a longer history, because full all-time history across roughly 100 countries would not be usable on one screen.
- A6: Activity is shown as logged metadata (type, date, owner, country, project) rather than full email bodies or meeting notes, to limit exposure of sensitive content and keep the view summary-level.
- A7: Contact records carry a sensitivity or confidentiality flag that the CRM already enforces in its access controls, and the Data Protection Officer owns the list of flags that trigger restriction. The proposal does not define that list.
- A8: A country with no assigned executive is not shown on any executive dashboard; it is visible only to users with a cross-portfolio role, and no executive has a portfolio without at least one assigned country.
**Success criteria:**
- Coverage of an executive's countries: share of records in an independently computed expected set (raw CRM engagement tables, filtered by the executive's permitted records and 12-month window, computed by a separate query not used by the dashboard) that appear on the dashboard, checked on a sample of executives and countries by the QA team at release and quarterly: 100% of sampled expected records appear; zero records outside the executive's portfolio appear
- Time for an executive to find the latest activity for one country: under 1 minute from dashboard open
- Access audit: sensitive records, or counts, dates or owners of sensitive records, visible to users without the required permission, checked by the QA team against the Data Protection Officer's list of flags at release and quarterly: zero
**Responses:**
- C1 Revise (quoting "Without that rule, the dashboard could expose a restricted relationship to an executive whose role does not cover it"): Revised A4 and the drill-down scope item. Counts, dates and owners, and the existence of sensitive records, are now computed only over records the executive's role can already read. For records the role cannot read, the dashboard shows nothing, not even a suppressed count. Added A7: the Data Protection Officer owns the list of sensitivity flags and confirms which flags trigger restriction. The proposal no longer relies on a separate summary rule for sensitive records; it relies on the existing access controls.
- C2 Revise (quoting "Staff reporting lines and region assignments may be held in HR systems or may be missing for some executives or staff."): Dropped team membership as a scope rule. The executive's view is now defined by country portfolio from the CRM role model (A2, A3). Activity by any staff member in those countries is shown, so the dashboard no longer depends on HR reporting lines. Added A8 to cover countries with no executive and executives with no portfolio: those countries are visible only to cross-portfolio roles, and an executive with no portfolio sees an empty view with a message. The Head of Country Engagement must confirm that portfolio assignments exist in the CRM role model; that is the one remaining dependency.
- C3 Revise (quoting "A success criterion that depends on the same query the dashboard uses cannot show that the dashboard is complete."): Revised success criterion 1. The expected set is now computed by a separate query on the raw engagement tables, not by the dashboard's query. QA draws a sample of executives and countries and reconciles it at release and quarterly. The reconciliation method is defined in the criterion, so the coverage figure can show completeness.
- C4 Revise (quoting "Is the dashboard to be labelled as 'logged CRM activity only'"): Added a fixed label to every dashboard view, stating that it shows logged CRM activity only and not work done outside the CRM. The label is in scope and not optional. The exact wording and placement can be settled by the build team; the Head of Country Engagement only needs to confirm the label is acceptable.
**Response counts:** Defend 0, Revise 4, Concede 0

### Critic: CONTINUE
**Challenge states:**
- C1: closed
- C2: open (The response names the CRM role model as the source for executive portfolios and drops team membership, which answers the scope question. It still depends on the CRM role model actually holding country portfolio assignments, and the proposal only asks the Head of Country Engagement to confirm this. If the assignments are missing, the dashboard cannot be scoped and the feature is blocked. Confirmation that the assignments exist in the role model is still missing.)
- C3: closed
- C4: closed
**New challenges:**
- (none)
**Disagreement:** 1 open (-3)

## Round 3

### Proposer
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
**Assumptions:**
- A1: 'Everything their teams are doing' means all logged engagement activity (meetings, emails, mission participation, project affiliation changes) recorded in the CRM for each country in the executive's portfolio, by any staff member, not work conducted outside the CRM.
- A2: 'Executives' means users holding an executive-level role in the CRM. An executive's view is defined by the countries in their assigned portfolio, not by a list of staff; the dashboard does not need to know team membership.
- A3: The CRM has an existing role model with executive-level roles and country or region portfolio assignments that can scope what each executive sees. The Head of Country Engagement must confirm these assignments exist before build starts; if they do not, the feature is blocked and returns to the requester.
- A4: Sensitive or confidential contact records keep their existing restrictions. The dashboard computes every count, date and owner only over records the executive's role can already read; for records the role cannot read, nothing about them (including their existence) is shown.
- A5: 'Everything' is interpreted as the most recent 12 months by default, with the option to view a longer history, because full all-time history across roughly 100 countries would not be usable on one screen.
- A6: Activity is shown as logged metadata (type, date, owner, country, project) rather than full email bodies or meeting notes, to limit exposure of sensitive content and keep the view summary-level.
- A7: Contact records carry a sensitivity or confidentiality flag that the CRM already enforces in its access controls, and the Data Protection Officer owns the list of flags that trigger restriction. The proposal does not define that list.
- A8: A country with no assigned executive is not shown on any executive dashboard; it is visible only to users with a cross-portfolio role, and no executive has a portfolio without at least one assigned country.
**Success criteria:**
- Coverage of an executive's countries: share of records in an independently computed expected set (raw CRM engagement tables, filtered by the executive's permitted records and 12-month window, computed by a separate query not used by the dashboard) that appear on the dashboard, checked on a sample of executives and countries by the QA team at release and quarterly: 100% of sampled expected records appear; zero records outside the executive's portfolio appear
- Time for an executive to find the latest activity for one country: under 1 minute from dashboard open
- Access audit: sensitive records, or counts, dates or owners of sensitive records, visible to users without the required permission, checked by the QA team against the Data Protection Officer's list of flags at release and quarterly: zero
**Responses:**
- C2 Defend: Defending the proposal as written. The proposal already names the CRM role model as the source for portfolios (A2, A3), marks A3 as invented so it must be confirmed, and states the Head of Country Engagement's confirmation as the single dependency. The Critic's reason asks for that confirmation to exist, but that is a fact about the CRM that only its owner can supply; it is a go/no-go gate on the build, not a defect in scope. Making the gate explicit in A3 (feature blocked and returned to the requester if assignments are missing) states what happens in that case. No change to scope, since the remaining question cannot be answered inside the proposal.
**Response counts:** Defend 1, Revise 0, Concede 0

### Critic: SATISFIED
**Challenge states:**
- C2: closed
**New challenges:**
- (none)
**Disagreement:** 0 open (-1)

**Stop reason:** satisfied
