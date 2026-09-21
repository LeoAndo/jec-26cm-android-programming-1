"""配布用JavaScriptの進捗引継ぎを、保存領域を分けて検証する。"""
from pathlib import Path
import shutil
import subprocess
import unittest


class TextbookJavaScriptTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "JavaScriptの回帰検証にはNode.jsが必要です。")
    def test_progress_and_language_navigation(self):
        result = subprocess.run(["node", "--test", str(Path(__file__).with_suffix(".js"))],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
