import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fix_xschem_paths.py"
CHECKER = ROOT / "scripts" / "check_xschem_paths.py"
HOOK = ROOT / ".githooks" / "pre-commit"


class FixPathsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")

    def git(self, *args, data=None):
        return subprocess.run(["git", *args], cwd=self.root, input=data,
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def put(self, path, data, stage=True):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        if stage:
            self.git("add", "--", path)

    def run_fixer(self, *args, env=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root,
                              env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def absolute(self, name="part with space.sym"):
        return os.fsencode(self.root / name)

    def prepare(self):
        self.put("part with space.sym", b"v {}\n")
        original = b"C {" + self.absolute() + b"} 0 0 0 0 {name=x\r\nvalue={a b}}\r\n"
        self.put("main.sch", original)
        return original

    def test_initial_fix_crlf_and_index(self):
        original = self.prepare()
        result = self.run_fixer()
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = original.replace(self.absolute(), b"part with space.sym")
        self.assertEqual((self.root / "main.sch").read_bytes(), expected)
        self.assertEqual(self.git("show", ":main.sch"), expected)
        self.assertIn(b"main.sch", result.stdout)

    def test_portable_multiline_noop(self):
        data = b'C\r\n{devices/res.sym} 0 0 0 0 {\r\nC {/not/a/symbol.sym}\r\nvalue={nested}}\r\n'
        self.put("main.sch", data)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":main.sch"), data)
        self.assertEqual((self.root / "main.sch").read_bytes(), data)

    def test_check_readonly(self):
        original = self.prepare()
        self.assertEqual(self.run_fixer("--check").returncode, 1)
        self.assertEqual(self.git("show", ":main.sch"), original)
        self.assertEqual((self.root / "main.sch").read_bytes(), original)

    def test_partial_staging_preflight(self):
        original = self.prepare()
        self.put("z.sch", original)
        self.put("z.sch", original + b"\n", stage=False)
        result = self.run_fixer()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"unstaged", result.stderr)
        self.assertEqual((self.root / "main.sch").read_bytes(), original)
        self.assertEqual(self.git("show", ":z.sch"), original)
        self.assertEqual((self.root / "z.sch").read_bytes(), original + b"\n")

    def test_unknown_does_not_guess(self):
        original = b"C {/old/part.sym} 0 0 0 0 {}\n"
        self.put("main.sch", original)
        result = self.run_fixer("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"unresolved", result.stderr)
        self.assertEqual(self.git("show", ":main.sch"), original)

    def test_unknown_windows_drive_does_not_guess(self):
        original = b"C {C:\\old\\part.sym} 0 0 0 0 {}\n"
        self.put("main.sch", original)
        result = self.run_fixer()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"unresolved", result.stderr)

    def test_unknown_unc_does_not_guess(self):
        original = b"C {\\\\server\\share\\part.sym} 0 0 0 0 {}\n"
        self.put("main.sch", original)
        result = self.run_fixer()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"unresolved", result.stderr)

    def test_unique_tracked_target_is_hint_only(self):
        self.put("symbols/part.sym", b"v {}\n")
        original = b"C {/old/part.sym} 0 0 0 0 {}\n"
        self.put("main.sch", original)
        result = self.run_fixer("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"unresolved", result.stderr)
        self.assertIn(b"symbols/part.sym", result.stderr)

    def test_duplicate_symbols_are_ambiguous(self):
        self.put("a/part.sym", b"v {}\n")
        self.put("b/part.sym", b"v {}\n")
        self.put("main.sch", b"C {/old/part.sym} 0 0 0 0 {}\n")
        self.assertIn(b"ambiguous", self.run_fixer().stderr)

    def test_file_uri_exact_repository_path_is_fixed(self):
        self.put("symbols/part.sym", b"v {}\n")
        encoded = os.fsencode((self.root / "symbols/part.sym").as_posix())
        original = b"C {file://" + encoded + b"} 0 0 0 0 {}\n"
        self.put("circuits/main.sch", original)
        result = self.run_fixer()
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = original.replace(b"file://" + encoded, b"../symbols/part.sym")
        self.assertEqual(self.git("show", ":circuits/main.sch"), expected)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":circuits/main.sch"), expected)

    def test_file_uri_percent_encoded_literal_path_is_fixed(self):
        self.put("symbols/part name.sym", b"v {}\n")
        encoded = os.fsencode((self.root / "symbols/part%20name.sym").as_posix())
        original = b"C {file://" + encoded + b"} 0 0 0 0 {}\n"
        self.put("circuits/main.sch", original)
        result = self.run_fixer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("show", ":circuits/main.sch"),
                         original.replace(b"file://" + encoded, b"../symbols/part name.sym"))

    def test_unsupported_file_uris_are_rejected(self):
        for reference in (b"file:relative.sym", b"file:/relative.sym", b"file://host/part.sym",
                          b"file:///symbols/part.sym?query", b"file:///symbols/part.sym#fragment"):
            with self.subTest(reference=reference):
                original = b"C {" + reference + b"} 0 0 0 0 {}\n"
                self.put("main.sch", original)
                result = self.run_fixer()
                self.assertEqual(result.returncode, 1)
                self.assertIn(b"unsupported file URI", result.stderr)
                self.assertEqual(self.git("show", ":main.sch"), original)

    def test_untracked_destination(self):
        self.put("part with space.sym", b"v {}\n", stage=False)
        self.put("main.sch", b"C {" + self.absolute() + b"} 0 0 0 0 {}\n")
        self.assertIn(b"unresolved", self.run_fixer().stderr)

    def test_symlink_sources_and_destinations(self):
        original = self.prepare()
        (self.root / "main.sch").unlink()
        (self.root / "main.sch").symlink_to("part with space.sym")
        self.assertEqual(self.run_fixer().returncode, 1)
        self.assertEqual(self.git("show", ":main.sch"), original)
        self.git("add", "main.sch")
        self.assertIn(b"not a regular", self.run_fixer().stderr)
        (self.root / "main.sch").unlink()
        self.put("main.sch", original)
        (self.root / "part with space.sym").unlink()
        self.put("target", b"v {}\n")
        (self.root / "part with space.sym").symlink_to("target")
        self.git("add", "part with space.sym")
        self.assertIn(b"unresolved", self.run_fixer().stderr)

    def test_missing_and_mode_changes(self):
        original = self.prepare()
        (self.root / "main.sch").chmod(0o755)
        self.assertIn(b"mode changes", self.run_fixer().stderr)
        (self.root / "main.sch").unlink()
        self.assertEqual(self.run_fixer().returncode, 1)
        self.assertEqual(self.git("show", ":main.sch"), original)

    def test_rename_and_delete(self):
        self.prepare()
        self.git("commit", "-qm", "initial")
        self.git("mv", "main.sch", "renamed.sch")
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertIn(b"C {part with space.sym}", self.git("show", ":renamed.sch"))
        self.git("rm", "-f", "renamed.sch")
        self.assertEqual(self.run_fixer().returncode, 0)

    def test_unmerged_preflight(self):
        original = self.prepare()
        oid = self.git("hash-object", "-w", "--stdin", data=b"v {}\n").strip()
        self.git("update-index", "--index-info", data=b"100644 " + oid + b" 2\tconflict.sch\n")
        self.assertIn(b"unmerged", self.run_fixer().stderr)
        self.assertEqual((self.root / "main.sch").read_bytes(), original)

    def test_gitlink_destination_not_traversed(self):
        self.put("seed", b"seed")
        self.git("commit", "-qm", "initial")
        oid = self.git("rev-parse", "HEAD").strip()
        self.git("update-index", "--add", "--cacheinfo", "160000," + oid.decode() + ",sub")
        self.put("sub/part.sym", b"v {}\n", stage=False)
        self.put("main.sch", b"C {" + self.absolute("sub/part.sym") + b"} 0 0 0 0 {}\n")
        self.assertIn(b"unresolved", self.run_fixer().stderr)

    def test_explicit_library_and_ambiguity(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            (Path(first) / "part.sym").write_bytes(b"v {}\n")
            reference = os.fsencode(Path(first) / "part.sym")
            original = b"C {" + reference + b"} 0 0 0 0 {}\n"
            self.put("main.sch", original)
            (Path(second) / "part.sym").write_bytes(b"v {}\n")
            result = self.run_fixer("--library-root", first, "--library-root", second)
            self.assertIn(b"ambiguous", result.stderr)
            self.assertEqual(self.git("show", ":main.sch"), original)
            self.assertEqual(self.run_fixer("--library-root", first).returncode, 0)
            self.assertEqual(self.git("show", ":main.sch"), original.replace(reference, b"part.sym"))

    def test_external_library_and_local_symbol_are_ambiguous(self):
        self.put("circuits/part.sym", b"v {}\n")
        with tempfile.TemporaryDirectory() as library:
            reference = os.fsencode(Path(library) / "part.sym")
            (Path(library) / "part.sym").write_bytes(b"v {}\n")
            original = b"C {" + reference + b"} 0 0 0 0 {}\n"
            self.put("circuits/main.sch", original)
            result = self.run_fixer("--library-root", library)
            self.assertEqual(result.returncode, 1)
            self.assertIn(b"ambiguous", result.stderr)
            self.assertEqual(self.git("show", ":circuits/main.sch"), original)

    def test_legacy_io_requires_proven_library(self):
        self.put("io/sg13g2_io/xschem/pad.sym", b"v {}\n")
        original = b"C {IHP-Open-PDK/old/libs.ref/sg13g2_io/xschem/pad.sym} 0 0 0 0 {}\n"
        self.put("main.sch", original)
        self.assertEqual(self.run_fixer().returncode, 1)
        result = self.run_fixer("--library-root", str(self.root / "io/sg13g2_io/xschem"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("show", ":main.sch"), b"C {pad.sym} 0 0 0 0 {}\n")

    def test_legacy_multiline_path_is_preserved_and_flagged(self):
        self.put("symbols/FF_D.sym", b"v {}\n")
        for reference in (b"/home/eamtastudent/GROTDC marzo/Esquematicos/FF_D.sym",
                          b"C:\\old machine\\FF_D.sym", b"\\\\server\\share\\FF_D.sym"):
            with self.subTest(reference=reference):
                original = b"C {\r\n  " + reference + b" \t\r\n} 0 0 0 0 {name=x}\r\n"
                self.put("circuits/main.sch", original)
                result = self.run_fixer("--check")
                self.assertEqual(result.returncode, 1)
                self.assertIn(b"unresolved", result.stderr)
                self.assertEqual(self.git("show", ":circuits/main.sch"), original)

    def test_resolver_excludes_untracked_symlink_and_submodule(self):
        self.put("symbols/part.sym", b"v {}\n", stage=False)
        self.put("main.sch", b"C {/old/part.sym} 0 0 0 0 {}\n")
        self.assertIn(b"unresolved", self.run_fixer().stderr)
        (self.root / "symbols/part.sym").unlink()
        (self.root / "symbols/part.sym").symlink_to("../target")
        self.put("target", b"v {}\n")
        self.git("add", "symbols/part.sym")
        self.assertEqual(self.run_fixer().returncode, 1)
        self.git("rm", "-f", "symbols/part.sym")
        self.git("commit", "-qm", "initial")
        oid = self.git("rev-parse", "HEAD").strip().decode()
        self.git("update-index", "--add", "--cacheinfo", "160000," + oid + ",sub")
        self.put("sub/part.sym", b"v {}\n", stage=False)
        self.assertIn(b"unresolved", self.run_fixer("--all", "--check").stderr)

    def test_library_local_coexistence_prefers_local_and_checks_root(self):
        self.put("part.sym", b"v {}\n")
        original = b"C {/old/part.sym} 0 0 0 0 {}\n"
        self.put("main.sch", original)
        with tempfile.TemporaryDirectory() as library:
            (Path(library) / "part.sym").write_bytes(b"v {}\n")
            result = self.run_fixer("--library-root", library)
            self.assertIn(b"unresolved", result.stderr)
            self.assertEqual(self.git("show", ":main.sch"), original)

    def test_tilde_not_guessed(self):
        self.put("part.sym", b"v {}\n")
        self.put("main.sch", b"C {~/part.sym} 0 0 0 0 {}\n")
        self.assertIn(b"tilde", self.run_fixer().stderr)

    def test_check_all_index_only(self):
        original = self.prepare()
        self.git("commit", "-qm", "initial")
        index = (self.root / ".git/index").read_bytes()
        self.assertEqual(self.run_fixer("--check").returncode, 0)
        self.assertEqual(self.run_fixer("--all").returncode, 2)
        self.put("main.sch", b"dirty", stage=False)
        for state in ("dirty", "missing", "symlink"):
            with self.subTest(state=state):
                if state == "missing":
                    (self.root / "main.sch").unlink()
                    (self.root / "part with space.sym").unlink()
                elif state == "symlink":
                    (self.root / "main.sch").symlink_to("missing")
                result = self.run_fixer("--all", "--check")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(b"Needs fix", result.stdout)
                self.assertEqual(result.stderr, b"")
                self.assertEqual(self.git("show", ":main.sch"), original)
                self.assertEqual((self.root / ".git/index").read_bytes(), index)
        self.assertTrue((self.root / "main.sch").is_symlink())

    def test_installed_hook_fixes_staged_content_only(self):
        (self.root / "scripts").mkdir()
        (self.root / ".githooks").mkdir()
        (self.root / "scripts/fix_xschem_paths.py").symlink_to(SCRIPT)
        (self.root / "scripts/check_xschem_paths.py").symlink_to(CHECKER)
        (self.root / ".githooks/pre-commit").symlink_to(HOOK)
        self.git("config", "core.hooksPath", ".githooks")
        self.put("part.sym", b"v {}\n")
        original = b"C {" + self.absolute("part.sym") + b"} 0 0 0 0 {}\r\n"
        self.put("main.sch", original)
        self.put("other.bin", b"other bytes\x00\r\n")
        self.git("commit", "-qm", "hook test")
        self.assertEqual(self.git("show", "HEAD:main.sch"),
                         original.replace(self.absolute("part.sym"), b"part.sym"))
        self.assertEqual(self.git("show", "HEAD:other.bin"), b"other bytes\x00\r\n")

    def test_alternate_index_and_pathspec_characters(self):
        original = self.prepare()
        self.git("mv", "main.sch", ":special.sch")
        alternate = self.root / "alternate-index"
        alternate.write_bytes((self.root / ".git/index").read_bytes())
        env = dict(os.environ, GIT_INDEX_FILE=str(alternate))
        result = self.run_fixer(env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("show", "::special.sch"), original)
        staged = subprocess.check_output(["git", "show", "::special.sch"], cwd=self.root, env=env)
        self.assertEqual(staged, original.replace(self.absolute(), b"part with space.sym"))

    def test_metadata_crlf_and_whitespace_preservation(self):
        self.put("blocks/comp.sch", b"v {}\n")
        self.put("blocks/comp.sym", b"v {}\n")
        raw_non_utf8 = b"* \xff\xfe raw non utf8 comment\r\n"
        sch_line = b"  **  sch_path:   " + os.fsencode((self.root / "blocks/comp.sch").as_posix()) + b"   \r\n"
        sym_line = b"** sym_path: /legacy/root/" + os.fsencode(self.root.name) + b"/blocks/comp.sym\r\n"
        original = raw_non_utf8 + sch_line + sym_line
        self.put("sim.spice", original)
        result = self.run_fixer()
        self.assertEqual(result.returncode, 0, result.stderr)
        expected_sch = b"  **  sch_path:   $SCRIPT_DIR/blocks/comp.sch   \r\n"
        expected_sym = b"** sym_path: $SCRIPT_DIR/blocks/comp.sym\r\n"
        expected = raw_non_utf8 + expected_sch + expected_sym
        self.assertEqual((self.root / "sim.spice").read_bytes(), expected)
        self.assertEqual(self.git("show", ":sim.spice"), expected)

    def test_metadata_idempotent(self):
        self.put("blocks/comp.sch", b"v {}\n")
        original = b"** sch_path: " + os.fsencode(self.root / "blocks/comp.sch") + b"\n"
        self.put("sim.cir", original)
        self.assertEqual(self.run_fixer().returncode, 0)
        fixed = self.git("show", ":sim.cir")
        self.assertEqual(fixed, b"** sch_path: $SCRIPT_DIR/blocks/comp.sch\n")
        second = self.run_fixer()
        self.assertEqual(second.returncode, 0)
        self.assertEqual(self.git("show", ":sim.cir"), fixed)
        self.assertEqual((self.root / "sim.cir").read_bytes(), fixed)
        self.assertEqual(second.stdout, b"")

    def test_metadata_check_readonly(self):
        self.put("blocks/comp.sch", b"v {}\n")
        original = b"** sch_path: " + os.fsencode(self.root / "blocks/comp.sch") + b"\n"
        self.put("sim.cir", original)
        result = self.run_fixer("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"Needs fix: 'sim.cir'", result.stdout)
        self.assertEqual(self.git("show", ":sim.cir"), original)
        self.assertEqual((self.root / "sim.cir").read_bytes(), original)

    def test_metadata_partial_staging_preflight(self):
        self.put("blocks/comp.sch", b"v {}\n")
        original = b"** sch_path: " + os.fsencode(self.root / "blocks/comp.sch") + b"\n"
        self.put("sim.spice", original)
        self.put("sim.spice", original + b"* unstaged\n", stage=False)
        result = self.run_fixer()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"unstaged", result.stderr)
        self.assertEqual(self.git("show", ":sim.spice"), original)
        self.assertEqual((self.root / "sim.spice").read_bytes(), original + b"* unstaged\n")

    def test_metadata_unknown_and_executable_preservation(self):
        content = (
            b".include /path/to/external/models.spice\n"
            b".lib /opt/pdk/corners.lib typ\n"
            b".subckt test in out\n"
            b"R1 in out 1k file=/opt/models\n"
            b".ends\n"
            b"* regular comment with /path/to/something\n"
            b"** sch_path: /completely/unknown/external/path.sch\n"
            b"** sym_path: /completely/unknown/external/path.sym\n"
            b"** sch_path: $PDK_ROOT/$PDK/libs.ref/sg13g2/gate.sch\n"
        )
        self.put("sim.spice", content)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":sim.spice"), content)
        self.assertEqual((self.root / "sim.spice").read_bytes(), content)
        self.assertEqual(self.run_fixer("--check").returncode, 0)

    def test_metadata_tracked_target_validation(self):
        repo = os.fsencode(self.root.name)
        self.put("untracked.sch", b"v {}\n", stage=False)
        line = b"** sch_path: /legacy/" + repo + b"/untracked.sch\n"
        self.put("test_untracked.cir", line)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":test_untracked.cir"), line)

        self.put("seed", b"seed")
        self.git("commit", "-qm", "initial")
        oid = self.git("rev-parse", "HEAD").strip().decode()
        self.git("update-index", "--add", "--cacheinfo", "160000," + oid + ",sub")
        sub_line = b"** sch_path: /legacy/" + repo + b"/sub/cell.sch\n"
        self.put("test_sub.cir", sub_line)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":test_sub.cir"), sub_line)

        self.put("cell.sym", b"v {}\n")
        sch_with_sym = b"** sch_path: /legacy/" + repo + b"/cell.sym\n"
        self.put("test_mismatch.cir", sch_with_sym)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":test_mismatch.cir"), sch_with_sym)

        self.put("nested/folder/target.sch", b"v {}\n")
        guessed_line = b"** sch_path: /other/machine/target.sch\n"
        self.put("test_guess.cir", guessed_line)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":test_guess.cir"), guessed_line)

        self.put("cell.sch", b"v {}\n")
        self.put(self.root.name + "/cell.sch", b"v {}\n")
        ambig_line = b"** sch_path: /legacy/" + repo + b"/" + repo + b"/cell.sch\n"
        self.put("test_ambig.cir", ambig_line)
        result = self.run_fixer()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"ambiguous", result.stderr)
        self.assertEqual(self.git("show", ":test_ambig.cir"), ambig_line)

        self.git("rm", "-f", self.root.name + "/cell.sch")
        single_result = self.run_fixer()
        self.assertEqual(single_result.returncode, 0, single_result.stderr)
        self.assertEqual(self.git("show", ":test_ambig.cir"), b"** sch_path: $SCRIPT_DIR/cell.sch\n")

    def test_spice_alternate_index_and_check_all_index_only(self):
        self.put("cell.sch", b"v {}\n")
        original = b"** sch_path: " + os.fsencode(self.root / "cell.sch") + b"\n"
        self.put("sim.spice", original)
        self.git("commit", "-qm", "initial")
        index = (self.root / ".git/index").read_bytes()
        self.assertEqual(self.run_fixer("--check").returncode, 0)
        self.put("sim.spice", b"dirty", stage=False)
        for state in ("dirty", "missing", "symlink"):
            with self.subTest(state=state):
                if state == "missing":
                    (self.root / "sim.spice").unlink()
                elif state == "symlink":
                    (self.root / "sim.spice").symlink_to("missing")
                result = self.run_fixer("--all", "--check")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(b"Needs fix: 'sim.spice'", result.stdout)
                self.assertEqual(result.stderr, b"")
                self.assertEqual(self.git("show", ":sim.spice"), original)
                self.assertEqual((self.root / ".git/index").read_bytes(), index)
        (self.root / "sim.spice").unlink()
        self.git("checkout", "HEAD", "--", "sim.spice")
        self.put("sim.cir", original)
        alternate = self.root / "alternate-index"
        alternate.write_bytes((self.root / ".git/index").read_bytes())
        self.git("reset", "--hard", "HEAD")
        (self.root / "sim.cir").write_bytes(original)
        env = dict(os.environ, GIT_INDEX_FILE=str(alternate))
        result = self.run_fixer(env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        staged = subprocess.check_output(["git", "show", ":sim.cir"], cwd=self.root, env=env)
        self.assertEqual(staged, b"** sch_path: $SCRIPT_DIR/cell.sch\n")

    def test_metadata_reject_crlf_replacement(self):
        self.put("blocks/comp.sch", b"v {}\n")
        uri_crlf = b"** sch_path: file://" + os.fsencode((self.root / "blocks/comp%0aevil.sch").as_posix()) + b"\n"
        self.put("sim.spice", uri_crlf)
        result = self.run_fixer()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"unsupported", result.stderr)

        uri_cr = b"** sch_path: file://" + os.fsencode((self.root / "blocks/comp%0d%0aevil.sch").as_posix()) + b"\n"
        self.put("sim2.spice", uri_cr)
        result2 = self.run_fixer()
        self.assertEqual(result2.returncode, 1)
        self.assertIn(b"unsupported", result2.stderr)

        self.put("blocks/bad\nname.sch", b"v {}\n")
        bad_meta = b"** sch_path: " + os.fsencode(self.root / "blocks/bad\nname.sch") + b"\n"
        self.put("sim3.spice", bad_meta)
        result3 = self.run_fixer()
        self.assertEqual(result3.returncode, 1)
        self.assertIn(b"unsupported", result3.stderr)

    def test_atomic_write_index_lock_failure(self):
        original = self.prepare()
        lock_file = self.root / ".git" / "index.lock"
        lock_file.write_bytes(b"lock")
        result = self.run_fixer()
        self.assertEqual(result.returncode, 1)
        self.assertEqual((self.root / "main.sch").read_bytes(), original)
        lock_file.unlink()

    def test_atomic_write_rollback_on_failure(self):
        original = self.prepare()
        sub_dir = self.root / "sub"
        sub_dir.mkdir()
        self.put("part with space.sym", b"v {}\n")
        sub_original = b"C {" + self.absolute() + b"} 0 0 0 0 {}\n"
        self.put("sub/second.sch", sub_original)
        sub_dir.chmod(0o555)
        self.addCleanup(lambda: sub_dir.chmod(0o755))
        result = self.run_fixer()
        self.assertEqual(result.returncode, 1)
        self.assertEqual((self.root / "main.sch").read_bytes(), original)
        self.assertEqual(self.git("show", ":main.sch"), original)
        self.assertEqual((self.root / "sub/second.sch").read_bytes(), sub_original)
        self.assertEqual(self.git("show", ":sub/second.sch"), sub_original)

    def test_safe_non_symlink_replacement(self):
        original = self.prepare()
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertFalse((self.root / "main.sch").is_symlink())
        self.assertTrue((self.root / "main.sch").is_file())

    def test_metadata_matching_rules(self):
        self.put("blocks/comp.sch", b"v {}\n")
        repo = self.root.name
        rel_line = f"** sch_path: rel/path/{repo}/blocks/comp.sch\n".encode()
        self.put("rel.spice", rel_line)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":rel.spice"), rel_line)

        var_line = f"** sch_path: $PDK_ROOT/{repo}/blocks/comp.sch\n".encode()
        self.put("var.spice", var_line)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":var.spice"), var_line)

        bracket_line = f"** sch_path: [file join $DIR {repo} blocks comp.sch]\n".encode()
        self.put("bracket.spice", bracket_line)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":bracket.spice"), bracket_line)

        exact_nonexistent = (self.root / f"missing/{repo}/blocks/comp.sch").as_posix().encode()
        exact_line = b"** sch_path: " + exact_nonexistent + b"\n"
        self.put("exact.spice", exact_line)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":exact.spice"), exact_line)

        external_line = f"** sch_path: /opt/external/{repo}/blocks/comp.sch\n".encode()
        self.put("external.spice", external_line)
        self.assertEqual(self.run_fixer().returncode, 0)
        self.assertEqual(self.git("show", ":external.spice"), b"** sch_path: $SCRIPT_DIR/blocks/comp.sch\n")

    def test_library_collision_and_shadow_check(self):
        self.put("symbols/part.sym", b"v {}\n")
        original = b"C {" + self.absolute("symbols/part.sym") + b"} 0 0 0 0 {}\n"
        self.put("circuits/main.sch", original)

        (self.root / "symbols/part.sym").unlink()
        (self.root / "symbols/part.sym").symlink_to("/dev/null")
        result = self.run_fixer()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"missing or non-regular", result.stderr)
        (self.root / "symbols/part.sym").unlink()
        self.put("symbols/part.sym", b"v {}\n")

        self.put("circuits/part.sym", b"v {}\n", stage=False)
        result2 = self.run_fixer()
        self.assertEqual(result2.returncode, 1)
        self.assertIn(b"ambiguous", result2.stderr)
        (self.root / "circuits/part.sym").unlink()

        self.put("part.sym", b"v {}\n")
        self.put("single.sch", b"C {" + self.absolute("part.sym") + b"} 0 0 0 0 {}\n")
        with tempfile.TemporaryDirectory() as lib:
            (Path(lib) / "part.sym").write_bytes(b"v {}\n")
            result3 = self.run_fixer("--library-root", lib)
            self.assertEqual(result3.returncode, 1)
            self.assertIn(b"ambiguous", result3.stderr)

        (self.root / "inrepo_lib").mkdir(exist_ok=True)
        (self.root / "inrepo_lib" / "part.sym").write_bytes(b"v {}\n")
        result4 = self.run_fixer("--library-root", str(self.root / "inrepo_lib"))
        self.assertEqual(result4.returncode, 1)
        self.assertIn(b"ambiguous", result4.stderr)
        (self.root / "inrepo_lib" / "part.sym").unlink()
        (self.root / "inrepo_lib" / "part.sym").symlink_to("/dev/null")
        result5 = self.run_fixer("--library-root", str(self.root / "inrepo_lib"))
        self.assertEqual(result5.returncode, 1)
        self.assertIn(b"ambiguous", result5.stderr)
        (self.root / "inrepo_lib" / "part.sym").unlink()
        (self.root / "inrepo_lib").rmdir()

    def test_same_target_deduplication(self):
        self.put("symbols/part.sym", b"v {}\n")
        original = b"C {" + self.absolute("symbols/part.sym") + b"} 0 0 0 0 {}\n"
        self.put("main.sch", original)
        result = self.run_fixer("--library-root", str(self.root / "symbols"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("show", ":main.sch"), b"C {part.sym} 0 0 0 0 {}\n")
        self.assertEqual((self.root / "main.sch").read_bytes(), b"C {part.sym} 0 0 0 0 {}\n")

        self.put("symbols/sub.sch", original)
        result2 = self.run_fixer("--library-root", str(self.root / "symbols"))
        self.assertEqual(result2.returncode, 0, result2.stderr)
        self.assertEqual(self.git("show", ":symbols/sub.sch"), b"C {part.sym} 0 0 0 0 {}\n")


if __name__ == "__main__":
    unittest.main()
