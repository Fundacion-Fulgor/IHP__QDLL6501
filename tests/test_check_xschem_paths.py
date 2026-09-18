from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import scripts.check_xschem_paths
from scripts.check_xschem_paths import _get_staged_paths, parse_content, run_checker


ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "scripts" / "check_xschem_paths.py"


class TestCheckXschemPaths(unittest.TestCase):
    def setUp(self) -> None:
        self.env_patch = patch.dict(
            os.environ,
            {
                "GIT_CONFIG_GLOBAL": "/dev/null",
                "GIT_CONFIG_SYSTEM": "/dev/null",
            },
        )
        self.env_patch.start()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        self.git(["init"])

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        self.env_patch.stop()

    def git(
        self,
        args: list[str],
        env: dict[str, str] | None = None,
        input: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        return subprocess.run(
            ["git"] + args,
            cwd=self.repo,
            env=merged_env,
            input=input,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def stage(self, name: str, content: str) -> Path:
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.git(["add", name])
        return path

    def cli(
        self,
        *args: str,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        return subprocess.run(
            [sys.executable, str(CHECKER), "--repo-root", str(self.repo), *args],
            cwd=self.repo,
            env=merged_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_current_repository_clean(self) -> None:
        self.stage("clean.sch", "C {clean.sym} 0 0 0 0 {}\n")
        proc = self.cli()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("0 path portability violations", proc.stdout)
        m = re.search(r"Checked (\d+) file\(s\)", proc.stdout)
        self.assertIsNotNone(m)
        self.assertGreater(int(m.group(1)), 0)

    def test_xschem_record_context_and_escaped_paths(self) -> None:
        content = (
            "C {devices/code_shown.sym} 0 0 0 0 {name=M format=\"tcleval( @value )\" value=\".include /opt/private/models.lib\"}\n"
            "C {devices/launcher.sym} 0 0 0 0 {name=h descr=\"Example file=/tmp/example.txt\"}\n"
            "C {\n/opt/path with spaces/bad.sym\n} 0 0 0 0 {name=x file=\"/tmp/input file.vec\"}\n"
            "C {devices/code_shown.sym} 0 0 0 0 {name=N value=\".include \\\"/opt/path with spaces/model.lib\\\"\"}\n"
            "C {cell\\{ok\\}.sym} 0 0 0 0 {name=x}\n"
        )
        violations = parse_content(content, "folder/tb.sch")
        refs = [v.offending_reference for v in violations]
        self.assertEqual(len(violations), 4)
        self.assertEqual(violations[0].line_number, 1)
        self.assertIn("/opt/private/models.lib", refs)
        self.assertIn("/opt/path with spaces/bad.sym", refs)
        self.assertIn("/tmp/input file.vec", refs)
        self.assertIn("/opt/path with spaces/model.lib", refs)
        self.assertNotIn("/tmp/example.txt", refs)

    def test_spice_tcl_and_variable_policy(self) -> None:
        content = (
            "C {devices/code_shown.sym} 0 0 0 0 {name=M value=\"\n"
            ".include C:\\Users\\alice\\models.lib\n"
            ".include C:relative\\models.lib\n"
            ".include $env(HOME)/models.lib\n"
            ".lib $HOME/models.lib tt\n"
            ".lib only_a_section\n"
            ".include /opt/bad.lib $ ordinary comment\n"
            "* /opt/comment.lib\n"
            "wrdata output.raw time a/b\n\"}\n"
            "C {devices/code_shown.sym} 0 0 0 0 {name=A format=\"tcleval( @value )\" value=\".include $PDK_ROOT/$PDK/models.lib\"}\n"
            "C {devices/code_shown.sym} 0 0 0 0 {name=B format=\"tcleval( @value )\" value=\".include $PDK/models.lib\"}\n"
            "C {devices/launcher.sym} 0 0 0 0 {name=C tclcommand=\"xschem raw_read $netlist_dir/tb.raw tran; source /home/alice/setup.tcl\"}\n"
            "C {devices/launcher.sym} 0 0 0 0 {name=D tclcommand=\"xschem raw_read [file join /home/alice sim.raw] tran\"}\n"
        )
        violations = parse_content(content, "tb.sch")
        refs = [v.offending_reference for v in violations]
        self.assertEqual(len(violations), 8)
        self.assertIn(r"C:\Users\alice\models.lib", refs)
        self.assertIn(r"C:relative\models.lib", refs)
        self.assertIn("$env(HOME)/models.lib", refs)
        self.assertIn("$HOME/models.lib", refs)
        self.assertIn("/opt/bad.lib", refs)
        self.assertIn("$PDK/models.lib", refs)
        self.assertIn("/home/alice/setup.tcl", refs)
        self.assertIn("/home/alice", refs)
        self.assertNotIn("$PDK_ROOT/$PDK/models.lib", refs)

    def test_posix_windows_unc_tilde_traversal_and_obsolete_prefix(self) -> None:
        content = (
            "C {/foss/designs/cell.sym} 0 0 0 0 {}\n"
            "C {\\\\server\\share\\cell.sym} 0 0 0 0 {}\n"
            "C {~/project/cell.sym} 0 0 0 0 {}\n"
            "C {../../../outside.sym} 0 0 0 0 {}\n"
            "C {IHP-Open-PDK/ihp-sg13g2/libs.ref/sg13g2_io/xschem/io.sym} 0 0 0 0 {}\n"
            "C {devices/res.sym} 0 0 0 0 {name=R value=10k/2}\n"
            "C {GROTDC.sym} 0 0 0 0 {}\n"
        )
        violations = parse_content(content, "a/b/tb.sch")
        messages = [v.message for v in violations]
        self.assertEqual(len(violations), 5)
        self.assertTrue(any("POSIX" in m for m in messages))
        self.assertTrue(any("UNC" in m for m in messages))
        self.assertTrue(any("tilde" in m for m in messages))
        self.assertTrue(any("traverses outside" in m for m in messages))
        self.assertTrue(any("obsolete PDK" in m for m in messages))

    def test_staged_blob_never_reads_worktree(self) -> None:
        sch = self.stage("block.sch", "C {/opt/staged-bad.sym} 0 0 0 0 {}\n")
        sch.write_text("C {working-tree-good.sym} 0 0 0 0 {}\n", encoding="utf-8")
        proc = self.cli("--staged")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("/opt/staged-bad.sym", proc.stderr)

        self.temp_dir.cleanup()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        self.git(["init"])
        sch = self.stage("block.sch", "C {staged-good.sym} 0 0 0 0 {}\n")
        sch.write_text("C {/opt/working-tree-bad.sym} 0 0 0 0 {}\n", encoding="utf-8")
        proc = self.cli("--staged")
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_staged_cli_catches_exact_bad_inputs(self) -> None:
        self.stage(
            "bad.sch",
            "C {devices/code_shown.sym} 0 0 0 0 {name=M value=\".include $env(HOME)/models.lib\"}\n"
            "C {devices/launcher.sym} 0 0 0 0 {name=h tclcommand=\"xschem raw_read [file join /home/alice sim.raw] tran\"}\n",
        )
        proc = self.cli("--staged")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("$env(HOME)/models.lib", proc.stderr)
        self.assertIn("/home/alice", proc.stderr)

    def test_alternate_index_and_non_source_symlink(self) -> None:
        self.stage("normal.sch", "C {clean.sym} 0 0 0 0 {}\n")
        link = self.repo / "latest"
        link.symlink_to("normal.sch")
        self.git(["add", "latest"])

        alt_index = str(self.repo / "alternate.index")
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = alt_index
        (self.repo / "alternate.sch").write_text("C {/opt/alternate-bad.sym} 0 0 0 0 {}\n", encoding="utf-8")
        self.git(["add", "alternate.sch"], env=env)

        proc = self.cli("--staged", env=env)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("/opt/alternate-bad.sym", proc.stderr)
        self.assertNotIn("symlink", proc.stderr)

    def test_non_source_symlink_passes_default_and_staged_modes(self) -> None:
        self.stage("clean.sch", "C {clean.sym} 0 0 0 0 {}\n")
        link = self.repo / "latest"
        link.symlink_to("clean.sch")
        self.git(["add", "latest"])

        code_default, violations_default, count_default = run_checker(staged=False, repo_root_arg=str(self.repo))
        self.assertEqual(code_default, 0, [v.format() for v in violations_default])
        self.assertEqual(count_default, 1)

        code_staged, violations_staged, count_staged = run_checker(staged=True, repo_root_arg=str(self.repo))
        self.assertEqual(code_staged, 0, [v.format() for v in violations_staged])
        self.assertEqual(count_staged, 1)

        proc_default = self.cli()
        self.assertEqual(proc_default.returncode, 0, proc_default.stderr)

        proc_staged = self.cli("--staged")
        self.assertEqual(proc_staged.returncode, 0, proc_staged.stderr)

    def test_unmerged_and_source_symlink_fail(self) -> None:
        source = self.repo / "conflict.sch"
        source.write_text("C {clean.sym} 0 0 0 0 {}\n", encoding="utf-8")
        sha = self.git(["hash-object", "-w", "conflict.sch"]).stdout.strip()
        self.git(
            ["update-index", "--index-info"],
            input=f"100644 {sha} 1\tconflict.sch\n100644 {sha} 2\tconflict.sch\n",
        )
        code, violations, _ = run_checker(staged=False, repo_root_arg=str(self.repo))
        self.assertEqual(code, 1)
        self.assertTrue(any("unmerged" in v.message for v in violations))

        self.temp_dir.cleanup()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        self.git(["init"])
        target = self.stage("real.sch", "C {clean.sym} 0 0 0 0 {}\n")
        (self.repo / "linked.sch").symlink_to(target)
        self.git(["add", "linked.sch"])
        proc = self.cli("--staged")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("symlink .sch/.sym source", proc.stderr)

    def test_staged_name_status_delete_rename_and_spaces(self) -> None:
        with patch(
            "scripts.check_xschem_paths._git_run",
            return_value=subprocess.CompletedProcess(
                ["git"],
                0,
                b"D\x00gone.sch\x00R100\x00old.sch\x00renamed file.sch\x00A\x00new file.sch\x00",
                b"",
            ),
        ):
            paths = _get_staged_paths(self.repo)
        self.assertEqual(paths, ["renamed file.sch", "new file.sch"])

    def test_gitlink_is_excluded(self) -> None:
        sub = self.repo / "submodule"
        sub.mkdir()
        (sub / "nested.sch").write_text("C {/opt/bad.sym} 0 0 0 0 {}\n", encoding="utf-8")
        oid = "1" * 40
        self.git(["update-index", "--add", "--index-info"], input=f"160000 {oid} 0\tsubmodule\n")
        self.stage("good.sch", "C {clean.sym} 0 0 0 0 {}\n")
        code, violations, count = run_checker(staged=False, repo_root_arg=str(self.repo))
        self.assertEqual(code, 0, [v.format() for v in violations])
        self.assertEqual(count, 1)

    def test_spice_and_cir_full_directives(self) -> None:
        content = (
            ".include /opt/abs/include.cir\n"
            ".inc /opt/abs/inc.cir\n"
            ".lib /opt/abs/models.lib corner\n"
            "source /opt/abs/source.spice\n"
            "load /opt/abs/load.raw\n"
            "wrdata /opt/abs/wrdata.raw v(1)\n"
            "write /opt/abs/write.raw v(1)\n"
            ".include relative/good.cir\n"
        )
        for ext in ("test.spice", "test.cir"):
            violations = parse_content(content, ext)
            refs = [v.offending_reference for v in violations]
            self.assertIn("/opt/abs/include.cir", refs)
            self.assertIn("/opt/abs/inc.cir", refs)
            self.assertIn("/opt/abs/models.lib", refs)
            self.assertIn("/opt/abs/source.spice", refs)
            self.assertIn("/opt/abs/load.raw", refs)
            self.assertIn("/opt/abs/wrdata.raw", refs)
            self.assertIn("/opt/abs/write.raw", refs)
            self.assertNotIn("relative/good.cir", refs)

    def test_sym_k_records_schematic_and_template(self) -> None:
        content = (
            "K {type=subcircuit schematic=/opt/abs_sub.sch}\n"
            "K {template=\"name=x file=/opt/abs_file.txt\"}\n"
            "K {template=\"name=y file=/opt/abs_raw.txt\"}\n"
        )
        violations = parse_content(content, "device.sym")
        refs = [v.offending_reference for v in violations]
        self.assertIn("/opt/abs_sub.sch", refs)
        self.assertIn("/opt/abs_file.txt", refs)
        self.assertIn("/opt/abs_raw.txt", refs)

    def test_sym_k_format_inline_include(self) -> None:
        content = 'K {type=subcircuit format="inline .include /opt/inline_model.lib"}\n'
        violations = parse_content(content, "device.sym")
        refs = [v.offending_reference for v in violations]
        self.assertIn("/opt/inline_model.lib", refs)

    def test_spice_continuation_lines(self) -> None:
        content_bad = ".include\n+ /opt/continued_bad.lib\n"
        v_bad = parse_content(content_bad, "test.spice")
        self.assertEqual(len(v_bad), 1)
        self.assertIn("/opt/continued_bad.lib", v_bad[0].offending_reference)

        content_good = ".include\n+ relative_continued.lib\n"
        v_good = parse_content(content_good, "test.spice")
        self.assertEqual(len(v_good), 0)

    def test_sym_k_tcleval_direct_format_body(self) -> None:
        content = 'K {type=netlist_commands format="tcleval(.include /opt/direct_tcl.lib)"}\n'
        violations = parse_content(content, "device.sym")
        self.assertEqual(len(violations), 1)
        self.assertIn("/opt/direct_tcl.lib", violations[0].offending_reference)

    def test_sym_template_inherits_enclosing_tcleval(self) -> None:
        content_clean = (
            "K {format=\"tcleval( @value )\"\n"
            "template=\"name=MODEL value=\\\".include $PDK_ROOT/$PDK/models.lib\\\"\"\n"
            "}\n"
        )
        v_clean = parse_content(content_clean, "device.sym")
        self.assertEqual(len(v_clean), 0)

        content_no_tcleval = (
            "K {format=\"@value\"\n"
            "template=\"name=MODEL value=\\\".include $PDK_ROOT/$PDK/models.lib\\\"\"\n"
            "}\n"
        )
        v_no_tcleval = parse_content(content_no_tcleval, "device.sym")
        self.assertEqual(len(v_no_tcleval), 1)
        self.assertTrue(any("interpolation" in v.message for v in v_no_tcleval))

        content_bad_var = (
            "K {format=\"tcleval( @value )\"\n"
            "template=\"name=MODEL value=\\\".include $env(HOME)/models.lib\\\"\"\n"
            "}\n"
        )
        v_bad_var = parse_content(content_bad_var, "device.sym")
        self.assertEqual(len(v_bad_var), 1)
        self.assertTrue(any("undeclared variable" in v.message for v in v_bad_var))

    def test_tcl_file_join_suffix_variable_pdk(self) -> None:
        content_good = 'C {devices/launcher.sym} 0 0 0 0 {name=A tclcommand="source [file join $PDK_ROOT $PDK libs.tech setup.tcl]"}\n'
        v_good = parse_content(content_good, "top.sch")
        self.assertEqual(len(v_good), 0)

        content_pdk_root = 'C {devices/launcher.sym} 0 0 0 0 {name=B tclcommand="source [file join $PDK libs.tech setup.tcl]"}\n'
        v_pdk_root = parse_content(content_pdk_root, "top.sch")
        self.assertEqual(len(v_pdk_root), 1)
        self.assertTrue(any("suffix component" in v.message for v in v_pdk_root))

        content_abs_in_join = 'C {devices/launcher.sym} 0 0 0 0 {name=C tclcommand="source [file join $PDK_ROOT /home/alice setup.tcl]"}\n'
        v_abs_in_join = parse_content(content_abs_in_join, "top.sch")
        self.assertEqual(len(v_abs_in_join), 1)
        self.assertTrue(any("POSIX" in v.message for v in v_abs_in_join))

    def test_sch_global_s_v_e_blocks_includes(self) -> None:
        content = (
            "V {\n.include /opt/abs_v.lib\n}\n"
            "S {\n.include /opt/abs_s.lib\n}\n"
            "E {\n.include /opt/abs_e.lib\n}\n"
        )
        violations = parse_content(content, "top.sch")
        refs = [v.offending_reference for v in violations]
        self.assertIn("/opt/abs_v.lib", refs)
        self.assertIn("/opt/abs_s.lib", refs)
        self.assertIn("/opt/abs_e.lib", refs)

    def test_code_attribute_includes(self) -> None:
        content = 'C {devices/code.sym} 0 0 0 0 {name=C1 code=".include /opt/abs_code.lib"}\n'
        violations = parse_content(content, "top.sch")
        refs = [v.offending_reference for v in violations]
        self.assertIn("/opt/abs_code.lib", refs)

    def test_tcl_braced_operands_reject(self) -> None:
        content = (
            "C {devices/launcher.sym} 0 0 0 0 {name=A tclcommand=\"source {/opt/script.tcl}\"}\n"
            "C {devices/launcher.sym} 0 0 0 0 {name=B tclcommand=\"xschem raw_read {/opt/sim.raw} tran\"}\n"
            "C {devices/launcher.sym} 0 0 0 0 {name=C tclcommand=\"source {/opt/path with spaces/run.tcl}\"}\n"
        )
        violations = parse_content(content, "top.sch")
        refs = [v.offending_reference for v in violations]
        self.assertIn("/opt/script.tcl", refs)
        self.assertIn("/opt/sim.raw", refs)
        self.assertIn("/opt/path with spaces/run.tcl", refs)

    def test_quoted_semicolon_filenames(self) -> None:
        content = (
            "C {devices/launcher.sym} 0 0 0 0 {name=A tclcommand=\"source \\\"/opt/dir;name/run.tcl\\\"\"}\n"
            "C {devices/code_shown.sym} 0 0 0 0 {name=B value=\".include \\\"/opt/dir;name/model.lib\\\"\"}\n"
        )
        violations = parse_content(content, "top.sch")
        refs = [v.offending_reference for v in violations]
        self.assertIn("/opt/dir;name/run.tcl", refs)
        self.assertIn("/opt/dir;name/model.lib", refs)

    def test_multi_command_newline_absolute_source(self) -> None:
        content = 'C {devices/launcher.sym} 0 0 0 0 {name=A tclcommand="puts start\nsource /opt/bad.tcl\nputs end"}\n'
        violations = parse_content(content, "top.sch")
        refs = [v.offending_reference for v in violations]
        self.assertIn("/opt/bad.tcl", refs)

    def test_tcl_source_with_encoding_flag(self) -> None:
        content = 'C {devices/launcher.sym} 0 0 0 0 {name=A tclcommand="source -encoding utf-8 /opt/encoded.tcl"}\n'
        violations = parse_content(content, "top.sch")
        refs = [v.offending_reference for v in violations]
        self.assertIn("/opt/encoded.tcl", refs)

    def test_tcl_file_join_traversal_fails(self) -> None:
        content = 'C {devices/launcher.sym} 0 0 0 0 {name=A tclcommand="xschem raw_read [file join $netlist_dir ../outside.raw] tran"}\n'
        violations = parse_content(content, "top.sch")
        self.assertGreater(len(violations), 0)
        self.assertTrue(any("outside" in v.offending_reference or "travers" in v.message or "outside" in v.message for v in violations))

    def test_unsupported_bracket_expression_in_path_fails(self) -> None:
        content = 'C {devices/launcher.sym} 0 0 0 0 {name=A tclcommand="source [get_script_path]"}\n'
        violations = parse_content(content, "top.sch")
        self.assertGreater(len(violations), 0)
        self.assertTrue(any("bracket expression" in v.message for v in violations))

    def test_non_path_tcl_bracket_expression_passes(self) -> None:
        content = 'C {devices/launcher.sym} 0 0 0 0 {name=A tclcommand="puts [expr 1+2]"}\n'
        violations = parse_content(content, "top.sch")
        self.assertEqual(len(violations), 0)

    def test_float_coordinates_do_not_skip_attrs(self) -> None:
        content = (
            "C {devices/code_shown.sym} 10.5 20.25 0.0 1.0 {name=M value=\".include /opt/bad.lib\"}\n"
            "C {devices/cell.sym} 100.0 -50.5 0 0 {name=X schematic=/opt/bad.sch}\n"
        )
        violations = parse_content(content, "top.sch")
        refs = [v.offending_reference for v in violations]
        self.assertIn("/opt/bad.lib", refs)
        self.assertIn("/opt/bad.sch", refs)

    def test_accurate_line_diagnostics_multiline_attrs_and_value(self) -> None:
        content = (
            "C {devices/code_shown.sym} 0 0 0 0 {\n"
            "name=M\n"
            "schematic=/opt/bad.sch\n"
            "value=\"\n"
            "* comment\n"
            ".include /opt/bad.lib\n"
            "\"}\n"
        )
        violations = parse_content(content, "top.sch")
        line_by_ref = {v.offending_reference: v.line_number for v in violations}
        self.assertEqual(line_by_ref.get("/opt/bad.sch"), 3)
        self.assertEqual(line_by_ref.get("/opt/bad.lib"), 6)

    def test_failed_git_diff_cached_fails_checker(self) -> None:
        real_git_run = scripts.check_xschem_paths._git_run

        def fake_git_run(args: list[str], repo_root: Path) -> subprocess.CompletedProcess[bytes]:
            if len(args) >= 2 and args[0] == "diff" and args[1] == "--cached":
                raise subprocess.CalledProcessError(1, ["git", "diff", "--cached"], b"", b"diff error")
            return real_git_run(args, repo_root)

        with patch("scripts.check_xschem_paths._git_run", side_effect=fake_git_run):
            code, violations, _ = run_checker(staged=True, repo_root_arg=str(self.repo))
        self.assertEqual(code, 1)
        self.assertGreater(len(violations), 0)

    def test_missing_tracked_worktree_file_fails_staged_passes(self) -> None:
        path = self.stage("good.sch", "C {clean.sym} 0 0 0 0 {}\n")
        path.unlink()
        code_default, violations_default, _ = run_checker(staged=False, repo_root_arg=str(self.repo))
        self.assertEqual(code_default, 1)
        self.assertTrue(any("missing" in v.message for v in violations_default))

        code_staged, violations_staged, _ = run_checker(staged=True, repo_root_arg=str(self.repo))
        self.assertEqual(code_staged, 0, [v.format() for v in violations_staged])

    def test_model_spice_fixture_cli(self) -> None:
        self.stage("models/bad.spice", ".include /opt/pdk/models.lib\n")
        proc_bad = self.cli()
        self.assertEqual(proc_bad.returncode, 1)
        self.assertIn("/opt/pdk/models.lib", proc_bad.stderr)

        self.temp_dir.cleanup()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        self.git(["init"])
        self.stage("models/good.spice", ".include relative.lib\n")
        proc_clean = self.cli()
        self.assertEqual(proc_clean.returncode, 0, proc_clean.stderr)
        self.assertIn("0 path portability violations", proc_clean.stdout)


if __name__ == "__main__":
    unittest.main()
