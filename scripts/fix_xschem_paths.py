#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import posixpath
import re
import stat
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

SOURCE_EXTENSIONS = {".sch", ".sym", ".spice", ".cir"}
SPICE_EXTENSIONS = {".spice", ".cir"}
SPICE_METADATA_RE = re.compile(rb"^([ \t]*\*\*(?!\*)[ \t]*(sch_path|sym_path):[ \t]*)(.*?)(\r\n|[\r\n])?$")


def git(repo_root: Path, *args: str, data: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=repo_root, input=data, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def component_spans(content: bytes):
    depth = 0
    pos = 0
    line_start = True
    while pos < len(content):
        if depth == 0 and line_start:
            match = re.match(rb"[ \t]*C\s+\{", content[pos:])
            if match:
                start = pos + match.end()
                end = start
                nested = 1
                while end < len(content):
                    char = content[end]
                    if char == 92 and end + 1 < len(content) and content[end + 1] in (123, 125):
                        end += 2
                        continue
                    if char == 123:
                        nested += 1
                    elif char == 125:
                        nested -= 1
                        if not nested:
                            break
                    end += 1
                if nested:
                    raise ValueError("unterminated component symbol path")
                yield start, end
                pos = end + 1
                line_start = False
                continue
        char = content[pos]
        if char == 92 and pos + 1 < len(content):
            pos += 2
            line_start = False
            continue
        if char == 123:
            depth += 1
        elif char == 125:
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced braces")
        line_start = char == 10
        pos += 1
    if depth:
        raise ValueError("unbalanced braces")


def regular_path(root: Path, relative: str) -> bool:
    current = root
    parts = Path(relative).parts
    if not parts or Path(relative).is_absolute() or ".." in parts:
        return False
    for index, part in enumerate(parts):
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError:
            return False
        if index == len(parts) - 1:
            return stat.S_ISREG(mode)
        if not stat.S_ISDIR(mode):
            return False
    return False


def file_uri_path(reference: str) -> str:
    if not reference.lower().startswith("file:///"):
        raise ValueError(f"unsupported file URI symbol reference {reference!r}")
    parsed = urlsplit(reference)
    if parsed.scheme.lower() != "file" or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError(f"unsupported file URI symbol reference {reference!r}")
    path = unquote(parsed.path)
    if not path or path.startswith("//") or any(char in path for char in "\r\n"):
        raise ValueError(f"unsupported file URI symbol reference {reference!r}")
    return path


def resolve_symbol(reference: str, source: str, root: Path,
                   entries: dict, libraries: list[Path],
                   check_worktree: bool = False) -> str:
    file_uri = reference.lower().startswith("file:")
    without_scheme = file_uri_path(reference) if file_uri else reference
    normalized = without_scheme.replace("\\", "/")
    obsolete = re.search(r"IHP-Open-PDK/.*/libs\.ref/sg13g2_io/xschem/(.+)$", normalized)
    if not (normalized.startswith(("/", "~")) or re.match(r"^[A-Za-z]:", normalized) is not None
            or file_uri or obsolete):
        return reference
    if normalized.startswith("~"):
        raise ValueError(f"unresolved literal tilde symbol reference {reference!r}")
    if file_uri and not obsolete and not (normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized)):
        stripped = without_scheme.replace("\\", "/")
        if not (stripped.startswith(("/", "~")) or re.match(r"^[A-Za-z]:", stripped)):
            return stripped
    symbols = {p for p, (mode, oid, stage) in entries.items()
               if mode in ("100644", "100755") and stage == "0" and p.endswith(".sym")}
    candidates = {}
    local_cand = None

    def local_candidate(relative):
        portable = posixpath.relpath(relative, posixpath.dirname(source) or ".")
        norm = posixpath.normpath(portable)
        contained = not (norm == ".." or norm.startswith("../")
                         or posixpath.isabs(norm) or re.match(r"^[A-Za-z]:", norm) is not None)
        if contained:
            for library in libraries:
                target = Path(os.path.abspath(library / norm))
                try:
                    local_target = target.relative_to(root).as_posix()
                except ValueError:
                    local_target = None
                if local_target is not None:
                    exists = local_target in entries or (check_worktree and (target.exists() or target.is_symlink()))
                else:
                    exists = regular_path(library, norm) or (check_worktree and (target.exists() or target.is_symlink()))
                if target.resolve() != (root / relative).resolve() and exists:
                    raise ValueError(f"ambiguous symbol reference {reference!r}")
        if check_worktree:
            local_shadow = root / (posixpath.dirname(source) or ".") / posixpath.basename(relative)
            is_same = False
            try:
                is_same = local_shadow.resolve() == (root / relative).resolve()
            except OSError:
                is_same = False
            if not is_same and (local_shadow.exists() or local_shadow.is_symlink()):
                raise ValueError(f"ambiguous symbol reference {reference!r}")
        return portable

    prefix = root.as_posix() + "/"
    if normalized.startswith(prefix):
        relative = normalized[len(prefix):]
        if relative in symbols:
            if check_worktree:
                target_dest = root / relative
                if target_dest.is_symlink() or not regular_path(root, relative):
                    raise ValueError(f"{relative!r}: missing or non-regular worktree symbol")
            local_cand = local_candidate(relative)
            candidates[local_cand] = (root / relative).resolve()
    for library in libraries:
        library_prefix = library.as_posix() + "/"
        relative = None
        if normalized.startswith(library_prefix):
            relative = normalized[len(library_prefix):]
        elif obsolete and library.name == "xschem" and library.parent.name == "sg13g2_io":
            relative = obsolete[1]
        if not relative:
            continue
        try:
            repo_relative = (library / relative).relative_to(root).as_posix()
        except ValueError:
            repo_relative = None
        if repo_relative is not None and repo_relative not in symbols:
            continue
        if repo_relative is None and not regular_path(library, relative):
            continue
        local = posixpath.normpath(posixpath.join(posixpath.dirname(source), relative))
        target_path = (library / relative).resolve()
        local_path = (root / local).resolve()
        if (local in symbols or (check_worktree and ((root / local).exists() or (root / local).is_symlink()))) and local_path != target_path:
            raise ValueError(f"ambiguous symbol reference {reference!r}")
        destinations = set()
        for search_root in libraries:
            target = search_root / relative
            try:
                tracked = target.relative_to(root).as_posix()
            except ValueError:
                tracked = None
            if tracked is not None:
                if tracked in entries:
                    destinations.add(str(target.resolve()))
            elif regular_path(search_root, relative):
                destinations.add(str(target.resolve()))
        if len(destinations) != 1:
            raise ValueError(f"ambiguous symbol reference {reference!r}")
        candidates[relative] = target_path

    if len(candidates) > 1 and len(set(candidates.values())) == 1:
        non_local = [c for c in candidates if local_cand is None or c != local_cand]
        if len(non_local) == 1:
            candidates = {non_local[0]: list(candidates.values())[0]}
    if len(candidates) == 1:
        result = next(iter(candidates))
        if any(char in result for char in "{}\\\r\n"):
            raise ValueError(f"unsupported symbol filename {reference!r}")
        return result
    same_name = sorted(p for p in symbols if posixpath.basename(p) == posixpath.basename(normalized))
    if len(candidates) > 1 or len(same_name) > 1:
        reason = "ambiguous"
    else:
        reason = "unresolved"
    message = f"{reason} symbol reference {reference!r}; supply an exact tracked path or --library-root"
    if reason == "unresolved" and len(same_name) == 1:
        message += f"; did you mean {same_name[0]!r}?"
    raise ValueError(message)


