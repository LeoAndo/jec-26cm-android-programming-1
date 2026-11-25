"""教員用の4択問題を、学校フッター付きJIS B4縦PDFへ組む。

依存: reportlab, pypdf。入力と出力はリポジトリ外の非公開領域に置く。
問題・正答・配点の並びは入力どおり。PDFに正答・解説は載せない。
"""

import argparse
from datetime import datetime
import importlib.util
import json
import math
from pathlib import Path
import re

from exam_common import load_exam, load_questions, private_output

SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[1]
FOOTER = SKILL / "assets/school-footer.json"
DEFAULT_FONT = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
DEFAULT_CODE_FONT = Path("/System/Library/Fonts/Menlo.ttc")
MM = 72 / 25.4
WIDTH, HEIGHT = 257 * MM, 364 * MM
LEFT, GAP, TOP = 36, 22, HEIGHT - 36
COLUMN_WIDTH = (WIDTH - LEFT * 2 - GAP) / 2
QUESTION_GAP = 14


def columns_for(heights, available, gap=QUESTION_GAP):
    """順番を保ち、最少ページの最大2段へ分配する。問題は分断しない。"""
    if not heights or any(h <= 0 or not math.isfinite(h) for h in heights):
        raise ValueError("問題の高さが不正です。")
    if max(heights) > available:
        raise ValueError("1問が1段に入りません。文字を縮めず問題文とコードを見直してください。")

    def split(limit):
        columns, column, used = [], [], 0
        for index, height in enumerate(heights):
            if column and used + gap + height > limit:
                columns.append(column)
                column, used = [], 0
            used += (gap if column else 0) + height
            column.append(index)
        return columns + [column]

    # まず容量で必要なページ数を求め、そのページ内で段の高さをそろえる。
    count = min(len(heights), 2 * math.ceil(len(split(available)) / 2))
    low, high = max(heights), available
    for _ in range(48):
        middle = (low + high) / 2
        if len(split(middle)) <= count:
            high = middle
        else:
            low = middle
    result = split(high)
    # 同じ高さが並ぶ場合も、少数の問題を2段に分ける。
    while len(result) < count:
        index = max(range(len(result)), key=lambda i: len(result[i]))
        result.insert(index + 1, result[index][1:])
        result[index] = result[index][:1]
    return result


def footer_values(exam, page, pages):
    footer = exam.get("footer")
    required = ("subject", "class_name", "author", "term", "period", "allowed_materials", "submission")
    if not isinstance(footer, dict):
        raise ValueError("学校フッターの設定 footer が必要です。")
    for key in required:
        if not isinstance(footer.get(key), str):
            raise ValueError(f"footer.{key} を文字列で指定してください（空欄は空文字列）。")
    if not footer["subject"] or not footer["class_name"] or not footer["author"]:
        raise ValueError("学校フッターの科目・組・出題者を指定してください。")
    if footer["term"] not in ("", "前期", "後期") or footer.get("course_type", "") not in ("", "必", "選"):
        raise ValueError("term は前期/後期、course_type は必/選、未指定は空文字列にしてください。")
    when = datetime.fromisoformat(exam["exam_datetime"])
    return {
        **footer, "subject": footer["subject"], "duration": str(exam["duration_minutes"]),
        "year": str(when.year), "month": str(when.month), "day": str(when.day),
        "page": str(page), "pages": str(pages),
    }


