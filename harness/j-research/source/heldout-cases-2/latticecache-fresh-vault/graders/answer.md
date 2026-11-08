---
type: llm
---
PASS if the answer reports from the LatticeCache 2.3 note:
1. Pro plan base cost of $45/month, including 20 GB of storage, 50 million read ops/month, and 10 million write ops/month.
2. Overage rates of $1.80 per GB-month of storage, $0.12 per million read ops, and $0.60 per million write ops.
3. Maximum single item size of 5 MB.

FAIL if it reports wrong pricing, included allowances, or max item size for LatticeCache 2.3, or claims the figures are unknown.
