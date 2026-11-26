#!/bin/bash
# eval-secrets.sh CMD [ARG...]: run CMD under this machine's eval secrets prefix, which injects the eval billing key.
# The prefix is local and untracked: $JSTACK_EVAL_SECRETS (a shell-quoted command), else "secrets_argv" in
# harness/retro-loop/wrapper.local.json (gitignored; see wrapper.example.json). Set JSTACK_EVAL_SECRETS=" " to run
# CMD with no prefix, using whatever key this shell already has.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
prefix=()
while IFS= read -r -d '' word; do prefix+=("$word"); done < <(python3 -I - "$here/retro-loop/wrapper.local.json" <<'PY'
import json, os, shlex, sys
text = os.environ.get('JSTACK_EVAL_SECRETS')
if text is not None:
    argv = shlex.split(text)
else:
    try:
        argv = json.load(open(sys.argv[1])).get('secrets_argv')
    except FileNotFoundError:
        sys.exit('eval-secrets.sh: no secrets prefix. Set $JSTACK_EVAL_SECRETS, or copy '
                 'harness/retro-loop/wrapper.example.json to wrapper.local.json and fill in secrets_argv.')
    if not (isinstance(argv, list) and all(isinstance(a, str) and a for a in argv)):
        sys.exit('eval-secrets.sh: secrets_argv in wrapper.local.json must be a list of strings')
    if any(a.startswith('<') and a.endswith('>') for a in argv):
        sys.exit('eval-secrets.sh: wrapper.local.json still has <...> placeholders in secrets_argv')
sys.stdout.write(''.join(a + '\0' for a in argv))
PY
)
exec ${prefix[@]+"${prefix[@]}"} "$@"
