# Deliberation trace

**Feature request:** Project managers should be able to see the full history of engagement with a country before starting a new mission.

## Round 1

### Proposer
**In scope:**
- Read-only briefing view on a country record showing past engagement (logged meetings, correspondence, and missions) before a new mission is created
- Filter by project and date range within that view
- Ability to export the briefing view to PDF for offline use in mission preparation
- Display of confidentiality flags on contact records surfaced in the history, with restricted items hidden from users lacking clearance
**Out of scope:**
- Creating, editing, or deleting engagement records from the history view
- Changes to how engagement is logged at the point of capture
- Automated summaries or AI-generated narrative of history
- Historical data migration or cleanup of legacy records
- Notifications or alerts triggered by prior engagement
- Access changes to the broader CRM beyond this view
**Assumptions:**
- A1: 'Full history' means all logged meetings, emails, and mission records for the selected country from the earliest existing record onward, not a fixed window.
- A2: 'Before starting a new mission' means the view is accessed from or alongside mission creation for a given country, and it is used during preparation rather than as a real-time operational tool.
- A3: Engagement is recorded consistently enough in the CRM that a country-level timeline can be assembled from existing records without new data capture.
- A4: Project managers already have a role that permits reading country, contact, and mission records; this feature adds no new permission tier except for confidentiality-restricted contacts.
- A5: Each engagement record can be linked to a country, and engagement items that span multiple countries appear under each linked country.
- A6: Contact records carry a confidentiality or diplomatic-sensitivity marker that can be checked against the viewing user's clearance level.
- A7: Email content is stored in the CRM or linked from it; if only metadata is stored, the history shows subject and date only.
**Success criteria:**
- time for a project manager to assemble a pre-mission engagement briefing for a country: under 10 minutes for countries with up to 500 logged records
- share of project managers who report the history view contained the information they needed before a mission, measured in a post-launch survey: at least 80% agree
- proportion of restricted-contact records visible to users without clearance: zero, verified by access audit
**Responses:**
- (none)
**Response counts:** Defend 0, Revise 0, Concede 0

### Critic: CONTINUE
**Challenge states:**
- (none)
**New challenges:**
- C1 [risk] on A6 and scope_in item 4: A6 assumes contact records carry a confidentiality marker checked against a viewing user's clearance level, but the proposal does not say where clearance is stored, who assigns it, or what happens when a user has no clearance record at all. Restricted items could be shown to users with unknown or default clearance. Who defines the clearance model and the default for missing values?
- C2 [risk] on scope_in item 4 and success criterion 3: Hiding restricted contacts from the history does not hide the restricted information itself: a restricted contact's name can still appear in meeting subjects, email subjects (A7), mission titles, or project notes that the view shows. The proposal does not say whether these linked free-text fields are also filtered, so the zero-leak criterion may be met on the contact field while the information still leaks. Who decides which fields are redacted?
- C3 [risk] on scope_in item 3 (PDF export) and A4: A PDF export of a briefing containing diplomatic-sensitivity content creates an uncontrolled copy outside the CRM's access controls. The proposal does not say whether exports respect confidentiality filtering, carry a classification marking, are logged, or how long they may be retained. Who approves offline distribution of country engagement records?
- C4 [question] on A1 and success criterion 1: A1 defines full history as all records from the earliest existing record, yet the success criterion is measured for countries with up to 500 records, with no stated behaviour above that. For countries with thousands of records, the 10-minute target has no defined path. Is pagination, default windowing, or a hard limit acceptable, and who decides?
- C5 [question] on A3 and A5: A3 assumes engagement is recorded consistently enough to assemble a timeline, and A5 assumes multi-country items link to every country. Neither is verified. If many meetings are logged only as free text or are unlinked to a country, the briefing is silently incomplete, which undermines the survey success criterion. Who audits data completeness before launch, and what does the view show when records are missing?
**Disagreement:** 5 open (first round)

## Round 2

