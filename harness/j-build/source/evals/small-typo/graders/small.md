---
type: llm
focus: last_message
---
PASS if the final reply is a short report (roughly 15 lines or fewer) that states the fix, the test result, and either the owner's next action or that nothing is needed, without presenting several options for the owner to choose between or asking for a go-ahead. FAIL if it asks the owner to choose between options or to approve before fixing, or is a long multi-section report.
