"""中間テスト対策の問題データから、単独で動くHTMLと教員用一覧を生成する。"""

import argparse
from collections import Counter
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
UNITS = [f"A{i:02}" for i in range(1, 11)]


def inline(text):
    """バッククォート内のAPI名・コード・画面の文字列は翻訳対象から保護する。"""
    parts = text.split("`")
    if len(parts) % 2 == 0:
        raise ValueError(f"バッククォートが閉じていません：{text}")
    return "".join('<code>' + html.escape(part) + '</code>' if index % 2 else html.escape(part)
                   for index, part in enumerate(parts))


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        self.ids.update(value for key, value in attrs if key == "id")


def validate(questions):
    if Counter(q["unit"] for q in questions) != Counter({u: 12 for u in UNITS}):
        raise ValueError("A01〜A10は各12問、合計120問にしてください。")
    ids = set()
    for q in questions:
        if q["id"] in ids or not q["id"].startswith(q["unit"] + "-"):
            raise ValueError(f"問題IDが重複、または単元と不一致：{q['id']}")
        ids.add(q["id"])
        for key in ("id", "unit", "topic", "prompt", "answer", "explanation", "source"):
            if not isinstance(q[key], str) or not q[key].strip():
                raise ValueError(f"{q['id']}：{key}が空です。")
        if (len(q["choices"]) != 4 or len(set(q["choices"])) != 4
                or any(not isinstance(c, str) or not c.strip() for c in q["choices"])
                or q["answer"] not in q["choices"]):
            raise ValueError(f"{q['id']}：異なる四択と、その中の正答を指定してください。")
        path, separator, anchor = q["source"].partition("#")
        source = (ROOT / "docs" / path).resolve()
        if not source.is_relative_to(ROOT / "docs") or not source.is_file() or not separator:
            raise ValueError(f"{q['id']}：出典がありません。")
        parser = Anchors()
        parser.feed(source.read_text())
        if anchor not in parser.ids:
            raise ValueError(f"{q['id']}：出典の見出しがありません：{anchor}")


def load_questions():
    questions = []
    for path in sorted((ROOT / "config/midterm-questions").glob("*.json")):
        questions.extend(json.loads(path.read_text()))
    validate(questions)
    return sorted(questions, key=lambda q: q["id"])


def render_bank(questions):
    blocks = []
    for q in questions:
        e = {key: inline(value) for key, value in q.items() if isinstance(value, str)}
        options = "\n".join(
            '<li' + (' data-correct="true"' if c == q["answer"] else '') + '>' + inline(c) + '</li>'
            for c in q["choices"])
        blocks.append(f'''<article data-unit="{e['unit']}" data-id="{e['id']}">
<h3>{e['id']} · {e['topic']}</h3>
<p class="prompt">{e['prompt']}</p>
<ol class="options">{options}</ol>
<div class="explanation"><p>正答：<strong>{e['answer']}</strong></p><p>{e['explanation']}</p></div>
<p class="source">復習する場所：<code>{e['source']}</code></p>
</article>''')
    return "\n".join(blocks)


