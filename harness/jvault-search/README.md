# jvault search: keyword only versus keyword plus meaning

12 queries (`queries.json`), each worded differently from the page it should find, with the expected page(s). Written before any results were seen, by the agent that built the search, from the list of wiki page titles; so they are not blind.

- Keyword only: jvault's BM25 (`vault-server/src/vault.ts` at jstack 77e6d0c) over the local vault checkout at 5dbc706, via `node keyword.ts VAULT_DIR vault.ts`. Results in `keyword-results.json`.
- Keyword plus meaning: the deployed jvault `search` tool (BM25 fused with Cloudflare AI Search vector matches, Worker version 3d1dc196), same vault, top 5. Ranks in `fused-ranks.json`.

Rank of the first expected page in the top 5 (`comparison.json`):

| | Rank 1 | Top 3 | Mean reciprocal rank |
|---|---|---|---|
| Keyword only | 6/12 | 10/12 | 0.65 |
| Keyword plus meaning | 8/12 | 12/12 | 0.82 |

Meaning helped on 4 queries (limping cows 3 to 1, CI servers 2 to 1, thread watcher missing to 3, notes app missing to 2) and made none worse. Limits: 12 queries, one vault of 116 files, queries by the builder.
