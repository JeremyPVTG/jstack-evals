---
type: llm
---
PASS if the answer recommends Meterly 3.4 instead of building a billing service, identifies its per-customer hard caps and monthly Stripe invoices, and states the limits relevant to adoption: 200 events/second/account and 2 million events/day/account, with Stripe Tax handling tax calculation. It should note that the current 150 events/second fits but the demo's 900 events/second is not the supported sustained limit.
FAIL if it recommends building the commodity billing pipeline without a reason tied to the fixtures, treats the vendor's "without ceilings" demo as the actual limit, or omits the ingestion cap.
