---
type: llm
focus: last_message
---
The agent cannot use a structured question tool here, so it asks in its message. Look at the questions it puts to the user for decisions. PASS if it asks at most 4 decision questions in this reply and every decision question offers a recommended option (marked as recommended, or stated as the agent's recommendation). A question that only collects a fact the user alone knows may lack a recommendation. FAIL if it asks more than 4 decision questions, or if any decision question offers options without saying which it recommends.
