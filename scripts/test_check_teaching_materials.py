"""教材整合性検査の回帰テスト。"""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("check-teaching-materials.py")
SPEC = importlib.util.spec_from_file_location("check_teaching_materials", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class TeachingMaterialsCheckTest(unittest.TestCase):
    def test_repository_is_consistent(self):
        self.assertEqual(CHECKER.validate(ROOT), [])

    def test_forbidden_spelling_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "README.md").write_text("jec_26cm_android1_Pixel_9a\n", encoding="utf-8")
            (root / "config/teaching-materials.json").write_text(
                json.dumps({
                    "scan_roots": ["README.md"],
                    "terms": [{
                        "name": "指定AVD名",
                        "canonical": "jec_26cm_android1_Pixel 9a",
                        "forbidden": ["jec_26cm_android1_Pixel_9a"],
                        "required_in": []
                    }],
                    "projects": []
                }),
                encoding="utf-8",
            )
            errors = CHECKER.validate(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("README.md:1", errors[0])
            self.assertIn("禁止表記", errors[0])

    def test_missing_scan_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "config/teaching-materials.json").write_text(
                json.dumps({"scan_roots": ["missing"], "terms": [], "projects": []}),
                encoding="utf-8",
            )

            errors = CHECKER.validate(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("missing:1", errors[0])
            self.assertIn("検査対象のパスがありません", errors[0])

    def test_archive_executable_bit_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            project = root / "Sample"
            gradle = project / "gradlew"
            gradle.parent.mkdir(parents=True)
            gradle.write_text("#!/bin/sh\n", encoding="utf-8")
            gradle.chmod(0o755)
            (project / "app").mkdir()
            (project / "app/build.gradle.kts").write_text(
                'namespace = "jp.example.sample"\napplicationId = "jp.example.sample"\n',
                encoding="utf-8",
            )
            java = project / "app/src/main/java/MainActivity.java"
            java.parent.mkdir(parents=True)
            java.write_text("package jp.example.sample;\n", encoding="utf-8")
            xml = project / "app/src/main/res/layout/activity_main.xml"
            xml.parent.mkdir(parents=True)
            xml.write_text("<View />\n", encoding="utf-8")
            (root / "docs.html").write_text("Sample jp.example.sample", encoding="utf-8")

            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "add", "Sample"], cwd=root, check=True, capture_output=True)
            archive_path = root / "Sample.zip"
            with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
                for path in [gradle, project / "app/build.gradle.kts", java, xml]:
                    name = path.relative_to(root).as_posix()
                    info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    info.compress_type = ZIP_DEFLATED
                    archive.writestr(info, path.read_bytes())
            (root / "config/teaching-materials.json").write_text(
                json.dumps({
                    "scan_roots": [],
                    "terms": [],
                    "projects": [{
                        "name": "Sample",
                        "package": "jp.example.sample",
                        "root": "Sample",
                        "docs": ["docs.html"],
                        "source_java": "Sample/app/src/main/java/MainActivity.java",
                        "source_xml": "Sample/app/src/main/res/layout/activity_main.xml",
                        "snippets": [],
                        "archive": "Sample.zip",
                    }],
                }),
                encoding="utf-8",
            )

            errors = CHECKER.validate(root)

            self.assertTrue(any("実行権限が一致しません: Sample/gradlew" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
