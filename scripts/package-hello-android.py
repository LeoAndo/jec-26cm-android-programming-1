"""教員用：学生に配布する完成プロジェクトを作成する。"""

import argparse
from pathlib import Path
from shutil import which
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


root = Path(__file__).resolve().parents[1]
git = which("git")
if git is None:
    raise SystemExit("Gitが見つかりません。Gitをインストールしてから再実行してください。")

try:
    git_root = subprocess.check_output(
        [git, "rev-parse", "--show-toplevel"], cwd=root, stderr=subprocess.PIPE
    ).decode().strip()
    if Path(git_root).resolve() != root:
        raise SystemExit(
            "このフォルダはGitリポジトリのルートではありません。"
            "READMEの手順でgit cloneした教材を使ってください。"
        )
except (OSError, subprocess.CalledProcessError):
    raise SystemExit(
        "Git管理情報を読み取れません。"
        "ZIPの再生成には、READMEの手順でgit cloneした教材が必要です。"
    ) from None
def package(project, output):
    """Gitで管理されたプロジェクトだけを、IDE設定を除外してZIPにする。"""
    try:
        tracked = subprocess.check_output(
            [git, "ls-files", "-z", "--", project], cwd=root
        ).decode().split("\0")
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit("Git管理情報を読み取れません。ZIPを再生成できません。") from None
    excluded = {".idea", ".gradle", ".kotlin", "build", "local.properties"}
    files = [name for name in tracked if name and not excluded.intersection(Path(name).parts)]
    if not files:
        raise SystemExit("配布対象のプロジェクトが見つかりません。")

    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name in sorted(files):
            source = root / name
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            # Gitで保持されないグループ・他ユーザーの権限差をZIPへ持ち込まない。
            mode = 0o100755 if source.stat().st_mode & 0o100 else 0o100644
            info.external_attr = mode << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, source.read_bytes())
    try:
        shown = output.relative_to(root)
    except ValueError:
        # リポジトリの外へ出力したときは、絶対パスのまま表示する。
        shown = output
    print(f"作成しました：{shown}（{len(files)}ファイル）")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="A01HelloAndroid")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or root / "docs/hello-android/downloads/A01HelloAndroid.zip"
    package(args.project, output.resolve())


if __name__ == "__main__":
    main()
