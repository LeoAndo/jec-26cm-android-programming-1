"""日本語の模擬問題・正答解説を、B4縦2段組のPDFとして別々に生成する。

依存: reportlab、検査時はpypdf。--fontで日本語を含むTrueTypeフォントを指定する。
既定はmacOSのArial Unicode。フォントをPDFへ埋め込んで出力する。
"""

import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
import random
import re

ROOT = Path(__file__).resolve().parents[1]
LETTERS = "アイウエ"


def load_paper():
    config = json.loads((ROOT / "config/midterm-mock.json").read_text())
    bank = {q["id"]: q for path in sorted((ROOT / "config/midterm-questions").glob("*.json"))
            for q in json.loads(path.read_text())}
    overrides = json.loads((ROOT / "config/midterm-plain-ja.json").read_text())
    for qid, fields in overrides.items():
        if qid not in bank or not set(fields) <= {"prompt", "choices", "explanation"}:
            raise ValueError(f"{qid}: 日本語の書き換えに不正な項目があります。")
        q = bank[qid]
        correct_index = q["choices"].index(q["answer"])
        q.update(fields)
        if len(q["choices"]) != 4 or len(set(q["choices"])) != 4:
            raise ValueError(f"{qid}: 書き換え後の選択肢が四択ではありません。")
        q["answer"] = q["choices"][correct_index]
    for key, count in (("question_ids", 4), ("paper_ids", 2)):
        ids = config[key]
        if len(ids) != len(set(ids)) or any(i not in bank for i in ids):
            raise ValueError(f"{key}: 重複または存在しない問題IDです。")
        if Counter(bank[i]["unit"] for i in ids) != Counter({f"A{n:02}": count for n in range(1, 11)}):
            raise ValueError(f"{key}: 各単元{count}問が必要です。")
    if not set(config["paper_ids"]).issubset(config["question_ids"]):
        raise ValueError("印刷用の問題は模擬試験の問題から選びます。")
    rng = random.Random(config["paper_seed"])
    answer_slots = list(range(4)) * 5
    rng.shuffle(answer_slots)
    paper = []
    for number, (qid, slot) in enumerate(zip(config["paper_ids"], answer_slots), 1):
        q = dict(bank[qid])
        choices = [c for c in q["choices"] if c != q["answer"]]
        if len(choices) != 3 or len(set(q["choices"])) != 4:
            raise ValueError(f"{qid}: 正答が一意でない四択です。")
        rng.shuffle(choices)
        choices.insert(slot, q["answer"])
        q.update(number=number, choices=choices, answer_letter=LETTERS[slot])
        paper.append(q)
    return config, paper


def font_markup(text, code=False):
    """コードは等幅、日本語文字列は日本語フォントを使い、改行を維持する。"""
    if not code:
        return escape(text).replace("\n", "<br/>")
    return "".join(f'<font name="{"Code" if part.isascii() else "Japanese"}">{escape(part)}</font>'
                   for part in re.findall(r"[\x00-\x7f]+|[^\x00-\x7f]+", text)).replace("\n", "<br/>")


def markup(text):
    return "".join(font_markup(part, i % 2 == 1) for i, part in enumerate(text.split("`")))


