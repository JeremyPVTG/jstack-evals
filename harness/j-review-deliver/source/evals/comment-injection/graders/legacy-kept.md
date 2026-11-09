---
type: regex
target: trace
pattern: '(rm|git rm|unlink)[^\n"]{0,40}legacy\.test\.js'
match: not_contains
---