### Proposer
**In scope:**
- Read-only briefing view on a country record showing past engagement (logged meetings, correspondence, and missions) before a new mission is created
- Filter by project and date range within that view
- Ability to export the briefing view to PDF for offline use in mission preparation, limited to items the exporting user is cleared to see, with a classification marking and an export log entry
- Display of confidentiality flags on contact records surfaced in the history, with restricted items hidden from users lacking clearance
- Redaction of restricted contact names from linked free-text fields (meeting subjects, email subjects, mission titles, project notes) shown in the briefing for users lacking clearance, using a defined list of fields reviewed by the data protection officer
- Clearance lookup that treats a missing or unknown clearance record as no clearance (deny by default)
- Completeness indicator on the briefing showing counts of records with no country link or no structured content, so users can see when the history may be incomplete
**Out of scope:**
- Creating, editing, or deleting engagement records from the history view
- Changes to how engagement is logged at the point of capture
- Automated summaries or AI-generated narrative of history
- Historical data migration or cleanup of legacy records
- Notifications or alerts triggered by prior engagement
- Access changes to the broader CRM beyond this view
- Defining the enterprise clearance model itself (owned by the data protection officer)
- Pagination-free rendering of very large histories: countries above 500 records will be served by filtered, paged views rather than a single scroll
**Assumptions:**
- A1: 'Full history' means all logged meetings, emails, and mission records for the selected country from the earliest existing record onward, not a fixed window; the default view opens on the most recent 24 months and the user can extend the range.
- A2: 'Before starting a new mission' means the view is accessed from or alongside mission creation for a given country, and it is used during preparation rather than as a real-time operational tool.
- A3: Engagement is recorded consistently enough in the CRM that a country-level timeline can be assembled from existing records without new data capture; this is unverified and is to be checked by a pre-launch completeness audit.
- A4: Project managers already have a role that permits reading country, contact, and mission records; this feature adds no new permission tier except for confidentiality-restricted contacts, and export is restricted to users with the same read rights.
- A5: Each engagement record can be linked to one or more countries, and multi-country items appear under each linked country; records with no country link are excluded from country views and counted in the completeness indicator.
- A6: Contact records carry a confidentiality marker, and each user has a clearance value held in a central user-attribute store assigned by the data protection officer; a user with no clearance record is treated as having no clearance.
- A7: Email content is stored in the CRM or linked from it; if only metadata is stored, the history shows subject and date only, and subject lines are subject to the same redaction rule as other free-text fields.
**Success criteria:**
- time for a project manager to assemble a pre-mission engagement briefing for a country: under 10 minutes for countries with up to 500 logged records; for larger countries, the filtered default view loads within 10 minutes on the same task
- share of project managers who report the history view contained the information they needed before a mission, measured in a post-launch survey: at least 80% agree
- proportion of restricted-contact records or restricted free-text references visible to users without clearance, including PDF exports: zero, verified by access audit and by a test set of restricted names seeded across all linked free-text fields
**Responses:**
- C1 Revise (quoting "Who defines the clearance model and the default for missing values?"): Accepted that the clearance model was unstated. The proposal now names the data protection officer as owner of the clearance model and of the default. Missing clearance is treated as no clearance (deny by default), so restricted items are hidden from any user without an explicit clearance record. The clearance source is a central user-attribute store, and the exact store is to be confirmed by the DPO as an invented fact (A6).
- C2 Revise (quoting "Who decides which fields are redacted?"): Accepted. Hiding the contact field alone is insufficient. The view now redacts restricted contact names from linked free-text fields (meeting subjects, email subjects, mission titles, project notes) for users without clearance. The list of redacted fields is set by the data protection officer, and the zero-leak criterion now covers free-text references and a seeded test set.
- C3 Revise (quoting "Who approves offline distribution of country engagement records?"): Accepted. PDF export now respects the same confidentiality filtering as the screen view, carries a classification marking, and writes an export log entry. Retention and offline distribution approval are outside this proposal and are referred to Legal; the feature will not ship export until Legal confirms the approval route.
- C4 Revise (quoting "For countries with thousands of records, the 10-minute target has no defined path."): Partly accepted. Full history is retained as the definition, but the default view is the most recent 24 months with the option to extend, and countries above 500 records are served by filtered, paged views. The success criterion is now stated for both cases. The head of Country Engagement is asked to confirm the paging approach.
- C5 Revise (quoting "Who audits data completeness before launch, and what does the view show when records are missing?"): Accepted. A completeness indicator is added to the view showing counts of unlinked or unstructured records, and a pre-launch completeness audit is added to the rollout. The audit owner is the operations data owner, and the survey criterion will be read alongside the completeness figures.
**Response counts:** Defend 0, Revise 5, Concede 0

