"""教材・完成プロジェクト・配布物の整合性を検査する。"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
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
        expected_names = {
            name for name in tracked_files(root, project["root"])
            if not any(part in IGNORED_ARCHIVE_PARTS for part in Path(name).parts)
            and Path(name).name != "local.properties"
        }
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
    for project in config["projects"]:
        check_project(root, project, errors)
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
