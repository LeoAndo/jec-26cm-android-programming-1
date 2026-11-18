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
GROUPS = ("layout", "view", "click", "read", "write", "parse", "snackbar", "empty", "condition", "loop")
KINDS = ("blank", "explain")


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
    expected = Counter({(group, kind): 2 for group in GROUPS for kind in KINDS})
    if Counter((q["group"], q["kind"]) for q in questions) != expected:
        raise ValueError("10の基本項目ごとに空欄2問・説明2問、合計40問にしてください。")
    ids = set()
    for q in questions:
        if q["id"] in ids or q["id"] not in {f"{prefix}{i:02}" for prefix in ("B", "E") for i in range(1, 21)}:
            raise ValueError(f"問題IDが重複、またはB01〜B20・E01〜E20の範囲外：{q['id']}")
        ids.add(q["id"])
        for key in ("id", "unit", "group", "kind", "topic", "prompt", "code", "answer", "explanation", "source"):
            if not isinstance(q[key], str) or not q[key].strip():
                raise ValueError(f"{q['id']}：{key}が空です。")
        if (len(q["choices"]) != 4 or len(set(q["choices"])) != 4
                or any(not isinstance(c, str) or not c.strip() for c in q["choices"])
                or q["answer"] not in q["choices"]):
            raise ValueError(f"{q['id']}：異なる四択と、その中の正答を指定してください。")
        if q["unit"] not in UNITS or q["id"].startswith("B") != (q["kind"] == "blank"):
            raise ValueError(f"{q['id']}：単元または出題形式が不正です。")
        if q["code"].count("【①】") != (1 if q["kind"] == "blank" else 0):
            raise ValueError(f"{q['id']}：空欄問題は【①】を1つ、説明問題は空欄なしにしてください。")
        if not isinstance(q.get("sources"), list) or len(set(q["sources"])) < 2 or q["source"] not in q["sources"]:
            raise ValueError(f"{q['id']}：複数単元の教科書出典を指定してください。")
        if len({source.split("/")[0] for source in q["sources"]}) < 2:
            raise ValueError(f"{q['id']}：出典は2つ以上の単元から選んでください。")
        for filename in q.get("source_files", []):
            source_file = (ROOT / filename).resolve()
            if not source_file.is_relative_to(ROOT) or not source_file.is_file():
                raise ValueError(f"{q['id']}：実コードの出典がありません：{filename}")
        if len(set(q.get("source_files", []))) < 2:
            raise ValueError(f"{q['id']}：実コードの出典を2つ以上指定してください。")
        for reference in q["sources"]:
            validate_source(q["id"], reference)


def validate_source(question_id, reference):
    path, separator, anchor = reference.partition("#")
    source = (ROOT / "docs" / path).resolve()
    if not source.is_relative_to(ROOT / "docs") or not source.is_file() or not separator:
        raise ValueError(f"{question_id}：出典がありません。")
    parser = Anchors()
    parser.feed(source.read_text())
    if anchor not in parser.ids:
        raise ValueError(f"{question_id}：出典の見出しがありません：{anchor}")

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
        blocks.append(f'''<article data-unit="{e['unit']}" data-id="{e['id']}" data-group="{e['group']}" data-kind="{e['kind']}">
<h3>{e['id']} · {e['topic']}</h3>
<p class="prompt">{e['prompt']}</p>
<pre class="question-code"><code>{html.escape(q["code"])}</code></pre>
<ol class="options">{options}</ol>
<div class="explanation"><p>正答：<strong>{e['answer']}</strong></p><p>{e['explanation']}</p></div>
<p class="source">復習する場所：<code>{e['source']}</code></p>
</article>''')
    return "\n".join(blocks)


