# Deliberation trace

**Feature request:** Stop two teams from contacting the same ministry about the same thing.

## Round 1

### Proposer
**In scope:**
- Detect when two users (regional coordinators, project managers, or mission delegates) log or plan outreach to the same government counterpart record about the same project or mission within a defined window
- Show a warning to the user creating or logging the second contact, naming the other team and the existing contact record
- Let the user proceed after acknowledging the overlap, with the overlap recorded on both engagement records
- Notify the owning project lead of the overlap when a warning is acknowledged
**Out of scope:**
- Automatic blocking of contact (warning only, no hard lock)
- Cross-country or cross-ministry overlap detection (only same counterpart record or same ministry within one country)
- Coordination workflow, approval routing, or assignment of a single owner
- Retroactive audit of historical contacts before launch
- Changes to email or calendar integrations
- Reading or surfacing content of confidential or diplomatic-flagged contact notes to users outside the record's permitted group
**Assumptions:**
- A1: 'Same ministry' means the same counterpart contact record or the same ministry organization record within one country; different countries never trigger an overlap.
- A2: 'About the same thing' means the same project ID or mission ID. Free-text topic matching is out of scope because it is unreliable.
- A3: 'Teams' means distinct owning teams or regions as recorded on the user's profile; two users in the same team do not trigger the warning.
- A4: Each contact or engagement record already carries a project or mission reference field that can be used for matching.
- A5: The overlap window is the 30 days before and after a planned contact date, or the current open period for logged contacts; the exact window is configurable by the CRM owner.
- A6: Overlap is a soft warning because legitimate parallel outreach (e.g. different sub-topics under one project) happens and must not be blocked.
- A7: Warnings must respect contact confidentiality: the warning shows only the other team's name and the date, not the details of any diplomatic-flagged note.
**Success criteria:**
- share of same-project, same-counterpart contacts by different teams that trigger a warning before or at logging: at least 90% in a test set of historical duplicates
- false-positive rate among warnings (warnings acknowledged as not a real overlap): under 20% after one month of use
- time added to logging a contact when no overlap exists: under 2 seconds added on average
**Responses:**
- (none)
**Response counts:** Defend 0, Revise 0, Concede 0

### Critic: CONTINUE
**Challenge states:**
- (none)
**New challenges:**
- C1 [risk] on A7 and scope_in item 2: Scope says the warning names the other team and the existing contact record, while A7 says it shows only the other team's name and the date. These conflict: if the existing contact record is a diplomatic-flagged or confidential record, naming it could expose its existence or counterpart to users outside its permitted group. The proposal never states who may see that a contact exists on a restricted record, or whether a confidential record can trigger a warning at all.
- C2 [question] on A4 and A2: A4 assumes every contact or engagement record already carries a project or mission reference field, but the proposal does not say whether that field is mandatory, consistently filled, or populated for historical records. If many records lack the reference, the 90% detection criterion cannot be met and the feature silently misses overlaps. Who owns filling that gap, and is it in scope?
- C3 [question] on A3 and scope_in item 1: A3 defines 'teams' as owning teams or regions on the user's profile, but a single regional coordinator may cover several teams and a project manager may sit in none. The proposal does not say how a user with multiple or no team assignments is classified, so it is unclear whether the warning fires for them at all.
- C4 [question] on Success criterion 1 (detection rate at least 90% on historical duplicates): The success criterion depends on a 'test set of historical duplicates', but scope_out excludes retroactive audit of historical contacts, and the proposal does not say who builds or labels that test set or what counts as a true duplicate. Without a defined labelling method the 90% threshold cannot be measured.
**Disagreement:** 4 open (first round)

## Round 2

