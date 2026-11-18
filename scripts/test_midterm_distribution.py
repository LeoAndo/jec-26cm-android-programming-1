"""配布時に7言語の欠落、模擬試験の範囲違い、正答のずれを検出する。"""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("midterm_distribution", Path(__file__).with_name("build-midterm-distribution.py"))
distribution = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(distribution)


class MidtermDistributionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = distribution.build_data()

    def test_all_languages_have_complete_questions_and_ui(self):
        self.assertEqual(set(self.data["banks"]), set(distribution.LANGUAGES))
        japanese = self.data["banks"]["ja"]
        self.assertEqual(len(japanese), 120)
        for language, bank in self.data["banks"].items():
            with self.subTest(language=language):
                self.assertEqual(set(bank), set(japanese))
                self.assertEqual(set(self.data["ui"][language]), set(self.data["ui"]["ja"]))
                self.assertTrue(all(self.data["ui"][language].values()))
                for key in bank:
                    self.assertEqual(bank[key]["answer"], japanese[key]["answer"])
                    self.assertEqual(len(bank[key]["choices"]), 4)

    def test_invalid_mock_selection_cannot_be_published(self):
        valid = {"question_ids": self.data["mockIds"], "paper_ids": self.data["paperIds"]}
        for mutation in ("duplicate", "unknown", "wrong_unit", "paper_outside_pool"):
            value = copy.deepcopy(valid)
            if mutation == "duplicate":
                value["question_ids"][0] = value["question_ids"][1]
            elif mutation == "unknown":
                value["question_ids"][0] = "A11-01"
            elif mutation == "wrong_unit":
                other = next(key for key in self.data["banks"]["ja"] if key.startswith("A02") and key not in value["question_ids"])
                value["question_ids"][0] = other
            else:
                first = value["paper_ids"][0]
                other = next(key for key in self.data["banks"]["ja"] if key[:3] == first[:3] and key not in value["question_ids"])
                value["paper_ids"][0] = other
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                distribution.validate_mock(value, self.data["banks"]["ja"])

    def test_plain_japanese_preserves_correct_choice_and_explanation(self):
        original = distribution.parse_bank((distribution.ROOT / distribution.PAGE).read_text())
        overrides = json.loads((distribution.ROOT / "config/midterm-plain-ja.json").read_text())
        generator = distribution.module("midterm_distribution_test_generator", "generate-midterm-practice.py")
        for key, changes in overrides.items():
            with self.subTest(question=key):
                question = self.data["banks"]["ja"][key]
                self.assertEqual(question["answer"], original[key]["answer"])
                if "choices" in changes:
                    self.assertEqual(question["choices"], [generator.inline(choice) for choice in changes["choices"]])
                    answer = question["choices"][question["answer"]]
                    self.assertTrue(question["explanation"].startswith('<p>正答：<strong>' + answer + '</strong></p>'))

    def test_supplemented_prompts_use_complete_updated_translations(self):
        translations = json.loads((distribution.ROOT / "config/midterm-question-translations.json").read_text())
        generator = distribution.module("midterm_distribution_test_generator", "generate-midterm-practice.py")
        for language, entries in translations.items():
            self.assertEqual(set(entries), distribution.UPDATED_PROMPTS)
            for key, fields in entries.items():
                with self.subTest(language=language, question=key):
                    self.assertEqual(self.data["banks"][language][key]["prompt"], generator.inline(fields["prompt"]))

    def test_incomplete_or_changed_code_in_updated_translation_is_rejected(self):
        valid = json.loads((distribution.ROOT / "config/midterm-question-translations.json").read_text())
        plain = json.loads((distribution.ROOT / "config/midterm-plain-ja.json").read_text())
        for mutation in ("language", "question", "field", "empty", "code", "extra_field"):
            translations = copy.deepcopy(valid)
            if mutation == "language":
                del translations["en"]
            elif mutation == "question":
                del translations["en"]["A03-10"]
            elif mutation == "field":
                del translations["en"]["A03-10"]["prompt"]
            elif mutation == "empty":
                translations["en"]["A03-10"]["prompt"] = " "
            elif mutation == "code":
                translations["en"]["A03-10"]["prompt"] += " `changedCode()`"
            else:
                translations["en"]["A03-10"]["answer"] = 3
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                distribution.apply_question_translations(copy.deepcopy(self.data), translations, plain)

    def test_embedded_data_is_self_contained_and_safe_in_script_element(self):
        rendered = distribution.render()
        marker = '<script id="midterm-data" type="application/json">'
        embedded = rendered.split(marker, 1)[1].split('</script>', 1)[0]
        self.assertNotIn('<', embedded)
        data = json.loads(embedded)
        self.assertEqual(data, self.data)
        self.assertNotIn('src="http', rendered)
        self.assertNotIn('href="http', rendered)
        self.assertNotIn('<!-- MIDTERM_DATA -->', rendered)


if __name__ == "__main__":
    unittest.main()