def render_teacher(questions):
    rows = "\n".join(
        f'<tr><td>{html.escape(q["id"])}</td><td>{"空欄補充" if q["kind"] == "blank" else "説明選択"}</td><td>{inline(q["topic"])}</td>'
        '<td>' + '<br>'.join(f'<a href="../../docs/{html.escape(source, quote=True)}">{html.escape(source)}</a>' for source in q["sources"]) + '</td>'
        '<td>' + '<br>'.join(f'<code>{html.escape(source)}</code>' for source in q["source_files"]) + '</td></tr>'
        for q in questions)
    return '''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>教員用：中間テスト対策問題集</title><link rel="stylesheet" href="../../docs/assets/textbook.css"></head>
<body class="plain"><main><h1>中間テスト対策問題集の確認・配布</h1>
<p>試験予定：2026年12月2日（水）2限、対面・60分。範囲はA01〜A10 RoomSampleまでの全内容。日本語のみ、4択（ア〜エ）、20問・各5点。資料の持ち込み・参照、Android Studio、インターネット検索は禁止です。</p>
<h2>この問題集の教材方針</h2>
<p>複数の単元で使う基本コードを中心に、空欄補充20問と短いコードの説明を選ぶ20問、計40問を用意します。画面設定、部品取得、クリック、文字取得、文字表示、整数変換、Snackbar、空入力、if・return、繰り返しの10項目に分け、各項目に空欄2問・説明2問を置きます。</p>
<p>1回は各項目から空欄1問・説明1問、合計20問です。問題と選択肢を並べ替え、何度でも解き直せます。単元ごとの抽選はしません。必要な条件とコードを問題内に載せ、特定アプリの手順を覚えていることを求めません。Room固有のアノテーションやDAO、WebView、Chronometer、anyMatch、do-whileなどの単元固有技術は外します。繰り返しは複数単元で使う拡張forを中心にします。</p>
<p>コードは教材と実Javaの使い方を短くした練習用の例です。アプリの実装全文をそのまま引用したものではありません。問題文・選択肢・解説は短い文とやさしい日本語にし、API名と表示する文字は翻訳でも保ちます。本番の試験問題そのものは作成・公開しません。</p>
<h2>全問題の内容を確認する</h2>
<p><a href="../../docs/practice/midterm.html#catalog">学生用HTMLの「全40問の正答・解説」</a>で、問題・四択・正答・解説を確認できます。HTMLの採点後の正答・解説と全問題の一覧は学生にも公開し、復習に使います。正答PDFは学生に公開しません。</p>
<p>問題の原本は <code>config/midterm-questions/*.json</code>、教材内ページの原本は <code>scripts/templates/midterm-practice.html</code> です。<code>python3 scripts/generate-midterm-practice.py</code> で日本語HTMLとこのガイドを生成します。生成HTMLを直接編集しません。問題文などのコードはバッククォート、ブロックコードは <code>code</code> フィールドで管理します。</p>
<h2>7言語の復習と日本語の模擬試験</h2>
<p>単体配布用は <code>python3 scripts/build-midterm-distribution.py</code> で生成します。教材内の復習ページと同じ40問と6言語の対訳カタログを使います。復習は教科書・自作プログラムを参照でき、時間制限なし／60分を選べます。言語切替や日本語併記でも回答・出題順・残り時間を維持します。</p>
<p>模擬試験は日本語のみ、60分・20問・各5点です。参照せずに解き、終了後は各言語の解説で復習できます。両モードとも同じ40問から空欄10問・説明10問を出します。時間は開始時刻から数え、別タブでも進みます。期限後の回答は採点に入れません。回答は送信・保存せず、ページを閉じる／再読み込みすると消えます。</p>
<h2>印刷用PDFと学生への配布</h2>
<p><code>python3 scripts/generate-midterm-pdf.py</code> で問題PDFを生成します（ReportLabが必要）。<code>config/midterm-mock.json</code> の <code>paper_ids</code> は各項目の空欄1問・説明1問、計20問です。JIS B4縦（257×364 mm）・2段組、解答欄なしです。本番は別配布のマークシートを使います。印刷用の問題は公開練習用であり、本試験と同じ内容ではありません。</p>
<p>学生用HTMLと問題PDFは <code>dist/midterm/</code> に生成します。教員用の正答PDFを作る場合だけ、<code>--answers-output /絶対パス/teacher/midterm-mock-answers.pdf</code> を指定します。リポジトリ内と学生向け出力先は拒否します。正答PDFは学生向けのフォルダ・教材ZIP・Classroomへ入れません。学生向け出力先に旧版の正答PDFが残る場合も生成を止めます。</p>
<p>学校アカウントの <a href="https://drive.google.com/drive/folders/1eyf3rPX_R5ldeS2q7s_lITMGd_u0Qd0C">materialsフォルダ直下</a>に、HTMLと問題PDFだけを置きます。Classroomの「中間テスト」の既存資料は同じ添付リンクを更新し、既存コメントを保持します。正答PDFの添付・リンク・案内は載せません。HTMLはダウンロードしてChromeなどのブラウザで開くよう案内します。通信・サーバー・外部CDNは不要です。</p>
<p>教材ZIP内の <code>docs/practice/midterm.html</code> も同じ40問と抽選条件で生成します。教材内ページは日本語と6言語のページから読めます。7言語を1画面で切り替える復習と日本語模擬試験には、単体の <code>midterm-practice.html</code> を使います。</p>
<h2>検証</h2>
<p><code>python3 scripts/generate-midterm-practice.py --check</code> で問題の形式・出典・生成漏れを検査します。配布前に対訳の差分翻訳と独立照合を終え、<code>localize-student-materials.py check</code> と <code>status --require-complete</code>、教材検査・スクリプトテスト・教材ZIP生成を通します。</p>
<p><code>scripts/check-midterm-distribution.cjs</code> はjsdom 26で、40問の抽選配分、採点、言語切替時の状態保持、時間切れ後の回答排除、再挑戦を検査します。実ブラウザはCUAで表示・操作を確認します。<code>python3 scripts/generate-midterm-pdf.py --check</code> で寸法・問題数・正答の整合を検査し、PDFの全ページを画像で見て、文字切れと選択肢の収まりを確認します。</p>
<h2>出題項目と出典</h2><table><thead><tr><th>問題ID</th><th>形式</th><th>項目</th><th>教科書</th><th>実Java</th></tr></thead><tbody>
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
    print("中間テスト対策：40問（空欄20・説明20）と生成HTMLを確認しました。")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