### Proposer
**In scope:**
- Detect when two users (regional coordinators, project managers, or mission delegates) log or plan outreach to the same government counterpart record or same ministry record within one country about the same project ID or mission ID within a defined window
- For ordinary records, show a warning to the user creating or logging the second contact naming the other team and the date of the existing contact
- For confidential or diplomatic-flagged records, show no warning to users outside the record's permitted group; record the overlap and notify the owning project lead only
- Let the user proceed after acknowledging the overlap, with the overlap recorded on both engagement records
- Notify the owning project lead when a warning is acknowledged or a restricted-record overlap is detected
- Compare teams using the team on the engagement record rather than the user profile; a user with several team assignments is classified by the team on the record, and a user with none is treated as its own team
- Make the project or mission reference a required field on newly planned or logged contacts
**Out of scope:**
- Automatic blocking of contact (warning only, no hard lock)
- Cross-country or cross-ministry overlap detection (only same counterpart record or same ministry within one country)
- Coordination workflow, approval routing, or assignment of a single owner
- Retroactive audit of historical contacts before launch
- Backfilling missing project or mission references on historical records (separate work item owned by Head of Country Engagement)
- Changes to email or calendar integrations
- Reading or surfacing content of confidential or diplomatic-flagged contact notes to users outside the record's permitted group
**Assumptions:**
- A1: 'Same ministry' means the same counterpart contact record or the same ministry organization record within one country; different countries never trigger an overlap.
- A2: 'About the same thing' means the same project ID or mission ID. Free-text topic matching is out of scope because it is unreliable.
- A3: 'Teams' means the owning team recorded on the engagement record. A user with several team assignments is classified by the team on the record; a user with none is treated as a separate team, so their contacts can trigger a warning against any other team.
- A4: Each contact or engagement record already carries a project or mission reference field that can be used for matching, and it can be made mandatory for new entries.
- A5: The overlap window is the 30 days before and after a planned contact date, or the current open period for logged contacts; the exact window is configurable by the CRM owner.
- A6: Overlap is a soft warning because legitimate parallel outreach (e.g. different sub-topics under one project) happens and must not be blocked.
- A7: Warnings must respect contact confidentiality: for ordinary records the warning shows only the other team's name and the date. For diplomatic-flagged or confidential records no warning is shown to users outside the permitted group, and only the owning project lead is notified.
- A8: Historical records lacking a project or mission reference are excluded from the detection criterion and are not backfilled by this feature.
- A9: Confidential and diplomatic-flagged records carry a permitted-group field that the CRM can check against the user's role when a warning is generated.
**Success criteria:**
- share of labelled duplicate pairs (same project or mission ID, same counterpart or ministry record, different team, within window) that trigger a warning before or at logging, measured on a pilot-period sample labelled independently by two coordinators; records without a reference are excluded: at least 90%
- false-positive rate among warnings (warnings acknowledged as not a real overlap): under 20% after one month of use
- time added to logging a contact when no overlap exists: under 2 seconds added on average
- share of newly planned or logged contacts that carry a project or mission reference: at least 95% after one month of use
**Responses:**
- C1 Revise (quoting "naming it could expose its existence or counterpart to users outside its permitted group"): The Critic is right that scope_in item 2 and A7 conflicted. Naming an existing confidential or diplomatic-flagged record could reveal its existence to users outside its permitted group. Scope now shows the warning with the other team and date only for ordinary records. For restricted records, no warning is shown to users outside the permitted group, and the overlap is recorded and sent only to the owning project lead. A9 states the permitted-group check this relies on, and it needs confirming by the CRM owner.
- C2 Revise (quoting "If many records lack the reference, the 90% detection criterion cannot be met and the feature silently misses overlaps."): The Critic is right that the detection criterion cannot be met if references are missing. The project or mission reference is now required on new planned and logged contacts, and a new criterion measures that fill rate. Historical gaps are excluded from the detection criterion and backfilling is a separate work item owned by the Head of Country Engagement (A8). Whether the reference can be made mandatory is an invented fact to confirm (A4).
- C3 Revise (quoting "a project manager may sit in none"): The Critic is right that the rule did not classify users with several or no team assignments. Team is now taken from the engagement record, not the user profile. A user with several assignments is classified by the record's team, and a user with none is treated as a separate team, so the warning can fire for them (A3, scope_in item 6).
- C4 Revise (quoting "Without a defined labelling method the 90% threshold cannot be measured."): The Critic is right that the 90% threshold was not measurable. The criterion now uses a defined duplicate definition and a pilot-period sample labelled independently by two coordinators, with records lacking a reference excluded. This measures the feature on live pilot logging and is not a retroactive audit of historical contacts.
**Response counts:** Defend 0, Revise 4, Concede 0

### Critic: CONTINUE
**Challenge states:**
- C1: escalated
- C2: closed
- C3: closed
- C4: closed
**New challenges:**
- C5 [risk] on scope_in items 3 and 4 (overlap recorded on both engagement records; restricted-record overlap recorded for owning project lead): scope_in item 4 says the overlap is recorded on both engagement records, but item 3 says a restricted-record overlap is recorded and sent only to the owning project lead. If the second user's engagement record carries a visible overlap entry naming the restricted record or its team, users outside the permitted group can infer that the restricted record exists. The proposal does not say whether restricted overlaps are written to the second user's record at all, or who can read those entries.
**Disagreement:** 1 open (-3)

## Round 3

