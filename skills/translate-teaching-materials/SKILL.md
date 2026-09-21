---
name: translate-teaching-materials
description: Translate the Japanese student textbooks (docs/**/*.html) into the students' native languages through per-sentence translation catalogs (i18n/<language>/<page>.json). Use when asked to translate teaching materials, prepare translations before a release, fix a translation, or review a translation PR in this repository.
---

# Translate teaching materials

日本語で書いた学生向けの教科書（`docs/**/*.html`）を、学生の母国語に展開する。翻訳済みのHTMLはコミットしない。コミットするのは、文単位の対訳カタログ `i18n/<言語>/<ページ>.json` で、各言語のHTMLはカタログから作る。決まった経緯は issue #215 にある。

## 前提

- **授業は日本語で進む。** 翻訳は、読んで理解するための補助である。先生が口にする言葉、画面に出る言葉と、訳文の言葉を、学生が結び付けられるようにする。
- **日本語版が正。** 日本語の教科書（`docs/`）は、翻訳の都合で書き換えない。原文が曖昧で訳せないときは、推測で訳さず、PR本文に挙げる。
- **訳すのは、未翻訳の文だけ。** 日本語の文を直すと、その文は自動で未翻訳に戻る（古い訳は外れ、学生には日本語で表示される）。変わっていない文の訳は触らない。
- 言語の一覧は `config/i18n.json`、言語ごとの用語集は `i18n/<言語>/glossary.md` にある。

| 学生の母国語 | コード | 書き方 |
| --- | --- | --- |
| 英語 | `en` | |
| 中国語 | `zh-Hans` | 簡体字 |
| 広東語 | `zh-Hant-HK` | 繁体字の書き言葉に、香港の語彙を使う（程式、檔案、螢幕）。話し言葉をそのまま書く粤語白話文にはしない |
| ミャンマー語 | `my` | Unicodeで書く（Zawgyiではない） |
| モンゴル語 | `mn` | キリル文字 |
| フランス語 | `fr` | 学生には vous で語りかける |

## 手順

1. 未翻訳の文を書き出す。

   ```sh
   python3 scripts/localize-student-materials.py sync --lang en
   ```

   `dist/i18n-work/<言語>/<ページ>/todo-NNN.json` ができる（`dist/` はGit管理の対象外）。1ファイルは40文ほど。同じ文が複数のページにあるときは、最初のページの作業ファイルにだけ出る。1回訳せば、全ページに入る。ページを絞るときは `--page docs/hello-android/index.html` を付ける。
2. 訳す前に、そのページの日本語のHTML（`docs/…`）を通して読む。文だけを見ても、見出しなのか、ボタンの名前なのか、表のどの列なのかが分からない。作業ファイルの `where` は、その文がどの要素にあるかを示す（`h2`、`td`、`img alt` など）。
3. 作業ファイル1つにつき、`done_file` に書いてあるパスへ、訳を `id` と訳文の組だけのJSONで書く。原文は書かない。

   ```json
   {
     "0dce59d92673": "① When you launch the finished app: <strong>Hello World!</strong> <a1>Open the full-size image</a1>",
     "4e8d3eaf93d9": "Three goals"
   }
   ```

   `previous_source` と `previous_translation` が付いている文は、日本語が少しだけ直された文である。ゼロから訳し直さず、前の訳を、変わった分だけ直す。
4. 検査する。落ちた訳は、理由が出るので直す。

   ```sh
   python3 scripts/localize-student-materials.py merge --lang en --dry-run dist/i18n-work/en/hello-android/index/done-001.json
   ```

5. カタログへ入れる。`--dry-run` を外す。ファイルを省くと、その言語の `done-*.json` をすべて入れる。すでに訳がある文は入れ替えない（入れ替えるときは `--overwrite`。1文だけ直すなら、カタログの `translation` を直接直してよい）。
6. 確かめる。

   ```sh
   python3 scripts/localize-student-materials.py check
   python3 scripts/localize-student-materials.py status --lang en
   python3 scripts/localize-student-materials.py build --lang en
   ```

   `build` は `dist/i18n-preview/docs/<言語>/…` にページを作る。`file://` で開くとCSSが当たらないことがあるので、ローカルのサーバーで開く。レイアウトの崩れ、リンク、画像、コードのコピー、共通資料の「もとの教科書へ戻る」を確かめる。
7. 新しく訳語を決めた用語を、`i18n/<言語>/glossary.md` に足す。

### 分担して訳すとき

ページごとにsubagentへ分けてよい。そのとき、次を守る。

- subagentは手順2〜4（`--dry-run` まで）を行う。**カタログへ入れる手順5は、親のセッションが1回で行う。** 同じカタログを同時に書き換えないためである。
- 用語集 `glossary.md` も、subagentには書き換えさせない。足したい用語は報告させ、親がまとめて足す。
- subagentには、このskill、用語集、日本語のページ、受け持つ作業ファイルのパスを渡す。

