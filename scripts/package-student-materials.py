"""学生向けのdocs一式と、展開済みの完成プロジェクト（samples）をZIPにまとめる。完成プロジェクトのZIPは再生成する。"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import html
import importlib.util
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import posixpath
import subprocess
import sys
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
ASSET_STEM = "android1-student-materials"
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


def add_localized_materials(files):
    """配布対象の言語だけを生成し、本文と導線を静的HTMLとして収録する。"""
    spec = importlib.util.spec_from_file_location("package_localizer", ROOT / "scripts/localize-student-materials.py")
    localizer = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = localizer
    spec.loader.exec_module(localizer)
    settings = localizer.load_settings(ROOT)
    languages = [item for item in settings.languages if item.get("distribute")]
    if not languages:
        return []
    # UI文言の確かめ方と渡し方は、確認用ページ（localize の build）と共通にする。
    ui = {code: localizer.ui_messages(settings, code)
          for code in [settings.source_language, *(item["code"] for item in languages)]}
    for item in languages:
        for key in ("name", "language_label", "translation_notice", "japanese_version", "open_instructions", "start_here"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"config/i18n.json: {item['code']} の {key} がありません")
    # 翻訳でも配布物の境界は同じ。Git未管理の確認用HTMLは生成しない。
    names = sorted(name for name in files if name.endswith(".html"))
    choices = [{"code": "ja", "name": "日本語"}, *languages]
    for language in languages:
        for name, text in localizer.localized_pages(
                settings, language["code"], mark_untranslated=True, page_names=names).items():
            files[name] = text.encode("utf-8")
    for source in names:
        for language in choices:
            code = language["code"]
            name = source if code == "ja" else localizer.output_name(source, code, settings.source_root)
            links = []
            for choice in choices:
                target_code = choice["code"]
                label = html.escape(choice["name"])
                if code == target_code:
                    links.append(f'<span lang="{code}" aria-current="page">{label}</span>')
                else:
                    target = source if target_code == "ja" else localizer.output_name(source, target_code, settings.source_root)
                    href = html.escape(posixpath.relpath(target, posixpath.dirname(name)), quote=True)
                    links.append(f'<a href="{href}" lang="{target_code}" hreflang="{target_code}" data-language-link>{label}</a>')
            label = "言語" if code == "ja" else language["language_label"]
            nav = f'<nav class="language-nav" aria-label="{html.escape(label, quote=True)}">' + " | ".join(links) + "</nav>"
            if code != "ja":
                original = html.escape(posixpath.relpath(source, posixpath.dirname(name)), quote=True)
                nav += ('<aside class="translation-note"><p>' + html.escape(language["translation_notice"])
                        + f'</p><a href="{original}" data-language-link hreflang="ja">'
                        + html.escape(language["japanese_version"]) + '</a></aside>')
            addition = f"\n{nav}\n{localizer.textbook_i18n_script(ui[code])}\n"
            files[name] = localizer.insert_into_body(files[name].decode("utf-8"), addition, name).encode("utf-8")
    # 翻訳された共通資料を入口にする。確認用の小さな教材にはA01を使う。
    start = "docs/common/setup.html" if "docs/common/setup.html" in files else "docs/hello-android/index.html"
    items = [f'<li lang="ja"><a href="{start}">日本語 — ここから始める</a></li>']
    for item in languages:
        target = localizer.output_name(start, item["code"], settings.source_root)
        items.append(f'<li lang="{item["code"]}"><a href="{html.escape(target, quote=True)}">'
                     + html.escape(item["name"] + " — " + item["start_here"]) + '</a></li>')
    files["index.html"] = ('<!doctype html>\n<html lang="ja"><head><meta charset="utf-8">'
                           '<meta name="viewport" content="width=device-width, initial-scale=1">'
                           '<title>Android Programming 1 — Language / 言語</title>'
                           '<link rel="stylesheet" href="docs/assets/textbook.css"></head>'
                           '<body class="plain"><main><h1>Android Programming 1</h1>'
                           '<p>Language / 言語</p><ul>' + ''.join(items) + '</ul></main></body></html>\n').encode("utf-8")
    return languages


def build(output_dir):
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    timestamp = subprocess.check_output(["git", "show", "-s", "--format=%ct", "HEAD"], cwd=ROOT, text=True).strip()
    published = datetime.fromtimestamp(int(timestamp), timezone(timedelta(hours=9)))
    version = f"materials-{published:%Y.%m.%d}-{revision[:12]}"
    # 学生のダウンロードフォルダで版を見分けられるよう、版タグと同じ日付を名前に入れる。
    stem = f"{ASSET_STEM}-{published:%Y-%m-%d}"
    asset_name = f"{stem}.zip"

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
    if (ROOT / "A11VocabularyBook").exists():
        projects.append((
            "A11VocabularyBook",
            "docs/vocabulary-book/downloads/A11VocabularyBook.zip",
        ))
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
    if ("docs/vocabulary-book/index.html" in files
            and "docs/vocabulary-book/downloads/A11VocabularyBook.zip" not in files):
        raise ValueError("VocabularyBookの完成プロジェクトが見つかりません。")
    languages = add_localized_materials(files)
    check_links(files)

    # 完成プロジェクトを、展開済みの見本として samples/ にも収録する。学生はダウンロードも展開もせず、
    # Android StudioのOpenで選ぶだけになる。中身は配布物に入れるZIPと同じなので、新たにcommitするファイルはない。
    # リンク検査のあとで足すので、検査の対象は教科書と多言語の入口で、samples の中は検査しない。
    executables = set()
    for _, archive_name in projects:
        if archive_name not in files:
            # 教科書をまだ足していない単元。ZIPを配らないので、見本も配らない。
            continue
        with ZipFile(io.BytesIO(files[archive_name])) as sample:
            for item in sample.infolist():
                name = f"samples/{item.filename}"
                files[name] = sample.read(item)
                # gradlew の実行権限を、配布物まで引き継ぐ。
                if (item.external_attr >> 16) & 0o100:
                    executables.add(name)

    metadata = {"version": version, "revision": revision, "asset": asset_name}
    metadata_text = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    files["VERSION.json"] = metadata_text.encode()
    files["はじめに.txt"] = (
        "Androidプログラミング1 学生用教材\n\n"
        f"教材の版：{version}\n\n"
        "1. ZIPを展開します。\n"
        "2. はじめて授業を受けるときは、docs/common/setup.html をブラウザで開き、上から順に準備します。\n"
        "   教材の置き場所を決めるところから、エミュレータを作り、日本語を打てるようにして、\n"
        "   最初のアプリが動くまでを説明しています。この準備は1回だけです。次からは3から始められます。\n"
        "3. 授業で使う単元の教科書をブラウザで開きます。\n"
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
        "   A11 VocabularyBook：docs/vocabulary-book/index.html\n"
        "4. 完成プロジェクト（先生が作った見本）は、samples フォルダに入っています。展開は済んでいるので、\n"
        "   Android StudioのOpenで samples/A01HelloAndroid のように選ぶだけで開けます。\n\n"
        "教科書・画像はオフラインで利用できます。Android Studioの準備やビルドにはネット接続が必要です。\n"
        "教材を更新するときは別のフォルダに展開し、自分で作ったAndroid Studioプロジェクトを上書きしないでください。\n"
        "授業中は先生が指定した版を使ってください。質問時には教材の版とSTEP番号を伝えてください。\n"
    ).encode()

    if languages:
        instructions = "\nLanguage / 言語\n日本語：index.html をブラウザで開き、言語を選んでください。\n"
        for language in languages:
            instructions += f"{language['name']}: {language['open_instructions']}\n"
        files["はじめに.txt"] += instructions.encode("utf-8")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / asset_name
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = ZipInfo(f"{stem}/{name}", date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100755 if name in executables else 0o100644) << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    (output_dir / "SHA256SUMS.txt").write_text(f"{digest}  {asset_name}\n", encoding="utf-8")
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
