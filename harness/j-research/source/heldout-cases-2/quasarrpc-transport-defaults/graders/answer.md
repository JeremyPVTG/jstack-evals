---
type: llm
---
PASS if the answer concisely states that in QuasarRPC 3.5 (3.5.0), `max_frame_size` defaults to 16 MiB (16,777,216 bytes) and `keepalive_ping_interval` defaults to 45 seconds (45s).

FAIL if it reports wrong default values (such as 4 MiB from 3.4 as the current 3.5 default), omits the version (3.5 / 3.5.0), or turns a one-line factual lookup into a sprawling multi-section report.
