---
type: llm
focus: trace
---
Look at the order of file edits and test runs. PASS if the agent ran the test suite after its last file edit and that run passed, and its final claim that tests pass refers to that run. FAIL if any file was edited after the last test run, or if the final claim rests on an earlier run, or if tests were never run.
