#!/usr/bin/env python3
from __future__ import annotations

import argparse
from bisect import bisect_right
from dataclasses import dataclass
import os
from pathlib import Path
import posixpath
import re
import subprocess
import sys


@dataclass(frozen=True)
class Violation:
    file_path: str
    line_number: int
    offending_reference: str
    message: str
    guidance: str

    def format(self) -> str:
        return (
            f"{self.file_path}:{self.line_number}: {self.offending_reference!r}: "
            f"{self.message}; {self.guidance}"
        )


@dataclass(frozen=True)
class Word:
    value: str
    start: int
    end: int
    braced: bool = False


TCL_VARIABLES = {
    "SCRIPT_DIR", "PDK", "PDK_ROOT", "IO_LIBRARY_PATH", "netlist_dir",
    "env(PDK)", "env(PDK_ROOT)",
}
TARGET_EXTENSIONS = (".sch", ".sym", ".spice", ".cir")
FILE_ATTRS = {"schematic", "model", "file", "stimulus", "spice_file"}
VARIABLE = re.compile(r"\$(?:\{([^}]+)\}|([:\w]+(?:\([^)]*\))?))")


def _group_end(text: str, start: int) -> int:
    opening = text[start]
    closing = {"{": "}", "[": "]", '"': '"', "'": "'"}[opening]
    depth = 1
    pos = start + 1
    while pos < len(text):
        char = text[pos]
        if char == "\\" and pos + 1 < len(text):
            pos += 2
            continue
        if char == closing:
            depth -= 1
            if depth == 0:
                return pos + 1
        elif char == opening and opening in "{[":
            depth += 1
        pos += 1
    raise ValueError(f"unclosed {opening!r} delimiter")


def _word(text: str, pos: int) -> Word:
    start = pos
    if text[pos] in "{\"'":
        end = _group_end(text, pos)
        return Word(text[pos + 1:end - 1], pos + 1, end, text[pos] == "{")
    while pos < len(text) and not text[pos].isspace() and text[pos] != ";":
        if text[pos] == "[":
            pos = _group_end(text, pos)
        elif text[pos] == "\\" and pos + 1 < len(text) and text[pos + 1].isspace():
            pos += 2
        else:
            pos += 1
    return Word(text[start:pos], start, pos)


def _commands(text: str) -> list[list[Word]]:
    commands: list[list[Word]] = []
    words: list[Word] = []
    pos = 0
    while pos < len(text):
        if text[pos] in ";\n":
            if words:
                commands.append(words)
                words = []
            pos += 1
        elif text[pos].isspace():
            pos += 1
        elif not words and text[pos] == "#":
            end = text.find("\n", pos)
            pos = len(text) if end < 0 else end
        else:
            token = _word(text, pos)
            words.append(token)
            pos = token.end
    if words:
        commands.append(words)
    return commands


