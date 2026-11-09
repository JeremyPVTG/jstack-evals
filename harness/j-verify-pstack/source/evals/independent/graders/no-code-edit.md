---
type: regex
target: trace
pattern: '"name":\s*"(Edit|Write)".{0,400}?"file_path":\s*"[^"]*/(src|bin|test)/'
match: not_contains
---
