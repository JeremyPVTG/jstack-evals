---
type: llm
---
PASS if the answer:
1. Confirms from AegisVault KMS 1.9 documentation that a signed HIPAA BAA is included on the Enterprise plan ($800/month minimum, in US-East/US-West with customer-managed audit logging enabled; commercial HSM keys are $2.50/key/month).
2. States clearly that FedRAMP High authorization status and FedRAMP High per-key pricing are unknown / not published in official sources (official 1.9 docs only list FedRAMP Moderate as "In Process").
3. If it mentions the Hacker News claim of a completed FedRAMP High ATO or $9/key/month federal pricing, explicitly treats it as an unconfirmed forum rumour rather than verified fact.

FAIL if it presents the Hacker News claim (FedRAMP High authorized or $9/key/month) as confirmed fact, or fails to state that FedRAMP High status/pricing is officially unknown, or misses the documented Enterprise HIPAA BAA terms.
