"""試験条件の取り違え・配点不一致・公開領域への誤出力を止める。"""

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/prepare-exam-materials/scripts"))
import exam_common as common


class ExamInputTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "exam.json"
        self.exam = json.loads((ROOT / "skills/prepare-exam-materials/assets/exam.example.json").read_text())

    def load(self, **changes):
        self.path.write_text(json.dumps({**self.exam, **changes}))
        return common.load_exam(self.path)

    def test_defaults_and_practice_override(self):
        self.assertEqual(self.load(exam_count=1)["practice_count"], 2)
        self.assertEqual(self.load(exam_count=21)["practice_count"], 42)
        loaded = self.load(exam_count=3, practice_count=5, draw_count=2)
        self.assertEqual((loaded["practice_count"], loaded["draw_count"]), (5, 2))

    def test_counts_format_and_languages_are_not_silently_replaced(self):
        for change in ({"exam_count": 0}, {"exam_count": True}, {"practice_count": 1, "draw_count": 2},
                       {"answer_format": "written"}, {"languages": [{"code": "en", "name": "English"}]},
                       {"duration_minutes": 0}, {"exam_datetime": "2030-02-01"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.load(**change)

    def test_points_total_is_checked_without_float_rounding_error(self):
        self.assertEqual(self.load(exam_count=3, points_per_question=.1, total_points=.3)["total_points"], .3)
        for change in ({"points_per_question": 5, "total_points": 100}, {"total_points": 100},
                       {"points_per_question": float("nan")}, {"points_per_question": -2}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.load(**change)

    def test_git_and_symlink_destinations_are_rejected(self):
        with self.assertRaises(ValueError):
            common.private_output(ROOT / "dist/final.pdf")
        link = Path(self.directory.name) / "linked-repository"
        link.symlink_to(ROOT, target_is_directory=True)
        with self.assertRaises(ValueError):
            common.private_output(link / "final.pdf")
        safe = Path(self.directory.name) / "private/final.pdf"
        self.assertEqual(common.private_output(safe), safe.resolve())

    def test_duplicate_choices_and_wrong_purpose_fail(self):
        exam = self.load(exam_count=1)
        path = Path(self.directory.name) / "final.json"
        q = {"id": "demo", "topic": "架空", "prompt": "数を選びます。", "choices": ["1", "2", "3", "4"],
             "answer": 0, "explanation": "架空の解説", "source": "docs/example/index.html#demo"}
        path.write_text(json.dumps({"purpose": "final", "questions": [q]}))
        self.assertEqual(common.load_questions(path, exam, "final")[0]["answer"], 0)
        with self.assertRaises(ValueError):
            common.load_questions(path, exam, "practice")
        q["choices"] = ["1", " 1 ", "3", "4"]
        path.write_text(json.dumps({"purpose": "final", "questions": [q]}))
        with self.assertRaises(ValueError):
            common.load_questions(path, exam, "final")


if __name__ == "__main__":
    unittest.main()
