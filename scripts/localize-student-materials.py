"""日本語の教科書から翻訳する文を取り出し、対訳カタログから各言語のHTMLを作る。

翻訳そのものは行わない。訳すのはエージェントで、このスクリプトは入口と出口をそろえる。

  sync    未翻訳の文を、訳す単位に分けた作業ファイルとして書き出す。使わなくなった訳は外す
  merge   訳した結果を検査して、対訳カタログへ入れる
  check   対訳カタログを検査する（CI用。未翻訳があっても落とさない）
  status  言語×ページごとに、訳した数を出す
  build   対訳カタログから各言語のHTMLを作る（確認用）

対訳カタログ（i18n/<言語>/<ページ>.json）には、訳した文だけを置く。
原文がカタログにない文が「未翻訳」で、HTMLを作るときは日本語のまま出す。
日本語の文を直すと原文が変わるので、その文は自動で未翻訳に戻る。古い訳は学生に届かない。
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import difflib
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import sys
from urllib.parse import unquote, urlsplit, urlunsplit


CONFIG = Path("config/i18n.json")
TERMS_CONFIG = Path("config/teaching-materials.json")
WORK_DIR = Path("dist/i18n-work")
PREVIEW_DIR = Path("dist/i18n-preview")

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# 文の途中に入る要素。これ以外の要素は、文の区切りになる。
INLINE = {
    "a", "abbr", "b", "br", "cite", "code", "em", "i", "img", "kbd", "mark", "q", "rp", "rt", "ruby",
    "s", "samp", "small", "span", "strong", "sub", "sup", "time", "u", "var", "wbr",
}
# 中身を訳さないインライン要素。訳文でも、中身を原文と同じにする。
PROTECTED = {"code", "kbd", "samp", "var"}
# 中を取り出さない要素。作ったHTMLでも、日本語版のバイト列をそのまま使う。
SKIPPED = {"pre", "script", "style"}
TRANSLATED_ATTRIBUTES = ("alt", "aria-label", "title", "placeholder")
LINK_ATTRIBUTES = ("href", "src")

# ひらがな・カタカナ・漢字。「・」（U+30FB）は、英字だけの文にも区切りとして出てくるので含めない。
JAPANESE = re.compile(r"[\u3041-\u309f\u30a1-\u30fa\u30fc-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f\u3005]")
KANA = re.compile(r"[\u3041-\u309f\u30a1-\u30fa\u30fc-\u30ff\uff66-\uff9f]")
# カタログの中のタグ。属性のないタグはそのまま（<strong>）、属性つきのタグは番号つきの目印（<a1>）で書く。
CATALOG_TAG = re.compile(r"<(/?)([a-z]+)(\d*)(/?)>")
ENTITY = re.compile(r"&(?:[A-Za-z][A-Za-z0-9]*|#[0-9]+|#[xX][0-9A-Fa-f]+);")
LANGUAGE_CODE = re.compile(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]+)*")


class LocalizeError(ValueError):
    """教材か対訳カタログに、このスクリプトが扱えない形がある。"""


# ---------------------------------------------------------------------------
# HTMLを、元の位置つきの木にする
# ---------------------------------------------------------------------------

@dataclass
class Text:
    start: int
    end: int


@dataclass
class Element:
    tag: str
    attrs: list
    start: int  # 開始タグの先頭
    inner_start: int  # 開始タグの直後
    inner_end: int = -1  # 終了タグの先頭（void要素は inner_start と同じ）
    end: int = -1  # 終了タグの直後
    children: list = field(default_factory=list)
    inline: bool = False  # 自分も子孫も、すべて文の途中に入る要素

    def attribute(self, name: str):
        return next((value for key, value in self.attrs if key == name), None)


class _TreeBuilder(HTMLParser):
    """開始タグと終了タグが必ず対応しているHTMLだけを受け付ける。

    生成するHTMLは、取り出した文と属性のほかは元のバイト列をそのまま使う。
    そのために、どのトークンも元の文字列のどこからどこまでかを記録する。
    """

    def __init__(self, text: str, name: str):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.name = name
        self._line_starts = [0] + [match.end() for match in re.finditer("\n", text)]
        self.root = Element("#root", [], 0, 0)
        self._stack = [self.root]
        self._covered = 0  # 次のトークンが始まるはずの位置。取りこぼしを見つけるために持つ。

    def _fail(self, message: str):
        raise LocalizeError(f"{self.name}:{self.getpos()[0]}: {message}")

    def _span(self, length: int | None = None, until: str | None = None) -> tuple:
        line, column = self.getpos()
        start = self._line_starts[line - 1] + column
        if start != self._covered:
            self._fail("HTMLを解析できない箇所があります")
        if until is not None:
            found = self.text.find(until, start)
            if found < 0:
                self._fail(f"「{until}」で閉じていません")
            length = found + len(until) - start
        self._covered = start + length
        return start, start + length

    def _open(self, tag: str, attrs: list, void: bool):
        start, end = self._span(len(self.get_starttag_text()))
        element = Element(tag, attrs, start, end)
        self._stack[-1].children.append(element)
        if void:
            element.inner_end = element.end = end
        else:
            self._stack.append(element)

    def handle_starttag(self, tag, attrs):
        self._open(tag, attrs, tag in VOID)

    def handle_startendtag(self, tag, attrs):
        if tag not in VOID:
            self._fail(f"<{tag}/> のような自己終了タグは使えません。</{tag}> で閉じてください")
        self._open(tag, attrs, True)

    def handle_endtag(self, tag):
        start, end = self._span(until=">")
        if tag in VOID:
            self._fail(f"</{tag}> は書けません（閉じタグのない要素です）")
        element = self._stack[-1]
        if element.tag != tag:
            opened = f"<{element.tag}>" if element is not self.root else "（なし）"
            self._fail(f"開始タグと終了タグが対応していません: 開いているのは{opened}、閉じようとしたのは</{tag}>")
        element.inner_end, element.end = start, end
        self._stack.pop()

    def _text(self, length: int):
        start, end = self._span(length)
        siblings = self._stack[-1].children
        if siblings and isinstance(siblings[-1], Text) and siblings[-1].end == start:
            siblings[-1].end = end
        else:
            siblings.append(Text(start, end))

    def handle_data(self, data):
        self._text(len(data))

    def handle_entityref(self, name):
        self._reference(f"&{name}")

    def handle_charref(self, name):
        self._reference(f"&#{name}")

    def _reference(self, raw: str):
        line, column = self.getpos()
        start = self._line_starts[line - 1] + column
        closed = self.text.startswith(";", start + len(raw))
        self._text(len(raw) + (1 if closed else 0))

    def handle_comment(self, data):
        self._span(until="-->")

    def handle_decl(self, decl):
        self._span(until=">")

    def handle_pi(self, data):
        self._span(until=">")

    def finish(self) -> Element:
        self.close()
        if len(self._stack) > 1:
            unclosed = self._stack[-1]
            line = self.text.count("\n", 0, unclosed.start) + 1
            raise LocalizeError(f"{self.name}:{line}: <{unclosed.tag}> が閉じていません")
        if self._covered != len(self.text):
            raise LocalizeError(f"{self.name}: HTMLを最後まで解析できません")
        self.root.inner_end = self.root.end = len(self.text)
        _mark_inline(self.root)
        return self.root


def _mark_inline(element: Element) -> bool:
    children_inline = True
    for child in element.children:
        if isinstance(child, Element) and not _mark_inline(child):
            children_inline = False
    element.inline = element.tag in INLINE and children_inline
    return element.inline


def parse(text: str, name: str) -> Element:
    builder = _TreeBuilder(text, name)
    builder.feed(text)
    return builder.finish()


# ---------------------------------------------------------------------------
# 文と属性を取り出す
# ---------------------------------------------------------------------------

@dataclass
class Segment:
    source: str  # カタログに書く形の原文
    where: str  # 訳す人への手がかり（p、td、img alt など）
    start: int = -1  # 本文の文：置き換える範囲
    end: int = -1
    placeholders: list = field(default_factory=list)  # 番号つきの目印に置き換えた要素。<a1> は placeholders[0]
    element: Element | None = None  # 属性の文：その属性を持つ要素
    attribute: str | None = None

    @property
    def id(self) -> str:
        return segment_id(self.source)


def segment_id(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]


def normalize(text: str) -> str:
    """改行や字下げの違いで原文が変わったことにならないよう、空白は1つにまとめる。"""
    return " ".join(text.split())


def _attribute_pattern(name: str) -> re.Pattern:
    return re.compile(rf'(\s{re.escape(name)}\s*=\s*)(?:"([^"]*)"|\'([^\']*)\')', re.IGNORECASE)


def _raw_attribute(text: str, element: Element, name: str) -> str | None:
    """開始タグに書いてあるままの属性値（&amp; などを戻していない形）。"""
    match = _attribute_pattern(name).search(text[element.start:element.inner_start])
    if not match:
        return None
    return match.group(2) if match.group(2) is not None else match.group(3)


def _translated_attributes(element: Element) -> list:
    names = [name for name in TRANSLATED_ATTRIBUTES if element.attribute(name)]
    if element.tag == "meta" and (element.attribute("name") or "").lower() == "description" and element.attribute("content"):
        names.append("content")
    return names


def _untranslatable(element: Element) -> bool:
    return element.tag in SKIPPED or (element.attribute("translate") or "").lower() == "no"


def plain_text(source: str) -> str:
    """カタログの形の文から、訳さない要素の中身とタグを除いた文字。"""
    stripped = re.sub(r"<(code|kbd|samp|var)(\d*)>.*?</\1\2>", " ", source)
    return CATALOG_TAG.sub(" ", stripped)


class _Extractor:
    def __init__(self, text: str, name: str):
        self.text = text
        self.name = name
        self.segments: list = []
        self.in_segment: set = set()  # 本文の文に含まれる要素。開始タグは、文を戻すときに一緒に作り直す

    def run(self, root: Element) -> list:
        self._walk(root)
        self._attributes(root)
        self.segments.sort(key=lambda item: item.start if item.element is None else item.element.start)
        return self.segments

    def _blank(self, node) -> bool:
        return isinstance(node, Text) and not self.text[node.start:node.end].strip()

    def _walk(self, container: Element):
        """子を、文の区切りになる要素で分けた「インラインの連なり」ごとに処理する。"""
        run: list = []
        for child in container.children:
            if isinstance(child, Text) or child.inline:
                run.append(child)
                continue
            self._flush(run, container)
            run = []
            if not _untranslatable(child):
                self._walk(child)
        self._flush(run, container)

    def _flush(self, run: list, container: Element):
        while run and self._blank(run[0]):
            run = run[1:]
        while run and self._blank(run[-1]):
            run = run[:-1]
        if not run:
            return
        if any(isinstance(node, Text) and not self._blank(node) for node in run):
            self._segment(run, container)
            return
        # 文字を直接持たない連なり（リンクの並びなど）は、要素を1つずつ別の文にする。
        for node in run:
            if isinstance(node, Element) and node.tag not in PROTECTED and not _untranslatable(node):
                self._walk(node)

    def _segment(self, run: list, container: Element):
        start, end = run[0].start, run[-1].end
        if isinstance(run[0], Text):
            raw = self.text[start:run[0].end]
            start += len(raw) - len(raw.lstrip())
        if isinstance(run[-1], Text):
            raw = self.text[run[-1].start:end]
            end -= len(raw) - len(raw.rstrip())
        placeholders: list = []
        source = normalize(self._serialize(run, placeholders, start, end))
        if not JAPANESE.search(plain_text(source)):
            return
        self._remember(run)
        self.segments.append(Segment(source, container.tag, start, end, placeholders))

    def _remember(self, nodes: list):
        for node in nodes:
            if isinstance(node, Element):
                self.in_segment.add(id(node))
                self._remember(node.children)

    def _serialize(self, nodes: list, placeholders: list, start: int, end: int) -> str:
        parts = []
        for node in nodes:
            if isinstance(node, Text):
                parts.append(self.text[max(node.start, start):min(node.end, end)])
                continue
            name = node.tag
            if node.attrs:
                placeholders.append(node)
                name = f"{node.tag}{len(placeholders)}"
            if node.tag in VOID:
                parts.append(f"<{name}/>" if node.attrs else f"<{name}>")
            else:
                parts.append(f"<{name}>{self._serialize(node.children, placeholders, start, end)}</{name}>")
        return "".join(parts)

    def _attributes(self, element: Element):
        for child in element.children:
            if not isinstance(child, Element) or _untranslatable(child):
                continue
            for name in _translated_attributes(child):
                raw = _raw_attribute(self.text, child, name)
                if raw is None:
                    line = self.text.count("\n", 0, child.start) + 1
                    raise LocalizeError(f"{self.name}:{line}: {name} 属性は引用符で囲んでください")
                source = normalize(raw)
                if JAPANESE.search(source):
                    self.segments.append(Segment(source, f"{child.tag} {name}", element=child, attribute=name))
            if child.tag not in PROTECTED:
                self._attributes(child)


@dataclass
class Page:
    name: str  # リポジトリの直下から見たパス（docs/hello-android/index.html）
    text: str
    root: Element
    segments: list
    in_segment: set

    def sources(self) -> list:
        """このページの原文。同じ文は1回だけ、文書に出てくる順で並べる。"""
        return list(dict.fromkeys(segment.source for segment in self.segments))


def read_page(root: Path, name: str) -> Page:
    text = (root / name).read_text(encoding="utf-8")
    tree = parse(text, name)
    extractor = _Extractor(text, name)
    return Page(name, text, tree, extractor.run(tree), extractor.in_segment)


# ---------------------------------------------------------------------------
# 訳文の検査
# ---------------------------------------------------------------------------

def _tags(text: str) -> list:
    return [match.group(0) for match in CATALOG_TAG.finditer(text)]


def _protected_contents(text: str) -> Counter:
    return Counter(
        normalize(match.group(3))
        for match in re.finditer(r"<(code|kbd|samp|var)(\d*)>(.*?)</\1\2>", text)
    )


def validate(source: str, translation: str, terms: list) -> list:
    """原文と訳文だけを見て分かる誤りを返す。訳の良し悪しは見ない。"""
    if not translation.strip():
        return ["訳文が空です"]
    errors = []
    if translation != normalize(translation):
        errors.append("訳文の前後か途中に、余分な空白や改行があります")
    rest = ENTITY.sub("", CATALOG_TAG.sub("", translation))
    if "<" in rest:
        errors.append("訳文に、原文にない形のタグか「<」があります（文字としての < は &lt; と書く）")
    if "&" in rest:
        errors.append("訳文に「&」がそのまま入っています（&amp; と書く）")
    missing = Counter(_tags(source)) - Counter(_tags(translation))
    extra = Counter(_tags(translation)) - Counter(_tags(source))
    if missing:
        errors.append("訳文にタグが足りません: " + " ".join(sorted(missing.elements())))
    if extra:
        errors.append("訳文にタグが余分にあります: " + " ".join(sorted(extra.elements())))
    if not missing and not extra:
        opened = []
        for match in CATALOG_TAG.finditer(translation):
            closing, name, number, self_closing = match.groups()
            if self_closing or name in VOID:
                continue
            if not closing:
                opened.append(name + number)
            elif not opened or opened.pop() != name + number:
                errors.append(f"訳文のタグの入れ子が正しくありません: {match.group(0)}")
                break
    if _protected_contents(source) != _protected_contents(translation):
        errors.append("<code>・<kbd> などの中身が、原文と違います（訳さず、そのまま残す）")
    for term in terms:
        if term["canonical"] in source and term["canonical"] not in translation:
            errors.append(f"{term['name']}の正式表記がありません: {term['canonical']}")
        for forbidden in term.get("forbidden", []):
            if forbidden in translation:
                errors.append(f"{term['name']}は{term['canonical']}を使用してください（禁止表記: {forbidden}）")
    if source == translation and KANA.search(plain_text(source)):
        errors.append("訳文が原文と同じです（訳されていません）")
    return errors


# ---------------------------------------------------------------------------
# 対訳カタログから、各言語のHTMLを作る
# ---------------------------------------------------------------------------

def output_name(page: str, language: str, source_root: str) -> str:
    """docs/hello-android/index.html → docs/en/hello-android/index.html

    言語のフォルダを source_root の直下に置くと、ページどうしの相対リンクと
    textbook.js の ?from= の戻り先が、日本語版のまま使える。
    """
    return posixpath.join(source_root, language, posixpath.relpath(page, source_root))


def _rewrite_link(value: str, page: str, language: str, source_root: str, pages: set) -> str:
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path:
        return value  # 外部のURLと、ページ内のリンク
    target = posixpath.normpath(posixpath.join(posixpath.dirname(page), url.path))
    if unquote(target) in pages:
        return value  # 同じ言語のページ。相対位置が変わらないので、そのまま使える
    # 画像・CSS・JS・ZIPは複製せず、日本語版のものを指す。
    moved = posixpath.relpath(target, posixpath.dirname(output_name(page, language, source_root)))
    return urlunsplit(("", "", moved, url.query, url.fragment))


class _Localizer:
    def __init__(self, page: Page, translations: dict, language: str, source_root: str, pages: set):
        self.page = page
        self.translations = translations
        self.language = language
        self.source_root = source_root
        self.pages = pages

    def start_tag(self, element: Element) -> str:
        """開始タグを、訳した属性・書き換えたリンク・言語の指定つきで作り直す。"""
        text = self.page.text
        raw = text[element.start:element.inner_start]
        values = {}
        for name in _translated_attributes(element):
            translation = self.translations.get(normalize(_raw_attribute(text, element, name) or ""))
            if translation is not None:
                values[name] = translation.replace('"', "&quot;")
        for name in LINK_ATTRIBUTES:
            value = _raw_attribute(text, element, name)
            if value is not None:
                moved = _rewrite_link(html.unescape(value), self.page.name, self.language, self.source_root, self.pages)
                if moved != html.unescape(value):
                    values[name] = html.escape(moved, quote=True)
        if element.tag == "html" and element.attribute("lang") is not None:
            values["lang"] = self.language
        for name, value in values.items():
            raw = _attribute_pattern(name).sub(lambda match: f'{match.group(1)}"{value}"', raw, count=1)
        return raw

    def _restore(self, segment: Segment, translation: str) -> str:
        """カタログの形の訳文を、HTMLに戻す。番号つきの目印は、元のタグに戻す。"""
        def replace(match):
            closing, _name, number, _self_closing = match.groups()
            if not number:
                return match.group(0)
            element = segment.placeholders[int(number) - 1]
            if closing:
                return self.page.text[element.inner_end:element.end]
            return self.start_tag(element)
        return CATALOG_TAG.sub(replace, translation)

    def run(self) -> str:
        text = self.page.text
        replacements = []
        for segment in self.page.segments:
            if segment.element is not None:
                continue
            # 未翻訳の文も作り直す。中のリンク（画像を大きく開く、など）を書き換えるため。
            translation = self.translations.get(segment.source)
            rendered = self._restore(segment, translation if translation is not None else self._source(segment))
            replacements.append((segment.start, segment.end, rendered))
        self._start_tags(self.page.root, replacements)
        parts, position = [], 0
        for start, end, rendered in sorted(replacements):
            parts.extend((text[position:start], rendered))
            position = end
        parts.append(text[position:])
        return "".join(parts)

    def _source(self, segment: Segment) -> str:
        """未翻訳の文。元の空白を保ちたいので、カタログの形ではなく元の文字列から、目印つきの形を作る。"""
        text = self.page.text
        marks = []
        for number, element in enumerate(segment.placeholders, 1):
            name = f"{element.tag}{number}"
            if element.tag in VOID:
                marks.append((element.start, element.end, f"<{name}/>"))
            else:
                marks.append((element.start, element.inner_start, f"<{name}>"))
                marks.append((element.inner_end, element.end, f"</{name}>"))
        parts, position = [], segment.start
        for start, end, mark in sorted(marks):
            parts.extend((text[position:start], mark))
            position = end
        parts.append(text[position:segment.end])
        return "".join(parts)

    def _start_tags(self, element: Element, replacements: list):
        for child in element.children:
            if not isinstance(child, Element):
                continue
            if id(child) not in self.page.in_segment:
                rendered = self.start_tag(child)
                if rendered != self.page.text[child.start:child.inner_start]:
                    replacements.append((child.start, child.inner_start, rendered))
            if child.tag not in SKIPPED:
                self._start_tags(child, replacements)


def localize(page: Page, translations: dict, language: str, source_root: str, pages: set) -> str:
    return _Localizer(page, translations, language, source_root, pages).run()


# ---------------------------------------------------------------------------
# 設定と対訳カタログ
# ---------------------------------------------------------------------------

@dataclass
class Settings:
    root: Path
    source_root: str
    catalog_root: str
    languages: list  # [{"code": "en", "name": "English", "distribute": false}, …]
    terms: list  # config/teaching-materials.json の terms。正式表記を訳文にも求める

    def codes(self) -> list:
        return [language["code"] for language in self.languages]

    def language(self, code: str) -> dict:
        found = next((language for language in self.languages if language["code"] == code), None)
        if found is None:
            raise LocalizeError(f"{CONFIG.as_posix()}にない言語です: {code}（使えるのは {'、'.join(self.codes())}）")
        return found

    def page_names(self) -> list:
        """翻訳の対象になる日本語のページ。確認用に作った各言語のページは数えない。"""
        base = self.root / self.source_root
        names = []
        for path in sorted(base.rglob("*.html")):
            relative = path.relative_to(base)
            if relative.parts[0] not in self.codes():
                names.append(posixpath.join(self.source_root, relative.as_posix()))
        return names

    def catalog_path(self, language: str, page: str) -> Path:
        relative = Path(posixpath.relpath(page, self.source_root)).with_suffix(".json")
        return self.root / self.catalog_root / language / relative


def load_settings(root: Path) -> Settings:
    try:
        config = json.loads((root / CONFIG).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LocalizeError(f"{CONFIG.as_posix()}を読み込めません: {error}") from None
    languages = config["languages"]
    codes = [language["code"] for language in languages]
    for code in codes:
        if not LANGUAGE_CODE.fullmatch(code):
            raise LocalizeError(f"{CONFIG.as_posix()}: 言語コードの形が正しくありません: {code}")
        if codes.count(code) > 1:
            raise LocalizeError(f"{CONFIG.as_posix()}: 言語コードが重複しています: {code}")
    terms = []
    if (root / TERMS_CONFIG).is_file():
        terms = json.loads((root / TERMS_CONFIG).read_text(encoding="utf-8")).get("terms", [])
    return Settings(root, config["source_root"], config["catalog_root"], languages, terms)


def read_catalog(path: Path) -> dict:
    """原文→訳文。ファイルがなければ空。形の検査は check_catalog が行う。"""
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {entry["source"]: entry["translation"] for entry in data["entries"]}
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise LocalizeError(f"{path}: 対訳カタログを読み込めません: {error}") from None


def write_catalog(path: Path, page: str, language: str, entries: dict, sources: list) -> bool:
    """文書に出てくる順で書く。ページにもうない原文の訳は、うしろに残す（外すのは sync）。"""
    ordered = {source: entries[source] for source in sources if source in entries}
    ordered.update({source: translation for source, translation in entries.items() if source not in ordered})
    if not ordered:
        if path.is_file():
            path.unlink()  # 訳が1つもないカタログは置かない
            return True
        return False
    data = {
        "source": page,
        "language": language,
        "entries": [{"source": source, "translation": translation} for source, translation in ordered.items()],
    }
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def check_catalog(settings: Settings, path: Path, errors: list) -> None:
    shown = path.relative_to(settings.root).as_posix()
    relative = path.relative_to(settings.root / settings.catalog_root)
    language = relative.parts[0]
    if language not in settings.codes():
        errors.append(f"{shown}:1: {CONFIG.as_posix()}にない言語のフォルダです: {language}")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{shown}:1: JSONとして読み込めません: {error}")
        return
    page = posixpath.join(settings.source_root, Path(*relative.parts[1:]).with_suffix(".html").as_posix())
    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        errors.append(f"{shown}:1: entries がありません（訳が1つもないカタログは置かない）")
        return
    if data.get("language") != language:
        errors.append(f"{shown}:1: language がフォルダの名前と違います: {data.get('language')!r}")
    if data.get("source") != page:
        errors.append(f"{shown}:1: source がファイルの場所と違います: {data.get('source')!r} != {page!r}")
    seen = set()
    for number, entry in enumerate(entries, 1):
        if (not isinstance(entry, dict) or set(entry) != {"source", "translation"}
                or not all(isinstance(value, str) for value in entry.values())):
            errors.append(f"{shown}: {number}番目の項目が、source と translation の組になっていません")
            continue
        source, translation = entry["source"], entry["translation"]
        label = f"{shown}: {number}番目「{source[:30]}」"
        if source in seen:
            errors.append(f"{label}: 同じ原文が2回あります")
        seen.add(source)
        if source != normalize(source):
            errors.append(f"{label}: 原文に余分な空白や改行があります（手で書き換えず、sync で作り直す）")
        errors.extend(f"{label}: {problem}" for problem in validate(source, translation, settings.terms))


# ---------------------------------------------------------------------------
# コマンド
# ---------------------------------------------------------------------------

def _selected_pages(settings: Settings, only: list) -> list:
    names = settings.page_names()
    unknown = [name for name in only if name not in names]
    if unknown:
        raise LocalizeError("翻訳の対象にないページです: " + "、".join(unknown))
    return [name for name in names if not only or name in only]


def _work_folder(work_dir: Path, language: str, page: str, source_root: str) -> Path:
    return work_dir / language / Path(posixpath.relpath(page, source_root)).with_suffix("")


def sync(settings: Settings, languages: list, only: list, work_dir: Path, chunk_size: int, chunk_chars: int) -> None:
    """カタログを今の日本語に合わせ、未翻訳の文を作業ファイルに書き出す。"""
    names = _selected_pages(settings, only)
    pages = {name: read_page(settings.root, name) for name in names}
    for code in languages:
        language = settings.language(code)
        catalogs = {name: read_catalog(settings.catalog_path(code, name)) for name in settings.page_names()}
        # 同じ原文には同じ訳を使い回す。ほかのページで訳してあれば、それを入れる。
        memory: dict = {}
        for entries in catalogs.values():
            for source, translation in entries.items():
                memory.setdefault(source, translation)
        total_missing = total_filled = total_removed = 0
        listed: set = set()  # 作業ファイルに出した原文。同じ文は1回訳せば、merge が全ページに入れる
        for name, page in pages.items():
            old = catalogs[name]
            kept, missing = {}, []
            filled = 0
            for source in page.sources():
                if source in old:
                    kept[source] = old[source]
                elif source in memory and not validate(source, memory[source], settings.terms):
                    kept[source] = memory[source]
                    filled += 1
                elif source not in listed:
                    listed.add(source)
                    missing.append(source)
            removed = {source: translation for source, translation in old.items() if source not in kept}
            write_catalog(settings.catalog_path(code, name), name, code, kept, page.sources())
            folder = _work_folder(work_dir, code, name, settings.source_root)
            if folder.is_dir():
                for stale in folder.glob("todo-*.json"):
                    stale.unlink()
            where = {}
            for segment in page.segments:
                where.setdefault(segment.source, segment.where)
            chunks, current, size = [], [], 0
            for source in missing:
                item = {"id": segment_id(source), "where": where[source], "source": source}
                # 少しだけ変わった文には、前の原文と訳を添える。訳し直しではなく、前の訳を直せばよい。
                close = difflib.get_close_matches(source, list(removed), n=1, cutoff=0.6)
                if close:
                    item["previous_source"] = close[0]
                    item["previous_translation"] = removed[close[0]]
                current.append(item)
                size += len(source)
                if len(current) >= chunk_size or size >= chunk_chars:
                    chunks.append(current)
                    current, size = [], 0
            if current:
                chunks.append(current)
            for number, chunk in enumerate(chunks, 1):
                folder.mkdir(parents=True, exist_ok=True)
                done = folder / f"done-{number:03d}.json"
                todo = {
                    "language": code,
                    "language_name": language["name"],
                    "page": name,
                    "done_file": _shown(settings.root, done),
                    "segments": chunk,
                }
                (folder / f"todo-{number:03d}.json").write_text(
                    json.dumps(todo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if missing or filled or removed:
                print(f"{code} {name}: 未翻訳 {len(missing)}（作業ファイル {len(chunks)}）、"
                      f"ほかのページの訳で補った文 {filled}、外した訳 {len(removed)}")
            total_missing += len(missing)
            total_filled += filled
            total_removed += len(removed)
        print(f"{code}: 未翻訳 {total_missing}、補った文 {total_filled}、外した訳 {total_removed}"
              f"（作業ファイルは {_shown(settings.root, work_dir / code)}）")


def _shown(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def merge(settings: Settings, code: str, files: list, work_dir: Path, overwrite: bool, dry_run: bool = False) -> int:
    """訳した結果（id→訳文）を検査して、その原文を持つすべてのページのカタログへ入れる。

    dry_run のときは検査だけ行う。ページごとに分かれて並行して訳すときは、各自が dry_run で確かめ、
    カタログへ入れるのは1か所でまとめて行う（同じカタログを同時に書き換えないため）。
    """
    settings.language(code)
    if not files:
        files = sorted((work_dir / code).rglob("done-*.json"))
    if not files:
        raise LocalizeError(f"訳した結果のファイルがありません: {_shown(settings.root, work_dir / code)} の done-*.json")
    pages = {name: read_page(settings.root, name) for name in settings.page_names()}
    index: dict = {}
    for page in pages.values():
        for source in page.sources():
            if index.setdefault(segment_id(source), source) != source:
                raise LocalizeError(f"別の原文が同じidになりました: {segment_id(source)}")
    catalogs = {name: read_catalog(settings.catalog_path(code, name)) for name in pages}
    problems, added, skipped = [], 0, 0
    changed: set = set()
    for path in files:
        try:
            done = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            problems.append(f"{path}: JSONとして読み込めません: {error}")
            continue
        if not isinstance(done, dict) or not all(isinstance(value, str) for value in done.values()):
            problems.append(f"{path}: 「id: 訳文」の組だけを書いたJSONにしてください")
            continue
        for identifier, translation in done.items():
            source = index.get(identifier)
            if source is None:
                problems.append(f"{path}: {identifier}: このidの原文がありません（日本語が変わったなら、sync からやり直す）")
                continue
            translation = normalize(translation)
            found = validate(source, translation, settings.terms)
            if found:
                problems.extend(f"{path}: {identifier}「{source[:30]}」: {problem}" for problem in found)
                continue
            for name, page in pages.items():
                if source not in page.sources():
                    continue
                current = catalogs[name].get(source)
                if current == translation:
                    continue
                if current is not None and not overwrite:
                    skipped += 1
                    continue
                catalogs[name][source] = translation
                changed.add(name)
                added += 1
    if not dry_run:
        for name in sorted(changed):
            write_catalog(settings.catalog_path(code, name), name, code, catalogs[name], pages[name].sources())
    print(f"{code}: {'検査に通った訳（カタログには入れていません）' if dry_run else 'カタログに入れた訳'} {added}"
          + (f"、すでに別の訳があるので入れなかった訳 {skipped}（入れ替えるなら --overwrite）" if skipped else ""))
    if problems:
        print("検査に落ちた訳（カタログには入れていません）:", file=sys.stderr)
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


def check(settings: Settings) -> list:
    """教材を取り出せることと、対訳カタログの中身を確かめる。未翻訳の数は見ない。"""
    errors = []
    for name in settings.page_names():
        try:
            read_page(settings.root, name)
        except LocalizeError as error:
            errors.append(str(error))
    base = settings.root / settings.catalog_root
    if base.is_dir():
        for path in sorted(base.rglob("*.json")):
            check_catalog(settings, path, errors)
    return errors


def progress(settings: Settings, languages: list) -> list:
    """言語ごとの、ページ別の進み具合。"""
    pages = {name: read_page(settings.root, name).sources() for name in settings.page_names()}
    report = []
    for code in languages:
        language = settings.language(code)
        rows = []
        for name, sources in pages.items():
            entries = read_catalog(settings.catalog_path(code, name))
            translated = sum(1 for source in sources if source in entries)
            rows.append({"page": name, "total": len(sources), "translated": translated,
                         "unused": sum(1 for source in entries if source not in sources)})
        base = settings.root / settings.catalog_root / code
        known = {settings.catalog_path(code, name) for name in pages}
        orphans = [_shown(settings.root, path) for path in sorted(base.rglob("*.json")) if path not in known] if base.is_dir() else []
        report.append({"language": language, "rows": rows, "orphans": orphans})
    return report


def status(settings: Settings, languages: list, require_complete: bool) -> int:
    report = progress(settings, languages)
    lines, summary = [], ["## 翻訳の進み具合", "", "| 言語 | 配布 | 訳した文 | 未翻訳 | 使っていない訳 |", "| --- | --- | --- | --- | --- |"]
    incomplete = []
    for item in report:
        language, rows = item["language"], item["rows"]
        total = sum(row["total"] for row in rows)
        translated = sum(row["translated"] for row in rows)
        unused = sum(row["unused"] for row in rows)
        distribute = bool(language.get("distribute"))
        lines.append(f"{language['code']}（{language['name']}、配布対象：{'はい' if distribute else 'いいえ'}）")
        for row in rows:
            note = f"  使っていない訳 {row['unused']}" if row["unused"] else ""
            lines.append(f"  {row['translated']:5d} / {row['total']:5d}  {row['page']}{note}")
        for orphan in item["orphans"]:
            lines.append(f"  ページがないカタログ: {orphan}")
        lines.append(f"  合計 {translated} / {total}、未翻訳 {total - translated}")
        summary.append(f"| {language['code']}（{language['name']}） | {'対象' if distribute else '—'} | "
                       f"{translated} / {total} | {total - translated} | {unused} |")
        if distribute and translated < total:
            incomplete.append(f"{language['code']}: 未翻訳 {total - translated}")
    print("\n".join(lines))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as output:
            output.write("\n".join(summary) + "\n\n未翻訳の文は、配布前の翻訳PRでまとめて訳します。日常のPRでは訳しません。\n")
    if require_complete and incomplete:
        print("配布対象の言語に、未翻訳の文が残っています: " + "、".join(incomplete), file=sys.stderr)
        return 1
    return 0


def localized_pages(settings: Settings, code: str) -> dict:
    """その言語の全ページ。出力先のパス→HTML。訳のないページも、リンクが切れないように作る。"""
    settings.language(code)
    names = settings.page_names()
    result = {}
    for name in names:
        page = read_page(settings.root, name)
        translations = read_catalog(settings.catalog_path(code, name))
        result[output_name(name, code, settings.source_root)] = localize(
            page, translations, code, settings.source_root, set(names))
    return result


def build(settings: Settings, languages: list, output: Path) -> None:
    """確認用。日本語の docs を写し、その中に docs/<言語>/ を作る。画像などは日本語版のものを指す。"""
    if output.resolve() == settings.root.resolve():
        raise LocalizeError("リポジトリの直下には作れません。--output で別のフォルダを指定してください")
    codes = set(settings.codes())
    shutil.copytree(
        settings.root / settings.source_root, output / settings.source_root, dirs_exist_ok=True,
        ignore=lambda folder, names: [name for name in names if Path(folder) == settings.root / settings.source_root and name in codes],
    )
    for code in languages:
        pages = localized_pages(settings, code)
        for name, text in pages.items():
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        print(f"{code}: {len(pages)}ページを作りました（{_shown(settings.root, output / settings.source_root / code)}）")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)

    sync_parser = commands.add_parser("sync", help="未翻訳の文を作業ファイルに書き出す")
    sync_parser.add_argument("--lang", action="append", required=True, help="言語コード。複数指定できる")
    sync_parser.add_argument("--page", action="append", default=[], help="ページを絞る（docs/hello-android/index.html）")
    sync_parser.add_argument("--chunk-size", type=int, default=40, help="1つの作業ファイルに入れる文の数")
    sync_parser.add_argument("--chunk-chars", type=int, default=3000, help="1つの作業ファイルに入れる原文の文字数")
    sync_parser.add_argument("--work-dir", type=Path)

    merge_parser = commands.add_parser("merge", help="訳した結果をカタログへ入れる")
    merge_parser.add_argument("--lang", required=True)
    merge_parser.add_argument("files", nargs="*", type=Path, help="省略すると、作業フォルダの done-*.json をすべて入れる")
    merge_parser.add_argument("--overwrite", action="store_true", help="すでにある訳を入れ替える")
    merge_parser.add_argument("--dry-run", action="store_true", help="検査だけ行い、カタログには入れない")
    merge_parser.add_argument("--work-dir", type=Path)

    commands.add_parser("check", help="対訳カタログを検査する")

    status_parser = commands.add_parser("status", help="訳した数を出す")
    status_parser.add_argument("--lang", action="append", help="省略すると全言語")
    status_parser.add_argument("--require-complete", action="store_true", help="配布対象の言語に未翻訳があれば失敗する")

    build_parser = commands.add_parser("build", help="各言語のHTMLを作る（確認用）")
    build_parser.add_argument("--lang", action="append", required=True)
    build_parser.add_argument("--output", type=Path)

    args = parser.parse_args()
    root = args.root.resolve()
    try:
        settings = load_settings(root)
        if args.command == "sync":
            sync(settings, args.lang, args.page, args.work_dir or root / WORK_DIR, args.chunk_size, args.chunk_chars)
        elif args.command == "merge":
            return merge(settings, args.lang, args.files, args.work_dir or root / WORK_DIR, args.overwrite, args.dry_run)
        elif args.command == "check":
            errors = check(settings)
            if errors:
                print("対訳カタログの検査: NG", file=sys.stderr)
                print("\n".join(errors), file=sys.stderr)
                return 1
            print("対訳カタログの検査: OK")
        elif args.command == "status":
            return status(settings, args.lang or settings.codes(), args.require_complete)
        elif args.command == "build":
            build(settings, args.lang, args.output or root / PREVIEW_DIR)
    except (LocalizeError, OSError, KeyError) as error:
        raise SystemExit(f"多言語展開の処理に失敗しました：{error}") from None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