def _path_issue(ref: str, file_path: str, line: int, tcl: bool) -> Violation | None:
    ref = ref.strip().strip("\"'")

    def issue(message: str, guidance: str = "use a library-relative name or an approved Tcl root") -> Violation:
        return Violation(file_path, line, ref, message, guidance)

    if not ref:
        return None
    if tcl and "[" in ref:
        if not (ref.startswith("[") and _group_end(ref, 0) == len(ref)):
            return issue("unsupported Tcl bracket expression in path", "use a direct approved-variable path")
        commands = _commands(ref[1:-1])
        if len(commands) != 1 or [w.value for w in commands[0][:2]] != ["file", "join"]:
            return issue("unsupported Tcl bracket expression in path", "use a direct approved-variable path")
        parts = commands[0][2:]
        if not parts or any("[" in part.value for part in parts):
            return issue("unsupported Tcl file join expression", "use a direct approved-variable path")
        for idx, part in enumerate(parts):
            if part.value.startswith(("/", "\\", "~")) or re.match(r"^[A-Za-z]:", part.value):
                found = _path_issue(part.value, file_path, line, not part.braced)
                if found:
                    return found
            elif part.value.startswith("$"):
                matches = list(VARIABLE.finditer(part.value))
                for match in matches:
                    name = match[1] or match[2]
                    if name not in TCL_VARIABLES:
                        return issue(f"undeclared variable '${name}' in path operand")
                    if idx == 0 and name in {"PDK", "env(PDK)"}:
                        return issue("PDK is a suffix component, not a filesystem root", "use $PDK_ROOT/$PDK/... in Tcl/tcleval")
        return _path_issue("/".join(part.value for part in parts), file_path, line, True)
    obsolete = re.search(r"IHP-Open-PDK/.*/libs\.ref/sg13g2_io/xschem/([^/]+)$", ref)
    if obsolete:
        return issue("obsolete PDK IO library prefix", f"use bare IO symbol name {obsolete[1]!r}")
    if re.match(r"^[A-Za-z]:", ref):
        return issue("Windows drive path is not portable")
    if ref.startswith(("\\", "//")):
        return issue("UNC or Windows rooted path is not portable")
    if ref.startswith("/") or ref.lower().startswith("file:"):
        return issue("literal absolute POSIX path is not portable")
    if ref.startswith("~"):
        return issue("tilde expansion depends on the user's environment")
    matches = list(VARIABLE.finditer(ref))
    if "$" in VARIABLE.sub("", ref):
        return issue("unsupported variable syntax in path operand")
    for match in matches:
        name = match[1] or match[2]
        if not tcl:
            return issue(f"variable '${name}' used outside Tcl/tcleval interpolation")
        if name not in TCL_VARIABLES:
            return issue(f"undeclared variable '${name}' in path operand")
    root_match = VARIABLE.match(ref)
    if root_match and (root_match[1] or root_match[2]) in {"PDK", "env(PDK)"}:
        return issue("PDK is a suffix component, not a filesystem root", "use $PDK_ROOT/$PDK/... in Tcl/tcleval")
    path = ref.replace("\\", "/")
    if root_match:
        relative = path[root_match.end():].lstrip("/")
        normalized = posixpath.normpath(relative)
        boundary = "variable root"
    else:
        normalized = posixpath.normpath(posixpath.join(posixpath.dirname(file_path), path))
        boundary = "repository root"
    if normalized == ".." or normalized.startswith("../"):
        return issue(f"relative path traverses outside {boundary}")
    return None


def _scan_tcl(text: str, file_path: str, base_line: int) -> list[Violation]:
    violations: list[Violation] = []
    for words in _commands(text):
        values = [word.value for word in words]
        operand = None
        if values[:2] == ["xschem", "raw_read"] and len(words) >= 3:
            operand = words[2]
        elif values[0] == "source":
            index = 3 if values[1:2] == ["-encoding"] else 1
            if index < len(words):
                operand = words[index]
        elif values[0] == "load":
            index = 1
            while index < len(words) and words[index].value.startswith("-"):
                index += 1
            if index < len(words):
                operand = words[index]
        if operand:
            line = base_line + text.count("\n", 0, operand.start)
            found = _path_issue(operand.value, file_path, line, not operand.braced)
            if found:
                violations.append(found)
    return violations


def _scan_spice(text: str, file_path: str, base_line: int, tcl: bool) -> list[Violation]:
    violations: list[Violation] = []
    raw_lines = text.splitlines()
    logical_lines: list[tuple[int, str]] = []
    for offset, raw_line in enumerate(raw_lines):
        line_no = base_line + offset
        stripped = raw_line.strip()
        if not stripped or stripped.startswith(("*", "$ ", ";", "//")):
            continue
        if stripped.startswith("+") and logical_lines:
            prev_line_no, prev_text = logical_lines[-1]
            logical_lines[-1] = (prev_line_no, prev_text + " " + stripped[1:].strip())
        else:
            logical_lines.append((line_no, stripped))

    for number, stripped in logical_lines:
        pos = 0
        words: list[Word] = []
        while pos < len(stripped):
            if stripped[pos].isspace():
                pos += 1
                continue
            if stripped[pos] == ";" or stripped[pos:pos + 2] == "$ ":
                break
            token = _word(stripped, pos)
            words.append(token)
            pos = token.end
        if not words:
            continue
        if words and words[0].value.lower() == "inline":
            words = words[1:]
        if not words:
            continue
        command = words[0].value.lower()
        operands: list[Word] = []
        if command in {".include", ".inc", "write", "wrdata"}:
            operands = words[1:2]
        elif command == ".lib":
            if len(words) >= 3 or (len(words) == 2 and re.search(r"[/\\~$:]", words[1].value)):
                operands = words[1:2]
        elif command in {"source", "load"}:
            operands = words[1:]
        for operand in operands:
            found = _path_issue(operand.value, file_path, number, tcl)
            if found:
                violations.append(found)
    return violations


