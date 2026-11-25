"""今回用の復習JSONだけから、多言語の単体HTMLをローカル生成する。"""

import argparse
from collections import Counter
import html
import importlib.util
import json
from pathlib import Path
import re
import string
import sys

import exam_common

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "exam_inline", ROOT / "scripts/generate-midterm-practice.py")
INLINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INLINE)


def japanese_ui(exam):
    """数値は設定から埋める。訳すときもトークンをそのまま残す。"""
    scored = exam.get("points_per_question") is not None
    return {
        "title": ("中間" if exam["exam_type"] == "midterm" else "期末") + "テスト対策問題集",
        "lead": "学んだことを、{draw_count}問ずつ確かめよう。",
        "facts": "4択（ア〜エ）",
        "points": ("{draw_count}問 × {points_per_question}点" if scored else "{draw_count}問・正答数で採点"),
        "repeat": "何度でも挑戦",
        "examDate": "試験予定：{exam_datetime}。試験時間は{duration_minutes}分、範囲は{scope}です。",
        "examRules": "本番は日本語の4択で、{exam_count}問です。解答は別のマークシートに書きます。",
        "untimed": "時間制限なし — 調べながら復習する",
        "timed": "{duration_minutes}分練習 — 時間切れで自動採点する",
        "start": "{draw_count}問を始める",
        "quizTitle": "問題を解く",
        "answered": "回答済み：",
        "noLimit": "時間制限なし",
        "remaining": "残り時間：",
        "answerInstructions": "答えを1つ選んでください。採点するまでは変更できます。",
        "grade": "採点する",
        "unansweredConfirm": "問が未回答です。未回答を不正解として採点しますか？",
        "confirmGrade": "このまま採点する",
        "keepAnswering": "回答を続ける",
        "results": "採点結果",
        "expired": "{duration_minutes}分が経過したため、自動で採点しました。",
        "scoreSuffix": (" / {score_total}点" if scored else " / {draw_count}問正解"),
        "correctPrefix": "正解：",
        "countSuffix": " / {draw_count}問",
        "blankPrefix": "　未回答：",
        "questionSuffix": "問",
        "retry": "新しい{draw_count}問に挑戦する",
        "chooseMode": "練習方法を選び直す",
        "catalog": "全{practice_count}問の正答・解説を見る",
        "sourceHelp": "各問題の参照先は、配布された教材の中の場所と見出しIDです。このHTMLだけで解答と解説を読めます。",
        "correct": "正解",
        "incorrect": "不正解",
        "blank": "未回答",
        "yours": "あなたの回答：",
        "answer": "正答：",
        "language": "言語を選ぶ",
        "showJapanese": "日本語もいっしょに見る",
        "practiceTitle": "教科書を見ながら復習",
        "practiceRules": "教科書や自分で作ったプログラムを見て答えてよいです。時間を決めない練習でも、時間を決めた練習でも同じです。",
        "translationNote": "訳文は学習を助けるためのものです。日本語もいっしょに見られます。コードと答えの記号は、どの言語でも同じです。",
        "privacy": "答えは送信・保存しません。ページを閉じる、または読み込み直すと消えます。時間を決めた練習では、別のタブを見ている間も時間が進みます。",
        "resultHint": "答えと説明を読み、分からなかったところを復習しましょう。言語を変えても、採点結果と自分の答えは変わりません。",
        "practiceCount": "全{practice_count}問から、1回に{draw_count}問を選びます。問題と選択肢の順番を変え、何度でも練習できます。",
    }


def tokens(value):
    result = Counter()
    for _, field, spec, conversion in string.Formatter().parse(value):
        if field is not None:
            if not re.fullmatch(r"[a-z_]+", field) or spec or conversion:
                raise ValueError("UIのトークンは {draw_count} のように指定してください。")
            result[field] += 1
    return result


