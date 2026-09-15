---
name: teaching-materials-review
description: Review teaching materials against Android project sources, canonical terminology, code snippets, and student distribution archives. Use for PRs that change docs, completed projects, packaging, or release workflows in this repository.
---

# Teaching materials review

このリポジトリの教材変更をレビューするときは、文章だけでなく、教材・完成プロジェクト・配布ZIPの整合性を確認する。

## 必須確認

1. `python3 scripts/check-teaching-materials.py` を実行する。
2. 検査が失敗した場合は、PRを承認可能と判断しない。
3. `config/teaching-materials.json` の正式表記を基準にし、禁止表記を個別に修正する。
4. 教材の完成コードとプロジェクトの実ファイルが一致することを確認する。
5. ZIPの内容が現行ソースと一致し、IDE設定・SDK設定・ビルド生成物を含まないことを確認する。
6. PRレビュー指摘には、妥当性・再現性・デグレの可能性・修正コスト・既存仕様への影響を確認したうえで、対応が必要、任意対応、対応不要のいずれかを明記する。

## 判断基準

- 正式表記や配布物の不一致は、学生配布前に直す必要がある指摘として扱う。
- 初学者向けのコード構成を変えるだけの改善は、教材の学習目標と変更範囲を比較して判断する。
- 自動レビューの指摘はそのまま実行せず、必ず現在のソースと検査結果で再確認する。
- マージ可否は、必須検査、関連テスト、レビュー指摘の状態を合わせて判断する。マージ操作自体はユーザーの依頼がない限り実行しない。
