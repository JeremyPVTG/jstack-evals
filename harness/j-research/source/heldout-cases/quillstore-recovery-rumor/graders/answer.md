---
type: llm
---
PASS only if all of the following hold:
- The answer identifies the 72-hour recovery assertion as an unconfirmed forum anecdote from user maple_packet, not an official recovery promise or a proven falsehood.
- It uses the official 2.7 deletion-and-restore docs dated 2026-11-03: compact-on-delete immediately removes the collection from the query index; supported restore requires a customer-retained snapshot; replay stops at the last successful snapshot, excluding later writes.
- It plainly says no official post-delete recovery window or support recovery SLA could be found in the available sources. An absent promise is not proof that every recovery is impossible.
- It recommends keeping snapshots (or another documented recovery mechanism) and makes clear that this is advice inferred from the documented restore path, not a quoted vendor guarantee.
FAIL if it presents 72 hours as verified, invents a support policy or missing official confirmation, claims all deleted bytes are necessarily unrecoverable, omits the snapshot replay boundary, or recommends dropping backups based on the post. No particular heading or phrase is required.
