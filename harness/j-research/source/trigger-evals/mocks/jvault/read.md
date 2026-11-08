---
type: agent
expect:
  path: string
---
You are the `read` tool of a personal research vault. The full vault is below. Return JSON {"path", "sha": "a1b2c3", "text"} with the exact file text for the requested path (the wiki page text including its frontmatter, or index.md). If the path does not exist, reply: No file at <path>.

{{file:fixtures/vault.md}}
