"""完成版ZIPの生成条件と、配布対象の選別を検証する。"""

from pathlib import Path
import os
from shutil import copy2, which
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile


SCRIPT = Path(__file__).with_name("package-hello-android.py")
GIT = which("git")


@unittest.skipUnless(GIT, "テスト用リポジトリの作成にはGitが必要です。")
class PackageHelloAndroidTest(unittest.TestCase):
    """実際のGitと一時フォルダで、配布用スクリプトを実行する。"""

    def setUp(self):
        """各テスト専用のソースと既存ZIPを用意する。"""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name)
        self.root = self.parent / "source"
        (self.root / "scripts").mkdir(parents=True)
        copy2(SCRIPT, self.root / "scripts" / SCRIPT.name)
        self.output = self.root / "docs/hello-android/downloads/A01HelloAndroid.zip"
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"previous archive")

    def git(self, *args, cwd=None):
        """指定フォルダでGitを実行し、失敗はテストエラーにする。"""
        return subprocess.run(
            [GIT, *args], cwd=cwd or self.root, check=True,
            capture_output=True, text=True,
        )

    def run_package(self, *, env=None):
        """独立したPythonプロセスで配布スクリプトを実行する。"""
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / SCRIPT.name)],
            cwd=self.root, env=env, capture_output=True, text=True,
        )

    def assert_rejected(self, result, message):
        """日本語の案内を返し、既存ZIPを保持することを確認する。"""
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.output.read_bytes(), b"previous archive")

    def test_no_git_metadata(self):
        """GitHubのDownload ZIPに相当するフォルダを拒否する。"""
        self.assert_rejected(self.run_package(), "git clone")

    def test_source_inside_another_repository(self):
        """上位フォルダのGit管理情報を誤って使用しない。"""
        self.git("init", cwd=self.parent)
        self.assert_rejected(self.run_package(), "ルートではありません")

    def test_git_not_installed(self):
        """Gitが見つからない場合にインストールを案内する。"""
        env = dict(os.environ, PATH="")
        self.assert_rejected(self.run_package(env=env), "Gitが見つかりません")

    def test_no_tracked_project_files(self):
        """配布対象がない場合に既存ZIPを維持する。"""
        self.git("init")
        self.assert_rejected(self.run_package(), "プロジェクトが見つかりません")

    def test_tracked_sources_only_and_repeatable_archive(self):
        """編集済みの管理対象と実行権限を保持し、ローカル状態を除外する。"""
        self.git("init")
        project = self.root / "A01HelloAndroid"
        for name in [
            "app/src/main/MainActivity.java", "gradlew", "local.properties",
            ".idea/misc.xml", ".gradle/cache", ".kotlin/cache", "app/build/out",
        ]:
            path = project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("original")
        (project / "gradlew").chmod(0o755)
        self.git("add", "A01HelloAndroid")
        (project / "app/src/main/MainActivity.java").write_text("edited")
        (project / "untracked.txt").write_text("not for distribution")
        result = self.run_package()
        self.assertEqual(result.returncode, 0, result.stderr)
        with ZipFile(self.output) as archive:
            self.assertEqual(archive.namelist(), [
                "A01HelloAndroid/app/src/main/MainActivity.java",
                "A01HelloAndroid/gradlew",
            ])
            self.assertEqual(archive.read(archive.namelist()[0]), b"edited")
            mode = archive.getinfo("A01HelloAndroid/gradlew").external_attr >> 16
            self.assertTrue(mode & 0o111)
        first = self.output.read_bytes()
        self.assertEqual(self.run_package().returncode, 0)
        self.assertEqual(self.output.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
