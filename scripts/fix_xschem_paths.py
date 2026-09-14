#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

SOURCE_EXTENSIONS = {".sch", ".sym"}
COMPONENT = re.compile(r"^(C\s*\{)([^}]+)(\}\s+.*)$")


def git(repo_root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=repo_root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def portable_symbol(reference: str) -> str:
    value = reference.strip()
    obsolete = re.search(r"IHP-Open-PDK/.*/libs\.ref/sg13g2_io/xschem/([^/]+)$", value)
    if obsolete:
        return obsolete.group(1)
    if not (value.startswith(("/", "\\", "~")) or re.match(r"^[A-Za-z]:", value)):
        return value
    normalized = value.replace("\\", "/")
    for prefix in ("sg13g2_pr/", "devices/"):
        index = normalized.rfind(prefix)
        if index >= 0:
            return normalized[index:]
    return Path(normalized).name


def fix_content(content: str) -> str:
    fixed: list[str] = []
    for line in content.splitlines(keepends=True):
        match = COMPONENT.match(line)
        if match:
            line = f"{match.group(1)}{portable_symbol(match.group(2))}{match.group(3)}"
        fixed.append(line)
    return "".join(fixed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize staged Xschem component references")
    parser.add_argument("--staged", action="store_true", required=True)
    parser.parse_args(argv)
    repo_root = Path(os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel")).strip()).resolve()

    changed = 0
    output = git(repo_root, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    for raw_path in output.split(b"\0"):
        if not raw_path:
            continue
        path = os.fsdecode(raw_path)
        if Path(path).suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        content = git(repo_root, "show", f":{path}").decode("utf-8")
        fixed = fix_content(content)
        if fixed == content:
            continue
        (repo_root / path).write_text(fixed, encoding="utf-8")
        git(repo_root, "add", path)
        changed += 1

    if changed:
        print(f"Normalized Xschem component paths in {changed} staged file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
