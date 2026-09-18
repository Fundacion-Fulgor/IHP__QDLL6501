import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from importlib.machinery import SourceFileLoader
import importlib.util

INSTALLER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install_hooks.py"
loader = SourceFileLoader("install_hooks", str(INSTALLER_PATH))
spec = importlib.util.spec_from_file_location("install_hooks", INSTALLER_PATH, loader=loader)
install_hooks_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install_hooks_mod)


class TestInstallHooks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        githooks = self.repo / ".githooks"
        githooks.mkdir()
        self.source_hook = githooks / "pre-commit"
        self.source_hook.write_text(
            '#!/bin/sh\nset -eu\nroot="$(git rev-parse --show-toplevel)"\n'
            'python3 "$root/scripts/fix_xschem_paths.py" --staged || exit $?\n'
            'exec python3 "$root/scripts/check_xschem_paths.py" --staged\n'
        )
        self.source_hook.chmod(0o755)

    def target(self):
        return self.repo / ".git" / "hooks" / "pre-commit"

    def test_fresh_install(self):
        config = (self.repo / ".git" / "config").read_bytes()
        rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 0)
        t = self.target()
        self.assertTrue(t.is_file())
        self.assertTrue(os.access(t, os.X_OK))
        self.assertEqual(t.read_text(), install_hooks_mod.FORWARDING_HOOK)
        self.assertEqual((self.repo / ".git" / "config").read_bytes(), config)

    def test_idempotent(self):
        self.assertEqual(install_hooks_mod.install_hooks(self.repo), 0)
        self.assertEqual(install_hooks_mod.install_hooks(self.repo), 0)
        self.assertEqual(self.target().read_text(), install_hooks_mod.FORWARDING_HOOK)

    def test_unrecognized_hook_refused(self):
        t = self.target()
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_bytes(b"#!/bin/sh\necho custom\n")
        stderr = io.StringIO()
        from contextlib import redirect_stderr
        with redirect_stderr(stderr):
            rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 1)
        self.assertIn(install_hooks_mod.MANUAL_CHAIN, stderr.getvalue())
        self.assertEqual(t.read_bytes(), b"#!/bin/sh\necho custom\n")

    def test_symlink_hook_refused(self):
        t = self.target()
        t.parent.mkdir(parents=True, exist_ok=True)
        t.symlink_to("/nonexistent")
        rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 1)
        self.assertTrue(t.is_symlink())

    def test_custom_hookspath_refused(self):
        custom = self.repo / "custom_hooks"
        custom.mkdir()
        subprocess.run(["git", "config", "core.hooksPath", str(custom)],
                       cwd=str(self.repo), check=True)
        rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 1)
        self.assertFalse((custom / "pre-commit").exists())

    def test_hookspath_githooks_ok(self):
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"],
                       cwd=str(self.repo), check=True)
        rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 0)
        self.assertFalse(self.target().exists())

    def test_unrelated_hooks_untouched(self):
        hooks = self.repo / ".git" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        commit_msg = hooks / "commit-msg"
        commit_msg.write_bytes(b"#!/bin/sh\necho commit-msg\n")
        self.assertEqual(install_hooks_mod.install_hooks(self.repo), 0)
        self.assertEqual(commit_msg.read_bytes(), b"#!/bin/sh\necho commit-msg\n")

    def test_missing_source_hook(self):
        self.source_hook.unlink()
        rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 1)

    def test_source_not_executable(self):
        self.source_hook.chmod(0o644)
        rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 1)

    def test_symlink_source_refused(self):
        replacement = self.repo / "replacement"
        replacement.write_text("#!/bin/sh\n")
        replacement.chmod(0o755)
        self.source_hook.unlink()
        self.source_hook.symlink_to(replacement)
        rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 1)
        self.assertFalse(self.target().exists())

    def test_git_config_unexpected_exit(self):
        real_run = subprocess.run

        def side_effect(cmd, *args, **kwargs):
            if len(cmd) >= 3 and cmd[0] == "git" and cmd[1] == "config" and cmd[2] == "core.hooksPath":
                res = subprocess.CompletedProcess(cmd, 2)
                res.stdout = ""
                res.stderr = "fatal: bad config"
                return res
            return real_run(cmd, *args, **kwargs)

        with patch("subprocess.run", side_effect=side_effect):
            rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 1)
        self.assertFalse(self.target().exists())

    def test_worktree(self):
        env = dict(os.environ,
                   GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@t",
                   GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@t")
        (self.repo / "f").write_text("x\n")
        subprocess.run(["git", "add", "f"], cwd=str(self.repo), check=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=str(self.repo),
                       check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wt = Path(self.temp.name) / "wt"
        subprocess.run(["git", "worktree", "add", str(wt), "-b", "wt-branch"],
                       cwd=str(self.repo), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wt_githooks = wt / ".githooks"
        wt_githooks.mkdir()
        shutil.copy2(self.source_hook, wt_githooks / "pre-commit")
        rc = install_hooks_mod.install_hooks(wt)
        self.assertEqual(rc, 0)

    def test_known_old_hook_upgraded(self):
        t = self.target()
        t.parent.mkdir(parents=True, exist_ok=True)
        for old_hook in install_hooks_mod.KNOWN_OLD_HOOKS:
            with self.subTest(old_hook=old_hook):
                t.write_bytes(old_hook)
                t.chmod(0o755)
                rc = install_hooks_mod.install_hooks(self.repo)
                self.assertEqual(rc, 0)
                self.assertEqual(t.read_text(), install_hooks_mod.FORWARDING_HOOK)
                self.assertTrue(os.access(t, os.X_OK))

    def test_known_old_hooks_definitions(self):
        self.assertTrue(len(install_hooks_mod.KNOWN_OLD_HOOKS) >= 2)
        qdll_old = b'#!/bin/sh\nroot="$(git rev-parse --show-toplevel)"\nexec python3 "$root/scripts/fix_xschem_paths.py" --staged\n'
        self.assertIn(qdll_old, install_hooks_mod.KNOWN_OLD_HOOKS)
        for old_hook in install_hooks_mod.KNOWN_OLD_HOOKS:
            self.assertTrue(old_hook.startswith(b"#!/bin/sh"))
            self.assertNotIn(b"check_xschem_paths.py", old_hook)

    def test_install_hooks_upgrade_write_error(self):
        t = self.target()
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_bytes(install_hooks_mod.KNOWN_OLD_HOOKS[0])
        t.chmod(0o755)
        with patch.object(Path, "write_bytes", side_effect=OSError("disk error")):
            rc = install_hooks_mod.install_hooks(self.repo)
        self.assertEqual(rc, 1)


class TestInstallHooksCLI(unittest.TestCase):
    def test_extra_args_rejected(self):
        result = subprocess.run(
            [sys.executable, str(INSTALLER_PATH), "--unexpected"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