def build_ui(exam, translations):
    originals = japanese_ui(exam)
    points = exam.get("points_per_question")
    values = {key: str(exam[key]) for key in
              ("draw_count", "practice_count", "duration_minutes", "exam_count", "exam_datetime")}
    values.update(scope="、".join(exam["scope"]),
                  points_per_question=format(points, ".15g") if points is not None else "",
                  score_total=format(points * exam["draw_count"], ".15g") if points is not None else "")
    result = {}
    for language in exam["languages"]:
        code = language["code"]
        source = originals if code == "ja" else translations.get(code)
        if not isinstance(source, dict) or set(source) != set(originals):
            raise ValueError(f"{code}: --print-ui-template にあるすべてのUIキーを翻訳してください。")
        translated = {}
        for key, original in originals.items():
            value = source[key]
            if not isinstance(value, str) or not value.strip() or tokens(value) != tokens(original):
                raise ValueError(f"{code}/{key}: UIの訳または数値トークンが一致しません。")
            translated[key] = html.escape(value.format_map(values))
        result[code] = translated
    return result


def protected_code(value):
    INLINE.inline(value)  # 閉じ忘れたバッククォートも検出する。
    return Counter(value.split("`")[1::2])


def build_data(exam, questions, translations):
    ui = build_ui(exam, translations)
    banks = {}
    for language in exam["languages"]:
        code = language["code"]
        bank = {}
        for question in questions:
            text = question if code == "ja" else question["translations"][code]
            for field in ("prompt", "explanation"):
                if protected_code(text[field]) != protected_code(question[field]):
                    raise ValueError(f"{code}/{question['id']}/{field}: コードが日本語版と一致しません。")
            for original, translated in zip(question["choices"], text["choices"]):
                if protected_code(original) != protected_code(translated):
                    raise ValueError(f"{code}/{question['id']}: 選択肢のコードまたは順序が一致しません。")
            # 公開用の必要な項目だけを作る。照合記録や本番用メタデータは写さない。
            bank[question["id"]] = {
                "heading": html.escape(question["id"]),
                "code": html.escape(question["code"]),
                "prompt": INLINE.inline(text["prompt"]),
                "choices": [INLINE.inline(choice) for choice in text["choices"]],
                "answer": question["answer"],
                "explanation": ("<p>" + ui[code]["answer"]
                                + INLINE.inline(text["choices"][question["answer"]]) + "</p><p>"
                                + INLINE.inline(text["explanation"]) + "</p>"),
                "source": html.escape(question["source"]),
            }
        banks[code] = bank
    return {"languages": [{"code": language["code"], "name": language["name"]}
                          for language in exam["languages"]], "banks": banks, "ui": ui,
            "settings": {"drawCount": exam["draw_count"],
                         "durationMinutes": exam["duration_minutes"],
                         "pointsPerQuestion": exam.get("points_per_question")}}


def render(exam, questions, translations):
    data = build_data(exam, questions, translations)
    template = (ROOT / "scripts/templates/midterm-distribution.html").read_text(encoding="utf-8")
    marker = "<!-- MIDTERM_DATA -->"
    if template.count(marker) != 1:
        raise ValueError("HTMLのデータ挿入位置が一意ではありません。")
    # JavaScriptが動く前の題名・案内にも、旧試験の条件を残さない。
    template = re.sub(r"<title>.*?</title>", lambda _: "<title>" + data["ui"]["ja"]["title"] + "</title>", template)
    header = ('<header><p class="eyebrow">' + html.escape("、".join(exam["scope"]))
              + '</p><h1 data-ui="title">' + data["ui"]["ja"]["title"]
              + '</h1><p class="lead" data-ui="lead">' + data["ui"]["ja"]["lead"] + '</p></header>')
    template = re.sub(r"<header>.*?</header>", lambda _: header, template)
    serialized = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template.replace(marker, '<script id="midterm-data" type="application/json">' + serialized + '</script>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exam", type=Path, required=True)
    parser.add_argument("--questions", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--print-ui-template", action="store_true",
                        help="今回の日本語UIをJSONで表示する。各言語へ訳し、復習JSONのuiへ保存する")
    args = parser.parse_args()
    exam = exam_common.load_exam(args.exam)
    if args.print_ui_template:
        print(json.dumps(japanese_ui(exam), ensure_ascii=False, indent=2))
        return
    if args.questions is None or args.output is None:
        parser.error("生成には --questions と --output が必要です。")
    output = exam_common.private_output(args.output)
    questions = exam_common.load_questions(args.questions, exam, kind="practice")
    raw = json.loads(args.questions.read_text(encoding="utf-8"))
    rendered = render(exam, questions, raw.get("ui", {}))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"復習HTMLをローカル生成しました：{output}（{len(questions)}問、1回{exam['draw_count']}問）")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
