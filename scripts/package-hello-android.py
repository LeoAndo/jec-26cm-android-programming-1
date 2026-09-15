"""教員用：学生に配布するHelloAndroidの完成プロジェクトを作成する。"""

from pathlib import Path
from shutil import which
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


root = Path(__file__).resolve().parents[1]
project = "A01HelloAndroid"
output = root / "docs/hello-android/downloads/A01HelloAndroid.zip"
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
    tracked = subprocess.check_output(
        [git, "ls-files", "-z", "--", project], cwd=root, stderr=subprocess.PIPE
    ).decode().split("\0")
except (OSError, subprocess.CalledProcessError):
    raise SystemExit(
        "Git管理情報を読み取れません。"
        "ZIPの再生成には、READMEの手順でgit cloneした教材が必要です。"
    ) from None
excluded = {".idea", ".gradle", ".kotlin", "build", "local.properties"}
files = [
    name for name in tracked if name and not excluded.intersection(Path(name).parts)
]
if not files:
    raise SystemExit("配布対象のプロジェクトが見つかりません。")

output.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
    for name in sorted(files):
        source = root / name
        info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = (source.stat().st_mode & 0xFFFF) << 16
        info.compress_type = ZIP_DEFLATED
        archive.writestr(info, source.read_bytes())

print(f"作成しました：{output.relative_to(root)}（{len(files)}ファイル）")