def render_teacher(questions):
    rows = "\n".join(
        f'<tr><td>{html.escape(q["id"])}</td><td>{inline(q["topic"])}</td>'
        f'<td><a href="../../docs/{html.escape(q["source"], quote=True)}">教科書の該当箇所</a></td></tr>'
        for q in questions)
    return '''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>教員用：中間テスト対策問題集</title><link rel="stylesheet" href="../../docs/assets/textbook.css"></head>
<body class="plain"><main><h1>中間テスト対策問題集の確認・配布</h1>
<p>試験予定：2026年12月2日（水）2限、対面・60分。範囲はA01〜A10 RoomSampleまでの全内容。4択（ア〜エ）、20問・各5点。</p>
<h2>この問題集の教材方針</h2>
<p>各単元12問、合計120問から各2問を抽選し、問題順と選択肢順を並べ替えます。1回で全内容を網羅するものではなく、繰り返して復習するための問題です。本番と同一の問題・単元配分であるとは保証しません。授業で扱っていないAPIや、教員用コードの内部実装の暗記は求めません。</p>
<p>時間制限なしを既定とし、60分練習も選べます。制限時間は開始時刻から数え、別タブへ切り替えても進みます。時間切れになると自動採点します。回答は保存・送信せず、ページを閉じる／再読み込みすると消えます。</p>
<h2>全問題の内容を確認する</h2>
<p><a href="../../docs/practice/midterm.html#catalog">学生用HTMLの「全120問の正答・解説」</a>を開くと、問題ID順に問題・四択・正答・解説・出典を確認できます。回答集は学生にも公開し、復習に利用できます。下表から出典の教科書へ移動できます。</p>
<p>配布前に、問題の範囲、正答の一意性、説明と授業内容の一致を確認してください。問題データは <code>config/midterm-questions/*.json</code>、画面の原本は <code>scripts/templates/midterm-practice.html</code> です。変更後に <code>python3 scripts/generate-midterm-practice.py</code> を実行します。生成HTMLを直接編集しません。問題・選択肢・解説内のAPI名、コード、アプリに表示する文字列はバッククォートで囲み、翻訳時に維持します。</p>
<p>更新漏れと問題データは <code>python3 scripts/generate-midterm-practice.py --check</code>、動作はmacOSのChromeとNode.js 22以降で <code>node scripts/check-midterm-browser.mjs</code> を実行して確認できます。ブラウザ検査は専用の一時プロファイルを作り、通信をオフにして、抽選・採点・時間切れ・再挑戦を操作します。</p>
<h2>7言語の復習と日本語の模擬試験</h2>
<p>単体配布用は <code>python3 scripts/build-midterm-distribution.py</code> で生成します。既存120問と6言語カタログを共用します。復習では教科書・自作プログラムを参照でき、時間制限なし／60分を選べます。言語切替や日本語併記でも回答・出題順・残り時間を維持します。</p>
<p>本番形式の模擬試験は日本語のみ、60分・20問・各5点です。参照せずに解き、終了後は各言語の解説で復習できます。<code>config/midterm-mock.json</code> にある、問題文だけで判断できる40問から各単元2問ずつ抽選します。問題文にない教材固有の状態を暗記させる設問を外します。公開するのは模擬問題であり、未公開の本試験問題は含めません。</p>
<p>印刷用は <code>python3 scripts/generate-midterm-pdf.py</code> で生成します（ReportLabが必要）。B4縦・2段組、解答欄なしで、解答は別配布のマークシートに記入する形式です。問題PDFと正答・解説PDFを分けます。問題と選択肢のまとまり、用紙サイズ、文字切れを配布前に確認してください。</p>
<p>出力先は <code>dist/midterm/</code> です。学生用の配布ファイルは、学校アカウントの <a href="https://drive.google.com/drive/folders/1eyf3rPX_R5ldeS2q7s_lITMGd_u0Qd0C">materialsフォルダ直下</a>に置きます。Classroomの「中間テスト」の既存資料へHTML・問題PDF・正答解説PDFを添付し、HTMLはダウンロードしてブラウザで開くよう案内します。配布時は既存ファイルを更新し、添付リンクを維持します。</p>
<h2>学生へ渡す</h2>
<p><code>docs/practice/midterm.html</code> はCSS・JavaScript・問題を含む1ファイルです。このファイルだけをClassroomに添付できます。学生にはダウンロードしてChromeなどのブラウザで開くよう案内します。Classroomのプレビューでの実行は前提にしません。投稿は教員が行います。通信・サーバー・外部CDNは不要です。</p>
<p>同じ問題集は学生用ZIPにも収録され、準備ページの末尾から開けます。日本語版の開発後、配布前の別工程で差分翻訳と公開を行います。</p>
<h2>出題項目と出典</h2><table><thead><tr><th>問題ID</th><th>項目</th><th>出典</th></tr></thead><tbody>
''' + rows + '\n</tbody></table></main></body></html>\n'


def outputs():
    questions = load_questions()
    template = (ROOT / "scripts/templates/midterm-practice.html").read_text()
    if template.count("<!-- QUESTION_BANK -->") != 1:
        raise ValueError("問題の挿入位置が一意ではありません。")
    return {
        "docs/practice/midterm.html": template.replace("<!-- QUESTION_BANK -->", render_bank(questions)),
        "teacher/midterm-practice/index.html": render_teacher(questions),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for name, text in outputs().items():
        path = ROOT / name
        if args.check:
            if not path.is_file() or path.read_text() != text:
                raise ValueError(f"生成結果が古くなっています：{name}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print("中間テスト対策：120問と生成HTMLを確認しました。")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
