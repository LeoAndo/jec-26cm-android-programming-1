# Figmaと共有CSSの対応付け

この表は2026-11-15の初回整備時点の調査用情報。反映時には最新のFigmaとCSSを再取得する。値の正本はFigmaであり、このファイルへ現在のhex値を複製し続ける運用にはしない。

## 参照先

- [A01 HelloAndroid 教科書｜PC版](https://www.figma.com/design/WMnEPpc4yGE1M1kBes8oHs?node-id=14-2)
- fileKey: `WMnEPpc4yGE1M1kBes8oHs`
- ページ: `A01 教科書・PC`、ID `12:12`
- 基準フレーム: `14:2`、PC幅1440px
- 用途別の色: `教科書｜色`。基本色の参照先: `教科書｜パレット`
- 書体・太さ: `教科書｜書体`。テキストスタイルの接頭辞: `教科書/`

名前やIDが変更・削除されていたら現状を調査する。本文内の取り込み時の改行や分割済みレイヤーは、文章を変更する根拠にしない。

## CSSのスコープ

`docs/assets/textbook.css` には、共通資料・教員用ガイドにも使う基本規則と、その後に単元教科書用の `.textbook` 規則がある。初回時点では `:root` と `.textbook` に同じ色変数名が別の値で定義されている。

学生用教科書の色を変える場合は `.textbook` 側を確認する。書体は `--font-body` と `--font-code` が `:root` にあり、言語別指定が一部を上書きする。基本規則だけを読んでA01の実効値を判断しない。

## 色の対応

「既存」は初回時点でCSS変数があるもの。「追加候補」はFigmaのコード構文に記載されているが、CSSにはまだ定義されていないもの。反映対象になった用途について、最新CSSに変数を定義して対象規則から参照する。候補名の `a01-` は全単元への適用を制限する意味ではない。名称変更が必要ならFigmaとの対応を記録し、今回の反映と無関係な整理は混ぜない。

| Figmaの用途 | CSS構文名 | 初回時点 | 対象・注意 |
| --- | --- | --- | --- |
| 本文/基本 | `--ink` | 既存 | 本文・見出し・目次アイコン。CSS: var(--ink)。 |
| 本文/補助 | `--muted` | 既存 | 補助説明・キャプション。CSS: var(--muted)。 |
| 背景/ページ | `--paper` | 既存 | ページとナビの背景。CSS: var(--paper)。 |
| 境界線/基本 | `--line` | 既存 | セクション・表・画像・各枠の区切り。CSS: var(--line)。 |
| 強調/基本 | `--blue` | 既存 | リンク・見出しの強調・STEP番号。CSS: var(--blue)。 |
| 確認/背景 | `--mint` | 既存 | 確認ボックスの背景。CSS: var(--mint)。 |
| 目標/背景 | `--surface-goal` | 追加候補 | .textbook .goal |
| 注意/背景 | `--surface-note` | 追加候補 | .textbook .note |
| コード/背景 | `--surface-code` | 追加候補 | .textbook pre |
| コード/見出し背景 | `--surface-code-heading` | 追加候補 | .textbook .code-head |
| コード/境界線 | `--border-code` | 追加候補 | .textbook pre / .code-head |
| 構文/キーワード | `--syntax-keyword` | 追加候補 | .textbook .syntax-keyword |
| 構文/文字列 | `--syntax-string` | 追加候補 | .textbook .syntax-string |
| 構文/コメント | `--syntax-comment` | 追加候補 | .textbook .syntax-comment |
| ナビ/ボタン境界線 | `--a01-nav-border` | 追加候補 | .textbook .lesson-menu > summary |
| ナビ/選択背景 | `--a01-nav-selected-bg` | 追加候補 | .textbook .lesson-menu-content a[aria-current=step] |
| ナビ/選択文字 | `--a01-nav-selected-text` | 追加候補 | .sidebar a[aria-current=step] |
| 注意/境界線 | `--a01-note-border` | 追加候補 | .textbook .note |
| 注意/見出し | `--a01-note-title` | 追加候補 | .textbook .note .box-title |
| 確認/チェック境界線 | `--a01-checkbox-border` | 追加候補 | チェックボックスのブラウザ標準境界線 |
| コード/インライン背景 | `--a01-code-inline-bg` | 追加候補 | .textbook code |
| ファイル/アイコン境界線 | `--a01-file-icon-border` | 追加候補 | .textbook .file-icon |
| 参照コード/見出し背景 | `--a01-reference-heading-bg` | 追加候補 | .code-head[data-code-kind=reference] |
| 参照コード/背景 | `--a01-reference-code-bg` | 追加候補 | .code-head[data-code-kind=reference] + pre |
| 練習/境界線 | `--a01-task-border` | 追加候補 | .textbook .task |
| 構文/型 | `--blue` | 要分離 | 構文の型名。CSS: .syntax-type は現在 #2458b8 直書き。var(--blue) と同値。用途別に変更する場合はCSSも別変数へ分離。 |
| 確認/強調 | `--a01-check-accent` | 追加候補 | 確認欄の見出し・チェック。現在のFigmaの色を維持。CSS .checkの上下線は #bad4c6 のため後続の画面照合で個別判断。 |
| 確認/チェック背景 | `--a01-checkbox-bg` | 追加候補 | チェックボックスの白い背景 |
| 確認/チェック記号 | `--a01-checkbox-mark` | 追加候補 | チェック済みの記号 |
| 操作/背景 | `--a01-action-bg` | 追加候補 | .textbook .next a / .button-link |
| ナビ/メニュー背景 | `--a01-nav-menu-bg` | 追加候補 | .textbook .lesson-menu-content |
| 影/メニュー | `--a01-menu-shadow` | 追加候補 | メニューの影。色・透明度のみ。オフセット0/10、ぼかし30は維持。 |

## 誤反映しやすい箇所

- **強調色と構文の型。** 初回の両変数は同じ色で、Figmaのコード構文も `--blue` になっている。しかし `.syntax-type` は色の直書きであり、別用途。片方だけを変更した場合は、例えば `--syntax-type` を分けて対象だけへ適用する。コード構文名だけで統合しない。
- **確認色と構文の文字列。** 初回は同じ緑だが別用途。確認欄だけを変えるときにコード内の文字列の色を変えない。
- **確認欄の境界線。** 初回Figmaの一部の緑の線と、CSSの上下線 `#bad4c6` に既存差がある。今回の対象に含まれる線か区別し、色の全面反映なら該当ノードと四辺の規則を調べて解決する。文字列だけの変更など対象外なら勝手に直さない。
- **チェックボックス。** 取り込みではブラウザの見た目が図形になるが、HTMLではネイティブinput。現状の `accent-color` と状態を調べる。図形の白い線や枠へ対応するCSSがあるとは限らない。独自のチェックボックスへ作り替える必要がある場合は、期待する表示・操作と作業範囲を確定してから扱う。
- **影。** 変数は影の色と不透明度。オフセット・ぼかしまで勝手に変更しない。
- **パレットの変更。** 複数の用途が同じ基本色を参照している。基本色が変わった場合は、参照する用途をすべて列挙してから影響範囲を決める。

## 書体と文字設定

| Figma | 現在のCSS対応 | 注意 |
| --- | --- | --- |
| 書体/本文 | `--font-body` | 初期値Noto Sans JP。日本語本文・見出し |
| 書体/コード | `--font-code` | 初期値Roboto Mono。日本語はNoto Sans JPへフォールバック |
| 太さ/400・600・700・750・800 | 各用途の `font-weight` または `font` shorthand | 初回時点ではCSSに太さ変数はない。数値を解決して各用途へ対応付ける |
| 用途別テキストスタイル | 既存の本文・見出し・表・コードなどの規則 | スタイル数や一覧を固定せず、変更したスタイルの利用箇所を調べる |

`コード` 書体は `pre/code/kbd` だけでなく、STEP番号、ファイル名、アイコン、パスにも使われる。フォント変更では `font-family` と `font` shorthandを両方検索する。

初回のFigmaでは、fontFamily変数を結び付けた際に600が500、750や800が700へ解決される事象があった。太さ変数もテキストスタイルへ結び付けて解消している。今後も名前がMedium/Boldだからという理由で値を決めず、実際のノードの解決値を確認する。

中国語（簡体字・香港繁体字）・ミャンマー語・モンゴル語の既存の言語別指定と、翻訳内の日本語指定を保つ。全言語を同じフォント名にすることを「統一」の既定にしない。
