#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

FORWARDING_HOOK = '#!/bin/sh\nset -eu\nroot="$(git rev-parse --show-toplevel)"\nexec sh "$root/.githooks/pre-commit"\n'
MANUAL_CHAIN = 'sh "$(git rev-parse --show-toplevel)/.githooks/pre-commit" || exit $?'

KNOWN_OLD_HOOKS = [
    b'#!/bin/sh\nroot="$(git rev-parse --show-toplevel)"\nexec python3 "$root/scripts/fix_xschem_paths.py" --staged\n',
    b'#!/bin/sh\nroot="$(git rev-parse --show-toplevel)"\npython3 "$root/scripts/fix_xschem_paths.py" --staged\n',
    b'#!/bin/sh\r\nroot="$(git rev-parse --show-toplevel)"\r\nexec python3 "$root/scripts/fix_xschem_paths.py" --staged\r\n',
    b'#!/bin/sh\r\nroot="$(git rev-parse --show-toplevel)"\r\npython3 "$root/scripts/fix_xschem_paths.py" --staged\r\n',
    b'#!/bin/sh\nroot="$(git rev-parse --show-toplevel)"\nexec sh "$root/.githooks/pre-commit"\n',
]


def install_hooks(repo_root: Path) -> int:
    src_hook = repo_root / ".githooks" / "pre-commit"
    if src_hook.is_symlink() or not src_hook.is_file():
        print(f"error: tracked hook is missing or not a regular file: {src_hook}", file=sys.stderr)
        return 1
    if not os.access(src_hook, os.X_OK):
        print(f"error: {src_hook} is not executable", file=sys.stderr)
        return 1
    try:
        proc_hp = subprocess.run(
            ["git", "config", "core.hooksPath"],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"error: git config query failed: {exc}", file=sys.stderr)
        return 1
    if proc_hp.returncode not in (0, 1):
        print(f"error: git config exited {proc_hp.returncode}: {proc_hp.stderr.strip()}", file=sys.stderr)
        return 1
    if proc_hp.returncode == 0 and proc_hp.stdout.strip():
        hooks_path_val = proc_hp.stdout.strip()
        configured = Path(hooks_path_val)
        if not configured.is_absolute():
            configured = repo_root / configured
        project_githooks = repo_root / ".githooks"
        if configured == project_githooks and not configured.is_symlink():
            print(f"core.hooksPath already points to {project_githooks}; nothing to do.")
            return 0
        print(
            f"error: core.hooksPath is set to {hooks_path_val!r} (not .githooks).\n"
            "Will not install into a foreign hooks directory.\n"
            "Add the following to your existing hook to stop the commit if the project hook fails:\n"
            f"  {MANUAL_CHAIN}",
            file=sys.stderr,
        )
        return 1
    try:
        proc_gp = subprocess.run(
            ["git", "rev-parse", "--git-path", "hooks"],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        hooks_path_out = proc_gp.stdout.strip()
        if hooks_path_out:
            path = Path(hooks_path_out)
            hooks_dir = path if path.is_absolute() else repo_root / path
        else:
            hooks_dir = None
    except (subprocess.CalledProcessError, FileNotFoundError):
        hooks_dir = None
    if hooks_dir is None:
        print("error: cannot determine git hooks directory", file=sys.stderr)
        return 1
    if hooks_dir.is_symlink():
        print(f"error: hooks directory is a symlink: {hooks_dir}", file=sys.stderr)
        return 1
    try:
        hooks_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot create hooks directory {hooks_dir}: {exc}", file=sys.stderr)
        return 1
    target = hooks_dir / "pre-commit"
    forwarding = FORWARDING_HOOK.encode()
    if target.is_symlink():
        print(
            f"error: {target} is a symlink; will not overwrite.\n"
            "Add the following to your existing hook to stop the commit if the project hook fails:\n"
            f"  {MANUAL_CHAIN}",
            file=sys.stderr,
        )
        return 1
    if target.exists():
        if not target.is_file():
            print(f"error: {target} is not a regular file", file=sys.stderr)
            return 1
        existing = target.read_bytes()
        if existing == forwarding:
            if not os.access(target, os.X_OK):
                target.chmod(target.stat().st_mode | 0o755)
            print(f"Hook already installed at {target}.")
            return 0
        if existing in KNOWN_OLD_HOOKS:
            try:
                target.write_bytes(forwarding)
                target.chmod(target.stat().st_mode | 0o755)
            except OSError as exc:
                print(f"error: cannot update hook at {target}: {exc}", file=sys.stderr)
                return 1
            print(f"Hook updated at {target}.")
            return 0
        print(
            f"error: unrecognized hook at {target}; will not overwrite.\n"
            "Add the following to your existing hook to stop the commit if the project hook fails:\n"
            f"  {MANUAL_CHAIN}",
            file=sys.stderr,
        )
        return 1
    target.write_bytes(forwarding)
    target.chmod(target.stat().st_mode | 0o755)
    print(f"Hook installed at {target}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv:
        print(f"usage: {Path(__file__).name}", file=sys.stderr)
        return 2
    try:
        toplevel = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return install_hooks(Path(toplevel))


if __name__ == "__main__":
    sys.exit(main())
