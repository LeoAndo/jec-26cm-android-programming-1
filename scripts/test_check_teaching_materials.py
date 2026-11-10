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
        """README・登録対象ファイルのどちらかに単元が無いと検出する。"""
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

    PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
    # 置き場所とファイル名を、同じSTEP（<section>）に書いた教科書。
    GUIDE = ('<section id="step-2"><ol><li>教材のフォルダの <code>docs → x → downloads</code> を開きます。</li>'
             "<li><code>title.png</code> をコピーします。</li></ol></section>")

    def _download_root(self, root: Path, download: bytes, textbook: str,
                       download_name: str = "title.png") -> None:
        """配布ファイルの検査に必要な最小限のリポジトリを作る。"""
        source = root / "Sample/app/src/main/res/drawable/title.png"
        source.parent.mkdir(parents=True)
        source.write_bytes(self.PNG)
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
                "downloads": [{
                    "download": f"docs/x/downloads/{download_name}",
                    "source": "Sample/app/src/main/res/drawable/title.png",
                }],
            }],
        })

    def _download_errors(self, root: Path) -> list[str]:
        return [error for error in CHECKER.validate(root) if "配布ファイル" in error]

    def test_download_identical_to_source_is_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._download_root(root, self.PNG, self.GUIDE)
            self.assertEqual(self._download_errors(root), [])

    def test_download_folder_written_as_separate_codes_is_accepted(self):
        """置き場所は、フォルダ名を1つずつ <code> で囲んでも、途中で改行しても通る。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._download_root(
                root, self.PNG,
                "<section><p><code>docs</code> →\n  <code>x</code> → <code>downloads</code> の title.png をコピーします。</p></section>")
            self.assertEqual(self._download_errors(root), [])

    def test_download_differing_by_one_byte_is_rejected(self):
        """配布ファイルが、完成プロジェクトのソースと1バイトでも違えば検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            changed = bytearray(self.PNG)
            changed[-1] ^= 0x01
            self._download_root(root, bytes(changed), self.GUIDE)
            errors = self._download_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/x/downloads/title.png:1", errors[0])
            self.assertIn("内容が一致しません: Sample/app/src/main/res/drawable/title.png", errors[0])

    def test_download_without_folder_guidance_is_rejected(self):
        """置き場所の案内が教科書から消えたら検出する。学生はファイルを見つけられない。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._download_root(root, self.PNG, "<section><p>先生から配られた title.png を使います。</p></section>")
            errors = self._download_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/x/index.html:1", errors[0])
            self.assertIn("置き場所の案内がありません: docs → x → downloads", errors[0])

    def test_download_button_is_not_guidance(self):
        """ダウンロードボタンだけでは通らない。file:// で開いた教科書では、押しても保存されない。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._download_root(
                root, self.PNG,
                '<section><a class="button-link" href="downloads/title.png" download>title.png</a></section>')
            errors = self._download_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("置き場所の案内がありません: docs → x → downloads", errors[0])

    def test_download_without_file_name_is_rejected(self):
        """ファイル名の案内が消えたら検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._download_root(root, self.PNG, "<section><p><code>docs → x → downloads</code> を開きます。</p></section>")
            errors = self._download_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("ファイル名の案内がありません: title.png", errors[0])

    def test_download_guided_only_in_another_step_is_rejected(self):
        """置き場所が別のSTEPにしか書かれていなければ検出する。

        同じフォルダのファイルを別々のSTEPで使うとき、片方のSTEPから置き場所の案内が消えても、
        教科書全体で探すと見つかってしまう。
        """
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._download_root(
                root, self.PNG,
                '<section id="step-2"><p>title.png をdrawableに入れます。</p></section>'
                '<section id="step-7"><p><code>docs → x → downloads</code> の Other.java をコピーします。</p></section>')
            errors = self._download_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("ファイル名の案内がありません: title.png", errors[0])
            self.assertIn("同じSTEP", errors[0])

    def test_download_renamed_from_source_is_rejected(self):
        """学生はコピーしたファイルをそのままdrawableに入れるので、名前の違いも検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._download_root(root, self.PNG, self.GUIDE.replace("title.png", "Title.png"),
                                download_name="Title.png")
            errors = self._download_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("ファイル名が一致しません", errors[0])

    def test_download_source_outside_archive_is_rejected(self):
        """元ファイルがGit管理されていなければ、完成プロジェクトZIPにも入らない。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._download_root(root, self.PNG, self.GUIDE)
            subprocess.run(["git", "rm", "--cached", "-q", "Sample/app/src/main/res/drawable/title.png"],
                           cwd=root, check=True, capture_output=True)
            errors = self._download_errors(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("完成プロジェクトZIPに入るファイルではありません", errors[0])

    SIDEBAR_UNITS = [("A01One", "one"), ("A02Two", "two"), ("A03Three", "three")]

    def _sidebar(self, current: str, order: list[str] | None = None, link_self: bool = False) -> str:
        """3単元ぶんのサイドバーを作る。current はいま開いている単元のフォルダ名。"""
        names = dict((folder, name) for name, folder in self.SIDEBAR_UNITS)
        entries = []
        for folder in order or [folder for _, folder in self.SIDEBAR_UNITS]:
            label = f"{names[folder][:3]}：{names[folder][3:]}"
            if folder == current and not link_self:
                entries.append(f'<span aria-current="page">{label}</span>')
            else:
                entries.append(f'<a href="../{folder}/index.html">{label}</a>')
        return ('<aside class="sidebar"><div class="progress"><span>0 / 3</span></div>\n'
                '<div class="resources"><a href="#help">困ったとき</a>' + "".join(entries)
                + f'<a href="../common/setup.html?from={current}">共通：はじめの準備</a></div></aside>')

    def _sidebar_errors(self, root: Path, textbooks: dict[str, str]) -> list[str]:
        """教科書を書き出して検査し、サイドバーについてのエラーだけを返す。"""
        for folder, content in textbooks.items():
            (root / "docs" / folder).mkdir(parents=True)
            (root / "docs" / folder / "index.html").write_text(content, encoding="utf-8")
        self._project_root(root, {
            "scan_roots": [],
            "terms": [],
            "projects": [{
                "name": name, "package": "p", "root": name,
                "docs": [f"docs/{folder}/index.html", f"teacher/{folder}/index.html"],
                "source_java": f"{name}/j.java", "source_xml": f"{name}/l.xml",
                "snippets": [], "archive": f"docs/{folder}/downloads/{name}.zip",
            } for name, folder in self.SIDEBAR_UNITS],
        })
        return [error for error in CHECKER.validate(root) if "サイドバー" in error]

    def test_sidebar_listing_every_unit_is_accepted(self):
        """どの単元でも全単元が並び、いま開いている単元だけが現在地になっている。"""
        with tempfile.TemporaryDirectory() as temporary:
            errors = self._sidebar_errors(Path(temporary), {
                folder: self._sidebar(folder) for _, folder in self.SIDEBAR_UNITS
            })
            self.assertEqual(errors, [])

    def test_sidebar_missing_later_unit_is_rejected(self):
        """単元を足したのに、前の単元のサイドバーを直し忘れた状態を検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            textbooks = {folder: self._sidebar(folder) for _, folder in self.SIDEBAR_UNITS}
            textbooks["one"] = self._sidebar("one", order=["one", "two"])
            errors = self._sidebar_errors(Path(temporary), textbooks)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/one/index.html:2", errors[0])
            self.assertIn('単元へのリンクがありません: <a href="../three/index.html">A03：Three</a>', errors[0])

    def test_sidebar_linking_current_unit_is_rejected(self):
        """いま開いている単元は、リンクではなく現在地として示す。"""
        with tempfile.TemporaryDirectory() as temporary:
            textbooks = {folder: self._sidebar(folder) for _, folder in self.SIDEBAR_UNITS}
            textbooks["two"] = self._sidebar("two", link_self=True)
            errors = self._sidebar_errors(Path(temporary), textbooks)
            self.assertEqual(len(errors), 2, errors)
            self.assertIn('現在地がありません: <span aria-current="page">A02：Two</span>', errors[0])
            self.assertIn("いま開いている単元がリンクになっています: A02：Two", errors[1])

    def test_sidebar_in_wrong_order_is_rejected(self):
        """過不足がなくても、projects の順に並んでいなければ検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            textbooks = {folder: self._sidebar(folder) for _, folder in self.SIDEBAR_UNITS}
            textbooks["three"] = self._sidebar("three", order=["two", "one", "three"])
            errors = self._sidebar_errors(Path(temporary), textbooks)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("projectsの順に並んでいません: A02：Two、A01：One、A03：Three", errors[0])

    def test_sidebar_with_unregistered_unit_is_rejected(self):
        """projects にない単元へのリンクが残っている状態を検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            textbooks = {folder: self._sidebar(folder) for _, folder in self.SIDEBAR_UNITS}
            textbooks["one"] = textbooks["one"].replace(
                '<a href="../common/', '<a href="../four/index.html">A04：Four</a><a href="../common/', 1)
            errors = self._sidebar_errors(Path(temporary), textbooks)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("登録のない単元があります: A04：Four（../four/index.html）", errors[0])

    def test_sidebar_with_duplicated_unit_is_rejected(self):
        """単元を足すときのコピーで、同じ単元が2回並んだ状態を検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            textbooks = {folder: self._sidebar(folder) for _, folder in self.SIDEBAR_UNITS}
            textbooks["two"] = self._sidebar("two", order=["one", "one", "two", "three"])
            errors = self._sidebar_errors(Path(temporary), textbooks)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("projectsの順に並んでいません: A01：One、A01：One、A02：Two、A03：Three", errors[0])

    def test_sidebar_with_link_around_current_unit_is_rejected(self):
        """現在地をリンクで包むと、リンクにしない決まりをすり抜けるので検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            textbooks = {folder: self._sidebar(folder) for _, folder in self.SIDEBAR_UNITS}
            textbooks["two"] = textbooks["two"].replace(
                '<span aria-current="page">A02：Two</span>',
                '<a href="../two/index.html"><span aria-current="page">A02：Two</span></a>', 1)
            errors = self._sidebar_errors(Path(temporary), textbooks)
            self.assertTrue(any("単元の中に、別のタグがあります: <span>" in error for error in errors), errors)
            self.assertTrue(any("いま開いている単元がリンクになっています: A02：Two" in error for error in errors), errors)

    def test_sidebar_ignores_topbar_and_nested_div(self):
        """topbarの単元リンクは検査しない。resources の中の <div> は、サイドバーの終わりと取り違えない。"""
        with tempfile.TemporaryDirectory() as temporary:
            textbooks = {folder: self._sidebar(folder) for _, folder in self.SIDEBAR_UNITS}
            textbooks["two"] = (
                '<header class="topbar"><a href="../one/index.html">A01 One</a></header>\n'
                + textbooks["two"].replace(
                    '<a href="../one/index.html">A01：One</a>',
                    '<div class="group"><a href="../one/index.html">A01：One</a></div>', 1))
            errors = self._sidebar_errors(Path(temporary), textbooks)
            self.assertEqual(errors, [])

    def test_projects_out_of_unit_number_order_are_rejected(self):
        """サイドバーは projects の順と照合するので、projects が単元番号順でなければ検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._project_root(root, {
                "scan_roots": [],
                "terms": [],
                "projects": [{
                    "name": name, "package": "p", "root": name,
                    "docs": [f"docs/{name}/index.html", f"teacher/{name}/index.html"],
                    "source_java": f"{name}/j.java", "source_xml": f"{name}/l.xml",
                    "snippets": [], "archive": f"docs/{name}/downloads/{name}.zip",
                } for name in ["A01One", "A03Three", "A02Two"]],
            })
            errors = [error for error in CHECKER.validate(root) if "単元番号順" in error]
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("config/teaching-materials.json:1", errors[0])
            self.assertIn("A03ThreeのあとにA02Twoがあります", errors[0])

    def test_textbook_without_sidebar_is_rejected(self):
        """サイドバーそのものがない教科書は、並びを確かめようがないので検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            textbooks = {folder: self._sidebar(folder) for _, folder in self.SIDEBAR_UNITS}
            textbooks["two"] = "<main><h1>Two</h1></main>"
            errors = self._sidebar_errors(Path(temporary), textbooks)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/two/index.html:1", errors[0])
            self.assertIn("サイドバー（<div class=\"resources\">）がありません", errors[0])

    def _guidance_errors(self, root: Path, pages: dict[str, str]) -> list[str]:
        """docs/ にページを書き出して検査し、完成プロジェクトへの案内についてのエラーだけを返す。"""
        for name, content in pages.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(content, encoding="utf-8")
        self._project_root(root, {
            "scan_roots": [], "terms": [],
            "projects": [{
                "name": "A01One", "package": "p", "root": "A01One",
                "docs": ["docs/one/index.html", "teacher/one/index.html"],
                "source_java": "A01One/j.java", "source_xml": "A01One/l.xml",
                "snippets": [], "archive": "docs/one/downloads/A01One.zip",
            }],
        })
        return [error for error in CHECKER.validate(root) if "README「授業用教科書の基本方針」10" in error]

    def test_textbook_without_sample_guidance_is_accepted(self):
        """画像の置き場所（downloads/）へのリンクや、属性の中の語は案内にあたらない。"""
        with tempfile.TemporaryDirectory() as temporary:
            errors = self._guidance_errors(Path(temporary), {
                "docs/one/index.html": '<p><a href="downloads/title.png">画像</a></p>\n<img src="images/samples.png" alt="">',
            })
            self.assertEqual(errors, [])

    def test_sample_guidance_words_are_rejected(self):
        """本文に「完成プロジェクト」「samples」が出たら、共通資料でも検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            errors = self._guidance_errors(Path(temporary), {
                "docs/one/index.html": "<p>見比べるときは</p>\n<p>完成プロジェクトを開きます。</p>",
                "docs/common/help.html": "<p><code>samples</code> フォルダを開きます。</p>",
            })
            self.assertEqual(len(errors), 2, errors)
            self.assertIn("docs/common/help.html:1", errors[0])
            self.assertIn("samples", errors[0])
            self.assertIn("docs/one/index.html:2", errors[1])
            self.assertIn("完成プロジェクト", errors[1])

    def test_link_to_project_archive_is_rejected(self):
        """完成プロジェクトZIPへのリンクは、文言にかかわらず検出する。別ページからの相対パスも解決する。"""
        with tempfile.TemporaryDirectory() as temporary:
            errors = self._guidance_errors(Path(temporary), {
                "docs/one/index.html": '<a href="downloads/A01One.zip" download>答え</a>',
                "docs/common/help.html": '<a href="../one/downloads/A01One.zip?from=x">見本</a>',
                "docs/common/setup.html": "<a href='../one/downloads/A01One.zip'>見本</a>",
                "docs/common/apk.html": '<a href="https://example.com/downloads/A01One.zip">見本</a>',
            })
            self.assertEqual(len(errors), 4, errors)
            self.assertIn("docs/common/apk.html:1", errors[0])  # 絶対URLでも拾う
            self.assertIn("docs/common/help.html:1", errors[1])
            self.assertIn("docs/common/setup.html:1", errors[2])  # 単一引用符の属性も拾う
            self.assertIn("docs/one/index.html:1", errors[3])
            self.assertTrue(all("完成プロジェクトZIPへリンク" in error for error in errors), errors)

    # コピーボタンを付けてよい、ただ1つのコードブロック（見出しの直後の <pre>）。
    COPY_BLOCK = ('<div class="code-head">Long.java · 全体を置き換える</div>\n'
                  '<pre id="code-long" tabindex="0" data-copy-button><code>class Long {}</code></pre>\n')
    # どのページの末尾にもある通知欄。名前は似ているが、コピーボタンの指定ではない。
    COPY_STATUS = '<p class="sr-only" role="status" aria-live="polite" data-copy-status></p>\n'

    def _copy_button_errors(self, root: Path, pages: dict[str, str], allowed: bool = True) -> list[str]:
        """docs/ にページを書き出して検査し、コピーボタンについてのエラーだけを返す。"""
        for name, content in pages.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(content, encoding="utf-8")
        snippet = {"html": "docs/one/index.html", "id": "code-long", "source": "A01One/Long.java"}
        if allowed:
            snippet["copy_button"] = True
        self._project_root(root, {
            "scan_roots": [], "terms": [],
            "projects": [{
                "name": "A01One", "package": "p", "root": "A01One",
                "docs": ["docs/one/index.html", "teacher/one/index.html"],
                "source_java": "A01One/j.java", "source_xml": "A01One/l.xml",
                "snippets": [snippet], "archive": "docs/one/downloads/A01One.zip",
            }],
        })
        return [error for error in CHECKER.validate(root) if "コピーボタン" in error]

    def test_copy_button_on_the_allowed_block_is_accepted(self):
        """設定で認めたコードブロックだけに指定があれば通る。末尾の通知欄（data-copy-status）は指定と取り違えない。"""
        with tempfile.TemporaryDirectory() as temporary:
            errors = self._copy_button_errors(Path(temporary), {
                "docs/one/index.html": self.COPY_BLOCK + self.COPY_STATUS,
                "docs/common/apk.html": '<div class="code-head">Terminal</div>\n<pre tabindex="0"><code>ls</code></pre>\n' + self.COPY_STATUS,
            })
            self.assertEqual(errors, [])

    def test_copy_button_on_other_blocks_is_rejected(self):
        """特例のほかのコードブロックに指定を足したら、同じページでも共通資料でも検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            errors = self._copy_button_errors(Path(temporary), {
                "docs/one/index.html": self.COPY_BLOCK
                + '<div class="code-head">Main.java</div>\n<pre id="code-main" data-copy-button><code>x</code></pre>',
                "docs/common/apk.html": '<div class="code-head">Terminal</div>\n<pre data-copy-button><code>ls</code></pre>',
            })
            self.assertEqual(len(errors), 2, errors)
            self.assertIn("docs/common/apk.html:2", errors[0])
            self.assertIn("<pre> の data-copy-button を外してください", errors[0])
            self.assertIn("docs/one/index.html:4", errors[1])
            self.assertIn('<pre id="code-main"> の data-copy-button を外してください', errors[1])
            self.assertTrue(all("README「授業用教科書の基本方針」9" in error for error in errors), errors)

    def test_copy_button_without_setting_is_rejected(self):
        """設定に "copy_button": true がなければ、snippets に載っているコードでも特例にしない。"""
        with tempfile.TemporaryDirectory() as temporary:
            errors = self._copy_button_errors(Path(temporary), {"docs/one/index.html": self.COPY_BLOCK}, allowed=False)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/one/index.html:2", errors[0])
            self.assertIn("コードのコピーボタンは付けません", errors[0])

    def test_missing_copy_button_mark_is_rejected(self):
        """指定が消えるとボタンが出なくなり、教科書の「コピーボタンを押します」が実行できなくなる。"""
        with tempfile.TemporaryDirectory() as temporary:
            errors = self._copy_button_errors(Path(temporary), {
                "docs/one/index.html": self.COPY_BLOCK.replace(" data-copy-button", "") + self.COPY_STATUS,
            })
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/one/index.html:1", errors[0])
            self.assertIn("コピーボタンの指定（data-copy-button）がありません: code-long", errors[0])

    def test_copy_button_mark_away_from_code_head_is_rejected(self):
        """見出しの直後の <pre> でなければ、textbook.js はボタンを作らない。"""
        between = self.COPY_BLOCK.replace("</div>\n", "</div>\n<p>メモ</p>\n")
        on_head = ('<div class="code-head" id="code-long" data-copy-button>Long.java</div>\n'
                   "<pre><code>class Long {}</code></pre>")
        for label, content in (("見出しとのあいだに段落", between), ("見出しに指定", on_head)):
            with self.subTest(label), tempfile.TemporaryDirectory() as temporary:
                errors = self._copy_button_errors(Path(temporary), {"docs/one/index.html": content})
                self.assertEqual(len(errors), 1, errors)
                self.assertIn('<div class="code-head"> の直後の <pre> に付けてください', errors[0])

    def test_duplicated_copy_button_mark_is_rejected(self):
        """同じidのコードブロックを写して、ボタンが2つになった状態を検出する。"""
        with tempfile.TemporaryDirectory() as temporary:
            errors = self._copy_button_errors(Path(temporary), {"docs/one/index.html": self.COPY_BLOCK * 2})
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/one/index.html:4", errors[0])
            self.assertIn("2回あります: code-long", errors[0])

    def test_copy_button_exception_is_only_billsplitter(self):
        """コピーボタンの特例は、A07のBillSplitter.javaの全体コードだけ（README「授業用教科書の基本方針」9）。

        特例を増やすときは、オーナーの判断を得て、READMEの方針9とこのテストをいっしょに直す。
        """
        config = json.loads((ROOT / "config/teaching-materials.json").read_text(encoding="utf-8"))
        allowed = [(snippet["html"], snippet["id"]) for project in config["projects"]
                   for snippet in project["snippets"] if snippet.get("copy_button")]
        self.assertEqual(allowed, [("docs/bill-splitter/index.html", "code-billsplitter")])


if __name__ == "__main__":
    unittest.main()