### Proposer
**In scope:**
- Detect when two users (regional coordinators, project managers, or mission delegates) log or plan outreach to the same government counterpart record or same ministry record within one country about the same project ID or mission ID within a defined window
- For ordinary records, show a warning to the user creating or logging the second contact naming the other team and the date of the existing contact
- For confidential or diplomatic-flagged records, show no warning to users outside the record's permitted group; record the overlap on the restricted record only and notify the owning project lead only
- Let the user proceed after acknowledging the overlap; for ordinary records, record the overlap on both engagement records; for restricted records, never write an overlap entry to the second user's engagement record, so that its existence is not inferable by users outside the permitted group
- Restrict read access to overlap entries on restricted records to the permitted group, and do not show them in any view available to users outside that group
- Notify the owning project lead when a warning is acknowledged or a restricted-record overlap is detected
- Compare teams using the team on the engagement record rather than the user profile; a user with several team assignments is classified by the team on the record, and a user with none is treated as its own team
- Make the project or mission reference a required field on newly planned or logged contacts
**Out of scope:**
- Automatic blocking of contact (warning only, no hard lock)
- Cross-country or cross-ministry overlap detection (only same counterpart record or same ministry within one country)
- Coordination workflow, approval routing, or assignment of a single owner
- Retroactive audit of historical contacts before launch
- Backfilling missing project or mission references on historical records (separate work item owned by Head of Country Engagement)
- Changes to email or calendar integrations
- Reading or surfacing content of confidential or diplomatic-flagged contact notes to users outside the record's permitted group
- Any visible trace of a restricted-record overlap on a record outside the permitted group
**Assumptions:**
- A1: 'Same ministry' means the same counterpart contact record or the same ministry organization record within one country; different countries never trigger an overlap.
- A2: 'About the same thing' means the same project ID or mission ID. Free-text topic matching is out of scope because it is unreliable.
- A3: 'Teams' means the owning team recorded on the engagement record. A user with several team assignments is classified by the team on the record; a user with none is treated as a separate team, so their contacts can trigger a warning against any other team.
- A4: Each contact or engagement record already carries a project or mission reference field that can be used for matching, and it can be made mandatory for new entries.
- A5: The overlap window is the 30 days before and after a planned contact date, or the current open period for logged contacts; the exact window is configurable by the CRM owner.
- A6: Overlap is a soft warning because legitimate parallel outreach (e.g. different sub-topics under one project) happens and must not be blocked.
- A7: Warnings must respect contact confidentiality: for ordinary records the warning shows only the other team's name and the date. For diplomatic-flagged or confidential records no warning is shown to users outside the permitted group, and only the owning project lead is notified.
- A8: Historical records lacking a project or mission reference are excluded from the detection criterion and are not backfilled by this feature.
- A9: Confidential and diplomatic-flagged records carry a permitted-group field that the CRM can check against the user's role when a warning is generated, and the same field can gate read access to overlap entries on those records.
- A10: For restricted records, the second user's engagement record shows only that their own contact was logged or planned; it carries no overlap marker, so the second user cannot infer the restricted record exists.
**Success criteria:**
- share of labelled duplicate pairs (same project or mission ID, same counterpart or ministry record, different team, within window) that trigger a warning before or at logging, measured on a pilot-period sample labelled independently by two coordinators; records without a reference are excluded: at least 90%
- false-positive rate among warnings (warnings acknowledged as not a real overlap): under 20% after one month of use
- time added to logging a contact when no overlap exists: under 2 seconds added on average
- share of newly planned or logged contacts that carry a project or mission reference: at least 95% after one month of use
**Responses:**
- C5 Revise (quoting "If the second user's engagement record carries a visible overlap entry naming the restricted record or its team, users outside the permitted group can infer that the restricted record exists."): The Critic is right that scope_in item 4 contradicted item 3. Writing a restricted-record overlap onto the second user's engagement record would let users outside the permitted group infer that the restricted record exists. Restricted-record overlaps are now recorded only on the restricted record, readable only by its permitted group, and they are not written to the second user's record. The second user's own contact still proceeds, with no overlap marker on their record (A10). Read access to restricted overlap entries is gated by the permitted-group field (A9). Who may read these entries should be confirmed by the Data protection officer.
**Response counts:** Defend 0, Revise 1, Concede 0

### Critic: SATISFIED
**Challenge states:**
- C5: closed (The revision removes the inference path: restricted-record overlaps are no longer written to the second user's engagement record (scope_in item 4, A10), and read access to those entries is gated by the permitted-group field (scope_in item 5, A9). Who may read them is flagged for Data protection officer confirmation, and the open visibility question is already escalated under C1.)
**New challenges:**
- (none)
**Disagreement:** 0 open (-1)

**Stop reason:** satisfied
