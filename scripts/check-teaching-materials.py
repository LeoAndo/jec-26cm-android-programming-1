"""教材・完成プロジェクト・配布物の整合性を検査する。"""

from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
from zipfile import BadZipFile, ZipFile


CONFIG = Path("config/teaching-materials.json")
TEXT_SUFFIXES = {
    ".bat", ".css", ".gradle", ".html", ".java", ".js", ".json", ".kts",
    ".md", ".properties", ".py", ".sh", ".toml", ".txt", ".xml", ".yml",
    ".yaml",
}
IGNORED_PARTS = {".git", ".gradle", ".idea", ".kotlin", "__pycache__", "build", "dist"}
IGNORED_ARCHIVE_PARTS = {".gradle", ".idea", ".kotlin", "build"}


def display(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def line_of(text: str, needle: str) -> int:
    position = text.find(needle)
    return text.count("\n", 0, position) + 1 if position >= 0 else 1


def text_files(root: Path, scan_roots: list[str]):
    seen = set()
    for item in scan_roots:
        path = root / item
        if not path.exists():
            continue
        candidates = [path] if path.is_file() else path.rglob("*")
        for candidate in candidates:
            if not candidate.is_file() or candidate.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if any(part in IGNORED_PARTS for part in candidate.relative_to(root).parts):
                continue
            key = candidate.resolve()
            if key not in seen:
                seen.add(key)
                yield candidate


def tracked_files(root: Path, project_root: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", project_root],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError("git ls-filesを実行できません。Git cloneしたリポジトリで実行してください。")
    return [name for name in result.stdout.decode().split("\0") if name]


def archive_sources(root: Path, project_root: str) -> set[str]:
    """完成プロジェクトZIPに入れるファイル。Git管理下で、IDE設定やビルド出力でないもの。"""
    return {
        name for name in tracked_files(root, project_root)
        if not any(part in IGNORED_ARCHIVE_PARTS for part in Path(name).parts)
        and Path(name).name != "local.properties"
    }


def add(errors: list[str], root: Path, path: Path | str, line: int, message: str) -> None:
    shown = path if isinstance(path, str) else display(root, path)
    errors.append(f"{shown}:{line}: {message}")


def check_terms(root: Path, config: dict, errors: list[str]) -> None:
    for item in config["scan_roots"]:
        if not (root / item).exists():
            add(errors, root, item, 1, "表記揺れ検査対象のパスがありません")
    files = list(text_files(root, config["scan_roots"]))
    contents = {path: read(path) for path in files}
    for term in config["terms"]:
        for path, content in contents.items():
            for line_number, line in enumerate(content.splitlines(), 1):
                for forbidden in term.get("forbidden", []):
                    if forbidden in line:
                        add(errors, root, path, line_number, f"{term['name']}は{term['canonical']}を使用してください（禁止表記: {forbidden}）")
        for required in term.get("required_in", []):
            path = root / required
            if not path.is_file():
                add(errors, root, required, 1, "正式表記を確認する対象ファイルがありません")
                continue
            content = read(path)
            if term["canonical"] not in content:
                add(errors, root, path, 1, f"{term['name']}の正式表記がありません: {term['canonical']}")


def value_from_gradle(text: str, key: str) -> str | None:
    match = re.search(rf'^\s*{re.escape(key)}\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else None


def check_project(root: Path, project: dict, errors: list[str]) -> None:
    project_root = root / project["root"]
    gradle_path = project_root / "app/build.gradle.kts"
    java_path = root / project["source_java"]
    xml_path = root / project["source_xml"]
    if not gradle_path.is_file():
        add(errors, root, gradle_path, 1, "app/build.gradle.ktsがありません")
        return
    gradle = read(gradle_path)
    for key in ("namespace", "applicationId"):
        actual = value_from_gradle(gradle, key)
        if actual != project["package"]:
            add(errors, root, gradle_path, line_of(gradle, key), f"{key}が一致しません: {actual!r} != {project['package']!r}")
    if not java_path.is_file():
        add(errors, root, java_path, 1, "MainActivity.javaがありません")
    else:
        java = read(java_path)
        match = re.search(r"^package\s+([\w.]+);", java, re.MULTILINE)
        actual = match.group(1) if match else None
        if actual != project["package"]:
            add(errors, root, java_path, line_of(java, "package"), f"Javaのpackageが一致しません: {actual!r} != {project['package']!r}")
    if not xml_path.is_file():
        add(errors, root, xml_path, 1, "activity_main.xmlがありません")

    for doc_name in project["docs"]:
        path = root / doc_name
        if not path.is_file():
            add(errors, root, path, 1, "教材ファイルがありません")
            continue
        content = read(path)
        for required in (project["name"], project["package"]):
            if required not in content:
                add(errors, root, path, 1, f"教材に必要な表記がありません: {required}")

    for snippet in project["snippets"]:
        html_path = root / snippet["html"]
        source_path = root / snippet["source"]
        if not html_path.is_file() or not source_path.is_file():
            continue
        document = read(html_path)
        match = re.search(rf'<pre\s+id="{re.escape(snippet["id"])}"[^>]*><code>(.*?)</code></pre>', document, re.DOTALL)
        if not match:
            add(errors, root, html_path, 1, f"コードスニペットがありません: {snippet['id']}")
            continue
        expected = read(source_path).rstrip()
        actual = html.unescape(match.group(1)).rstrip()
        if actual != expected:
            add(errors, root, html_path, line_of(document, f'id="{snippet["id"]}"'), f"{snippet['id']}と{snippet['source']}が一致しません")

    archive_path = root / project["archive"]
    if not archive_path.is_file():
        add(errors, root, archive_path, 1, "完成プロジェクトZIPがありません")
        return
    try:
        expected_names = archive_sources(root, project["root"])
        with ZipFile(archive_path) as archive:
            actual_names = set(archive.namelist())
            for name in sorted(expected_names - actual_names):
                add(errors, root, archive_path, 1, f"ZIPにソースがありません: {name}")
            for name in sorted(actual_names - expected_names):
                add(errors, root, archive_path, 1, f"ZIPに配布対象外ファイルがあります: {name}")
            for name in sorted(expected_names & actual_names):
                source = root / name
                if archive.read(name) != source.read_bytes():
                    add(errors, root, archive_path, 1, f"ZIPとソースの内容が一致しません: {name}")
                source_executable = bool(source.stat().st_mode & 0o100)
                archive_executable = bool((archive.getinfo(name).external_attr >> 16) & 0o100)
                if archive_executable != source_executable:
                    add(errors, root, archive_path, 1, f"ZIPとソースの実行権限が一致しません: {name}")
    except (BadZipFile, OSError) as error:
        add(errors, root, archive_path, 1, f"ZIPを読み込めません: {error}")



class AnchorLinks(HTMLParser):
    """<a> のリンク先を集める。download 属性が付いているものは別に覚える。"""

    def __init__(self):
        super().__init__()
        self.hrefs: set[str] = set()
        self.downloads: set[str] = set()

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        values = dict(attrs)
        href = values.get("href")
        if not href:
            return
        self.hrefs.add(href)
        if "download" in values:
            self.downloads.add(href)


def check_images(root: Path, project: dict, errors: list[str]) -> None:
    """教科書から直接ダウンロードさせる画像が、完成プロジェクトの画像と同じか確かめる。

    ZIPの検査が「ZIPの中身＝ソース」を保証するので、ここで「配布画像＝ソース」を確かめれば、
    学生がどちらから取っても同じ画像になる。
    """
    images = project.get("images", [])
    if not images:
        return
    sources = archive_sources(root, project["root"])
    textbook_name = project["docs"][0]
    textbook_path = root / textbook_name
    textbook = read(textbook_path) if textbook_path.is_file() else None
    links = AnchorLinks()
    if textbook is not None:
        links.feed(textbook)
    for image in images:
        download_path = root / image["download"]
        source_path = root / image["source"]
        if Path(image["download"]).name != Path(image["source"]).name:
            # 学生は落としたファイルをそのままdrawableに入れる。名前が違うと @drawable/… が解決できない。
            add(errors, root, image["download"], 1, f"配布画像とソースのファイル名が一致しません: {image['source']}")
        if image["source"] not in sources:
            add(errors, root, image["source"], 1, "配布画像の元ファイルが、完成プロジェクトZIPに入るファイルではありません")
        elif not download_path.is_file():
            add(errors, root, image["download"], 1, "配布画像がありません")
        else:
            try:
                if download_path.read_bytes() != source_path.read_bytes():
                    add(errors, root, download_path, 1, f"配布画像とソースの内容が一致しません: {image['source']}（ソースからコピーし直してください）")
            except OSError as error:
                add(errors, root, download_path, 1, f"配布画像を読み込めません: {error}")
        if textbook is not None:
            link = posixpath.relpath(image["download"], posixpath.dirname(textbook_name))
            if link not in links.hrefs:
                add(errors, root, textbook_path, 1, f"配布画像へのリンクがありません: {link}")
            elif link not in links.downloads:
                # download がないと、httpで配信したときも保存されず、画像がブラウザに表示される。
                add(errors, root, textbook_path, line_of(textbook, f'href="{link}"'), f"配布画像へのリンクにdownload属性がありません: {link}")


def _split_unit(name: str) -> tuple[str, str]:
    """A09MemoApp を ("A09", "MemoApp") に分ける。"""
    match = re.match(r"^(A\d+)(.*)$", name)
    return (match.group(1), match.group(2)) if match else (name, name)


def check_registration(root: Path, config: dict, errors: list[str]) -> None:
    """単元が設定・README・配布スクリプトのすべてに登録されているか確かめる。"""
    setting = config.get("registration")
    if not setting:
        return
    scan_roots = set(config["scan_roots"])
    required_in = {name for term in config["terms"] for name in term.get("required_in", [])}
    targets = []
    for target in setting["targets"]:
        path = root / target["path"]
        if not path.is_file():
            add(errors, root, target["path"], 1, "登録確認の対象ファイルがありません")
            continue
        targets.append((target["path"], read(path), target["requires"]))
    for project in config["projects"]:
        name = project["name"]
        if project["root"] not in scan_roots:
            add(errors, root, CONFIG.as_posix(), 1, f"{name}がscan_rootsにありません")
        for doc in project["docs"]:
            if doc not in required_in:
                add(errors, root, CONFIG.as_posix(), 1, f"{name}の{doc}がterms.required_inにありません")
        number, label = _split_unit(name)
        paths = {
            "student_doc": project["docs"][0],
            "teacher_doc": project["docs"][1],
            "archive": project["archive"],
            # 案内文の1行。単元がどこか1か所だけ抜ける事故を捕まえる。
            "guidance_line": f"{number} {label}：{project['docs'][0]}",
        }
        for shown, content, requires in targets:
            for key in requires:
                needed = paths[key]
                if needed not in content:
                    add(errors, root, shown, 1, f"{name}の{needed}への参照がありません")


def check_project_layout(root: Path, config: dict, errors: list[str]) -> None:
    """単元プロジェクトの.gitignoreと、追跡してはいけないファイルを確かめる。"""
    setting = config.get("project_layout")
    if not setting:
        return
    reference_path = root / setting["gitignore_reference"]
    if not reference_path.is_file():
        add(errors, root, setting["gitignore_reference"], 1, ".gitignoreの基準ファイルがありません")
        return
    reference = read(reference_path)
    parts = set(setting.get("untracked_parts", []))
    names = set(setting.get("untracked_names", []))
    for project in config["projects"]:
        path = root / project["root"] / ".gitignore"
        if not path.is_file():
            add(errors, root, path, 1, ".gitignoreがありません")
        elif read(path) != reference:
            add(errors, root, path, 1, f"{setting['gitignore_reference']}と内容が異なります")
        for name in tracked_files(root, project["root"]):
            tracked = Path(name)
            if parts.intersection(tracked.parts) or tracked.name in names:
                add(errors, root, name, 1, "Git管理してはいけないファイルです")


def validate(root: Path) -> list[str]:
    config_path = root / CONFIG
    if not config_path.is_file():
        return [f"{CONFIG}:1: 設定ファイルがありません"]
    try:
        config = json.loads(read(config_path))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{CONFIG}:1: 設定ファイルを読み込めません: {error}"]
    errors: list[str] = []
    check_terms(root, config, errors)
    check_registration(root, config, errors)
    check_project_layout(root, config, errors)
    for project in config["projects"]:
        check_project(root, project, errors)
        check_images(root, project, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("教材整合性チェック: NG", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("教材整合性チェック: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
