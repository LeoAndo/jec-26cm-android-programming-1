"""架空の問題で、今回用HTMLの数値・言語・公開データの境界を検査する。"""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL_SCRIPTS = Path(__file__).resolve().parents[1] / "skills/prepare-exam-materials/scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
SPEC = importlib.util.spec_from_file_location("exam_practice", SKILL_SCRIPTS / "build_practice.py")
practice = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(practice)


def fixture(count=3, **overrides):
    """実試験を参照しない、数値とコード表示だけの動作確認用入力。"""
    exam = {"exam_type": "final", "exam_datetime": "2030-02-01T10:00:00+09:00",
            "duration_minutes": 37, "scope": ["架空教材の数値"], "answer_format": "four_choice",
            "exam_count": count, "languages": [{"code": "ja", "name": "日本語"},
                                                 {"code": "en", "name": "English"}]}
    exam.update(overrides)
    questions = []
    for index in range(exam.get("practice_count", count * 2)):
        choices = [f"`{index + offset}`" for offset in range(4)]
        questions.append({"id": f"P{index + 1}", "topic": "架空の数値", "code": f"var number = {index};",
                          "prompt": "変数に入る数を選んでください。", "choices": choices,
                          "answer": 0, "explanation": f"右側の `{index}` が入ります。",
                          "source": "docs/example/index.html#number",
                          "translations": {"en": {"prompt": "Choose the value assigned to the variable.",
                                                   "choices": choices,
                                                   "explanation": f"The assigned value is `{index}`."}}})
    return exam, {"purpose": "practice", "questions": questions, "ui": {}}


def load_fixture(directory, count=3, **overrides):
    exam, questions = fixture(count, **overrides)
    exam_path = directory / "exam.json"
    question_path = directory / "practice.json"
    exam_path.write_text(json.dumps(exam), encoding="utf-8")
    loaded = practice.exam_common.load_exam(exam_path)
    # UIの意味はこのテストの対象外。同じトークンを保つ別言語キーを用意する。
    questions["ui"]["en"] = practice.japanese_ui(loaded)
    question_path.write_text(json.dumps(questions), encoding="utf-8")
    bank = practice.exam_common.load_questions(question_path, loaded, kind="practice")
    return loaded, bank, questions["ui"], exam_path, question_path


class ExamPracticeTest(unittest.TestCase):
    def test_small_and_odd_counts_use_requested_settings(self):
        with tempfile.TemporaryDirectory() as temp:
            for count in (1, 3, 21):
                with self.subTest(count=count):
                    exam, bank, ui, *_ = load_fixture(Path(temp), count)
                    data = practice.build_data(exam, bank, ui)
                    self.assertEqual(len(data["banks"]["ja"]), count * 2)
                    self.assertEqual(data["settings"]["drawCount"], count)
                    self.assertEqual(data["settings"]["durationMinutes"], 37)
                    self.assertIsNone(data["settings"]["pointsPerQuestion"])
                    self.assertEqual(data["ui"]["ja"]["title"], "期末テスト対策問題集")
                    self.assertIn(f"{count}問", data["ui"]["ja"]["scoreSuffix"])

    def test_pool_draw_and_score_are_separate(self):
        with tempfile.TemporaryDirectory() as temp:
            exam, bank, ui, *_ = load_fixture(Path(temp), 3, practice_count=5, draw_count=2,
                                               points_per_question=2.5, total_points=7.5)
            data = practice.build_data(exam, bank, ui)
            self.assertEqual(len(data["banks"]["ja"]), 5)
            self.assertEqual(data["settings"]["drawCount"], 2)
            self.assertEqual(data["ui"]["ja"]["scoreSuffix"], " / 5点")
            self.assertEqual(data["ui"]["ja"]["points"], "2問 × 2.5点")
            self.assertIn("3問", data["ui"]["ja"]["examRules"])

    def test_missing_ui_and_dropped_count_tokens_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            exam, bank, ui, *_ = load_fixture(Path(temp))
            for mutation in ("language", "key", "token"):
                translated = copy.deepcopy(ui)
                if mutation == "language":
                    translated.clear()
                elif mutation == "key":
                    del translated["en"]["start"]
                else:
                    translated["en"]["start"] = "Start"
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    practice.build_data(exam, bank, translated)

    def test_translated_choice_code_cannot_move_to_another_answer_slot(self):
        with tempfile.TemporaryDirectory() as temp:
            exam, bank, ui, *_ = load_fixture(Path(temp))
            choices = bank[0]["translations"]["en"]["choices"]
            choices[0], choices[1] = choices[1], choices[0]
            with self.assertRaises(ValueError):
                practice.build_data(exam, bank, ui)

    def test_render_only_embeds_public_fields_and_escapes_program_text(self):
        with tempfile.TemporaryDirectory() as temp:
            exam, bank, ui, *_ = load_fixture(Path(temp))
            bank[0]["code"] = '</script><script>alert("fixture")</script>'
            bank[0]["teacher_note"] = "PRIVATE_FIXTURE_MARKER"
            rendered = practice.render(exam, bank, ui)
            embedded = rendered.split('<script id="midterm-data" type="application/json">')[1].split('</script>')[0]
            self.assertNotIn("<", embedded)
            self.assertNotIn("PRIVATE_FIXTURE_MARKER", rendered)
            self.assertEqual(json.loads(embedded)["banks"]["ja"]["P1"]["code"],
                             '&lt;/script&gt;&lt;script&gt;alert(&quot;fixture&quot;)&lt;/script&gt;')
            self.assertIn('<title>期末テスト対策問題集</title>', rendered)
            self.assertNotIn("ANDROID PROGRAMMING 1 · A01–A10", rendered)
            self.assertNotIn("2026年12月2日", rendered)

    def test_cli_rejects_final_questions_without_writing_html(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            *_, exam_path, question_path = load_fixture(directory)
            value = json.loads(question_path.read_text())
            value["purpose"] = "final"
            question_path.write_text(json.dumps(value))
            output = directory / "practice.html"
            result = subprocess.run([sys.executable, str(SKILL_SCRIPTS / "build_practice.py"),
                                     "--exam", str(exam_path), "--questions", str(question_path),
                                     "--output", str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