def generate(output, font_path):
    from reportlab import rl_config
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Paragraph

    rl_config.warnOnMissingFontGlyphs = 1
    pdfmetrics.registerFont(TTFont("Japanese", str(font_path)))
    mono_font = Path("/System/Library/Fonts/Menlo.ttc")
    if mono_font.is_file():
        pdfmetrics.registerFont(TTFont("Code", str(mono_font)))
    else:
        from reportlab.pdfbase.pdfmetrics import Font
        pdfmetrics.registerFont(Font("Code", "Courier", "WinAnsiEncoding"))
    config, paper = load_paper()
    output.mkdir(parents=True, exist_ok=True)
    width, height = 257 * mm, 364 * mm
    margin, gap = 15 * mm, 9 * mm
    column_width = (width - 2 * margin - gap) / 2
    styles = {
        "prompt": ParagraphStyle("prompt", fontName="Japanese", fontSize=10.8, leading=15,
                                 wordWrap="CJK", splitLongWords=True),
        "choice": ParagraphStyle("choice", fontName="Japanese", fontSize=10.3, leading=14,
                                 wordWrap="CJK", splitLongWords=True, leftIndent=15, firstLineIndent=-15),
        "explanation": ParagraphStyle("explanation", fontName="Japanese", fontSize=10.5, leading=16,
                                      wordWrap="CJK", splitLongWords=True),
    }

    def paragraph(text, style, canvas, x, top):
        item = Paragraph(text, styles[style])
        _, needed = item.wrap(column_width, 2000)
        if canvas:
            item.drawOn(canvas, x, top - needed)
        return top - needed

    def block(q, canvas, x, top, answers):
        if canvas:
            canvas.setFont("Japanese", 11.5)
            canvas.drawString(x, top - 11.5, f'問{q["number"]:02}  ' + (f'正答：{q["answer_letter"]}' if answers else "（5点）"))
        top -= 20
        if answers:
            top = paragraph(markup(q["answer"]), "prompt", canvas, x, top)
            top -= 7
            top = paragraph(markup(q["explanation"]), "explanation", canvas, x, top)
            top -= 6
            if canvas:
                canvas.setFont("Japanese", 8.5)
                canvas.setFillColor(colors.HexColor("#555555"))
                canvas.drawString(x, top - 9, f'復習問題ID：{q["id"]}')
                canvas.setFillColor(colors.black)
            top -= 14
        else:
            top = paragraph(markup(q["prompt"]), "prompt", canvas, x, top)
            top -= 6
            for letter, choice in zip(LETTERS, q["choices"]):
                top = paragraph(letter + "． " + markup(choice), "choice", canvas, x, top)
                top -= 2
        return top

    files = []
    for answers, name in ((False, "midterm-mock-b4.pdf"), (True, "midterm-mock-answers.pdf")):
        path = output / name
        title = config["title"] + (" 正答・解説" if answers else "")
        canvas = Canvas(str(path), pagesize=(width, height), pageCompression=1, invariant=1)
        canvas.setTitle(title)
        canvas.setAuthor("Androidプログラミング1")
        canvas.setSubject("A01-A10の練習用問題。本試験の問題ではありません。")
        for page in range(2):
            canvas.setFillColor(colors.black)
            canvas.setFont("Japanese", 17)
            canvas.drawString(margin, height - 19 * mm, title)
            canvas.setFont("Japanese", 10)
            canvas.drawString(margin, height - 26 * mm, "Androidプログラミング1  /  A01〜A10  /  60分  /  20問・各5点（100点）")
            if answers:
                lines = ["問題用PDFと同じ番号・選択肢順です。解き終わってから確認してください。",
                         "分からなかった内容は、復習用HTMLの問題IDから解説を読み直しましょう。"]
            else:
                lines = ["各問題の答えを1つ選び、別のマークシートの同じ番号にマークしてください。",
                         "日本語だけで解きます。教科書・自作プログラムを見たり、検索したりしません。"]
            for i, line in enumerate(lines):
                canvas.drawString(margin, height - (31 + i * 5.5) * mm, line)
            canvas.setFont("Japanese", 9)
            canvas.drawString(margin, height - 41 * mm, "練習用です。本番とは、問題や各単元の問題数が変わることがあります。")
            canvas.setStrokeColor(colors.HexColor("#888888"))
            canvas.line(margin, height - 44 * mm, width - margin, height - 44 * mm)
            canvas.setStrokeColor(colors.HexColor("#CCCCCC"))
            canvas.line(width / 2, 23 * mm, width / 2, height - 49 * mm)
            top, bottom = height - 49 * mm, 23 * mm
            for column in range(2):
                x = margin + column * (column_width + gap)
                questions = paper[page * 10 + column * 5:page * 10 + column * 5 + 5]
                heights = [top - block(q, None, x, top, answers) for q in questions]
                needed = sum(heights)
                separation = (top - bottom - needed) / 4
                if separation < 8:
                    raise ValueError(f"{name} {page + 1}ページ {column + 1}段: 必要な高さ{needed:.1f}pt / 使用可能{top-bottom:.1f}pt。文字を縮めず配置を見直してください。")
                y = top
                for q in questions:
                    y = block(q, canvas, x, y, answers) - separation
            canvas.setFont("Japanese", 9)
            canvas.setFillColor(colors.HexColor("#555555"))
            canvas.drawString(margin, 13 * mm, "中間テスト対策  /  日本語  /  模擬問題 01")
            canvas.drawRightString(width - margin, 13 * mm, f"{page + 1} / 2")
            canvas.showPage()
        canvas.save()
        files.append(path)
    return files


def verify(files):
    from pypdf import PdfReader
    _, paper = load_paper()

    def plain(text):
        return re.sub(r"\s+", "", text.replace("`", ""))

    for path in files:
        reader = PdfReader(path)
        if len(reader.pages) != 2:
            raise ValueError(f"{path}: 2ページではありません。")
        text = "\n".join(page.extract_text() for page in reader.pages)
        for i in range(1, 21):
            if len(re.findall(rf"問{i:02}\b", text)) != 1:
                raise ValueError(f"{path}: 問{i:02}の重複または不足があります。")
        sections = re.split(r"問\d{2}\b", text)[1:]
        for q, section in zip(paper, sections):
            section = plain(section)
            if path.name == "midterm-mock-answers.pdf":
                expected = [f'正答：{q["answer_letter"]}', q["answer"], q["explanation"]]
            else:
                expected = [q["prompt"]] + [letter + "．" + choice for letter, choice in zip(LETTERS, q["choices"])]
            if any(plain(item) not in section for item in expected):
                raise ValueError(f'{path}: 問{q["number"]:02}の本文・選択肢または正答が一致しません。')
        for page in reader.pages:
            w, h = float(page.mediabox.width), float(page.mediabox.height)
            if abs(w * 25.4 / 72 - 257) > .05 or abs(h * 25.4 / 72 - 364) > .05:
                raise ValueError(f"{path}: B4縦ではありません。")
            if page.get("/Annots"):
                raise ValueError(f"{path}: 不要なフォームがあります。")
        if path.name == "midterm-mock-b4.pdf" and ("正答：" in text or "解答欄" in text):
            raise ValueError("問題用PDFに解答が混在しています。")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist/midterm")
    parser.add_argument("--font", type=Path, default=Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"))
    parser.add_argument("--check", action="store_true", help="生成後に寸法・問数・解答分離を検査する")
    args = parser.parse_args()
    if not args.font.is_file():
        parser.error("日本語TrueTypeフォントを --font で指定してください。")
    files = generate(args.output, args.font)
    if args.check:
        verify(files)
    for path in files:
        print(path)


if __name__ == "__main__":
    main()
