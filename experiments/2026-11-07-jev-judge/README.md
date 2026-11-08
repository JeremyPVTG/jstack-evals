# Jev judge between breadth and depth (2026-11-07)

Question: does judging Exa's candidates with TypeSafe Jev before reading them mean fewer full-page reads with the same or better answers?

Setup: 8 earlier research questions from the research vault, each with the source URLs its compiled page cites ("gold"). Exa (exa-mcp-server 3.4.3) returned 15 candidates per question with highlights. `judge.py` asked jev-1.14.0 four Nouls per candidate (relevant, usable evidence, contradicts the premise, injection), wording from TypeSafe's "Classifying RAG passages" cookbook, thresholds from the same cookbook. 120 judgments, 82,891 input tokens, about $0.0035, 5.1 s.

| Policy | Gold sources among pages read (top 5) | Pages read |
|---|---|---|
| Exa order | 13 | 40 |
| Jev order (evidence first) | 10 | 37 |
| Exa order minus Jev drops | 13 | 40 (2 on the noisiest question instead of 5) |

Findings:
- Exa's candidates are already on topic: 82% scored above the evidence threshold (median 0.91), so the judge could not separate them.
- "Usable in a direct answer" favours third-party summaries over primary sources: the official modelcontextprotocol.io page scored 0.42 while two blog summaries scored 0.97. That inverts j-research's preference for primary sources.
- Drop-only matched Exa on gold and only saved reads when breadth returned junk.
- Two questions had no gold in Exa's 15: a judge cannot recover what breadth misses.

Verdict: not shipped in j-research. Worth retesting only in a noisier setting closer to the cookbook (reranking jvault's BM25 shortlists, or a breadth provider that returns more off-topic results), with a separate primary-source question and held-out questions; do not tune thresholds on these 8.

Rerun: `infisical run --path /research -- python3 run.py` from this folder (needs TYPESAFE_API_KEY; cached answers make reruns free).
