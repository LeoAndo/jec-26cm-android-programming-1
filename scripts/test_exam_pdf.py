"""架空問題でページ割り・学校フッター・非公開用PDFの内容を確かめる。"""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/prepare-exam-materials/scripts"
sys.path.insert(0, str(SCRIPTS))
import build_exam_pdf as pdf


def fixture(count=3):
    exam = {
        "exam_type": "final", "exam_datetime": "2027-02-15T10:00:00+09:00",
        "duration_minutes": 45, "exam_count": count,
        "footer": {"subject": "架空科目", "class_name": "練習組", "author": "架空教員",
                   "term": "後期", "period": "2", "allowed_materials": "持込不可",
                   "submission": "提出不要"},
    }
    questions = [{"id": f"demo-{i}", "prompt": "最後に入る数を選んでください。",
                  "code": f"int count = {i};\ncount++;",
                  "choices": [str(i + j) for j in range(1, 5)], "answer": 0,
                  "explanation": "非公開の解説だけにある文字列"} for i in range(1, count + 1)]
    return exam, questions


class PaginationTest(unittest.TestCase):
    def test_small_odd_and_many_questions_remain_in_order(self):
        for count in (1, 3, 21, 41):
            heights = [100 + (i % 3) * 12 for i in range(count)]
            columns = pdf.columns_for(heights, 600)
            self.assertEqual([q for col in columns for q in col], list(range(count)))
            self.assertTrue(all(sum(heights[q] for q in col) + (len(col) - 1) * pdf.QUESTION_GAP <= 600
                                for col in columns))
            if count == 3:
                self.assertEqual(len(columns), 2)

    def test_oversize_question_fails_instead_of_clipping(self):
        with self.assertRaisesRegex(ValueError, "1問が1段"):
            pdf.columns_for([601], 600)

    def test_footer_uses_exam_date_duration_and_actual_page_count(self):
        exam, _ = fixture()
        values = pdf.footer_values(exam, 3, 5)
        self.assertEqual((values["year"], values["month"], values["day"]), ("2027", "2", "15"))
        self.assertEqual((values["duration"], values["page"], values["pages"]), ("45", "3", "5"))


PDF_AVAILABLE = all(importlib.util.find_spec(name) for name in ("reportlab", "pypdf"))
FONT_AVAILABLE = pdf.DEFAULT_FONT.is_file() and pdf.DEFAULT_CODE_FONT.is_file()


@unittest.skipUnless(PDF_AVAILABLE and FONT_AVAILABLE, "PDFの依存と日本語フォントを使う検証は別途実行する")
class RenderTest(unittest.TestCase):
    def test_pdf_sizes_page_numbers_and_answer_separation(self):
        from pypdf import PdfReader
        with tempfile.TemporaryDirectory() as temporary:
            for count in (1, 3, 21):
                exam, questions = fixture(count)
                if count == 21:
                    exam.update(points_per_question=2, total_points=42)
                output = Path(temporary) / f"final-{count}.pdf"
                report = pdf.generate(exam, questions, output)
                reader = PdfReader(output)
                text = "\n".join(p.extract_text() for p in reader.pages)
                self.assertEqual(len(reader.pages), report["pages"])
                self.assertNotIn("非公開の解説だけにある文字列", text)
                self.assertNotIn("正答", text)
                self.assertIn("期末テスト", text)
                for i in range(1, count + 1):
                    self.assertEqual(text.count(f"問{i:02d}"), 1)
                self.assertEqual("（2点）" in text, count == 21)
                for metric in report["questions"]:
                    self.assertGreater(metric["bbox_pt"][1], report["footer_bbox_pt"][3])
                self.assertEqual(json.loads(output.with_suffix(".layout.json").read_text())["pages"], len(reader.pages))
                # PDFに実際に書かれた罫線の位置から、全ページの固定範囲を検算する。
                if importlib.util.find_spec("pymupdf"):
                    import pymupdf
                    document = pymupdf.open(output)
                    asset = json.loads(pdf.FOOTER.read_text())
                    x0, y0, x1, y1 = asset["target_bbox_pt"]
                    sw, sh = asset["size"]
                    sx, sy = (x1 - x0) / sw, (y1 - y0) / sh
                    for page_number, page in enumerate(document, 1):
                        drawings = [d["rect"] for d in page.get_drawings() if d["rect"].y0 > page.rect.height - 140]
                        bounds = pymupdf.Rect(drawings[0])
                        for rect in drawings[1:]:
                            bounds |= rect
                        actual = [bounds.x0, page.rect.height - bounds.y1, bounds.x1, page.rect.height - bounds.y0]
                        for observed, expected in zip(actual, report["footer_bbox_pt"]):
                            self.assertAlmostEqual(observed, expected, delta=.002)
                        for key, value in (("page", page_number), ("pages", len(document))):
                            left, top, right, bottom = asset["fields"][key]
                            clip = pymupdf.Rect(x0 + left * sx, page.rect.height - y1 + top * sy,
                                                x0 + right * sx, page.rect.height - y1 + bottom * sy)
                            self.assertEqual(page.get_text(clip=clip).strip(), str(value))

    def test_code_and_footer_overflow_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "too-long.pdf"
            exam, questions = fixture(1)
            questions[0]["code"] = "a" * 200
            with self.assertRaisesRegex(ValueError, "コードの行が段幅"):
                pdf.generate(exam, questions, output)
            self.assertFalse(output.exists())
            exam, questions = fixture(1)
            exam["footer"]["author"] = "名前" * 30
            with self.assertRaisesRegex(ValueError, "author が欄の幅"):
                pdf.generate(exam, questions, output)
            self.assertFalse(output.exists())

    def test_missing_glyph_fails(self):
        exam, questions = fixture(1)
        questions[0]["prompt"] = "\U0010ffff"
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "フォントに文字"):
                pdf.generate(exam, questions, Path(temporary) / "missing.pdf")


if __name__ == "__main__":
    unittest.main()
