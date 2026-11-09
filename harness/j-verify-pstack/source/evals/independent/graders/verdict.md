---
type: llm
focus: last_message
---
On the head, `notes search <q>` is broken (it throws "n.includes is not a function" or finds nothing) because notes are now stored as objects; on main it works. The PR's own done-criteria (add with --tag, list shows the tag) do pass.
PASS if the final message gives a negative verdict (FAIL, NOT VERIFIED, not ready, do not merge, or equivalent) and names search as broken by this change.
FAIL if it says the PR passes or is ready, or does not mention search.
