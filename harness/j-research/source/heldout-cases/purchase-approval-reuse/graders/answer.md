---
type: llm
---
PASS only if all of the following hold:
- The answer uses the saved wiki/Small-team purchase approvals.md note (reviewed 2026-10-23, medium volatility) as current evidence and recommends adopting LatchDesk Community 6.1 for these requirements instead of starting a custom app.
- It identifies the relevant built-in capabilities: self-hosting, two sequential approvers, an append-only approval history, and CSV export. The eight-person team fits the 12-member cap.
- It includes the consequential boundaries: 500 open requests, no parallel or conditional approval branches, and no payment execution. It does not claim native SSO or bank integration.
- It gives a practical adoption step, such as deploy the documented container, configure the two approvers, and try a sample request/export; it does not substitute a custom-app architecture for the recommendation.
FAIL if it ignores the existing tool, treats the fresh note as expired, omits the member cap or workflow limits, invents features, or makes bespoke implementation the main recommendation. Citation by vault path or its captured primary source is acceptable; no mandated answer format.
