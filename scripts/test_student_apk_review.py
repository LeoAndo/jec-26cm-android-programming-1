"""提出APKの証拠収集が原本・既存結果を壊さず、未確認を正しく残すことを確かめる。"""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
from shutil import copy2, which
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile


SCRIPT = Path(__file__).with_name("student-apk-review.py")


@unittest.skipUnless(which("git"), "検証用リポジトリにはGitが必要です。")
class StudentApkReviewTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name).resolve()
        self.root = self.parent / "repository"
        (self.root / "scripts").mkdir(parents=True)
        self.script = self.root / "scripts" / SCRIPT.name
        copy2(SCRIPT, self.script)
        (self.root / "config").mkdir()
        config = {"projects": [{"name": "A01HelloAndroid", "root": "A01HelloAndroid",
                               "package": "jp.ac.jec.reference",
                               "docs": ["docs/hello/index.html", "teacher/hello/index.html"]}]}
        self.config = self.root / "config/teaching-materials.json"
        self.config.write_text(json.dumps(config), encoding="utf-8")
        self.git("init")
        self.git("add", "scripts/student-apk-review.py", "config/teaching-materials.json")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "commit", "-m", "検証用の教材")
        self.git("tag", "materials-test")
        self.commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.apk = self.parent / "submission.apk"
        with ZipFile(self.apk, "w") as archive:
            archive.writestr("AndroidManifest.xml", "fixture manifest")
            archive.writestr("classes.dex", "fixture dex")
            archive.writestr("res/layout/activity_main.xml", "fixture layout")
        self.original = self.apk.read_bytes()
        self.output = self.parent / "results"
        self.analyzer = self.parent / "fake-apkanalyzer"
        self.analyzer.write_text(
            f"#!{sys.executable}\n"
            "import sys, time\n"
            "if 'manifest' in sys.argv:\n"
            " print('<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\" '"
            "'package=\"student.changed\" android:versionCode=\"1\">'"
            "'<uses-sdk android:minSdkVersion=\"24\" android:targetSdkVersion=\"36\"/>'"
            "'</manifest>')\n"
            "elif 'dex' in sys.argv:\n"
            " print('C student.changed.MainActivity')\n"
            "else:\n"
            " print('<TextView/>')\n",
            encoding="utf-8",
        )
        self.analyzer.chmod(0o755)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True)

    def run_review(self, *extra, output=None, ref="materials-test", analyzer=None):
        return subprocess.run(
            [sys.executable, str(self.script), "inspect", "--apk", str(self.apk),
             "--project", "A01HelloAndroid", "--baseline-ref", ref,
             "--output", str(output or self.output), "--apkanalyzer",
             str(analyzer or self.analyzer), *extra],
            cwd=self.root, capture_output=True, text=True,
        )

    def evidence(self):
        return json.loads((self.output / "evidence.json").read_text(encoding="utf-8"))

    def test_collects_exact_baseline_and_does_not_grade_changed_package(self):
        self.config.write_text('{"projects": []}', encoding="utf-8")
        result = self.run_review("--resource", "/res/layout/activity_main.xml")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = self.evidence()
        self.assertEqual(data["baseline"]["commit"], self.commit)
        self.assertEqual(data["apk"]["sha256"], hashlib.sha256(self.original).hexdigest())
        self.assertEqual(data["manifest"]["application_id"], "student.changed")
        self.assertEqual(data["manifest"]["target_sdk"], "36")
        self.assertEqual(data["dynamic_review"], "not_run")
        self.assertEqual(data["status"], "complete")
        self.assertEqual(len(data["commands"]), 3)
        self.assertEqual(self.apk.read_bytes(), self.original)
        self.assertTrue((self.output / "report.md").exists())
        self.assertTrue((self.output / "feedback.md").exists())

    def test_missing_analyzer_is_partial_not_success(self):
        result = self.run_review(analyzer=self.parent / "missing")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.evidence()["status"], "partial")
        self.assertNotIn("manifest", self.evidence())

    def test_failed_tool_retains_stderr_and_other_evidence(self):
        self.analyzer.write_text(f"#!{sys.executable}\nimport sys\n"
                                 "print('bad dex', file=sys.stderr)\nsys.exit(7)\n")
        result = self.run_review()
        self.assertEqual(result.returncode, 2)
        data = self.evidence()
        self.assertEqual(data["commands"]["dex-packages"]["exit_code"], 7)
        self.assertIn("bad dex", (self.output / "dex-packages.stderr.txt").read_text())
        self.assertEqual(data["apk"]["sha256"], hashlib.sha256(self.original).hexdigest())

    def test_timeout_is_partial(self):
        self.analyzer.write_text(f"#!{sys.executable}\nimport time\ntime.sleep(2)\n")
        result = self.run_review("--timeout", "0.05")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.evidence()["commands"]["manifest"]["status"], "timeout")

    def test_malformed_successful_manifest_is_not_accepted(self):
        self.analyzer.write_text(f"#!{sys.executable}\nprint('not XML')\n")
        result = self.run_review()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.evidence()["commands"]["manifest"]["status"], "invalid_output")

    def test_existing_output_and_input_are_never_overwritten(self):
        self.output.mkdir()
        marker = self.output / "marker.txt"
        marker.write_text("prior review")
        result = self.run_review()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(marker.read_text(), "prior review")
        self.assertEqual(self.apk.read_bytes(), self.original)
        self.assertEqual(self.run_review(output=self.apk).returncode, 1)

    def test_output_inside_repo_or_symlink_to_repo_is_rejected(self):
        self.assertEqual(self.run_review(output=self.root / "results").returncode, 1)
        alias = self.parent / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(self.run_review(output=alias / "results").returncode, 1)
        self.assertFalse((self.root / "results").exists())

    def test_output_inside_another_worktree_is_rejected(self):
        other = self.parent / "another-worktree"
        self.git("worktree", "add", "--detach", str(other), "HEAD")
        result = self.run_review(output=other / "results")
        self.assertEqual(result.returncode, 1)
        self.assertFalse((other / "results").exists())

    def test_unknown_baseline_and_project_create_no_output(self):
        result = self.run_review(ref="unknown-version")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.output.exists())
        result = self.run_review("--project", "A99Unknown")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.output.exists())

    def test_head_requires_provisional_and_records_it(self):
        self.assertEqual(self.run_review(ref="HEAD").returncode, 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.run_review("--provisional", ref="HEAD").returncode, 0)
        self.assertTrue(self.evidence()["baseline"]["provisional"])

    def test_invalid_apk_creates_no_output(self):
        self.apk.write_bytes(b"not an apk")
        result = self.run_review()
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.output.exists())

    def test_zip_paths_cannot_escape_output(self):
        with ZipFile(self.apk, "a") as archive:
            archive.writestr("../escaped.xml", "not allowed")
        result = self.run_review()
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.output.exists())
        self.assertFalse((self.parent / "escaped.xml").exists())

    def test_sdk_analyzer_uses_numeric_version_order(self):
        spec = importlib.util.spec_from_file_location("student_apk_review", self.script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sdk = self.parent / "sdk"
        for version in ("9.0", "21.0"):
            executable = sdk / "cmdline-tools" / version / "bin/apkanalyzer"
            executable.parent.mkdir(parents=True)
            executable.write_text("fake executable")
            executable.chmod(0o755)
        with patch.object(module.shutil, "which", return_value=None), patch.dict(
                os.environ, {"ANDROID_HOME": str(sdk)}):
            self.assertEqual(module.find_analyzer(None),
                             str(sdk / "cmdline-tools/21.0/bin/apkanalyzer"))


if __name__ == "__main__":
    unittest.main()
