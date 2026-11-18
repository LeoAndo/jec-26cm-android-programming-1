"""問題データの欠落・正答の不整合・配布HTMLの更新漏れを検出する。"""

import copy
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("midterm", Path(__file__).with_name("generate-midterm-practice.py"))
midterm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(midterm)


class MidtermPracticeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = midterm.load_questions()

    def test_generated_files_are_current(self):
        for name, expected in midterm.outputs().items():
            with self.subTest(name=name):
                self.assertEqual((midterm.ROOT / name).read_text(), expected)

    def test_missing_unit_question_is_rejected(self):
        with self.assertRaises(ValueError):
            midterm.validate(self.questions[:-1])

    def test_ambiguous_choices_and_missing_answer_are_rejected(self):
        for change in ("duplicate", "missing"):
            questions = copy.deepcopy(self.questions)
            if change == "duplicate":
                questions[0]["choices"][1] = questions[0]["choices"][0]
            else:
                questions[0]["answer"] = "選択肢にない答え"
            with self.subTest(change=change), self.assertRaises(ValueError):
                midterm.validate(questions)

    def test_duplicate_id_and_broken_source_are_rejected(self):
        for key, value in (("id", self.questions[1]["id"]), ("source", "hello-android/index.html#missing-heading")):
            questions = copy.deepcopy(self.questions)
            questions[0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                midterm.validate(questions)

    def test_inline_code_is_escaped_and_protected_for_translation(self):
        self.assertEqual(midterm.inline("値を `a < 3` で比較"), "値を <code>a &lt; 3</code> で比較")
        with self.assertRaises(ValueError):
            midterm.inline("閉じない `code")


if __name__ == "__main__":
    unittest.main()
