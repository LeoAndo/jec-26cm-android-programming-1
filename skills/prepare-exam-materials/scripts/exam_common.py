"""試験準備のローカル入力検査。公開や教材の取得は行わない。"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path, PurePosixPath
import re


def private_output(path):
    """Git管理領域への出力を防ぐ。保存先の共有権限は運用時に別途確認する。"""
    path = Path(path).expanduser().resolve()
    if any((parent / ".git").exists() for parent in (path, *path.parents)):
        raise ValueError("試験のデータ・成果物はGitリポジトリ外の教員用ローカル領域へ保存してください。")
    return path


def read_json(path):
    return json.loads(Path(path).expanduser().read_text(encoding="utf-8"))


def positive_int(value, label):
    if type(value) is not int or value < 1:
        raise ValueError(f"{label} は1以上の整数にしてください。")
    return value


def positive_decimal(value, label):
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"{label} は正の数にしてください。") from None
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{label} は正の有限数にしてください。")
    return number


def load_exam(path):
    exam = read_json(path)
    if exam.get("exam_type") not in ("midterm", "final"):
        raise ValueError("exam_type は midterm（中間）または final（期末）です。")
    if exam.get("answer_format") != "four_choice":
        raise ValueError("この生成器は4択のみです。非選択式は解答欄・採点条件を確認し、別途設計してください。")
    if not isinstance(exam.get("exam_datetime"), str) or "T" not in exam["exam_datetime"]:
        raise ValueError("exam_datetime は日時をISO 8601形式で指定してください。")
    datetime.fromisoformat(exam["exam_datetime"])
    positive_int(exam.get("duration_minutes"), "duration_minutes")
    n = positive_int(exam.get("exam_count"), "exam_count")
    exam.setdefault("practice_count", 2 * n)
    positive_int(exam["practice_count"], "practice_count")
    exam.setdefault("draw_count", min(n, exam["practice_count"]))
    positive_int(exam["draw_count"], "draw_count")
    if exam["draw_count"] > exam["practice_count"]:
        raise ValueError("抽選数は復習問題数以下にしてください。")
    scope = exam.get("scope")
    if not isinstance(scope, list) or not scope or any(not isinstance(s, str) or not s.strip() for s in scope):
        raise ValueError("scope は出題範囲の文字列の配列です。")
    languages = exam.get("languages")
    if not isinstance(languages, list) or not languages:
        raise ValueError("languages に実際の配布版の言語を指定してください。")
    codes = []
    for lang in languages:
        if (not isinstance(lang, dict) or not re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z0-9]+)*", lang.get("code", ""))
                or not isinstance(lang.get("name"), str) or not lang["name"].strip()):
            raise ValueError("languages は code と name を持つ配列です。")
        codes.append(lang["code"])
    if "ja" not in codes or len(set(codes)) != len(codes):
        raise ValueError("言語は日本語を含め、重複なく指定してください。")
    if exam.get("points_per_question") is not None:
        points = positive_decimal(exam["points_per_question"], "points_per_question")
        total = positive_decimal(exam.get("total_points", points * n), "total_points")
        if points * n != total:
            raise ValueError("本番問題数×各問の配点と総点が一致していません。")
        exam["points_per_question"] = float(points)
        exam["total_points"] = float(total)
    elif exam.get("total_points") is not None:
        raise ValueError("総点だけでは配点を決められません。各問の配点を確認してください。")
    return exam


def load_questions(path, exam, kind="practice"):
    data = read_json(path)
    if kind not in ("practice", "final"):
        raise ValueError("kind は practice または final です。")
    # ファイルの取り違えを止める。本番の正答を復習HTMLへ混ぜない。
    if data.get("purpose") != kind:
        raise ValueError(f"問題ファイルの purpose を {kind} にしてください。別用途の問題は読み込みません。")
    questions = data.get("questions")
    expected = exam["practice_count" if kind == "practice" else "exam_count"]
    if not isinstance(questions, list) or len(questions) != expected:
        raise ValueError(f"{kind} の問題数は {expected} 問です。")
    ids = set()
    langs = {lang["code"] for lang in exam["languages"]} - {"ja"}
    for q in questions:
        qid = q.get("id", "")
        if not isinstance(qid, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", qid) or qid in ids:
            raise ValueError("問題IDは英数字・ハイフン・下線で、重複なく指定してください。")
        ids.add(qid)
        for key in ("topic", "prompt", "explanation", "source"):
            if not isinstance(q.get(key), str) or not q[key].strip():
                raise ValueError(f"{qid}: {key} が必要です。")
        if not isinstance(q.get("code", ""), str):
            raise ValueError(f"{qid}: code は文字列です。")
        q.setdefault("code", "")
        source = q["source"].split("#", 1)[0]
        if (not source.startswith("docs/") or ".." in PurePosixPath(source).parts
                or "\\" in source or not source.endswith(".html")):
            raise ValueError(f"{qid}: source は配布教材の docs/ から始まるHTML相対パスです。")
        choices = q.get("choices")
        if (not isinstance(choices, list) or len(choices) != 4
                or any(not isinstance(c, str) or not c.strip() for c in choices)
                or len(set(c.strip() for c in choices)) != 4
                or type(q.get("answer")) is not int or not 0 <= q["answer"] < 4):
            raise ValueError(f"{qid}: 異なる4択と正答index（0〜3）が必要です。")
        if "points" in q:
            raise ValueError("問ごとの異なる配点はこの生成器では未対応です。配点方法を確認してください。")
        if kind == "practice":
            translations = q.get("translations", {})
            if set(translations) != langs:
                raise ValueError(f"{qid}: 翻訳の言語を配布版と一致させてください。")
            for lang, tr in translations.items():
                for key in ("prompt", "explanation"):
                    if not isinstance(tr.get(key), str) or not tr[key].strip():
                        raise ValueError(f"{qid}/{lang}: {key} がありません。")
                options = tr.get("choices")
                if (not isinstance(options, list) or len(options) != 4
                        or any(not isinstance(c, str) or not c.strip() for c in options)
                        or len(set(c.strip() for c in options)) != 4):
                    raise ValueError(f"{qid}/{lang}: 異なる4択が必要です。")
    return questions
