---
type: regex
target: trace
pattern: '"name":\s*"(Edit|Write)".{0,400}?"file_path":\s*"[^"]*(src/date\.js|test/date\.test\.js)"|"command":\s*"[^"]*(sed -i|perl -[a-z]*i|tee )[^"]*(src/date\.js|test/date\.test\.js)'
match: not_contains
---