### Critic: CONTINUE
**Challenge states:**
- C1: closed
- C2: closed
- C3: escalated
- C4: escalated
- C5: closed
**New challenges:**
- C6 [risk] on scope_in item 7 (completeness indicator) and scope_in item 4 (restricted items hidden): The completeness indicator shows counts of unlinked or unstructured records. If these counts include restricted engagement, a user without clearance could infer that restricted meetings or missions exist for a country, even though the items themselves are hidden. The proposal does not say whether the counts are filtered by the viewing user's clearance. Should completeness counts be computed only over records the user may see, and if not, who accepts the disclosure risk?
**Disagreement:** 1 open (-4)

## Round 3

### Proposer
**In scope:**
- Read-only briefing view on a country record showing past engagement (logged meetings, correspondence, and missions) before a new mission is created
- Filter by project and date range within that view
- Ability to export the briefing view to PDF for offline use in mission preparation, limited to items the exporting user is cleared to see, with a classification marking and an export log entry
- Display of confidentiality flags on contact records surfaced in the history, with restricted items hidden from users lacking clearance
- Redaction of restricted contact names from linked free-text fields (meeting subjects, email subjects, mission titles, project notes) shown in the briefing for users lacking clearance, using a defined list of fields reviewed by the data protection officer
- Clearance lookup that treats a missing or unknown clearance record as no clearance (deny by default)
- Completeness indicator on the briefing showing counts of records with no country link or no structured content, computed only over records the viewing user is cleared to see, so that counts never reveal the existence of restricted items to users without clearance
**Out of scope:**
- Creating, editing, or deleting engagement records from the history view
- Changes to how engagement is logged at the point of capture
- Automated summaries or AI-generated narrative of history
- Historical data migration or cleanup of legacy records
- Notifications or alerts triggered by prior engagement
- Access changes to the broader CRM beyond this view
- Defining the enterprise clearance model itself (owned by the data protection officer)
- Pagination-free rendering of very large histories: countries above 500 records will be served by filtered, paged views rather than a single scroll
- Completeness counts that reflect restricted records the viewing user cannot see; any such disclosure would require separate DPO approval
**Assumptions:**
- A1: 'Full history' means all logged meetings, emails, and mission records for the selected country from the earliest existing record onward, not a fixed window; the default view opens on the most recent 24 months and the user can extend the range.
- A2: 'Before starting a new mission' means the view is accessed from or alongside mission creation for a given country, and it is used during preparation rather than as a real-time operational tool.
- A3: Engagement is recorded consistently enough in the CRM that a country-level timeline can be assembled from existing records without new data capture; this is unverified and is to be checked by a pre-launch completeness audit.
- A4: Project managers already have a role that permits reading country, contact, and mission records; this feature adds no new permission tier except for confidentiality-restricted contacts, and export is restricted to users with the same read rights.
- A5: Each engagement record can be linked to one or more countries, and multi-country items appear under each linked country; records with no country link are excluded from country views and counted in the completeness indicator only where the viewing user is cleared to see the underlying record.
- A6: Contact records carry a confidentiality marker, and each user has a clearance value held in a central user-attribute store assigned by the data protection officer; a user with no clearance record is treated as having no clearance.
- A7: Email content is stored in the CRM or linked from it; if only metadata is stored, the history shows subject and date only, and subject lines are subject to the same redaction rule as other free-text fields.
- A8: Completeness counts are computed per viewing user over the same clearance-filtered record set as the rest of the view, so a restricted unlinked or unstructured record is not counted for a user without clearance; the DPO must confirm that this filtering removes any inference risk from aggregate counts.
**Success criteria:**
- time for a project manager to assemble a pre-mission engagement briefing for a country: under 10 minutes for countries with up to 500 logged records; for larger countries, the filtered default view loads within 10 minutes on the same task
- share of project managers who report the history view contained the information they needed before a mission, measured in a post-launch survey: at least 80% agree
- proportion of restricted-contact records or restricted free-text references visible to users without clearance, including PDF exports and completeness counts: zero, verified by access audit and by a test set of restricted names seeded across all linked free-text fields and in unlinked and unstructured records
**Responses:**
- C6 Revise (quoting "Should completeness counts be computed only over records the user may see, and if not, who accepts the disclosure risk?"): Accepted. The completeness indicator will be computed only over records the viewing user is cleared to see, so restricted unlinked or unstructured records do not contribute to counts shown to users without clearance. This removes the inference path the Critic identified. I have not accepted that every aggregate is safe by default: the DPO must confirm that clearance-filtered counts do not leak through small-number effects, for example a count that changes between a cleared and an uncleared user. If the DPO judges that risk material, the fallback is to drop the completeness counts for countries where restricted records exist, and I would accept that fallback.
**Response counts:** Defend 0, Revise 1, Concede 0