## 翻訳ルール（全言語に共通）

### そのまま残すもの

検査で強制するもの：

- `<code>`・`<kbd>` の中身。1文字も変えない。日本語が入っていても訳さない（`<code>/Users/ユーザ名/Documents</code>`、`<code>テキストを変更</code>`）。
- 指定AVD名 `jec_26cm_android1_Pixel 9a`。

検査はしないが、必ず守るもの：

- ファイル名、フォルダ名、パス、パッケージ名、クラス名、メソッド名、id、プロジェクト名（`A01HelloAndroid`）。
- **Android Studioの画面に出る言葉。** 学生のAndroid Studioは英語表示なので、原文が英語で書いているもの（**New Project**、**Run**、**Logcat**、**Empty Views Activity**）は、どの言語でも英語のまま残す。訳が要るときは、うしろにかっこで添える。
- **macOSの画面に出る言葉。** 原文が日本語で書いているメニュー名やフォルダ名（**移動 → ホーム**、**書類**）は、日本語のまま残し、その言語での名前をかっこで添える。学生のMacの表示言語は、学生ごとに違うためである。

  ```text
  原文：Finderの <strong>移動 → ホーム</strong> を開き、
  英語：In Finder, open <strong>移動 → ホーム</strong> (Go → Home),
  ```

- **学生がアプリに打ち込む日本語と、スクリーンショットに写っている日本語。** 完成プロジェクトと画像は日本語のままなので、訳文でも日本語のまま書き、意味をかっこで添える。

  ```text
  原文：「テキストを変更」ボタンを押します。
  英語：Press the 「テキストを変更」 (Change text) button.
  ```

### タグと目印

- `<a1>…</a1>`、`<span2>…</span2>`、`<img3/>` は、属性つきのタグを番号で置き換えた目印である。原文にあるものを、同じ数だけ使う。語順に合わせて、並べる順番は変えてよい。
- `<strong>`、`<em>`、`<br>` などのタグも、原文と同じ数だけ使う。足さない。減らさない。
- 文字としての `<`、`>`、`&` は、`&lt;`、`&gt;`、`&amp;` と書く。原文にある `&amp;` などは、そのまま残す。
- 訳文の前後に空白や改行を入れない。

### 文体

- 読むのは、プログラミングの初学者である。短い文と、やさしい言葉で書く。1つの原文を2つの文に分けてよい。内容は足さない。引かない。
- 操作の手順は、その言語の手順書のふつうの言い方で書く（英語なら命令形：Click **Run**.）。
- **ふりがなは落とす。** 「起動（きどう）できる」の「（きどう）」は、日本語の読みを助けるためのもので、訳文には要らない。
- **用語の表の用語は、日本語を残して訳を添える。** 「まず使う言葉」のように、言葉とその意味を並べた表の「言葉」の列は、`エミュレータ — emulator`、`実行（じっこう） / Run（ラン） — run` のように、原文（読みも含む）のうしろに「 — 」と訳を書く。先生が授業で口にする言葉を、学生が聞き取れるようにするためである。
- かぎかっこ「」は、その言語の引用符にする。ただし、上の「画面やアプリに出る日本語」を囲むときは、「」のまま残してよい。
- 全角の記号（：（）、。）は、その言語の記号にする。`→`、`①②③`、`STEP 01` はそのまま残す。
- 単元の名前（`A01：HelloAndroid`）は訳さない。「共通：エミュレータ」のような共通資料の名前は訳す。

### 一貫性

- 用語集 `i18n/<言語>/glossary.md` の訳語を使う。
- 同じ原文は、同じ訳になる（`merge` が、その原文を持つ全ページへ入れる）。ページによって訳し分けたいときは、まず原文のほうが曖昧でないかを疑う。

## 翻訳PRのレビュー

- `check` が通っていること。未翻訳の数は `status` で見る。
- 訳したのとは別のsubagent（できれば別のモデル）が、カタログの `source` と `translation` を並べて読み、意味の違い・訳し落とし・足しすぎ・用語集との不一致を挙げる。教員側で読めない言語（`my`、`mn`、`zh-Hant-HK`）では、訳文を日本語へ訳し戻して原文と比べる。
- 見つけた誤訳は、カタログの `translation` を直接直す。`source` は手で書き換えない（原文と合わなくなり、その訳が使われなくなる）。

## やってはいけないこと

- `docs/` の日本語を、翻訳の都合で書き換える。
- カタログの `source` を手で書き換える。並べ替えも `sync` と `merge` に任せる。
- 各言語のHTML（`dist/i18n-preview/` の中身、`docs/<言語>/`）をコミットする。
- 変わっていない文の訳を、好みで書き直す。差分が増え、レビューできなくなる。