def resolve_metadata(reference: str, kind: str, root: Path, entries: dict) -> str:
    quoted = len(reference) >= 2 and reference[0] == reference[-1] and reference[0] in ('"', "'")
    unquoted = reference[1:-1] if quoted else reference
    if not unquoted or unquoted.startswith("$SCRIPT_DIR/"):
        return reference
    if unquoted.lower().startswith("file:"):
        try:
            without_scheme = file_uri_path(unquoted)
        except ValueError as error:
            if any(char in unquote(unquoted) for char in "\r\n"):
                raise ValueError(f"unsupported metadata path {unquoted!r}") from error
            return reference
    else:
        without_scheme = unquoted
    if any(char in without_scheme for char in "\r\n"):
        raise ValueError(f"unsupported metadata path {unquoted!r}")
    normalized = without_scheme.replace("\\", "/")
    expected_ext = ".sch" if kind == "sch_path" else ".sym"
    targets = {p for p, (mode, oid, stage) in entries.items()
               if mode in ("100644", "100755") and stage == "0" and p.endswith(expected_ext)}
    candidates = set()
    prefix = root.as_posix() + "/"
    if normalized.startswith(prefix):
        relative = normalized[len(prefix):]
        if relative in targets:
            candidates.add(relative)
    else:
        is_abs = (normalized.startswith(("/", "//")) or
                  re.match(r"^[A-Za-z]:", normalized) is not None)
        is_variable_or_rel = (without_scheme.startswith(("$", "~", "[")) or not is_abs)
        if is_abs and not is_variable_or_rel:
            marker = f"/{root.name}/"
            search_str = normalized if normalized.startswith("/") else f"/{normalized}"
            pos = 0
            while True:
                idx = search_str.find(marker, pos)
                if idx < 0:
                    break
                suffix = search_str[idx + len(marker):]
                if suffix in targets:
                    candidates.add(suffix)
                pos = idx + 1
    if len(candidates) > 1:
        raise ValueError(f"ambiguous metadata path {unquoted!r}")
    if len(candidates) == 1:
        target = candidates.pop()
        if any(char in target for char in "\r\n"):
            raise ValueError(f"unsupported metadata path {unquoted!r}")
        fixed = f"$SCRIPT_DIR/{target}"
        if any(char in fixed for char in "\r\n"):
            raise ValueError(f"unsupported metadata path {unquoted!r}")
        return f'"{fixed}"' if quoted else fixed
    return reference