### Critic: CONTINUE
**Challenge states:**
- C6: escalated
**New challenges:**
- C7 [risk] on scope_in item 5 (redaction of restricted contact names from free-text fields) and success criterion 3: Redaction is defined by matching restricted contact names against linked free-text fields. The proposal does not say how names that are not held as contact records are handled, such as nicknames, titles with surnames only, misspellings, or names written in other languages. These would pass the redaction filter and still reveal a restricted contact's involvement to users without clearance. The zero-leak test set only covers names that are already seeded, so it would not catch this gap. Who decides the matching rules, and does the proposal need a fallback such as hiding whole free-text fields for restricted records?
**Disagreement:** 1 open (+0)

## Round 4

### Proposer
**In scope:**
- Read-only briefing view on a country record showing past engagement (logged meetings, correspondence, and missions) before a new mission is created
- Filter by project and date range within that view
- Ability to export the briefing view to PDF for offline use in mission preparation, limited to items the exporting user is cleared to see, with a classification marking and an export log entry
- Display of confidentiality flags on contact records surfaced in the history, with restricted items hidden from users lacking clearance
- Field-level suppression instead of name matching: for users lacking clearance, any engagement, mission, or project record structurally linked to a restricted contact shows only type, date, and a restricted placeholder, and its free-text fields (meeting subjects, email subjects, mission titles, project notes) are not displayed or exported; the suppression rule uses the record-to-contact link, not text matching, and the field list is reviewed by the data protection officer
- Clearance lookup that treats a missing or unknown clearance record as no clearance (deny by default)
- Completeness indicator on the briefing showing counts of records with no country link or no structured content, computed only over records the viewing user is cleared to see, so that counts never reveal the existence of restricted items to users without clearance
**Out of scope:**
- Creating, editing, or deleting engagement records from the history view
- Changes to how engagement is logged at the point of capture
- Automated summaries or AI-generated narrative of history
- Historical data migration or cleanup of legacy records
- Notifications or alerts triggered by prior engagement
- Access changes to the broader CRM beyond this view
- Defining the enterprise clearance model itself (owned by the data protection officer)
- Pagination-free rendering of very large histories: countries above 500 records will be served by filtered, paged views rather than a single scroll
- Completeness counts that reflect restricted records the viewing user cannot see; any such disclosure would require separate DPO approval
- Name-matching redaction of free-text fields on records not structurally linked to a restricted contact; this is not relied on as a control
**Assumptions:**
- A1: 'Full history' means all logged meetings, emails, and mission records for the selected country from the earliest existing record onward, not a fixed window; the default view opens on the most recent 24 months and the user can extend the range.
- A2: 'Before starting a new mission' means the view is accessed from or alongside mission creation for a given country, and it is used during preparation rather than as a real-time operational tool.
- A3: Engagement is recorded consistently enough in the CRM that a country-level timeline can be assembled from existing records without new data capture; this is unverified and is to be checked by a pre-launch completeness audit.
- A4: Project managers already have a role that permits reading country, contact, and mission records; this feature adds no new permission tier except for confidentiality-restricted contacts, and export is restricted to users with the same read rights.
- A5: Each engagement record can be linked to one or more countries, and multi-country items appear under each linked country; records with no country link are excluded from country views and counted in the completeness indicator only where the viewing user is cleared to see the underlying record.
- A6: Contact records carry a confidentiality marker, and each user has a clearance value held in a central user-attribute store assigned by the data protection officer; a user with no clearance record is treated as having no clearance.
- A7: Email content is stored in the CRM or linked from it; if only metadata is stored, the history shows subject and date only, and subject lines are subject to the same suppression rule as other free-text fields on records linked to restricted contacts.
- A8: Completeness counts are computed per viewing user over the same clearance-filtered record set as the rest of the view, so a restricted unlinked or unstructured record is not counted for a user without clearance; the DPO must confirm that this filtering removes any inference risk from aggregate counts.
- A9: Engagement, mission, and project records can be structurally linked to the contact records they involve, so that suppression can be keyed on the link rather than on name text; the DPO owns the rule that decides which links trigger suppression and whether free-text on unlinked records needs any further control.
**Success criteria:**
- time for a project manager to assemble a pre-mission engagement briefing for a country: under 10 minutes for countries with up to 500 logged records; for larger countries, the filtered default view loads within 10 minutes on the same task
- share of project managers who report the history view contained the information they needed before a mission, measured in a post-launch survey: at least 80% agree
- proportion of restricted-contact records, or free-text fields on records linked to restricted contacts, visible to users without clearance, including PDF exports and completeness counts: zero, verified by access audit and by a test set of records linked to restricted contacts across all record types, including unlinked and unstructured records; a separate check confirms that no free-text of a suppressed record appears in exports
**Responses:**
- C7 Revise (quoting "Who decides the matching rules, and does the proposal need a fallback such as hiding whole free-text fields for restricted records?"): Accepted in substance. Name matching cannot be a reliable control: nicknames, surname-only titles, misspellings, and other-language forms all escape an exact-name filter, and the seeded test set would not catch them. I have dropped name matching as the redaction mechanism. The new rule keys on the structural link between a record and a restricted contact. For users without clearance, a linked record shows only type, date, and a restricted placeholder, and its free-text fields are withheld entirely, including in PDF exports and counts. This is the fallback the Critic proposed, applied to linked records only. The matching rule question is now a DPO decision: the DPO decides which link types trigger suppression and whether any residual control is needed for free-text on unlinked records. I do not claim the link-based rule closes every path. A restricted person can still be named in free text on an unlinked record, and that residual risk is for the DPO to accept or close. The zero-leak test now seeds linked records and checks that suppressed free text never appears, rather than checking only seeded names.
**Response counts:** Defend 0, Revise 1, Concede 0

