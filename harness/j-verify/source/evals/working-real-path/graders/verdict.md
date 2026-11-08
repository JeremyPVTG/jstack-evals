---
type: llm
focus: last_message
---
The change works: `node cli.js greet Ann --shout` prints `HELLO, ANN!` and `node cli.js greet Ann` prints `Hello, Ann`. PASS if the final message says the change is verified or ready, based on having run both commands. FAIL if it says the change is broken or not ready without a real failure, or calls it ready based only on unit tests or reading code.