def fix_spice_content(content: bytes, root: Path, entries: dict) -> bytes:
    lines = content.splitlines(keepends=True)
    result = []
    for line in lines:
        match = SPICE_METADATA_RE.match(line)
        if match:
            prefix, kind_bytes, raw_val, ending = match.groups()
            trimmed_val = raw_val.rstrip(b" \t")
            trailing_ws = raw_val[len(trimmed_val):]
            reference = os.fsdecode(trimmed_val)
            fixed = resolve_metadata(reference, kind_bytes.decode("ascii"), root, entries)
            if fixed != reference:
                if any(char in fixed for char in "\r\n"):
                    raise ValueError(f"unsupported metadata path {reference!r}")
                line = prefix + os.fsencode(fixed) + trailing_ws + (ending or b"")
        result.append(line)
    return b"".join(result)


def fix_xschem_content(content: bytes, source: str, root: Path, entries: dict,
                       libraries: list[Path], check_worktree: bool = False) -> bytes:
    replacements = []
    for start, end in component_spans(content):
        span = content[start:end]
        trimmed = span.strip()
        reference = os.fsdecode(trimmed)
        fixed = resolve_symbol(reference, source, root, entries, libraries, check_worktree)
        if fixed != reference:
            leading = len(span) - len(span.lstrip())
            replacements.append((start + leading, start + leading + len(trimmed), os.fsencode(fixed)))
    for start, end, replacement in reversed(replacements):
        content = content[:start] + replacement + content[end:]
    return content


