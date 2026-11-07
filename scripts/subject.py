#!/usr/bin/env python3
"""Pin or verify a clean committed evaluation subject; runs no agent tasks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def snapshot(repo):
    repo = Path(repo).resolve()
    root = Path(git(repo, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    if root != repo:
        raise ValueError('Pass the repository root')
    if git(repo, 'status', '--porcelain', '--untracked-files=all').strip():
        raise ValueError('Subject must be clean, including untracked files')
    if not (repo / 'packs.json').is_file() or not (repo / 'skills').is_dir():
        raise ValueError('Subject is not a jstack skill package')
    names = git(repo, 'ls-files', '-z').decode().split('\0')
    files = {}
    for name in filter(None, names):
        # Git blobs include symlink targets, not content outside the repository.
        data = git(repo, 'show', 'HEAD:' + name)
        files[name] = hashlib.sha256(data).hexdigest()
    return {'version': 1, 'subject': 'jstack',
            'commit': git(repo, 'rev-parse', 'HEAD').decode().strip(),
            'tree': git(repo, 'rev-parse', 'HEAD^{tree}').decode().strip(),
            'files_sha256': files}


def verify(repo, lock):
    if snapshot(repo) != lock:
        raise ValueError('Subject does not match the pinned commit and files')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    pin = sub.add_parser('pin')
    pin.add_argument('--repo', required=True)
    pin.add_argument('--output', required=True)
    check = sub.add_parser('verify')
    check.add_argument('--repo', required=True)
    check.add_argument('--lock', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'pin':
            data = snapshot(args.repo)
            # Refuse accidental overwrites; intentional re-pinning uses a new file.
            with Path(args.output).open('x') as stream:
                json.dump(data, stream, indent=2, sort_keys=True)
                stream.write('\n')
            print('Pinned jstack', data['commit'])
        else:
            verify(args.repo, json.loads(Path(args.lock).read_text()))
            print('Verified pinned subject')
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
