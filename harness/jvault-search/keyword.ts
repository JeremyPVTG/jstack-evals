// Keyword-only ranking (jvault's BM25) for each query in queries.json, over a local vault checkout.
// Usage: node keyword.ts VAULT_DIR VAULT_TS
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
const [vaultDir, vaultTs] = process.argv.slice(2);
const { search } = await import(vaultTs);
const files: Record<string, string> = {};
const walk = (dir: string) => { for (const name of readdirSync(dir)) { if (name.startsWith(".")) continue; const p = join(dir, name); if (statSync(p).isDirectory()) walk(p); else if (p.endsWith(".md")) files[relative(vaultDir, p)] = readFileSync(p, "utf8"); } };
walk(vaultDir);
const queries = JSON.parse(readFileSync(new URL("./queries.json", import.meta.url), "utf8"));
const out = queries.map((item: { q: string; expect: string[] }) => ({ q: item.q, top: search(files, item.q, 5, new Date("2026-11-08")).map((h: { path: string }) => h.path) }));
console.log(JSON.stringify(out, null, 1));
