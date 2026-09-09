import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCEME_FILE = ROOT / "SOURCEME"


def has_shell(shell_name):
    return shutil.which(shell_name) is not None


class TestSourceme(unittest.TestCase):
    def setUp(self):
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.temp_dir_obj.name)

    def tearDown(self):
        self.temp_dir_obj.cleanup()

    def _create_mock_repo(self, path: Path):
        pdk_ihp = path / "IHP-Open-PDK" / "ihp-sg13g2"
        tech_dir = pdk_ihp / "libs.tech" / "klayout" / "tech"
        gds_dir = pdk_ihp / "libs.ref" / "sg13g2_stdcell" / "gds"
        lib_dir = path / "klayout" / "libraries"

        tech_dir.mkdir(parents=True, exist_ok=True)
        gds_dir.mkdir(parents=True, exist_ok=True)
        lib_dir.mkdir(parents=True, exist_ok=True)

        (tech_dir / "sg13g2.lyt").write_text("mock_lyt")
        (gds_dir / "sg13g2_stdcell.gds").write_bytes(b"mock_gds")

        rel_gds = os.path.relpath(gds_dir / "sg13g2_stdcell.gds", lib_dir)
        os.symlink(rel_gds, lib_dir / "sg13g2_stdcell.gds")

        shutil.copy(SOURCEME_FILE, path / "SOURCEME")
        return path / "SOURCEME"

    def _run_shell(self, shell: str, command: str, cwd: Path = None, env: dict = None):
        clean_env = os.environ.copy()
        for var in ("PDK_ROOT", "PDK", "KLAYOUT_PATH", "BASH_ENV", "ENV"):
            clean_env.pop(var, None)
        if env:
            clean_env.update(env)

        if shell == "bash":
            cmd_args = ["bash", "--noprofile", "--norc", "-c", command]
        elif shell == "zsh":
            cmd_args = ["zsh", "-f", "-c", command]
        else:
            cmd_args = [shell, "-c", command]

        return subprocess.run(
            cmd_args,
            cwd=cwd or ROOT,
            env=clean_env,
            capture_output=True,
            text=True,
        )

    def test_repo_symlink_static(self):
        symlink_path = ROOT / "klayout" / "libraries" / "sg13g2_stdcell.gds"
        self.assertTrue(
            symlink_path.is_symlink(),
            "klayout/libraries/sg13g2_stdcell.gds must exist and be a symlink",
        )
        target = os.readlink(symlink_path)
        self.assertFalse(os.path.isabs(target), "Symlink must be relative, not absolute")
        self.assertIn("IHP-Open-PDK", target)
        self.assertIn("sg13g2_stdcell.gds", target)
        expected_target = (
            ROOT
            / "IHP-Open-PDK"
            / "ihp-sg13g2"
            / "libs.ref"
            / "sg13g2_stdcell"
            / "gds"
            / "sg13g2_stdcell.gds"
        ).resolve(strict=False)
        self.assertEqual(symlink_path.resolve(strict=False), expected_target)

    def test_export_pinned_values(self):
        repo_sourceme = self._create_mock_repo(self.temp_dir / "repo")
        expected_pdk_root = str((repo_sourceme.parent / "IHP-Open-PDK").resolve())
        expected_klayout = ":".join(
            [
                str((repo_sourceme.parent / "klayout").resolve()),
                str(
                    (
                        repo_sourceme.parent
                        / "IHP-Open-PDK"
                        / "ihp-sg13g2"
                        / "libs.tech"
                        / "klayout"
                    ).resolve()
                ),
                str(
                    (
                        repo_sourceme.parent
                        / "IHP-Open-PDK"
                        / "ihp-sg13g2"
                        / "libs.tech"
                        / "klayout"
                        / "tech"
                    ).resolve()
                ),
            ]
        )

        inherited_env = {
            "PDK_ROOT": "/inherited/custom/pdk",
            "PDK": "other-pdk",
        }

        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = (
                    f'source "{repo_sourceme}"\n'
                    f'printf "%s\\n" "$PDK_ROOT" "$PDK" "$KLAYOUT_PATH"\n'
                )
                res = self._run_shell(shell, cmd, cwd=ROOT, env=inherited_env)
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                lines = res.stdout.strip().splitlines()
                self.assertEqual(lines[0], expected_pdk_root)
                self.assertEqual(lines[1], "ihp-sg13g2")
                self.assertEqual(lines[2], expected_klayout)

    def test_arbitrary_working_directory(self):
        repo_sourceme = self._create_mock_repo(self.temp_dir / "repo")
        outside_dir = self.temp_dir / "outside"
        outside_dir.mkdir()
        expected_pdk_root = str((repo_sourceme.parent / "IHP-Open-PDK").resolve())

        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = f'source "{repo_sourceme}"\necho "$PDK_ROOT"\n'
                res = self._run_shell(shell, cmd, cwd=outside_dir)
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                self.assertEqual(res.stdout.strip(), expected_pdk_root)

    def test_paths_with_spaces(self):
        repo_with_spaces = self.temp_dir / "repo with spaces in dir name"
        repo_with_spaces.mkdir()
        repo_sourceme = self._create_mock_repo(repo_with_spaces)
        expected_pdk_root = str((repo_with_spaces / "IHP-Open-PDK").resolve())

        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = f'source "{repo_sourceme}"\necho "$PDK_ROOT"\n'
                res = self._run_shell(shell, cmd)
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                self.assertEqual(res.stdout.strip(), expected_pdk_root)

    def test_inherited_klayout_path_preserved_and_idempotent(self):
        repo_sourceme = self._create_mock_repo(self.temp_dir / "repo")
        inherited = "/custom/klayout/path:/opt/other/klayout"
        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = (
                    f'source "{repo_sourceme}"\n'
                    f'first="$KLAYOUT_PATH"\n'
                    f'source "{repo_sourceme}"\n'
                    f'second="$KLAYOUT_PATH"\n'
                    f'printf "%s\\n%s\\n" "$first" "$second"\n'
                )
                res = self._run_shell(
                    shell, cmd, env={"KLAYOUT_PATH": inherited}
                )
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                lines = res.stdout.strip().splitlines()
                self.assertEqual(lines[0], lines[1])
                self.assertTrue(lines[0].endswith(f":{inherited}"))
                self.assertNotIn("+", lines[0])

    def test_shell_options_and_cwd_unchanged(self):
        repo_sourceme = self._create_mock_repo(self.temp_dir / "repo")
        outside_dir = self.temp_dir / "outside"
        outside_dir.mkdir()

        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = (
                    f'opt_before="$-"; cwd_before="$PWD"\n'
                    f'source "{repo_sourceme}"\n'
                    f'opt_after="$-"; cwd_after="$PWD"\n'
                    f'printf "%s|%s|%s|%s\\n" "$opt_before" "$opt_after" "$cwd_before" "$cwd_after"\n'
                )
                res = self._run_shell(shell, cmd, cwd=outside_dir)
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                parts = res.stdout.strip().split("|")
                self.assertEqual(parts[0], parts[1], "Shell options changed")
                self.assertEqual(parts[2], parts[3], "Working directory changed")

    def test_compatible_with_set_eu(self):
        repo_sourceme = self._create_mock_repo(self.temp_dir / "repo")
        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = (
                    "set -eu\n"
                    f'source "{repo_sourceme}"\n'
                    "echo success\n"
                )
                res = self._run_shell(shell, cmd)
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                self.assertEqual(res.stdout.strip(), "success")

    def test_incomplete_pdk_fails_cleanly(self):
        empty_repo = self.temp_dir / "incomplete_repo"
        empty_repo.mkdir()
        shutil.copy(SOURCEME_FILE, empty_repo / "SOURCEME")
        incomplete_sourceme = empty_repo / "SOURCEME"

        prior_env = {
            "PDK_ROOT": "/prior/pdk/root",
            "PDK": "prior-pdk",
            "KLAYOUT_PATH": "/prior/klayout/path",
        }

        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = (
                    f'source "{incomplete_sourceme}"; ret=$?\n'
                    'printf "ret=%s|pdk_root=%s|pdk=%s|klayout=%s|alive\\n" '
                    '"$ret" "$PDK_ROOT" "$PDK" "$KLAYOUT_PATH"\n'
                )
                res = self._run_shell(shell, cmd, env=prior_env)
                self.assertEqual(res.returncode, 0)
                parts = res.stdout.strip().split("|")
                self.assertEqual(parts[0], "ret=1")
                self.assertEqual(parts[1], "pdk_root=/prior/pdk/root")
                self.assertEqual(parts[2], "pdk=prior-pdk")
                self.assertEqual(parts[3], "klayout=/prior/klayout/path")
                self.assertEqual(parts[4], "alive")
                self.assertIn("git submodule update --init --recursive", res.stderr)

    def test_missing_symlink_fails_cleanly(self):
        repo_path = self.temp_dir / "missing_symlink_repo"
        repo_sourceme = self._create_mock_repo(repo_path)
        symlink = repo_path / "klayout" / "libraries" / "sg13g2_stdcell.gds"
        symlink.unlink()

        prior_env = {
            "PDK_ROOT": "/prior/pdk/root",
            "PDK": "prior-pdk",
            "KLAYOUT_PATH": "/prior/klayout/path",
        }

        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = (
                    f'source "{repo_sourceme}"; ret=$?\n'
                    'printf "ret=%s|pdk_root=%s|pdk=%s|klayout=%s|alive\\n" '
                    '"$ret" "$PDK_ROOT" "$PDK" "$KLAYOUT_PATH"\n'
                )
                res = self._run_shell(shell, cmd, env=prior_env)
                self.assertEqual(res.returncode, 0)
                parts = res.stdout.strip().split("|")
                self.assertEqual(parts[0], "ret=1")
                self.assertEqual(parts[1], "pdk_root=/prior/pdk/root")
                self.assertEqual(parts[2], "pdk=prior-pdk")
                self.assertEqual(parts[3], "klayout=/prior/klayout/path")
                self.assertEqual(parts[4], "alive")
                self.assertIn("git submodule update --init --recursive", res.stderr)

    def test_missing_lyt_fails_cleanly(self):
        repo_path = self.temp_dir / "missing_lyt_repo"
        repo_sourceme = self._create_mock_repo(repo_path)
        lyt_file = repo_path / "IHP-Open-PDK" / "ihp-sg13g2" / "libs.tech" / "klayout" / "tech" / "sg13g2.lyt"
        lyt_file.unlink()

        prior_env = {
            "PDK_ROOT": "/prior/pdk/root",
            "PDK": "prior-pdk",
            "KLAYOUT_PATH": "/prior/klayout/path",
        }

        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = (
                    f'source "{repo_sourceme}"; ret=$?\n'
                    'printf "ret=%s|pdk_root=%s|pdk=%s|klayout=%s|alive\\n" '
                    '"$ret" "$PDK_ROOT" "$PDK" "$KLAYOUT_PATH"\n'
                )
                res = self._run_shell(shell, cmd, env=prior_env)
                self.assertEqual(res.returncode, 0)
                parts = res.stdout.strip().split("|")
                self.assertEqual(parts[0], "ret=1")
                self.assertEqual(parts[1], "pdk_root=/prior/pdk/root")
                self.assertEqual(parts[2], "pdk=prior-pdk")
                self.assertEqual(parts[3], "klayout=/prior/klayout/path")
                self.assertEqual(parts[4], "alive")
                self.assertIn("git submodule update --init --recursive", res.stderr)

    def test_direct_execution_detection(self):
        repo_sourceme = self._create_mock_repo(self.temp_dir / "repo")
        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell):
                cmd = (
                    ["bash", "--noprofile", "--norc", str(repo_sourceme)]
                    if shell == "bash"
                    else ["zsh", "-f", str(repo_sourceme)]
                )
                res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("must be sourced", res.stderr)

    def test_cleanup_helpers_on_success_and_failure(self):
        repo_sourceme = self._create_mock_repo(self.temp_dir / "repo")
        shells = ["bash"]
        if has_shell("zsh"):
            shells.append("zsh")

        for shell in shells:
            with self.subTest(shell=shell, case="success"):
                cmd = (
                    f'source "{repo_sourceme}"\n'
                    'typeset -f _sourceme_main >/dev/null && echo "func_main_exists"\n'
                    'typeset -f _sourceme_add_path >/dev/null && echo "func_add_exists"\n'
                    'echo "done"\n'
                )
                res = self._run_shell(shell, cmd)
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                self.assertNotIn("func_main_exists", res.stdout)
                self.assertNotIn("func_add_exists", res.stdout)
                self.assertIn("done", res.stdout)

            with self.subTest(shell=shell, case="failure"):
                fail_dir = self.temp_dir / f"fail_{shell}"
                fail_dir.mkdir()
                shutil.copy(SOURCEME_FILE, fail_dir / "SOURCEME")
                fail_sourceme = fail_dir / "SOURCEME"
                cmd = (
                    f'source "{fail_sourceme}"; ret=$?\n'
                    'typeset -f _sourceme_main >/dev/null && echo "func_main_exists"\n'
                    'typeset -f _sourceme_add_path >/dev/null && echo "func_add_exists"\n'
                    'echo "ret=$ret"\n'
                )
                res = self._run_shell(shell, cmd)
                self.assertEqual(res.returncode, 0)
                self.assertNotIn("func_main_exists", res.stdout)
                self.assertNotIn("func_add_exists", res.stdout)
                self.assertIn("ret=1", res.stdout)


if __name__ == "__main__":
    unittest.main()