def fix_content(content: bytes, source: str, root: Path, entries: dict,
                libraries: list[Path], check_worktree: bool = False) -> bytes:
    if Path(source).suffix.lower() in SPICE_EXTENSIONS:
        return fix_spice_content(content, root, entries)
    return fix_xschem_content(content, source, root, entries, libraries, check_worktree)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Safely normalize staged Xschem component paths")
    parser.add_argument("--staged", action="store_true", help="inspect the index (default)")
    parser.add_argument("--check", action="store_true", help="read-only; fail if fixes are needed")
    parser.add_argument("--all", action="store_true", help="scan all index sources; requires --check")
    parser.add_argument("--library-root", action="append", default=[], metavar="PATH",
                        help="explicit installed Xschem search root (repeatable)")
    args = parser.parse_args(argv)
    if args.all and not args.check:
        parser.error("--all requires --check")
    try:
        root = Path(os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel").rstrip(b"\n")))
        libraries = []
        for value in args.library_root:
            library = Path(os.path.abspath(value))
            if library.resolve() != library or not library.is_dir():
                raise ValueError(f"library root must be an existing non-symlink directory: {value!r}")
            libraries.append(library)
        entries = {}
        for record in git(root, "ls-files", "--stage", "-z").split(b"\0"):
            if not record:
                continue
            metadata, raw_path = record.split(b"\t", 1)
            mode, oid, stage = metadata.decode("ascii").split()
            path = os.fsdecode(raw_path)
            if stage != "0" and Path(path).suffix.lower() in SOURCE_EXTENSIONS:
                raise ValueError(f"{path!r}: unmerged Xschem source")
            entries[path] = (mode, oid, stage)
        paths = (b"\0".join(os.fsencode(path) for path in entries) if args.all else
                 git(root, "diff", "--cached", "--name-only", "--no-renames", "--diff-filter=ACMT", "-z"))
        plans = []
        snapshots = {}
        original_index_entries = bytearray()
        for raw_path in paths.split(b"\0"):
            if not raw_path:
                continue
            path = os.fsdecode(raw_path)
            if Path(path).suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            mode, oid, stage = entries[path]
            if mode not in ("100644", "100755") or stage != "0":
                raise ValueError(f"{path!r}: source is not a regular staged file")
            content = git(root, "cat-file", "blob", oid)
            try:
                fixed = fix_content(content, path, root, entries, libraries, check_worktree=not args.check)
            except ValueError as error:
                raise ValueError(f"{path!r}: {error}") from error
            if fixed == content:
                continue
            if args.check:
                plans.append((path, mode, fixed))
                continue
            full_path = root / path
            if not regular_path(root, path):
                raise ValueError(f"{path!r}: missing or non-regular worktree source")
            st = full_path.lstat()
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
                raise ValueError(f"{path!r}: missing or non-regular worktree source")
            work_mode = "100755" if st.st_mode & 0o111 else "100644"
            cur_bytes = full_path.read_bytes()
            if cur_bytes != content or work_mode != mode:
                raise ValueError(f"{path!r}: unstaged content or mode changes; refusing to overwrite")
            snapshots[path] = (cur_bytes, st.st_mode)
            original_index_entries.extend(mode.encode() + b" " + oid.encode() + b"\t" + os.fsencode(path) + b"\0")
            plans.append((path, mode, fixed))
        if args.check:
            for path, mode, fixed in plans:
                print(f"Needs fix: {path!r}")
            return int(bool(plans))
        if not plans:
            return 0
        updates = bytearray()
        for path, mode, fixed in plans:
            oid = git(root, "hash-object", "-w", "--stdin", data=fixed).strip()
            updates.extend(mode.encode() + b" " + oid + b"\t" + os.fsencode(path) + b"\0")
        index_updated = False
        written_paths = []
        try:
            if updates:
                git(root, "update-index", "-z", "--index-info", data=bytes(updates))
                index_updated = True
            for path, mode, fixed in plans:
                full_path = root / path
                if not regular_path(root, path):
                    raise ValueError(f"{path!r}: worktree file changed during write")
                st = full_path.lstat()
                if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
                    raise ValueError(f"{path!r}: worktree file changed to non-regular during write")
                work_mode = "100755" if st.st_mode & 0o111 else "100644"
                orig_bytes, orig_mode = snapshots[path]
                cur_bytes = full_path.read_bytes()
                if cur_bytes != orig_bytes or work_mode != mode:
                    raise ValueError(f"{path!r}: worktree content or mode modified during write")
                tmp = tempfile.NamedTemporaryFile(dir=full_path.parent, prefix=".tmp_fix_", delete=False)
                tmp_path = Path(tmp.name)
                try:
                    tmp.write(fixed)
                    tmp.flush()
                    os.fsync(tmp.fileno())
                    tmp.close()
                    os.chmod(tmp_path, stat.S_IMODE(orig_mode))
                    pre_st = full_path.lstat()
                    if stat.S_ISLNK(pre_st.st_mode) or not stat.S_ISREG(pre_st.st_mode) or not regular_path(root, path):
                        raise ValueError(f"{path!r}: worktree file changed before replacement")
                    os.replace(tmp_path, full_path)
                    written_paths.append(path)
                except Exception:
                    if tmp_path.exists():
                        try:
                            tmp_path.unlink()
                        except OSError:
                            pass
                    raise
        except Exception:
            for w_path in written_paths:
                try:
                    w_full = root / w_path
                    w_bytes, w_mode = snapshots[w_path]
                    w_tmp = tempfile.NamedTemporaryFile(dir=w_full.parent, prefix=".tmp_rollback_", delete=False)
                    w_tmp_path = Path(w_tmp.name)
                    w_tmp.write(w_bytes)
                    w_tmp.flush()
                    os.fsync(w_tmp.fileno())
                    w_tmp.close()
                    os.chmod(w_tmp_path, stat.S_IMODE(w_mode))
                    os.replace(w_tmp_path, w_full)
                except Exception:
                    pass
            if index_updated and original_index_entries:
                try:
                    git(root, "update-index", "-z", "--index-info", data=bytes(original_index_entries))
                except Exception:
                    pass
            raise
        for path, mode, fixed in plans:
            print(f"Fixed: {path!r}")
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Xschem path fixer: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
