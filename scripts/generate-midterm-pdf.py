"""日本語の練習問題をB4縦2段組で生成する。正答PDFは教員用の明示指定時だけ作る。

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
    questions = [q for path in sorted((ROOT / "config/midterm-questions").glob("*.json"))
                 for q in json.loads(path.read_text())]
    bank = {q["id"]: q for q in questions}
    if len(bank) != len(questions):
        raise ValueError("問題の原本に重複したIDがあります。")
    groups = {'click', 'enabled', 'orientation', 'private', 'margin', 'empty', 'read', 'view', 'width', 'write', 'loop', 'condition', 'parse', 'concat', 'create', 'snackbar', 'import', 'layout', 'increment', 'return'}
    ids = config["paper_ids"]
    if len(ids) != 20 or len(set(ids)) != 20 or any(i not in bank for i in ids):
        raise ValueError("印刷用は重複しない20問を指定してください。")
    if Counter(bank[i]["group"] for i in ids) != Counter({group: 1 for group in groups}):
        raise ValueError("印刷用は20の基本事項から各1問を選んでください。")
    if Counter(bank[i]["kind"] for i in ids) != Counter(blank=10, explain=10):
        raise ValueError("印刷用は空欄10問・説明10問にしてください。")
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


def generate(output, font_path, answers_output=None):
    output = output.resolve()
    if (output / "midterm-mock-answers.pdf").exists():
        raise ValueError("学生用の出力先に旧版の正答PDFがあります。教員用フォルダへ移してから生成してください。")
    if answers_output is not None:
        answers_output = answers_output.resolve()
        if answers_output.is_relative_to(ROOT) or answers_output.is_relative_to(output):
            raise ValueError("正答PDFはリポジトリ外かつ学生用の出力先の外へ保存してください。")
        if answers_output.suffix.lower() != ".pdf":
            raise ValueError("--answers-output には教員用PDFファイルの保存先を指定してください。")
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
        "prompt": ParagraphStyle("prompt", fontName="Japanese", fontSize=11, leading=15.2,
                                 wordWrap="CJK", splitLongWords=True),
        "choice": ParagraphStyle("choice", fontName="Japanese", fontSize=10.5, leading=14.2,
                                 wordWrap="CJK", splitLongWords=True, leftIndent=15, firstLineIndent=-15),
        "explanation": ParagraphStyle("explanation", fontName="Japanese", fontSize=10.5, leading=16,
                                      wordWrap="CJK", splitLongWords=True),
    }

    def paragraph(text, style, canvas, x, top, width=column_width):
        item = Paragraph(text, styles[style])
        _, needed = item.wrap(width, 2000)
        if canvas:
            item.drawOn(canvas, x, top - needed)
        return top - needed

    def code_block(text, canvas, x, top):
        # 行頭の字下げを保ち、幅に入らない行だけを折り返す。文字の省略や画像化はしない。
        size, leading, padding = 10.2, 13.5, 6
        available = column_width - padding * 2
        lines = []
        for original in text.split("\n"):
            rest = original
            while rest:
                used = 0
                limit = 0
                for char in rest:
                    char_width = pdfmetrics.stringWidth(char, "Code" if char.isascii() else "Japanese", size)
                    if used + char_width > available:
                        break
                    used += char_width
                    limit += 1
                if limit == len(rest):
                    lines.append(rest)
                    break
                if not limit:
                    raise ValueError("コードの1文字が段幅を超えています。")
                # 空白または区切りの後で折り返し、識別子の分断をできるだけ避ける。
                candidates = [i + 1 for i, c in enumerate(rest[:limit]) if c in " ,.("]
                cut = max((i for i in candidates if i > len(rest) - len(rest.lstrip()) + 2), default=limit)
                lines.append(rest[:cut].rstrip())
                rest = "  " + rest[cut:].lstrip()
            if not original:
                lines.append("")
        needed = len(lines) * leading + 8
        if canvas:
            canvas.setStrokeColor(colors.HexColor("#777777"))
            canvas.setLineWidth(.5)
            canvas.line(x, top, x, top - needed)
            y = top - 4 - size
            for line in lines:
                cursor = x + padding
                for part in re.findall(r"[\x00-\x7f]+|[^\x00-\x7f]+", line):
                    font = "Code" if part.isascii() else "Japanese"
                    canvas.setFont(font, size)
                    canvas.drawString(cursor, y, part)
                    cursor += pdfmetrics.stringWidth(part, font, size)
                y -= leading
        return top - needed

    def columns_for(questions, answers, top, bottom):
        # 問題を途中で割らず、順番を保ったまま4段へ均等に分ける。
        heights = [top - block(q, None, 0, top, answers) for q in questions]
        prefix = [0]
        for value in heights:
            prefix.append(prefix[-1] + value)
        states = {(0, 0): (0, [])}
        for count in range(1, 5):
            for end in range(count, len(questions) + 1):
                candidates = []
                for start in range(count - 1, end):
                    previous = states.get((count - 1, start))
                    if previous is None:
                        continue
                    used = prefix[end] - prefix[start] + 10 * (end - start - 1)
                    if used <= top - bottom:
                        candidates.append((max(previous[0], used), previous[1] + [(start, end)]))
                if candidates:
                    states[count, end] = min(candidates, key=lambda value: value[0])
        result = states.get((4, len(questions)))
        if result is None:
            raise ValueError("20問がB4の2ページに入りません。文字を縮めずコードと配置を見直してください。")
        return [questions[start:end] for start, end in result[1]]

    def block(q, canvas, x, top, answers):
        if canvas:
            canvas.setFont("Japanese", 11.5)
            canvas.drawString(x, top - 11.5, f'問{q["number"]:02}  ' + (f'正答：{q["answer_letter"]}' if answers else ("空欄補充" if q["kind"] == "blank" else "コードの説明") + "（5点）"))
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
            # 長いインラインコードの直前で改行し、識別子の分断を避ける。
            prompt = re.sub(r"`([^`]*)`", lambda match:
                            ("\n" if match.start() and len(match[1]) >= 20 else "") + match[0],
                            q["prompt"])
            top = paragraph(markup(prompt), "prompt", canvas, x, top)
            top -= 6
            top = code_block(q["code"], canvas, x, top)
            top -= 6
            option_texts = [letter + "． " + markup(choice) for letter, choice in zip(LETTERS, q["choices"])]
            half = (column_width - 10) / 2
            # 短いAPI名や数値の選択肢は2列にする。長い説明は1列で読む。
            fits = all(paragraph(text, "choice", None, 0, 0, half) >= -styles["choice"].leading - .01
                       for text in option_texts)
            if fits:
                for row in range(2):
                    bottoms = [paragraph(option_texts[row * 2 + col], "choice", canvas,
                                         x + col * (half + 10), top, half) for col in range(2)]
                    top = min(bottoms) - 4
            else:
                for text in option_texts:
                    top = paragraph(text, "choice", canvas, x, top)
                    top -= 2
        return top

    files = []
    targets = [(False, output / "midterm-mock-b4.pdf")]
    if answers_output is not None:
        targets.append((True, answers_output))
    for answers, path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        title = config["title"] + (" 教員用 正答・解説" if answers else "")
        top, bottom = height - 49 * mm, 23 * mm
        columns = columns_for(paper, answers, top, bottom)
        canvas = Canvas(str(path), pagesize=(width, height), pageCompression=1, invariant=1)
        canvas.setTitle(title)
        canvas.setAuthor("Androidプログラミング1")
        canvas.setSubject("A01-A10の練習用問題。本試験の問題ではありません。")
        for page in range(2):
            canvas.setFillColor(colors.black)
            canvas.setFont("Japanese", 17)
            canvas.drawString(margin, height - 19 * mm, title)
            canvas.setFont("Japanese", 10)
            canvas.drawString(margin, height - 26 * mm, "Androidプログラミング1  /  A01〜A10  /  印刷用練習  /  20問・各5点（100点）")
            if answers:
                lines = ["教員用です。この正答PDFは、学生へ配布・公開しません。",
                         "問題用PDFと同じ番号・選択肢順です。HTMLの採点後には正答・解説を表示します。"]
            else:
                lines = ["空欄10問と説明10問です。答えを1つ選んでください。20の基本事項を1問ずつ練習します。",
                         "教科書や自作プログラムを見て構いません。分からないところを調べて復習しましょう。"]
            for i, line in enumerate(lines):
                canvas.drawString(margin, height - (31 + i * 5.5) * mm, line)
            canvas.setFont("Japanese", 9)
            canvas.drawString(margin, height - 41 * mm, "練習用です。空欄の【①】に入るコードや、コードの意味を選びます。本試験の問題ではありません。")
            canvas.setStrokeColor(colors.HexColor("#888888"))
            canvas.line(margin, height - 44 * mm, width - margin, height - 44 * mm)
            canvas.setStrokeColor(colors.HexColor("#CCCCCC"))
            canvas.line(width / 2, 23 * mm, width / 2, height - 49 * mm)
            top, bottom = height - 49 * mm, 23 * mm
            for column in range(2):
                x = margin + column * (column_width + gap)
                questions = columns[page * 2 + column]
                heights = [top - block(q, None, x, top, answers) for q in questions]
                needed = sum(heights)
                separation = (top - bottom - needed) / max(1, len(questions) - 1)
                if separation < 8:
                    raise ValueError(f"{path.name} {page + 1}ページ {column + 1}段: 必要な高さ{needed:.1f}pt / 使用可能{top-bottom:.1f}pt。文字を縮めず配置を見直してください。")
                y = top
                for q in questions:
                    y = block(q, canvas, x, y, answers) - separation
            canvas.setFont("Japanese", 9)
            canvas.setFillColor(colors.HexColor("#555555"))
            canvas.drawString(margin, 13 * mm, "中間テスト対策  /  日本語  /  練習問題")
            canvas.drawRightString(width - margin, 13 * mm, f"{page + 1} / 2")
            canvas.showPage()
        canvas.save()
        files.append(path)
    return files


def verify(files, answers_output=None):
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
            if answers_output is not None and path.resolve() == answers_output.resolve():
                expected = [f'正答：{q["answer_letter"]}', q["answer"], q["explanation"]]
            else:
                expected = [q["prompt"], q["code"]] + [letter + "．" + choice for letter, choice in zip(LETTERS, q["choices"])]
            if any(plain(item) not in section for item in expected):
                raise ValueError(f'{path}: 問{q["number"]:02}の本文・選択肢または正答が一致しません。')
        for page in reader.pages:
            w, h = float(page.mediabox.width), float(page.mediabox.height)
            if abs(w * 25.4 / 72 - 257) > .05 or abs(h * 25.4 / 72 - 364) > .05:
                raise ValueError(f"{path}: B4縦ではありません。")
            if page.get("/Annots"):
                raise ValueError(f"{path}: 不要なフォームがあります。")
        is_answer = answers_output is not None and path.resolve() == answers_output.resolve()
        if not is_answer and ("正答：" in text or "解答欄" in text):
            raise ValueError("問題用PDFに解答が混在しています。")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist/midterm")
    parser.add_argument("--answers-output", type=Path,
                        help="教員用正答PDFの保存先。リポジトリ外・学生用出力先の外を明示したときだけ生成")
    parser.add_argument("--font", type=Path, default=Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"))
    parser.add_argument("--check", action="store_true", help="生成後に寸法・問数・解答分離を検査する")
    args = parser.parse_args()
    if not args.font.is_file():
        parser.error("日本語TrueTypeフォントを --font で指定してください。")
    files = generate(args.output, args.font, args.answers_output)
    if args.check:
        verify(files, args.answers_output)
    for path in files:
        print(path)


if __name__ == "__main__":
    main()
