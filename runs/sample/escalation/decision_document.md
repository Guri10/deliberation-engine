# Decision Document
_Stop reason: satisfied_

## Agreed Scope
**In scope:**
- Detect when two users (regional coordinators, project managers, or mission delegates) log or plan outreach to the same government counterpart record or same ministry record within one country about the same project ID or mission ID within a defined window
- For ordinary records, show a warning to the user creating or logging the second contact naming the other team and the date of the existing contact
- For confidential or diplomatic-flagged records, show no warning to users outside the record's permitted group; record the overlap on the restricted record only and notify the owning project lead only
- Let the user proceed after acknowledging the overlap; for ordinary records, record the overlap on both engagement records; for restricted records, never write an overlap entry to the second user's engagement record
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

## Surfaced Assumptions
- A1: 'Same ministry' means the same counterpart contact record or the same ministry organization record within one country; different countries never trigger an overlap. (Accepted; raised in round 1)
- A2: 'About the same thing' means the same project ID or mission ID. Free-text topic matching is out of scope because it is unreliable. (Accepted; raised in round 1)
- A3: 'Teams' means the owning team recorded on the engagement record; a user with several team assignments is classified by the record's team, and a user with none is treated as a separate team. (Revised; raised in round 1)
- A4: Each contact or engagement record already carries a project or mission reference field that can be used for matching, and it can be made mandatory for new entries. (Challenged-and-held; raised in round 1)
- A5: The overlap window is the 30 days before and after a planned contact date, or the current open period for logged contacts; the exact window is configurable by the CRM owner. (Challenged-and-held; raised in round 1)
- A6: Overlap is a soft warning because legitimate parallel outreach happens and must not be blocked. (Accepted; raised in round 1)
- A7: Warnings must respect contact confidentiality: for ordinary records the warning shows only the other team's name and the date; for diplomatic-flagged or confidential records no warning is shown to users outside the permitted group and only the owning project lead is notified. (Revised; raised in round 1)
- A8: Historical records lacking a project or mission reference are excluded from the detection criterion and are not backfilled by this feature. (Challenged-and-held; raised in round 2)
- A9: Confidential and diplomatic-flagged records carry a permitted-group field that the CRM can check against the user's role when a warning is generated, and the same field can gate read access to overlap entries on those records. (Challenged-and-held; raised in round 2)
- A10: For restricted records, the second user's engagement record shows only that their own contact was logged or planned; it carries no overlap marker. (Revised; raised in round 3)

## Open Questions
- **Blocking:** Can a confidential or diplomatic-flagged record trigger a warning at all, and may the existence of a restricted contact or its counterpart ever be named to users outside its permitted group? Scope and A7 were revised to suppress warnings, but the rule for who may know a restricted contact exists remains unconfirmed. (answer: Data protection officer; source: deliberation)
- **Blocking:** Who may read overlap entries recorded on restricted records, and is the permitted-group gating in A9 valid in the CRM? (answer: Data protection officer; source: deliberation)
- **Non-blocking:** Who owns the separate backfill of missing project or mission references on historical records, which the 90% detection criterion depends on, and when will it be scheduled? (answer: Head of Country Engagement; source: deliberation)
- **Non-blocking:** Can the project or mission reference be made mandatory on new entries in the current CRM, as assumed in A4? (answer: Head of Country Engagement; source: deliberation)
- **Blocking:** Scope says the warning names the other team and the existing contact record, while A7 says it shows only the other team's name and the date. These conflict: if the existing contact record is a diplomatic-flagged or confidential record, naming it could expose its existence or counterpart to users outside its permitted group. The proposal never states who may see that a contact exists on a restricted record, or whether a confidential record can trigger a warning at all. (answer: Data protection officer; source: escalated, C1)
- **Non-blocking:** Confirm A3: 'Teams' means the owning team recorded on the engagement record. A user with several team assignments is classified by the team on the record; a user with none is treated as a separate team, so their contacts can trigger a warning against any other team. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A4: Each contact or engagement record already carries a project or mission reference field that can be used for matching, and it can be made mandatory for new entries. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A5: The overlap window is the 30 days before and after a planned contact date, or the current open period for logged contacts; the exact window is configurable by the CRM owner. (answer: CRM system owner; source: invented fact)
- **Non-blocking:** Confirm A9: Confidential and diplomatic-flagged records carry a permitted-group field that the CRM can check against the user's role when a warning is generated, and the same field can gate read access to overlap entries on those records. (answer: CRM system owner; source: invented fact)

## Invented Facts
- A3: 'Teams' means the owning team recorded on the engagement record. A user with several team assignments is classified by the team on the record; a user with none is treated as a separate team, so their contacts can trigger a warning against any other team.
- A4: Each contact or engagement record already carries a project or mission reference field that can be used for matching, and it can be made mandatory for new entries.
- A5: The overlap window is the 30 days before and after a planned contact date, or the current open period for logged contacts; the exact window is configurable by the CRM owner.
- A9: Confidential and diplomatic-flagged records carry a permitted-group field that the CRM can check against the user's role when a warning is generated, and the same field can gate read access to overlap entries on those records.

## Success Criteria
- share of labelled duplicate pairs (same project or mission ID, same counterpart or ministry record, different team, within window) that trigger a warning before or at logging, measured on a pilot-period sample labelled independently by two coordinators; records without a reference are excluded: at least 90%
- false-positive rate among warnings (warnings acknowledged as not a real overlap): under 20% after one month of use
- time added to logging a contact when no overlap exists: under 2 seconds added on average
- share of newly planned or logged contacts that carry a project or mission reference: at least 95% after one month of use

## Deliberation Summary
- Rounds run: 3
- Stop reason: satisfied
- Disagreement per round: R1 4, R2 1 (-3), R3 0 (-1)
- Proposer confidence: 55 (The scope is largely concrete, but the escalated C1 (whether a restricted record's existence or counterpart can be named in warnings) is unresolved and awaits Data protection officer input, and the 90% detection criterion depends on an unassigned reference-field backfill and an unspecified labelled test set (C2, C4 closed without concrete owners in scope).)
- Critic confidence: 45 (Scope is coherent and most gaps closed, but C1 (what a restricted-record warning may reveal, and whether confidential records trigger warnings at all) is escalated and unresolved, and the 90% detection target depends on reference-field completeness and historical data that is out of scope, so the feature could silently miss overlaps.)