def _attribute_word(text: str, pos: int) -> Word:
    if text[pos] != '"':
        return _word(text, pos)
    start = pos + 1
    pos = start
    while pos < len(text):
        if text[pos] == "\\" and pos + 1 < len(text):
            pos += 2
            continue
        if text[pos] == '"':
            remaining = text[pos + 1:].lstrip()
            if not remaining or re.match(r"\w+\s*=", remaining):
                return Word(text[start:pos], start, pos + 1)
        pos += 1
    raise ValueError("unclosed quoted attribute")


def _attributes(text: str) -> dict[str, Word]:
    attrs: dict[str, Word] = {}
    pos = 0
    while pos < len(text):
        if text[pos].isspace() or text[pos] == ";":
            pos += 1
            continue
        match = re.match(r"([\w]+)\s*=\s*", text[pos:])
        if not match:
            pos = _word(text, pos).end
            continue
        key = match[1].lower()
        pos += match.end()
        if pos >= len(text):
            break
        token = _attribute_word(text, pos)
        value = token.value.replace('\\"', '"').replace("\\{", "{").replace("\\}", "}")
        attrs[key] = Word(value, token.start, token.end, token.braced)
        pos = token.end
    return attrs


def _scan_attrs(text: str, file_path: str, base_line: int, parent_tcl: bool = False, template: bool = False) -> list[Violation]:
    violations: list[Violation] = []
    attrs = _attributes(text)
    format_word = attrs.get("format")
    if format_word:
        tcl = bool(re.search(r"\btcleval\s*\(", format_word.value))
    else:
        tcl = parent_tcl
    for key, token in attrs.items():
        line = base_line + text.count("\n", 0, token.start)
        if key in FILE_ATTRS:
            found = _path_issue(token.value, file_path, line, False)
            if found:
                violations.append(found)
        elif key == "tclcommand":
            violations.extend(_scan_tcl(token.value, file_path, line))
        elif key in {"value", "code"}:
            violations.extend(_scan_spice(token.value, file_path, line, tcl))
        elif key == "format":
            val = token.value
            m_eval = re.search(r"\btcleval\s*\((.*)\)\s*$", val, re.DOTALL)
            if m_eval:
                val = m_eval.group(1)
            violations.extend(_scan_spice(val, file_path, line, tcl))
        elif key == "template" and not template:
            violations.extend(_scan_attrs(token.value, file_path, line, parent_tcl=tcl, template=True))
    return violations


def parse_content(content: str, file_rel_path: str) -> list[Violation]:
    violations: list[Violation] = []
    pos = 0
    try:
        if Path(file_rel_path).suffix.lower() in {".spice", ".cir"}:
            return _scan_spice(content, file_rel_path, 1, False)
        offsets = [0] + [match.end() for match in re.finditer("\n", content)]
        while pos < len(content):
            if content[pos].isspace():
                pos += 1
                continue
            start = pos
            record = content[pos]
            pos += 1
            words: list[Word] = []
            while pos < len(content) and content[pos] != "\n":
                if content[pos].isspace() or content[pos] == ";":
                    pos += 1
                    continue
                token = _word(content, pos)
                words.append(token)
                pos = token.end
            line = bisect_right(offsets, start)
            if record == "C":
                if len(words) != 6 or not words[0].braced or not words[-1].braced:
                    raise ValueError("malformed component record: expected symbol, four coordinates and attributes")
                found = _path_issue(words[0].value, file_rel_path, line, False)
                if found:
                    violations.append(found)
                attrs = words[-1]
                violations.extend(_scan_attrs(attrs.value, file_rel_path, bisect_right(offsets, attrs.start)))
            elif record == "K" and words:
                violations.extend(_scan_attrs(words[0].value, file_rel_path, bisect_right(offsets, words[0].start)))
            elif record in {"S", "V", "E", "G"} and words:
                violations.extend(_scan_spice(words[0].value, file_rel_path, bisect_right(offsets, words[0].start), False))
    except ValueError as error:
        violations.append(Violation(
            file_rel_path, content.count("\n", 0, pos) + 1, "",
            f"cannot statically parse source: {error}", "use well-formed literal or approved-variable path syntax",
        ))
    return violations