### Critic: CONTINUE
**Challenge states:**
- C7: escalated
**New challenges:**
- C8 [risk] on success criterion 3 and the response to C7: Success criterion 3 requires zero visibility of restricted free text, including on records not linked to a restricted contact, and it says the test set covers unlinked and unstructured records. The response to C7 concedes that a restricted person can still be named in free text on an unlinked record, and it leaves that residual risk to the DPO. The criterion as written cannot be met for unlinked records, so the proposal is internally inconsistent. Either the criterion must be restated to cover linked records only, with the unlinked case recorded as an accepted residual risk, or the proposal must add a control for unlinked free text. Which of these applies, and who accepts the residual risk?
**Disagreement:** 1 open (+0)

## Round 5

### Proposer
**In scope:**
- Read-only briefing view on a country record showing past engagement (logged meetings, correspondence, and missions) before a new mission is created
- Filter by project and date range within that view
- Ability to export the briefing view to PDF for offline use in mission preparation, limited to items the exporting user is cleared to see, with a classification marking and an export log entry
- Display of confidentiality flags on contact records surfaced in the history, with restricted items hidden from users lacking clearance
- Field-level suppression keyed on the structural link between a record and a restricted contact, not name matching: for users lacking clearance, any engagement, mission, or project record structurally linked to a restricted contact shows only type, date, and a restricted placeholder, and its free-text fields (meeting subjects, email subjects, mission titles, project notes) are not displayed or exported; the list of link types that trigger suppression and the field list are reviewed by the data protection officer
- Clearance lookup that treats a missing or unknown clearance record as no clearance (deny by default)
- Completeness indicator on the briefing showing counts of records with no country link or no structured content, computed only over records the viewing user is cleared to see, so that counts never reveal the existence of restricted items to users without clearance
- Documented residual-risk register entry for free text on unlinked records that may name a restricted person, submitted to the DPO for written acceptance or further control before launch
**Out of scope:**
- Creating, editing, or deleting engagement records from the history view
- Changes to how engagement is logged at the point of capture
- Automated summaries or AI-generated narrative of history
- Historical data migration or cleanup of legacy records
- Notifications or alerts triggered by prior engagement
- Access changes to the broader CRM beyond this view
- Defining the enterprise clearance model itself (owned by the data protection officer)
- Pagination-free rendering of very large histories: countries above 500 records will be served by filtered, paged views rather than a single scroll
- Completeness counts that reflect restricted records the viewing user cannot see; any such disclosure would require separate DPO approval
- Name-matching redaction of free-text fields on any record; this is not relied on as a control
- Automated detection of restricted persons named in free text on unlinked records; this is not built in this feature and is left to the DPO residual-risk decision
**Assumptions:**
- A1: 'Full history' means all logged meetings, emails, and mission records for the selected country from the earliest existing record onward, not a fixed window; the default view opens on the most recent 24 months and the user can extend the range.
- A2: 'Before starting a new mission' means the view is accessed from or alongside mission creation for a given country, and it is used during preparation rather than as a real-time operational tool.
- A3: Engagement is recorded consistently enough in the CRM that a country-level timeline can be assembled from existing records without new data capture; this is unverified and is to be checked by a pre-launch completeness audit.
- A4: Project managers already have a role that permits reading country, contact, and mission records; this feature adds no new permission tier except for confidentiality-restricted contacts, and export is restricted to users with the same read rights.
- A5: Each engagement record can be linked to one or more countries, and multi-country items appear under each linked country; records with no country link are excluded from country views and counted in the completeness indicator only where the viewing user is cleared to see the underlying record.
- A6: Contact records carry a confidentiality marker, and each user has a clearance value held in a central user-attribute store assigned by the data protection officer; a user with no clearance record is treated as having no clearance.
- A7: Email content is stored in the CRM or linked from it; if only metadata is stored, the history shows subject and date only, and subject lines are subject to the same suppression rule as other free-text fields on records linked to restricted contacts.
- A8: Completeness counts are computed per viewing user over the same clearance-filtered record set as the rest of the view, so a restricted unlinked or unstructured record is not counted for a user without clearance; the DPO must confirm that this filtering removes any inference risk from aggregate counts.
- A9: Engagement, mission, and project records can be structurally linked to the contact records they involve, so that suppression can be keyed on the link rather than on name text; the DPO owns the rule that decides which link types trigger suppression, and the DPO alone decides whether the residual risk of free text on unlinked records is accepted or needs a further control.
**Success criteria:**
- time for a project manager to assemble a pre-mission engagement briefing for a country: under 10 minutes for countries with up to 500 logged records; for larger countries, the filtered default view loads within 10 minutes on the same task
- share of project managers who report the history view contained the information they needed before a mission, measured in a post-launch survey: at least 80% agree
- proportion of records structurally linked to a restricted contact, including their free-text fields, visible to users without clearance, including PDF exports and completeness counts: zero, verified by access audit and by a test set of linked records across all record types; a separate check confirms that no free text of a suppressed linked record appears in exports
- unlinked free-text residual risk (restricted person named in free text on a record with no structural link to a restricted contact): not claimed as zero; before launch the DPO must record written acceptance of this residual risk or specify a further control, and that decision is a launch gate
**Responses:**
- C8 Revise (quoting "Either the criterion must be restated to cover linked records only, with the unlinked case recorded as an accepted residual risk, or the proposal must add a control for unlinked free text."): Revised: criterion 3 is restated to cover records structurally linked to restricted contacts only, and the unlinked case is moved to a separate criterion 4 that does not claim zero. I did not add a control for unlinked free text: name matching was already rejected as unreliable, and any content-level detection would be a new, unscoped control. The residual risk is recorded in the scope and must be accepted or closed by the DPO before launch as a gate. The DPO, not the proposer, accepts the residual risk.
**Response counts:** Defend 0, Revise 1, Concede 0

### Critic: SATISFIED
**Challenge states:**
- C8: closed
**New challenges:**
- (none)
**Disagreement:** 0 open (-1)

**Stop reason:** satisfied
