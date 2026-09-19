"""GitHubの変更履歴を準備し、明示された場合だけ学生用教材を公開する。"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CHECKSUMS = "SHA256SUMS.txt"
# 配布ZIPの名前は版ごとに変わるので、release-metadata.jsonから受け取る。
ASSET_PATTERN = re.compile(r"android1-student-materials-\d{4}-\d{2}-\d{2}\.zip")


def gh(*args, payload=None):
    command = ["gh", *args]
    if payload is not None:
        command.extend(["--input", "-"])
    return subprocess.check_output(
        command, input=json.dumps(payload) if payload is not None else None,
        text=True, cwd=ROOT,
    )


def api(path, payload=None):
    return json.loads(gh("api", path, payload=payload))


def releases(repo):
    pages = json.loads(gh("api", "--paginate", "--slurp", f"repos/{repo}/releases?per_page=100"))
    return [release for page in pages for release in page]


def previous_release(items, version):
    candidates = [
        item for item in items
        if not item["draft"] and not item["prerelease"]
        and item["tag_name"].startswith("materials-") and item["tag_name"] != version
    ]
    return max(candidates, key=lambda item: item["published_at"], default=None)


def summary(text):
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as output:
            output.write(text + "\n")


def prepare(repo, metadata):
    version, revision, asset = metadata["version"], metadata["revision"], metadata["asset"]
    previous = previous_release(releases(repo), version)
    payload = {"tag_name": version, "target_commitish": revision, "configuration_file_path": ".github/release.yml"}
    commit_range = revision
    if previous:
        payload["previous_tag_name"] = previous["tag_name"]
        base = api(f"repos/{repo}/commits/{quote(previous['tag_name'], safe='')}")["sha"]
        # 過去のrunを再実行した場合、最新の配布版より古い変更履歴を作らない。
        subprocess.run(["git", "merge-base", "--is-ancestor", base, revision], cwd=ROOT, check=True)
        commit_range = f"{base}..{revision}"
    generated = api(f"repos/{repo}/releases/generate-notes", payload)["body"]
    commits = subprocess.check_output(
        ["git", "log", "--no-merges", "--format=- %s (%h)", commit_range], cwd=ROOT, text=True,
    ).strip()
    student_notes = os.environ.get("STUDENT_NOTES", "").strip()
    body = (
        f"# Androidプログラミング1 教材 {version}\n\n"
        "## ダウンロードと開き方\n\n"
        f"1. Assetsの **{asset}** をダウンロードして展開します。\n"
        "2. はじめて授業を受けるときは、`docs/common/setup.html` をブラウザで開き、上から順に準備します。\n"
        "   教材の置き場所を決めるところから、エミュレータを作り、日本語を打てるようにして、\n"
        "   最初のアプリが動くまでを説明しています。この準備は1回だけです。次からは3から始められます。\n"
        "3. 授業で使う単元の教科書をブラウザで開きます。\n\n"
        "   - `A01 HelloAndroid：docs/hello-android/index.html`\n"
        "   - `A02 CalcGame：docs/calc-game/index.html`\n"
        "   - `A03 RockPaperScissorsGame：docs/rock-paper-scissors-game/index.html`\n"
        "   - `A04 WebViewApp：docs/webview-app/index.html`\n"
        "   - `A05 BombGame：docs/bomb-game/index.html`\n"
        "   - `A06 ScreenTransitionSample：docs/screen-transition-sample/index.html`\n"
        "   - `A07 BillSplitter：docs/bill-splitter/index.html`\n"
        "   - `A08 SharedPreferencesSample：docs/shared-preferences-sample/index.html`\n"
        "   - `A09 MemoApp：docs/memo-app/index.html`\n"
        "   - `A10 RoomSample：docs/room-sample/index.html`\n"
        "   - `A11 VocabularyBook：docs/vocabulary-book/index.html`\n\n"
        "4. 完成プロジェクトは教科書内のリンクから開けます。\n\n"
        "教材を更新するときは別フォルダに展開し、自分で作ったプロジェクトを上書きしないでください。\n"
        "授業中は先生が指定した版を使ってください。\n\n"
        f"## 学生向けの補足\n\n{student_notes or '対象単元・作業のやり直しの要否は、先生の案内を確認してください。'}\n\n"
        f"## 変更履歴\n\n{generated}\n\n"
        f"<details>\n<summary>コミット一覧（直接mainに入った修正を含む）</summary>\n\n{commits or '追加のコミットはありません。'}\n\n</details>\n\n"
        f"教材の版：`{version}`  \nソース：`{revision}`\n"
    )
    (DIST / "release-notes.md").write_text(body, encoding="utf-8")
    summary(f"## 教材の準備完了\n\n版：`{version}`\n\n`student-materials-ready`で始まる成果物にZIPとリリースノートを保存します。\n\n{body}")


def publish(repo, metadata):
    version, revision, asset = metadata["version"], metadata["revision"], metadata["asset"]
    # 公開処理はActionsのmainからの明示的な手動実行に限定する。
    if os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch" or os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise ValueError("公開はmainを選んだRun workflowから実行してください。")
    checksum = (DIST / CHECKSUMS).read_text(encoding="utf-8").strip()
    actual = hashlib.sha256((DIST / asset).read_bytes()).hexdigest()
    if checksum != f"{actual}  {asset}":
        raise ValueError("教材ZIPのチェックサムが一致しません。")

    current = next((item for item in releases(repo) if item["tag_name"] == version), None)
    if current and not current["draft"]:
        # 再実行で公開済みZIPやノートを上書きしない。
        summary(f"公開済みのため変更しません：{current['html_url']}")
        return
    if api(f"repos/{repo}/commits/main")["sha"] != revision:
        raise ValueError("実行開始後にmainが更新されています。mainから新しくRun workflowを実行してください。")
    refs = api(f"repos/{repo}/git/matching-refs/tags/{quote(version, safe='')}")
    if any(ref["ref"] == f"refs/tags/{version}" for ref in refs):
        if api(f"repos/{repo}/commits/{quote(version, safe='')}")["sha"] != revision:
            raise ValueError("同じタグが別のコミットを指しています。公開を中止しました。")
    if current and current["target_commitish"] != revision:
        raise ValueError("既存の下書きが別のコミットを指しています。公開を中止しました。")

    notes = DIST / "release-notes.md"
    if current:
        gh("release", "edit", version, "--repo", repo, "--notes-file", str(notes))
    else:
        gh("release", "create", version, "--repo", repo, "--target", revision,
           "--title", f"Androidプログラミング1 教材 {version}", "--draft", "--notes-file", str(notes))
    # 添付が揃ってから公開する。失敗時は下書きに留まり、同じrunの再実行で再開できる。
    gh("release", "upload", version, *(str(DIST / name) for name in (asset, CHECKSUMS)), "--repo", repo, "--clobber")
    if api(f"repos/{repo}/commits/main")["sha"] != revision:
        raise ValueError("実行中にmainが更新されています。下書きの公開を中止しました。mainから新しくRun workflowを実行してください。")
    gh("release", "edit", version, "--repo", repo, "--draft=false", "--latest")
    summary(f"## 学生向けに公開しました\n\nhttps://github.com/{repo}/releases/tag/{version}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "publish"))
    args = parser.parse_args()
    try:
        repo = os.environ["GH_REPO"]
        metadata = json.loads((DIST / "release-metadata.json").read_text(encoding="utf-8"))
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        if metadata["revision"] != revision:
            raise ValueError("教材の生成元とワークフローのコミットが一致しません。")
        if not ASSET_PATTERN.fullmatch(metadata["asset"]):
            raise ValueError(f"配布ZIPの名前が想定の形式ではありません：{metadata['asset']}")
        {"prepare": prepare, "publish": publish}[args.action](repo, metadata)
    except (KeyError, OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"リリース処理に失敗しました：{error}") from None


if __name__ == "__main__":
    main()
