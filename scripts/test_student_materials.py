"""配布物の境界、リンク切れ、GitHub公開の失敗・再実行を検証する。"""

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
from shutil import copy2
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile


SCRIPTS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("release", SCRIPTS / "release-student-materials.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

# JSTでは翌日になる時刻。配布物の名前が版タグと同じJSTの日付になることを確かめる。
FIXTURE_COMMITTED = "2026-09-19T15:30:00+00:00"
FIXTURE_STEM = "android1-student-materials-2026-09-20"


class PackageStudentMaterialsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "scripts").mkdir()
        for script in ("check-teaching-materials.py", "package-hello-android.py", "package-student-materials.py"):
            copy2(SCRIPTS / script, self.root / "scripts" / script)
        (self.root / "config").mkdir()
        (self.root / "config/teaching-materials.json").write_text(
            json.dumps({"scan_roots": [], "terms": [], "projects": []}), encoding="utf-8"
        )
        for name, text in {
            "docs/hello-android/index.html": '<a href="downloads/A01HelloAndroid.zip">完成版</a><img src="images/test.png">',
            "docs/hello-android/downloads/A01HelloAndroid.zip": "stale ZIP",
            "docs/hello-android/images/test.png": "image",
            "docs/.DS_Store": "finder settings",
            "teacher/index.html": "teacher only",
            "Panda2JavaEmptyViewActivity/MainActivity.java": "teacher template",
            "A01HelloAndroid/MainActivity.java": "original source",
            "A01HelloAndroid/gradlew": "#!/bin/sh",
            "A01HelloAndroid/.idea/misc.xml": "IDE settings",
            "A01HelloAndroid/local.properties": "local SDK",
        }.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        (self.root / "A01HelloAndroid/gradlew").chmod(0o755)
        self.git("init")
        self.git("add", ".")
        self.git(
            "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "fixture",
            env={"GIT_AUTHOR_DATE": FIXTURE_COMMITTED, "GIT_COMMITTER_DATE": FIXTURE_COMMITTED},
        )
        self.archive = self.root / f"dist/{FIXTURE_STEM}.zip"

    def git(self, *args, env=None):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True,
            env={**os.environ, **env} if env else None,
        )

    def package(self):
        return subprocess.run([sys.executable, "scripts/package-student-materials.py"], cwd=self.root, capture_output=True, text=True)

    def test_student_contents_regeneration_and_repeatable_zip(self):
        (self.root / "docs/untracked.txt").write_text("not for distribution")
        (self.root / "A01HelloAndroid/MainActivity.java").write_text("updated source")
        result = self.package()
        self.assertEqual(result.returncode, 0, result.stderr)
        prefix = f"{FIXTURE_STEM}/"
        with ZipFile(self.archive) as archive:
            names = archive.namelist()
            self.assertFalse(any("teacher" in name or "Panda2" in name or ".DS_Store" in name or "untracked" in name for name in names))
            self.assertIn(prefix + "はじめに.txt", names)
            self.assertIn(prefix + "VERSION.json", names)
            data = archive.read(prefix + "docs/hello-android/downloads/A01HelloAndroid.zip")
            with ZipFile(io.BytesIO(data)) as project:
                self.assertEqual(project.read("A01HelloAndroid/MainActivity.java"), b"updated source")
                self.assertFalse(any(".idea" in name or "local.properties" in name for name in project.namelist()))
                self.assertEqual(project.getinfo("A01HelloAndroid/gradlew").external_attr >> 16, 0o100755)
        first = self.archive.read_bytes()
        self.assertEqual(self.package().returncode, 0)
        self.assertEqual(self.archive.read_bytes(), first)
        checksum = (self.root / "dist/SHA256SUMS.txt").read_text()
        self.assertEqual(checksum.split()[0], hashlib.sha256(first).hexdigest())

    def test_asset_name_and_folder_carry_the_release_date(self):
        self.assertEqual(self.package().returncode, 0)
        with ZipFile(self.archive) as archive:
            names = archive.namelist()
        # 別の版を同じ場所に展開しても混ざらないよう、先頭フォルダにも日付を入れる。
        self.assertTrue(all(name.startswith(f"{FIXTURE_STEM}/") for name in names), names)
        checksum = (self.root / "dist/SHA256SUMS.txt").read_text()
        self.assertEqual(checksum.split()[1], self.archive.name)
        metadata = json.loads((self.root / "dist/release-metadata.json").read_text())
        self.assertEqual(metadata["asset"], self.archive.name)
        self.assertEqual(metadata["version"][:len("materials-2026.09.20")], "materials-2026.09.20")

    def test_missing_link_rejects_package(self):
        (self.root / "docs/hello-android/index.html").write_text('<a href="../missing.html">資料</a>')
        result = self.package()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("リンク先がありません", result.stderr)
        self.assertFalse(self.archive.exists())

    def test_link_to_teacher_rejects_package(self):
        (self.root / "docs/hello-android/index.html").write_text('<a href="../../teacher/index.html">教員用</a>')
        self.assertNotEqual(self.package().returncode, 0)

    def test_symlink_rejects_package(self):
        (self.root / "docs/private.txt").symlink_to(self.root / "teacher/index.html")
        self.git("add", "docs/private.txt")
        result = self.package()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("シンボリックリンク", result.stderr)


class StudentReleaseTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.dist = Path(temporary.name)
        self.repo = "owner/repo"
        self.asset = "android1-student-materials-2026-09-15.zip"
        self.metadata = {"version": "materials-2026.09.15-123456789abc", "revision": "123456789abc" * 3 + "1234", "asset": self.asset}
        (self.dist / self.asset).write_bytes(b"student package")
        (self.dist / release.CHECKSUMS).write_text(f"{hashlib.sha256(b'student package').hexdigest()}  {self.asset}\n")
        (self.dist / "release-notes.md").write_text("学生向けノート")
        self.enterContext(patch.object(release, "DIST", self.dist))
        self.enterContext(patch.dict(os.environ, {"GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/main", "STUDENT_NOTES": "STEP 4の説明修正。やり直し不要。"}))
        self.enterContext(patch.object(release, "summary"))
        self.gh = self.enterContext(patch.object(release, "gh", return_value=""))
        self.items = self.enterContext(patch.object(release, "releases", return_value=[]))
        self.api = self.enterContext(patch.object(release, "api", side_effect=self.api_response))

    def api_response(self, path, payload=None):
        if path.endswith("/commits/main"):
            return {"sha": self.metadata["revision"]}
        if "/git/matching-refs/" in path:
            return []
        if path.endswith("/generate-notes"):
            return {"body": "* HelloAndroidの説明を修正 #2"}
        raise AssertionError(f"Unexpected API: {path}")

    def test_first_publish_uploads_before_publication(self):
        release.publish(self.repo, self.metadata)
        commands = [call.args[:2] for call in self.gh.call_args_list]
        self.assertEqual(commands, [("release", "create"), ("release", "upload"), ("release", "edit")])
        self.assertIn("--draft", self.gh.call_args_list[0].args)
        self.assertIn(self.metadata["revision"], self.gh.call_args_list[0].args)
        # 添付するのは版の日付が入ったZIP。名前はrelease-metadata.jsonから受け取る。
        self.assertIn(str(self.dist / self.asset), self.gh.call_args_list[1].args)
        self.assertIn("--draft=false", self.gh.call_args_list[-1].args)

    def test_upload_failure_does_not_publish(self):
        def execute(*args, **kwargs):
            if args[:2] == ("release", "upload"):
                raise subprocess.CalledProcessError(1, "upload")
            return ""
        self.gh.side_effect = execute
        with self.assertRaises(subprocess.CalledProcessError):
            release.publish(self.repo, self.metadata)
        self.assertFalse(any("--draft=false" in call.args for call in self.gh.call_args_list))

    def test_existing_draft_resumes_without_creating_another(self):
        self.items.return_value = [{"tag_name": self.metadata["version"], "draft": True, "target_commitish": self.metadata["revision"]}]
        release.publish(self.repo, self.metadata)
        self.assertEqual([call.args[:2] for call in self.gh.call_args_list], [("release", "edit"), ("release", "upload"), ("release", "edit")])

    def test_published_release_is_not_overwritten(self):
        self.items.return_value = [{"tag_name": self.metadata["version"], "draft": False, "html_url": "https://github.com/owner/repo/releases/tag/materials-test"}]
        release.publish(self.repo, self.metadata)
        self.gh.assert_not_called()

    def test_main_changed_stops_before_mutation(self):
        self.api.side_effect = lambda *args: {"sha": "different revision"}
        with self.assertRaisesRegex(ValueError, "mainが更新"):
            release.publish(self.repo, self.metadata)
        self.gh.assert_not_called()

    def test_main_changed_during_upload_keeps_release_as_draft(self):
        def execute(*args, **kwargs):
            if args[:2] == ("release", "upload"):
                self.api.side_effect = lambda *args: {"sha": "updated during upload"}
            return ""
        self.gh.side_effect = execute
        with self.assertRaisesRegex(ValueError, "下書きの公開を中止"):
            release.publish(self.repo, self.metadata)
        self.assertEqual([call.args[:2] for call in self.gh.call_args_list], [("release", "create"), ("release", "upload")])

    def test_automatic_event_cannot_publish(self):
        with patch.dict(os.environ, {"GITHUB_EVENT_NAME": "push"}):
            with self.assertRaisesRegex(ValueError, "Run workflow"):
                release.publish(self.repo, self.metadata)
        self.gh.assert_not_called()

    def test_corrupt_package_cannot_publish(self):
        (self.dist / self.asset).write_bytes(b"corrupt package")
        with self.assertRaisesRegex(ValueError, "チェックサム"):
            release.publish(self.repo, self.metadata)
        self.gh.assert_not_called()

    def test_prepare_first_release_has_student_notes_and_direct_commits(self):
        with patch.object(release.subprocess, "check_output", return_value="- 直接修正 (abc123)"):
            release.prepare(self.repo, self.metadata)
        text = (self.dist / "release-notes.md").read_text()
        self.assertIn(f"**{self.asset}**", text)
        self.assertIn("STEP 4の説明修正。やり直し不要。", text)
        self.assertIn("HelloAndroidの説明を修正 #2", text)
        self.assertIn("直接修正", text)
        payload = self.api.call_args.args[1]
        self.assertEqual(payload["target_commitish"], self.metadata["revision"])
        self.assertNotIn("previous_tag_name", payload)
        self.gh.assert_not_called()

    def test_previous_release_ignores_drafts_prereleases_and_other_products(self):
        def item(tag, date, **kwargs):
            return {"tag_name": tag, "published_at": date, "draft": False, "prerelease": False, **kwargs}
        previous = item("materials-previous", "2026-09-14")
        items = [previous, item("other-product", "2026-09-15"), item("materials-draft", None, draft=True), item("materials-preview", "2026-09-15", prerelease=True), item(self.metadata["version"], "2026-09-15")]
        self.assertEqual(release.previous_release(items, self.metadata["version"]), previous)

    def test_notes_compare_against_last_published_materials(self):
        self.items.return_value = [{"tag_name": "materials-previous", "published_at": "2026-09-14", "draft": False, "prerelease": False}]
        base = "a" * 40
        self.api.side_effect = [{"sha": base}, {"body": "前回からのPR一覧"}]
        with patch.object(release.subprocess, "run") as ancestry, patch.object(release.subprocess, "check_output", return_value="- 追加修正 (def456)") as log:
            release.prepare(self.repo, self.metadata)
        payload = self.api.call_args.args[1]
        self.assertEqual(payload["previous_tag_name"], "materials-previous")
        self.assertEqual(log.call_args.args[0][-1], f"{base}..{self.metadata['revision']}")
        self.assertEqual(ancestry.call_args.args[0], ["git", "merge-base", "--is-ancestor", base, self.metadata["revision"]])

    def test_conflicting_tag_stops_before_mutation(self):
        self.api.side_effect = [
            {"sha": self.metadata["revision"]},
            [{"ref": f"refs/tags/{self.metadata['version']}"}],
            {"sha": "different revision"},
        ]
        with self.assertRaisesRegex(ValueError, "タグが別のコミット"):
            release.publish(self.repo, self.metadata)
        self.gh.assert_not_called()


if __name__ == "__main__":
    unittest.main()
