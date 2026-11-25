"""既存の問題・対訳を使い、7言語の復習を1つのHTMLにまとめる。"""

import argparse
from collections import Counter
import html
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGE = "docs/practice/midterm.html"
LANGUAGES = ("ja", "en", "zh-Hans", "zh-Hant-HK", "my", "mn", "fr")
GROUPS = ('layout', 'view', 'click', 'read', 'write', 'parse', 'snackbar', 'empty', 'condition', 'loop', 'create', 'import', 'enabled', 'orientation', 'width', 'margin', 'private', 'concat', 'increment', 'return')


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


localizer = module("midterm_distribution_localizer", "localize-student-materials.py")


def elements(node):
    for child in node.children:
        if isinstance(child, localizer.Element):
            yield child
            yield from elements(child)


def one(node, predicate):
    matches = [el for el in elements(node) if predicate(el)]
    if len(matches) != 1:
        raise ValueError(f"問題集の要素が一意ではありません（{len(matches)}件）。")
    return matches[0]


def parse_bank(text):
    tree = localizer.parse(text, PAGE)
    bank = one(tree, lambda el: el.attribute("id") == "question-bank")
    inner = lambda el: text[el.inner_start:el.inner_end]
    result = {}
    for article in (el for el in bank.children if isinstance(el, localizer.Element)):
        choices = one(article, lambda el: el.attribute("class") == "options")
        options = [el for el in choices.children if isinstance(el, localizer.Element)]
        correct = [i for i, el in enumerate(options) if el.attribute("data-correct") == "true"]
        if len(options) != 4 or len(correct) != 1:
            raise ValueError(f"{article.attribute('data-id')} の正答が一意ではありません。")
        key = article.attribute("data-id")
        if key in result:
            raise ValueError(f"問題IDが重複しています：{key}")
        result[key] = {
            "unit": article.attribute("data-unit"),
            "group": article.attribute("data-group"),
            "kind": article.attribute("data-kind"),
            "code": inner(one(one(article, lambda el: el.attribute("class") == "question-code"), lambda el: el.tag == "code")),
            "heading": inner(one(article, lambda el: el.tag == "h3")),
            "prompt": inner(one(article, lambda el: el.attribute("class") == "prompt")),
            "choices": [inner(el) for el in options],
            "answer": correct[0],
            "explanation": inner(one(article, lambda el: el.attribute("class") == "explanation")),
            "source": inner(one(article, lambda el: el.attribute("class") == "source")),
        }
    expected = Counter({(group, kind): 1 for group in GROUPS for kind in ("blank", "explain")})
    if Counter((q["group"], q["kind"]) for q in result.values()) != expected:
        raise ValueError("復習問題は20事項に空欄1問・説明1問、計40問が必要です。")
    return result


def label_before(text, target_id):
    """文単位で一緒に翻訳された表示から、カウンター直前のラベルを取り出す。"""
    tree = localizer.parse(text, PAGE)
    for parent in [tree, *elements(tree)]:
        siblings = [el for el in parent.children if isinstance(el, localizer.Element)]
        for index, child in enumerate(siblings):
            if child.attribute("id") == target_id and index:
                previous = siblings[index - 1]
                return text[previous.inner_start:previous.inner_end]
    raise ValueError(f"表示ラベルを取得できません：{target_id}")


# 既存の日本語HTMLと同じ原文を使い、照合済みの対訳を再利用する。
EXISTING_UI = {
    "title": "中間テスト対策",
    "lead": "学んだことを、20問ずつ確かめよう。",
    "facts": "4択（ア〜エ）",
    "points": "20問 × 5点",
    "repeat": "何度でも挑戦",
    "examDate": "試験予定：<strong>2026年12月2日（水）2限</strong>。対面・60分で行います。範囲はA01〜A10 RoomSampleまでの全内容です。",
    "untimed": "時間制限なし — 調べながら復習する",
    "timed": "60分練習 — 時間切れで自動採点する",
    "start": "20問を始める",
    "quizTitle": "問題を解く",
    "answered": "回答済み：",
    "noLimit": "時間制限なし",
    "remaining": "残り時間：",
    "answerInstructions": "答えを1つ選んでください。採点するまでは変更できます。未回答は0点です。",
    "grade": "採点する",
    "unansweredConfirm": "問が未回答です。未回答を0点として採点しますか？",
    "confirmGrade": "このまま採点する",
    "keepAnswering": "回答を続ける",
    "results": "採点結果",
    "expired": "60分が経過したため、自動で採点しました。",
    "scoreSuffix": " / 100点",
    "correctPrefix": "正解：",
    "countSuffix": " / 20問",
    "blankPrefix": "　未回答：",
    "questionSuffix": "問",
    "retry": "新しい20問に挑戦する",
    "chooseMode": "練習方法を選び直す",
    "catalog": "全40問の正答・解説を見る",
    "sourceHelp": "「復習する場所」は教材ZIPのdocsフォルダからの場所と見出しIDです。このHTMLだけで解答と解説を読めます。",
    "correct": "正解",
    "incorrect": "不正解",
    "blank": "未回答",
    "yours": "あなたの回答：",
    "answer": "正答：",
}