def _git_run(args: list[str], repo_root: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git"] + args, cwd=repo_root, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True,
    )


def _get_staged_paths(repo_root: Path) -> list[str]:
    output = _git_run(["diff", "--cached", "--name-status", "-z"], repo_root).stdout
    tokens = [os.fsdecode(token) for token in output.split(b"\0") if token]
    paths: list[str] = []
    pos = 0
    while pos < len(tokens):
        status = tokens[pos][0]
        pos += 1
        if status in {"R", "C"}:
            pos += 1
        path = tokens[pos]
        pos += 1
        if status != "D":
            paths.append(path)
    return paths


def run_checker(staged: bool, repo_root_arg: str | None) -> tuple[int, list[Violation], int]:
    violations: list[Violation] = []
    checked = 0
    try:
        root = Path(repo_root_arg) if repo_root_arg else Path(os.fsdecode(
            _git_run(["rev-parse", "--show-toplevel"], Path.cwd()).stdout
        ).strip())
        root = root.resolve()
        entries = _git_run(["ls-files", "--stage", "-z"], root).stdout
        candidates = set(_get_staged_paths(root)) if staged else None
        seen: set[str] = set()
        for entry in entries.split(b"\0"):
            if not entry:
                continue
            header, raw_path = entry.split(b"\t", 1)
            mode, oid, stage = header.decode("ascii").split()
            path = os.fsdecode(raw_path)
            if mode == "160000" or not path.lower().endswith(TARGET_EXTENSIONS):
                continue
            if path in seen or (candidates is not None and path not in candidates):
                continue
            seen.add(path)
            if stage != "0":
                violations.append(Violation(path, 1, path, "unmerged source file in index", "resolve merge conflict"))
                continue
            if mode == "120000":
                violations.append(Violation(path, 1, path, "symlink .sch/.sym source not allowed", "use a regular source file"))
                continue
            if staged:
                content = _git_run(["cat-file", "blob", oid], root).stdout.decode("utf-8")
            else:
                full = root / path
                if full.is_symlink() or any(parent.is_symlink() for parent in full.parents if parent != root and root in parent.parents):
                    violations.append(Violation(path, 1, path, "working-tree source traverses symlink", "use a regular source file"))
                    continue
                if not full.is_file():
                    violations.append(Violation(path, 1, path, "tracked source missing from working tree", "restore it or stage its deletion"))
                    continue
                content = full.read_text(encoding="utf-8")
            checked += 1
            violations.extend(parse_content(content, path))
    except (OSError, subprocess.CalledProcessError, UnicodeError, ValueError, IndexError) as error:
        violations.append(Violation("git", 1, "", f"path check failed: {error}", "fix the read/index error and retry"))
    return int(bool(violations)), violations, checked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Statically check tracked Xschem and SPICE path references")
    parser.add_argument("--staged", action="store_true", help="check changed index blobs, not working-tree files")
    parser.add_argument("--repo-root", help="repository to inspect (defaults to current repository)")
    args = parser.parse_args(argv)
    code, violations, count = run_checker(args.staged, args.repo_root)
    for violation in violations:
        print(violation.format(), file=sys.stderr)
    if violations:
        print(f"Checked {count} file(s). Found {len(violations)} path portability violation(s).", file=sys.stderr)
    else:
        print(f"Checked {count} file(s). 0 path portability violations found.")
    return code


if __name__ == "__main__":
    sys.exit(main())
