"""配布時に7言語の欠落、出題形式の偏り、正答・コードのずれを検出する。"""

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
        self.assertEqual(len(japanese), 40)
        self.assertEqual(self.data["groups"], list(distribution.GROUPS))
        for language, bank in self.data["banks"].items():
            with self.subTest(language=language):
                self.assertEqual(set(bank), set(japanese))
                self.assertEqual(set(self.data["ui"][language]), set(self.data["ui"]["ja"]))
                self.assertTrue(all(self.data["ui"][language].values()))
                for key in bank:
                    for field in ("answer", "group", "kind", "code"):
                        self.assertEqual(bank[key][field], japanese[key][field])
                    self.assertEqual(len(bank[key]["choices"]), 4)

    def test_invalid_paper_selection_cannot_be_published(self):
        valid = {"paper_ids": self.data["paperIds"]}
        bank = self.data["banks"]["ja"]
        for mutation in ("duplicate", "unknown", "missing", "wrong_group", "wrong_kind"):
            value = copy.deepcopy(valid)
            if mutation == "duplicate":
                value["paper_ids"][0] = value["paper_ids"][1]
            elif mutation == "unknown":
                value["paper_ids"][0] = "B99"
            elif mutation == "missing":
                value["paper_ids"].pop()
            else:
                first = value["paper_ids"][0]
                same_kind = mutation == "wrong_group"
                other = next(key for key, question in bank.items()
                             if key not in value["paper_ids"]
                             and (question["kind"] == bank[first]["kind"]) == same_kind
                             and (question["group"] == bank[first]["group"]) != same_kind)
                value["paper_ids"][0] = other
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                distribution.validate_paper(value, bank)

    def test_single_html_uses_same_japanese_bank_without_overrides(self):
        original = distribution.parse_bank((distribution.ROOT / distribution.PAGE).read_text())
        self.assertEqual(self.data["banks"]["ja"], original)

    def test_bad_question_markup_is_rejected(self):
        original = (distribution.ROOT / distribution.PAGE).read_text()
        for before, after in (("data-kind=\"blank\"", "data-kind=\"explain\""),
                              ("data-group=\"layout\"", "data-group=\"view\""),
                              ('data-correct="true"', 'data-correct="false"')):
            with self.subTest(before=before), self.assertRaises(ValueError):
                distribution.parse_bank(original.replace(before, after, 1))

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
        self.assertNotIn('mockIds', data)
        self.assertNotIn('start-mock', rendered)
        self.assertFalse(any(key.startswith('mock') or key == 'languageLocked' for key in data['ui']['ja']))


if __name__ == "__main__":
    unittest.main()