def validate_paper(config, bank):
    ids = config["paper_ids"]
    if len(ids) != 20 or len(set(ids)) != 20 or any(key not in bank for key in ids):
        raise ValueError("paper_ids に重複・未知の問題、または件数の誤りがあります。")
    if Counter(bank[key]["group"] for key in ids) != Counter({group: 1 for group in GROUPS}):
        raise ValueError("印刷用は20の基本事項から各1問を選んでください。")
    if Counter(bank[key]["kind"] for key in ids) != Counter(blank=10, explain=10):
        raise ValueError("印刷用は空欄10問・説明10問にしてください。")


def build_data(root=ROOT):
    settings = localizer.load_settings(root)
    page = localizer.read_page(root, PAGE)
    added = json.loads((root / "config/midterm-ui-source.json").read_text())
    translations = json.loads((root / "config/midterm-ui.json").read_text())
    data = {"languages": [], "banks": {}, "ui": {}, "groups": list(GROUPS)}
    for code in LANGUAGES:
        catalog = None if code == "ja" else localizer.read_catalog(settings.catalog_path(code, PAGE))
        if catalog is not None:
            missing = [source for source, where in page.locations() if catalog.translation(source, where) is None]
            if missing:
                raise ValueError(f"{code}: 既存問題集に未翻訳が{len(missing)}件あります。")
            translated = localizer.localize(page, catalog, code, settings.source_root, {PAGE}, settings.language(code).get("android_docs_hl", "en"))
        else:
            translated = page.text
        data["banks"][code] = parse_bank(translated)
        ui = {}
        for key, source in EXISTING_UI.items():
            # この教材の再利用UIには場所別の訳はない。
            value = source if catalog is None else catalog.entries.get(localizer.normalize(source))
            if key in ("answered", "blankPrefix"):
                value = label_before(translated, "answered" if key == "answered" else "blank-count")
            if value is None:
                raise ValueError(f"{code}: 既存UIの訳がありません：{source}")
            ui[key] = value
        for key, source in added.items():
            value = source if code == "ja" else translations.get(code, {}).get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{code}: 新しいUIの訳がありません：{key}")
            if "<" in value or ">" in value:
                raise ValueError(f"{code}/{key}: UI追加文はタグを含まない文章にしてください。")
            ui[key] = html.escape(value)
        data["ui"][code] = ui
        data["languages"].append({"code": code, "name": "日本語" if code == "ja" else settings.language(code)["name"]})
    ja = data["banks"]["ja"]
    for code, bank in data["banks"].items():
        if set(bank) != set(ja):
            raise ValueError(f"{code}: 言語間の問題IDが一致しません。")
        for key, q in bank.items():
            if any(q[field] != ja[key][field] for field in ("answer", "unit", "group", "kind", "code")):
                raise ValueError(f"{code}/{key}: 正答・出題項目・形式・コードが日本語版と一致しません。")
            for field in ("prompt", "choices", "explanation"):
                code_parts = lambda value: re.findall(r"<code>(.*?)</code>", " ".join(value) if isinstance(value, list) else value, re.S)
                protected = lambda value: Counter(localizer.normalize(part) for part in code_parts(value))
                if protected(q[field]) != protected(ja[key][field]):
                    raise ValueError(f"{code}/{key}: {field} のコードが日本語版と一致しません。")
                # 対訳カタログは改行を正規化する。コードの読みやすい字下げは日本語版から戻す。
                originals = {localizer.normalize(part): part for part in code_parts(ja[key][field])}
                restore = lambda value: re.sub(r"<code>(.*?)</code>", lambda match: '<code>' + originals[localizer.normalize(match[1])] + '</code>', value, flags=re.S)
                q[field] = [restore(value) for value in q[field]] if isinstance(q[field], list) else restore(q[field])
    paper = json.loads((root / "config/midterm-mock.json").read_text())
    validate_paper(paper, ja)
    data["paperIds"] = paper["paper_ids"]
    return data


def render(root=ROOT):
    template = (root / "scripts/templates/midterm-distribution.html").read_text()
    marker = "<!-- MIDTERM_DATA -->"
    if template.count(marker) != 1:
        raise ValueError("データの挿入位置が一意ではありません。")
    serialized = json.dumps(build_data(root), ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template.replace(marker, '<script id="midterm-data" type="application/json">' + serialized + '</script>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist/midterm/midterm-practice.html")
    args = parser.parse_args()
    output = render()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"7言語・各40問（空欄20・説明20）の配布HTMLを生成しました：{args.output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
