"""学生向けdocs一式を、完成プロジェクトを再生成してZIPにまとめる。"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import subprocess
import sys
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
ASSET_NAME = "android1-student-materials.zip"
EXCLUDED = {".git", ".idea", ".gradle", ".kotlin", "build", "local.properties", ".DS_Store", "__pycache__"}


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key in {"href", "src"} and value)


def check_links(files):
    """収録したHTMLの相対リンク先が、配布物の中にも存在するか確認する。"""
    for name, data in files.items():
        if not name.endswith(".html"):
            continue
        parser = LocalLinks()
        parser.feed(data.decode("utf-8"))
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(url.path)))
            if target not in files:
                raise ValueError(f"配布物内にリンク先がありません：{name} → {link}")


def build(output_dir):
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    timestamp = subprocess.check_output(["git", "show", "-s", "--format=%ct", "HEAD"], cwd=ROOT, text=True).strip()
    date = datetime.fromtimestamp(int(timestamp), timezone(timedelta(hours=9))).strftime("%Y.%m.%d")
    version = f"materials-{date}-{revision[:12]}"

    # リポジトリ内の古いZIPをそのまま配布せず、現在の完成コードを反映する。
    projects = [("A01HelloAndroid", "docs/hello-android/downloads/A01HelloAndroid.zip")]
    if (ROOT / "A02CalcGame").exists():
        projects.append(("A02CalcGame", "docs/calc-game/downloads/A02CalcGame.zip"))
    if (ROOT / "A03RockPaperScissorsGame").exists():
        projects.append((
            "A03RockPaperScissorsGame",
            "docs/rock-paper-scissors-game/downloads/A03RockPaperScissorsGame.zip",
        ))
    if (ROOT / "A04WebViewApp").exists():
        projects.append(("A04WebViewApp", "docs/webview-app/downloads/A04WebViewApp.zip"))
    if (ROOT / "A05BombGame").exists():
        projects.append(("A05BombGame", "docs/bomb-game/downloads/A05BombGame.zip"))
    if (ROOT / "A06ScreenTransitionSample").exists():
        projects.append((
            "A06ScreenTransitionSample",
            "docs/screen-transition-sample/downloads/A06ScreenTransitionSample.zip",
        ))
    if (ROOT / "A07BillSplitter").exists():
        projects.append(("A07BillSplitter", "docs/bill-splitter/downloads/A07BillSplitter.zip"))
    if (ROOT / "A08SharedPreferencesSample").exists():
        projects.append((
            "A08SharedPreferencesSample",
            "docs/shared-preferences-sample/downloads/A08SharedPreferencesSample.zip",
        ))
    if (ROOT / "A09MemoApp").exists():
        projects.append(("A09MemoApp", "docs/memo-app/downloads/A09MemoApp.zip"))
    if (ROOT / "A10RoomSample").exists():
        projects.append(("A10RoomSample", "docs/room-sample/downloads/A10RoomSample.zip"))
    for project, output in projects:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/package-hello-android.py"),
             "--project", project, "--output", str(ROOT / output)],
            cwd=ROOT, check=True,
        )
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/check-teaching-materials.py")],
        cwd=ROOT,
        check=True,
    )
    tracked = subprocess.check_output(["git", "ls-files", "-z", "--", "docs"], cwd=ROOT).decode().split("\0")
    files = {}
    for name in sorted(filter(None, tracked)):
        source = ROOT / name
        if EXCLUDED.intersection(Path(name).parts):
            continue
        if source.is_symlink() or not source.resolve().is_relative_to(ROOT / "docs"):
            raise ValueError(f"配布対象にシンボリックリンクは使えません：{name}")
        files[name] = source.read_bytes()
    if "docs/hello-android/index.html" not in files:
        raise ValueError("HelloAndroidの教科書が見つかりません。")
    if "docs/calc-game/index.html" in files and "docs/calc-game/downloads/A02CalcGame.zip" not in files:
        raise ValueError("CalcGameの完成プロジェクトが見つかりません。")
    if ("docs/rock-paper-scissors-game/index.html" in files
            and "docs/rock-paper-scissors-game/downloads/A03RockPaperScissorsGame.zip" not in files):
        raise ValueError("RockPaperScissorsGameの完成プロジェクトが見つかりません。")
    if "docs/webview-app/index.html" in files and "docs/webview-app/downloads/A04WebViewApp.zip" not in files:
        raise ValueError("WebViewAppの完成プロジェクトが見つかりません。")
    if "docs/bomb-game/index.html" in files and "docs/bomb-game/downloads/A05BombGame.zip" not in files:
        raise ValueError("BombGameの完成プロジェクトが見つかりません。")
    if ("docs/screen-transition-sample/index.html" in files
            and "docs/screen-transition-sample/downloads/A06ScreenTransitionSample.zip" not in files):
        raise ValueError("ScreenTransitionSampleの完成プロジェクトが見つかりません。")
    if ("docs/bill-splitter/index.html" in files
            and "docs/bill-splitter/downloads/A07BillSplitter.zip" not in files):
        raise ValueError("BillSplitterの完成プロジェクトが見つかりません。")
    if ("docs/shared-preferences-sample/index.html" in files
            and "docs/shared-preferences-sample/downloads/A08SharedPreferencesSample.zip" not in files):
        raise ValueError("SharedPreferencesSampleの完成プロジェクトが見つかりません。")
    if ("docs/memo-app/index.html" in files
            and "docs/memo-app/downloads/A09MemoApp.zip" not in files):
        raise ValueError("MemoAppの完成プロジェクトが見つかりません。")
    if ("docs/room-sample/index.html" in files
            and "docs/room-sample/downloads/A10RoomSample.zip" not in files):
        raise ValueError("RoomSampleの完成プロジェクトが見つかりません。")
    check_links(files)

    metadata = {"version": version, "revision": revision, "asset": ASSET_NAME}
    metadata_text = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    files["VERSION.json"] = metadata_text.encode()
    files["はじめに.txt"] = (
        "Androidプログラミング1 学生用教材\n\n"
        f"教材の版：{version}\n\n"
        "1. ZIPを展開します。\n"
        "2. 授業で使う単元の教科書をブラウザで開きます。\n"
        "   A01 HelloAndroid：docs/hello-android/index.html\n"
        "   A02 CalcGame：docs/calc-game/index.html\n"
        "   A03 RockPaperScissorsGame：docs/rock-paper-scissors-game/index.html\n"
        "   A04 WebViewApp：docs/webview-app/index.html\n"
        "   A05 BombGame：docs/bomb-game/index.html\n"
        "   A06 ScreenTransitionSample：docs/screen-transition-sample/index.html\n"
        "   A07 BillSplitter：docs/bill-splitter/index.html\n"
        "   A08 SharedPreferencesSample：docs/shared-preferences-sample/index.html\n"
        "   A09 MemoApp：docs/memo-app/index.html\n"
        "   A10 RoomSample：docs/room-sample/index.html\n"
        "3. 完成プロジェクトは教科書内のリンクから開けます。\n\n"
        "教科書・画像はオフラインで利用できます。Android Studioの準備やビルドにはネット接続が必要です。\n"
        "教材を更新するときは別のフォルダに展開し、自分で作ったAndroid Studioプロジェクトを上書きしないでください。\n"
        "授業中は先生が指定した版を使ってください。質問時には教材の版とSTEP番号を伝えてください。\n"
    ).encode()

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / ASSET_NAME
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = ZipInfo(f"android1-student-materials/{name}", date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    (output_dir / "SHA256SUMS.txt").write_text(f"{digest}  {ASSET_NAME}\n", encoding="utf-8")
    (output_dir / "release-metadata.json").write_text(metadata_text, encoding="utf-8")
    print(f"作成しました：{archive_path}（{len(files)}ファイル、{version}）")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        build(args.output_dir.resolve())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"教材のパッケージ化に失敗しました：{error}") from None


if __name__ == "__main__":
    main()
