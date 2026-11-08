# Hill-climb log (protocol: docs/decisions/2026-11-08-j-research-hill-climb-protocol.md)

Incumbent: a7f940a + hook. Spend counted from here against the $550 cap (review at $300).

## Candidate 1: b58df5c (open vault pages before relying on them)
Hypothesis: agents cite a vault page from its search snippet without opening it; adding that to the every-run checklist makes them read it.
Targeted cases: heldout-cases/purchase-approval-reuse, heldout-cases-2/latticecache-fresh-vault, evals/vault-fresh.
Screen: targeted cases, 3 runs, Sonnet and Opus, candidate and incumbent interleaved.
Screen result ($7.71): purchase-approval-reuse Opus 0.50 -> 0.83, Sonnet 0.50 -> 0.50 (Sonnet calls vault search, never read); latticecache and vault-fresh 1.00 both. Not the same direction on both models: **not kept**.

## Candidate 2: d93de69 (open a vault page with the read tool before citing it)
Hypothesis: the general wording did not move Sonnet; naming the action at the point of use (open the page with the read tool before citing it; search results show only snippets) will. Same targeted cases and screen.

## Test set 1 sealed
Written by Kimi K3.1 Pro (10 cases, 2 owner-sourced). Content hash 057d1c842d2becd9. Not opened by the climber; first look only on a frozen candidate.
