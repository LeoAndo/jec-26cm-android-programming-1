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

    def _project_root(self, root: Path, config: dict) -> None:
        """検査に必要な最小限のファイルを作る。"""
        (root / "config").mkdir(exist_ok=True)
        (root / "config/teaching-materials.json").write_text(
            json.dumps(config, ensure_ascii=False), encoding="utf-8"
        )

    def test_missing_registration_is_reported(self):
        """README・配布スクリプトのどちらかに単元が無いと検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text(
                "docs/x/index.html teacher/x/index.html docs/x/downloads/A01X.zip\n",
                encoding="utf-8",
            )
            # 配布スクリプト側にだけ単元の記載がない。
            (root / "pack.py").write_text("# 何も登録されていない\n", encoding="utf-8")
            self._project_root(root, {
                "scan_roots": ["README.md"],
                "terms": [{"name": "t", "canonical": "c", "forbidden": [],
                           "required_in": ["docs/x/index.html", "teacher/x/index.html"]}],
                "registration": {"targets": [
                    {"path": "README.md", "requires": ["student_doc", "teacher_doc", "archive"]},
                    {"path": "pack.py", "requires": ["student_doc", "archive"]},
                ]},
                "projects": [{
                    "name": "A01X", "package": "p", "root": "A01X",
                    "docs": ["docs/x/index.html", "teacher/x/index.html"],
                    "source_java": "A01X/j.java", "source_xml": "A01X/l.xml",
                    "snippets": [], "archive": "docs/x/downloads/A01X.zip",
                }],
            })
            errors = CHECKER.validate(root)
            self.assertTrue(
                any("pack.py" in e and "への参照がありません" in e for e in errors),
                errors,
            )

    def test_guidance_line_is_required(self):
        """案内文から単元が1つだけ抜けた場合も検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            # パスは含むが、案内文の行（A01 X：…）が無い。
            (root / "pack.py").write_text(
                "docs/x/index.html docs/x/downloads/A01X.zip\n", encoding="utf-8"
            )
            self._project_root(root, {
                "scan_roots": ["pack.py"],
                "terms": [{"name": "t", "canonical": "c", "forbidden": [], "required_in": []}],
                "registration": {"targets": [
                    {"path": "pack.py", "requires": ["guidance_line"]},
                ]},
                "projects": [{
                    "name": "A01X", "package": "p", "root": "A01X",
                    "docs": ["docs/x/index.html", "teacher/x/index.html"],
                    "source_java": "A01X/j.java", "source_xml": "A01X/l.xml",
                    "snippets": [], "archive": "docs/x/downloads/A01X.zip",
                }],
            })
            errors = CHECKER.validate(root)
            self.assertTrue(any("A01 X：docs/x/index.html" in e for e in errors), errors)

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

    def _image_root(self, root: Path, download: bytes, textbook: str,
                    download_name: str = "title.png", guidance: str | None = None) -> None:
        """配布ファイルの検査に必要な最小限のリポジトリを作る。"""
        source = root / "Sample/app/src/main/res/drawable/title.png"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"\x89PNG\r\n\x1a\n" + bytes(range(64)))
        (root / "docs/x/downloads").mkdir(parents=True)
        (root / "docs/x/downloads" / download_name).write_bytes(download)
        (root / "docs/x/index.html").write_text(textbook, encoding="utf-8")
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "add", "Sample"], cwd=root, check=True, capture_output=True)
        self._project_root(root, {
            "scan_roots": [],
            "terms": [],
            "projects": [{
                "name": "Sample", "package": "jp.example.sample", "root": "Sample",
                "docs": ["docs/x/index.html", "teacher/x/index.html"],
                "source_java": "Sample/j.java", "source_xml": "Sample/l.xml",
                "snippets": [], "archive": "docs/x/downloads/Sample.zip",
                "downloads": [dict({
                    "download": f"docs/x/downloads/{download_name}",
                    "source": "Sample/app/src/main/res/drawable/title.png",
                }, **({"guidance": guidance} if guidance else {}))],
            }],
        })

    def _image_errors(self, root: Path) -> list[str]:
        return [error for error in CHECKER.validate(root) if "配布ファイル" in error]

    def test_image_identical_to_source_is_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
            self._image_root(root, source, '<a href="downloads/title.png" download>title.png</a>')
            self.assertEqual(self._image_errors(root), [])

    def test_image_differing_by_one_byte_is_rejected(self):
        """配布ファイルが、完成プロジェクトのソースと1バイトでも違えば検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            changed = bytearray(b"\x89PNG\r\n\x1a\n" + bytes(range(64)))
            changed[-1] ^= 0x01
            self._image_root(root, bytes(changed), '<a href="downloads/title.png" download>title.png</a>')
            errors = self._image_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/x/downloads/title.png:1", errors[0])
            self.assertIn("内容が一致しません: Sample/app/src/main/res/drawable/title.png", errors[0])

    def test_image_without_textbook_link_is_rejected(self):
        """画像を置いただけで、教科書からリンクしていない状態を検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
            self._image_root(root, source, "<p>先生から配られた title.png を使います。</p>")
            errors = self._image_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/x/index.html:1", errors[0])
            self.assertIn("リンクがありません: downloads/title.png", errors[0])

    def test_image_link_without_download_attribute_is_rejected(self):
        """リンクはあっても download 属性がなければ検出する。属性の順番は問わない。"""
        source = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._image_root(root, source, '<p>1行目</p>\n<a class="button-link" href="downloads/title.png">title.png</a>')
            errors = self._image_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/x/index.html:2", errors[0])
            self.assertIn("download属性がありません: downloads/title.png", errors[0])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._image_root(root, source, '<a download class="button-link" href="downloads/title.png">title.png</a>')
            self.assertEqual(self._image_errors(root), [])

    def test_image_renamed_from_source_is_rejected(self):
        """学生は落としたファイルをそのままdrawableに入れるので、名前の違いも検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
            self._image_root(root, source, '<a href="downloads/Title.png" download>Title.png</a>',
                             download_name="Title.png")
            errors = self._image_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("ファイル名が一致しません", errors[0])

    def test_finder_guidance_is_accepted(self):
        """Finderで開かせる形では、置き場所のフォルダとファイル名が書いてあれば通る。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
            self._image_root(root, source,
                             "<p>書類 → 教材フォルダ → <code>docs → x → downloads</code> の title.png をコピーします。</p>",
                             guidance="finder")
            self.assertEqual(self._image_errors(root), [])

    def test_finder_guidance_without_folder_is_rejected(self):
        """置き場所の案内が教科書から消えたら検出する。学生はファイルを見つけられない。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
            self._image_root(root, source, "<p>title.png をコピーします。</p>", guidance="finder")
            errors = self._image_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("置き場所の案内がありません: docs → x → downloads", errors[0])

    def test_finder_guidance_without_file_name_is_rejected(self):
        """ファイル名の案内が消えたら検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
            self._image_root(root, source, "<p><code>docs → x → downloads</code> を開きます。</p>", guidance="finder")
            errors = self._image_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("ファイル名の案内がありません: title.png", errors[0])

    def test_finder_guidance_differing_from_source_is_rejected(self):
        """Finderで開かせる形でも、ソースとの一致は同じように検査する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            changed = bytearray(b"\x89PNG\r\n\x1a\n" + bytes(range(64)))
            changed[-1] ^= 0x01
            self._image_root(root, bytes(changed),
                             "<p><code>docs → x → downloads</code> の title.png をコピーします。</p>",
                             guidance="finder")
            errors = self._image_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("内容が一致しません: Sample/app/src/main/res/drawable/title.png", errors[0])

    def test_image_source_outside_archive_is_rejected(self):
        """元ファイルがGit管理されていなければ、完成プロジェクトZIPにも入らない。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
            self._image_root(root, source, '<a href="downloads/title.png" download>title.png</a>')
            subprocess.run(["git", "rm", "--cached", "-q", "Sample/app/src/main/res/drawable/title.png"],
                           cwd=root, check=True, capture_output=True)
            errors = self._image_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("完成プロジェクトZIPに入るファイルではありません", errors[0])


if __name__ == "__main__":
    unittest.main()