def load_markup():
    # 既存PDFと同じ、日本語/コードのフォント切替・エスケープを使う。
    spec = importlib.util.spec_from_file_location("exam_pdf_markup", ROOT / "scripts/generate-midterm-pdf.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.markup


def generate(exam, questions, output, font_path=DEFAULT_FONT, code_font=DEFAULT_CODE_FONT):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph

    output = private_output(Path(output))
    if output.suffix.lower() != ".pdf":
        raise ValueError("--output は教員用のPDFファイルパスを指定してください。")
    report_path = private_output(output.with_suffix(".layout.json"))
    asset = json.loads(FOOTER.read_text())
    x0, y0, x1, y1 = asset["target_bbox_pt"]
    bottom = y1 + 20
    values = footer_values(exam, 1, 1)
    if len(questions) != exam["exam_count"]:
        raise ValueError("本番問題数と問題データの件数が一致しません。")
    for name, path in (("Japanese", font_path), ("Code", code_font)):
        if not Path(path).is_file():
            raise ValueError(f"フォントがありません。--font / --code-font で指定してください: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    markup = load_markup()

    def check_glyphs(text, code=False):
        for char in text:
            if char in "\n\r\t":
                continue
            name = "Code" if code and char.isascii() else "Japanese"
            if not pdfmetrics.getFont(name).face.charToGlyph.get(ord(char), 0):
                raise ValueError(f"{name} フォントに文字 U+{ord(char):04X} がありません。")

    for q in questions:
        check_glyphs(q["prompt"])
        check_glyphs(q.get("code", ""), True)
        for choice in q["choices"]:
            check_glyphs(choice)
    check_glyphs("問アイウエ点（）0123456789" + "".join(t["text"] for t in asset["labels"]))
    for value in values.values():
        if isinstance(value, str):
            check_glyphs(value)

    styles = {
        "body": ParagraphStyle("exam-body", fontName="Japanese", fontSize=10.5,
                               leading=15, wordWrap="CJK", splitLongWords=True),
        "choice": ParagraphStyle("exam-choice", fontName="Japanese", fontSize=10,
                                 leading=13.5, wordWrap="CJK", splitLongWords=True),
    }

    def paragraph(text, style, canvas, x, top, width=COLUMN_WIDTH):
        item = Paragraph(markup(text), styles[style])
        _, needed = item.wrap(width, HEIGHT)
        if canvas is not None:
            item.drawOn(canvas, x, top - needed)
        return top - needed

    def code_block(text, canvas, x, top):
        if not text:
            return top
        size, leading, pad = 9.25, 12, 8
        lines = text.expandtabs(4).splitlines()
        needed = len(lines) * leading + 12
        runs = []
        for line in lines:
            parts = [(part, "Code" if part.isascii() else "Japanese")
                     for part in re.findall(r"[\x00-\x7f]+|[^\x00-\x7f]+", line)]
            if sum(pdfmetrics.stringWidth(s, f, size) for s, f in parts) > COLUMN_WIDTH - pad * 2:
                raise ValueError("コードの行が段幅を超えます。入力のコードを短くするか、意味を保って改行してください。")
            runs.append(parts)
        if canvas is not None:
            canvas.setLineWidth(.45)
            canvas.rect(x, top - needed, COLUMN_WIDTH, needed, stroke=1, fill=0)
            for row, parts in enumerate(runs):
                cursor = x + pad
                for part, font in parts:
                    canvas.setFont(font, size)
                    canvas.drawString(cursor, top - 5 - size - row * leading, part)
                    cursor += pdfmetrics.stringWidth(part, font, size)
        return top - needed

    def question(q, number, canvas, x, top):
        if canvas is not None:
            points = exam.get("points_per_question")
            label = f"問{number:02d}" + (f"（{float(points):g}点）" if points is not None else "")
            canvas.setFont("Japanese", 11.5)
            canvas.drawString(x, top - 11.5, label)
        top -= 18
        top = paragraph(q["prompt"], "body", canvas, x, top) - 6
        top = code_block(q.get("code", ""), canvas, x, top) - 6
        choices = [f"{letter}．{text}" for letter, text in zip("アイウエ", q["choices"])]
        half = (COLUMN_WIDTH - 10) / 2
        fits = all(paragraph(text, "choice", None, 0, 0, half) >= -13.51 for text in choices)
        if fits:
            for row in (0, 2):
                top = min(paragraph(choices[row + col], "choice", canvas,
                                    x + col * (half + 10), top, half) for col in range(2)) - 2
        else:
            for text in choices:
                top = paragraph(text, "choice", canvas, x, top) - 2
        return top

    def draw_footer(canvas, page, pages):
        vals = footer_values(exam, page, pages)
        sw, sh = asset["size"]
        canvas.saveState()
        canvas.translate(x0, y0)
        canvas.scale((x1 - x0) / sw, (y1 - y0) / sh)
        for left, top, right, bottom_ in asset["rectangles"]:
            canvas.rect(left, sh - bottom_, right - left, bottom_ - top, stroke=0, fill=1)
        canvas.setLineWidth(.675)
        for left, top, right, bottom_ in asset["lines"]:
            canvas.line(left, sh - top, right, sh - bottom_)
        for item in asset["labels"]:
            canvas.setFont("Japanese", item["size"])
            canvas.drawString(item["x"], sh - item["baseline"], item["text"])
        for key, box in asset["fields"].items():
            value = vals[key]
            left, top, right, bottom_ = box
            size = 8.16
            lines = value.splitlines() or [""]
            if key == "subject":
                # 試験名は学校欄の中だけへ。本文上部には見出しを足さない。
                lines += ["中間テスト" if exam["exam_type"] == "midterm" else "期末テスト"]
            if len(lines) * (size + 2) > bottom_ - top:
                raise ValueError(f"学校フッターの {key} が欄の高さを超えます。短い表記へ直してください。")
            if any(pdfmetrics.stringWidth(line, "Japanese", size) > right - left for line in lines):
                raise ValueError(f"学校フッターの {key} が欄の幅を超えます。短い表記へ直してください。")
            start = sh - (top + bottom_) / 2 + (len(lines) - 1) * (size + 2) / 2 - size * .35
            canvas.setFont("Japanese", size)
            for index, line in enumerate(lines):
                canvas.drawCentredString((left + right) / 2, start - index * (size + 2), line)
        for key, options in asset["selections"].items():
            value = vals.get(key, "")
            if value:
                left, top, right, bottom_ = options[value]
                canvas.setLineWidth(.8)
                canvas.ellipse(left, sh - bottom_, right, sh - top, stroke=1, fill=0)
        canvas.restoreState()

    heights = [TOP - question(q, n, None, 0, TOP) for n, q in enumerate(questions, 1)]
    columns = columns_for(heights, TOP - bottom)
    pages = math.ceil(len(columns) / 2)
    # 書き出す前に最終枚数を含むフッターの幅/高さも検査する。
    import io
    check_canvas = Canvas(io.BytesIO(), pagesize=(WIDTH, HEIGHT))
    draw_footer(check_canvas, pages, pages)
    check_canvas.save()
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output), pagesize=(WIDTH, HEIGHT), pageCompression=1, invariant=1)
    canvas.setTitle("中間テスト" if exam["exam_type"] == "midterm" else "期末テスト")
    canvas.setAuthor(exam["footer"]["author"])
    metrics = []
    for page in range(pages):
        for col in range(2):
            index = page * 2 + col
            if index >= len(columns):
                continue
            x, y = LEFT + col * (COLUMN_WIDTH + GAP), TOP
            for qi in columns[index]:
                lower = question(questions[qi], qi + 1, canvas, x, y)
                metrics.append({"question": qi + 1, "id": questions[qi]["id"], "page": page + 1,
                                "column": col + 1, "bbox_pt": [x, lower, x + COLUMN_WIDTH, y]})
                y = lower - QUESTION_GAP
        draw_footer(canvas, page + 1, pages)
        canvas.showPage()
    canvas.save()
    from pypdf import PdfReader
    reader = PdfReader(output)
    if len(reader.pages) != pages or any(abs(float(p.mediabox.width) - WIDTH) > .01 or
                                         abs(float(p.mediabox.height) - HEIGHT) > .01 for p in reader.pages):
        raise ValueError("生成PDFのページ数またはB4寸法が一致しません。")
    report = {"pages": pages, "question_count": len(questions), "page_mm": [257, 364],
              "coordinate_origin": "lower-left, points", "footer_bbox_pt": [x0, y0, x1, y1],
              "footer_mm": {"left": x0 / MM, "bottom": y0 / MM,
                            "width": (x1 - x0) / MM, "height": (y1 - y0) / MM},
              "questions": metrics, "visual_review": "未確認：全ページをレンダリングして目視する"}
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exam", required=True, type=Path)
    parser.add_argument("--questions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--code-font", type=Path, default=DEFAULT_CODE_FONT)
    args = parser.parse_args()
    try:
        exam = load_exam(args.exam)
        questions = load_questions(args.questions, exam, kind="final")
        report = generate(exam, questions, args.output, args.font, args.code_font)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(f"本番PDFを生成：{report['question_count']}問 / {report['pages']}ページ。全ページの目視は別途必要です。")


if __name__ == "__main__":
    main()
