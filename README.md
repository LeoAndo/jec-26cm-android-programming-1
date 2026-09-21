# Androidプログラミング1 — 授業用教材

## HelloAndroidの教科書

1コマ90分、全2コマを目安にした、JavaとXMLの入門教材です。予習なしで授業内の操作・確認・ミニ練習まで進められる構成です。

- [HelloAndroid：はじめてのアプリ作り](docs/hello-android/index.html)
- [完成プロジェクト（初回から参照可能）](docs/hello-android/downloads/A01HelloAndroid.zip)
- [CalcGame：計算ゲームを作ろう](docs/calc-game/index.html)
- [完成プロジェクト（A02CalcGame）](docs/calc-game/downloads/A02CalcGame.zip)
- [RockPaperScissorsGame：じゃんけんゲームを作ろう](docs/rock-paper-scissors-game/index.html)
- [完成プロジェクト（A03RockPaperScissorsGame）](docs/rock-paper-scissors-game/downloads/A03RockPaperScissorsGame.zip)
- [WebViewApp：アプリの中でWebページを表示しよう](docs/webview-app/index.html)
- [完成プロジェクト（A04WebViewApp）](docs/webview-app/downloads/A04WebViewApp.zip)
- [BombGame：爆弾ゲームを作ろう](docs/bomb-game/index.html)
- [完成プロジェクト（A05BombGame）](docs/bomb-game/downloads/A05BombGame.zip)
- [ScreenTransitionSample：画面を切り替えて値を渡そう](docs/screen-transition-sample/index.html)
- [完成プロジェクト（A06ScreenTransitionSample）](docs/screen-transition-sample/downloads/A06ScreenTransitionSample.zip)
- [BillSplitter：割り勘アプリを作ろう](docs/bill-splitter/index.html)
- [完成プロジェクト（A07BillSplitter）](docs/bill-splitter/downloads/A07BillSplitter.zip)
- [SharedPreferencesSample：アプリを閉じても消えないデータ](docs/shared-preferences-sample/index.html)
- [完成プロジェクト（A08SharedPreferencesSample）](docs/shared-preferences-sample/downloads/A08SharedPreferencesSample.zip)
- [MemoApp：消えないメモ帳を作ろう](docs/memo-app/index.html)
- [完成プロジェクト（A09MemoApp）](docs/memo-app/downloads/A09MemoApp.zip)
- [RoomSample：データベースに保存しよう](docs/room-sample/index.html)
- [完成プロジェクト（A10RoomSample）](docs/room-sample/downloads/A10RoomSample.zip)
- [VocabularyBook：2つの画面でデータを共有しよう](docs/vocabulary-book/index.html)
- [完成プロジェクト（A11VocabularyBook）](docs/vocabulary-book/downloads/A11VocabularyBook.zip)
- [共通資料：授業を始めるまでの準備（教材の受け取りから最初の実行まで）](docs/common/setup.html)
- [共通資料：エミュレータの準備とアプリの実行](docs/common/emulator.html)
- [共通資料：Auto Importの設定](docs/common/auto-import.html)
- [共通資料：Logcatの使い方](docs/common/logcat.html)
- [共通資料：提出課題とAPKの作り方（自分で作ったアプリを3つ選んで提出する）](docs/common/apk.html)
- [共通資料：開発Tips（画面の余白・キーボード・画面回転）](docs/common/dev-tips.html)
- [共通資料：ちがうAndroid Studioのバージョンで進めるとき（サポート範囲と読み替え）](docs/common/other-versions.html)
- [教員用：HelloAndroidの授業の進め方・確認項目](teacher/hello-android/index.html)
- [教員用：CalcGameの授業の進め方・確認項目](teacher/calc-game/index.html)
- [教員用：RockPaperScissorsGameの授業の進め方・確認項目](teacher/rock-paper-scissors-game/index.html)
- [教員用：WebViewAppの授業の進め方・確認項目](teacher/webview-app/index.html)
- [教員用：BombGameの授業の進め方・確認項目](teacher/bomb-game/index.html)
- [教員用：ScreenTransitionSampleの授業の進め方・確認項目](teacher/screen-transition-sample/index.html)
- [教員用：BillSplitterの授業の進め方・確認項目](teacher/bill-splitter/index.html)
- [教員用：SharedPreferencesSampleの授業の進め方・確認項目](teacher/shared-preferences-sample/index.html)
- [教員用：MemoAppの授業の進め方・確認項目](teacher/memo-app/index.html)
- [教員用：RoomSampleの授業の進め方・確認項目](teacher/room-sample/index.html)
- [教員用：VocabularyBookの授業の進め方・確認項目](teacher/vocabulary-book/index.html)

### 開き方

教員はこのリポジトリをダウンロードした後、Finderで `docs/hello-android/index.html` をダブルクリックし、ブラウザで開きます。GitHub上のHTMLファイルはソース表示になるため、ローカルで開いてください。教材の本文・画像・操作機能は外部ライブラリを使わず、オフラインで利用できます。Android Studioの初回準備・ビルドと公式資料の閲覧にはインターネット接続が必要です。

ブラウザの印刷（macOS：`⌘ P`）で、教材を紙やPDFに出力できます。チェック欄は自分の進み具合を確認するためのものです。教員への提出・送信は行いません。

### 学生への配布

学生には [最新の教材リリース](https://github.com/LeoAndo/jec-26cm-android-programming-1/releases/latest) の Assets にあるZIPを案内します（初回公開後から利用可能）。ファイル名には `android1-student-materials-2026-09-19.zip` のように版の日付が入り、展開してできるフォルダも同じ名前になります。ダウンロードフォルダでどの版か分かり、別の版を同じ場所に展開しても混ざりません。展開後、はじめて授業を受ける学生は [共通資料：授業を始めるまでの準備](docs/common/setup.html) をブラウザで開き、上から順に準備します（同梱の `はじめに.txt` でも、単元一覧より前に案内しています）。準備が済んだら、授業で使う単元の `docs/hello-android/index.html`、`docs/calc-game/index.html`、`docs/rock-paper-scissors-game/index.html`、`docs/webview-app/index.html`、`docs/bomb-game/index.html`、`docs/screen-transition-sample/index.html`、`docs/bill-splitter/index.html`、`docs/shared-preferences-sample/index.html`、`docs/memo-app/index.html`、`docs/room-sample/index.html`、`docs/vocabulary-book/index.html` のいずれかをブラウザで開きます。完成プロジェクトは、展開済みの見本として配布物の `samples` フォルダに入っています。Android Studioの Open で `samples/A01HelloAndroid` のように選ぶだけで開け、初回から参考資料として使えます（各教科書からZIPでも受け取れます）。

学生用ZIPには `docs` 一式と、展開済みの完成プロジェクト（`samples`）、開き方・版情報を収録します。`teacher` フォルダと `Panda2JavaEmptyViewActivity` は収録しません。GitHubが自動で表示する **Source code (zip)** はリポジトリ全体のため、学生用ZIPには使いません。なお、このリポジトリ自体はPublicなので、教員用ファイルもGitHub上では閲覧できます。

授業中は教員が指定した版を使います。授業ごとの案内には、内容が固定された個別リリースのURLを使ってください。更新版は別フォルダに展開し、学生自身のAndroid Studioプロジェクトは上書きしません。

各単元で、学生自身が毎回Android Studioからプロジェクトを新規作成します。完成版は動作確認とコード比較の参考資料として使います。作成先は `/Users/ユーザ名/Documents/Android1/プロジェクト名` です。HelloAndroidは `A01HelloAndroid`、CalcGameは `A02CalcGame`、RockPaperScissorsGameは `A03RockPaperScissorsGame`、WebViewAppは `A04WebViewApp`、BombGameは `A05BombGame`、ScreenTransitionSampleは `A06ScreenTransitionSample`、BillSplitterは `A07BillSplitter`、SharedPreferencesSampleは `A08SharedPreferencesSample`、MemoAppは `A09MemoApp`、RoomSampleは `A10RoomSample`、VocabularyBookは `A11VocabularyBook` として保存します。

### 教員が確認に使うプロジェクト

| フォルダ | 役割 |
| --- | --- |
| `Panda2JavaEmptyViewActivity` | 教員が出発点を確認するためのJava / Empty Views Activityのひな形（学生には非公開）。授業の基準バージョン **Android Studio Panda 2 \| 2025.3.2** で作成 |
| `Quail4JavaEmptyViewActivity` | 上と同じ設定を **Android Studio Quail 4** で作ったひな形（学生には非公開）。基準より新しい版との差分を確認するための比較用。結果は[共通資料：ちがうAndroid Studioのバージョンで進めるとき](docs/common/other-versions.html)に掲載 |
| `A01HelloAndroid` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能 |
| `A02CalcGame` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能 |
| `A03RockPaperScissorsGame` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能。STEP 2の画像もこのZIPから取り出す |
| `A04WebViewApp` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能。実行時にインターネット接続が必要 |
| `A05BombGame` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能。STEP 2の画像もこのZIPから取り出す |
| `A06ScreenTransitionSample` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能。受け取った値は画面ではなくLogcat（tag `TestActivity`）で確認する |
| `A07BillSplitter` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能。STEP 2の画像と、STEP 7で配布する `BillSplitter.java` もこのZIPから取り出す |
| `A08SharedPreferencesSample` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能。配布する画像やクラスはなく、結果はすべてアプリの画面に表示する（Logcatを使わない） |
| `A09MemoApp` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能。STEP 2の画像 `title_memo.png` もこのZIPから取り出す |
| `A10RoomSample` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能。配布する画像やクラスはなく、結果はすべてアプリの画面に表示する |
| `A11VocabularyBook` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能。STEP 2の画像 `logoeng.png` もこのZIPから取り出す |

教員用ガイドとステップごとの照合用コードは `teacher/hello-android`、`teacher/calc-game`、`teacher/rock-paper-scissors-game`、`teacher/webview-app`、`teacher/bomb-game`、`teacher/screen-transition-sample`、`teacher/bill-splitter`、`teacher/shared-preferences-sample`、`teacher/memo-app`、`teacher/room-sample`、`teacher/vocabulary-book` にまとめています。完成版の見本は、配布物の `samples` フォルダに展開済みで入っています（`samples/A01HelloAndroid` / `A02CalcGame` / `A03RockPaperScissorsGame` / `A04WebViewApp` / `A05BombGame` / `A06ScreenTransitionSample` / `A07BillSplitter` / `A08SharedPreferencesSample` / `A09MemoApp` / `A10RoomSample` / `A11VocabularyBook`）。学生が自分で置き場所を作ったり、ZIPを展開したりする必要はありません。授業で作るプロジェクトは `Documents/Android1/A01HelloAndroid` / `A02CalcGame` / `A03RockPaperScissorsGame` / `A04WebViewApp` / `A05BombGame` / `A06ScreenTransitionSample` / `A07BillSplitter` / `A08SharedPreferencesSample` / `A09MemoApp` / `A10RoomSample` / `A11VocabularyBook` に置きます。

### 完成プロジェクトのZIPを更新する（教員用）

ZIPの再生成には、GitとPython 3、および **`git clone` で取得したリポジトリ** が必要です。GitHubの「Download ZIP」で取得したフォルダにはGit管理情報がないため、再生成には使えません。教材の閲覧と、同梱済みの完成プロジェクトZIPの利用は「Download ZIP」でも可能です。

```sh
git clone https://github.com/LeoAndo/jec-26cm-android-programming-1.git
cd jec-26cm-android-programming-1
```

完成コードを変更したときは、このリポジトリ直下で次を実行し、配布用ZIPも更新します。

```sh
python3 scripts/package-hello-android.py
python3 scripts/package-hello-android.py --project A02CalcGame --output docs/calc-game/downloads/A02CalcGame.zip
python3 scripts/package-hello-android.py --project A03RockPaperScissorsGame --output docs/rock-paper-scissors-game/downloads/A03RockPaperScissorsGame.zip
python3 scripts/package-hello-android.py --project A04WebViewApp --output docs/webview-app/downloads/A04WebViewApp.zip
python3 scripts/package-hello-android.py --project A05BombGame --output docs/bomb-game/downloads/A05BombGame.zip
python3 scripts/package-hello-android.py --project A06ScreenTransitionSample --output docs/screen-transition-sample/downloads/A06ScreenTransitionSample.zip
python3 scripts/package-hello-android.py --project A07BillSplitter --output docs/bill-splitter/downloads/A07BillSplitter.zip
python3 scripts/package-hello-android.py --project A08SharedPreferencesSample --output docs/shared-preferences-sample/downloads/A08SharedPreferencesSample.zip
python3 scripts/package-hello-android.py --project A09MemoApp --output docs/memo-app/downloads/A09MemoApp.zip
python3 scripts/package-hello-android.py --project A10RoomSample --output docs/room-sample/downloads/A10RoomSample.zip
python3 scripts/package-hello-android.py --project A11VocabularyBook --output docs/vocabulary-book/downloads/A11VocabularyBook.zip
```

学生用ZIPを作成するときは、A01〜A11の完成版ZIPを再生成し、HTMLのリンク確認も行います。

```sh
python3 scripts/package-student-materials.py
```

ZIPにはGitで管理しているプロジェクトのファイルを収録し、IDE設定・ローカルSDK設定・ビルド出力を除外します。既存ファイルの編集内容も反映します。ファイルを新しく追加した場合は、配布対象であることを確認して、そのファイルを `git add` してから再生成してください。

### GitHub Actionsでパッケージ化・リリースする（教員用）

**main更新時に自動準備し、学生向けの公開は手動で行います。** 学生からのフィードバックは随時mainへ反映し、授業前や修正がまとまったタイミングで公開します。

| 操作 | 自動で行う処理 | 学生向け公開 |
| --- | --- | --- |
| mainへのpush・PRマージ | テスト、完成版ZIPの再生成、教材ZIP生成、HTMLの相対リンク確認、リリースノート生成。未翻訳はSummaryに表示 | しない |
| main向けのPR | テスト、教材ZIP生成、相対リンク確認。未翻訳はSummaryに表示 | しない |
| 配布準備の翻訳PR | 配布対象の言語の差分翻訳、別AIによる照合、教材ZIPの確認 | しない |
| Run workflow（publishオフ） | mainの教材とリリースノートを再生成 | しない |
| Run workflow（publishオン） | mainの教材とリリースノートを再生成。配布対象の未翻訳が0文ならGitHub Releasesへ添付 | する |
| Run workflow（publishオン・allow_untranslatedオン） | 緊急公開として未翻訳だけを許可。日本語で表示される件数をリリースノートに記録 | する |

#### 初回の導入

1. `.github/workflows/student-materials.yml` を含む変更をmainへマージします。
2. GitHubの **Actions → Student materials** で実行結果を確認します。
3. `student-materials-ready-…` の成果物をダウンロードし、教材ZIPと `release-notes.md` を確認します。成果物の保存期間は30日です。GitHub Releasesの下書きはこの時点では作りません。
4. 公開したいタイミングで、以下の手動公開を実行します。

追加のSecretは不要です。リポジトリのGitHub Actionsが有効で、ワークフローの `contents: write` を許可するポリシーになっている必要があります。教材のパッケージ化にAndroid SDKは不要です。このワークフローではAndroidアプリのビルド・実機動作までは検証しません。

#### 手動公開

1. 配布準備のissueを起票し、`config/i18n.json` で `distribute: true` の言語の未翻訳を確認します。エージェントが [翻訳用skill](skills/translate-teaching-materials/SKILL.md) に従って差分だけを訳し、翻訳PRを作ります。翻訳はエージェントのセッションで行い、Actionsから翻訳APIは呼びません。
2. **翻訳PRを開いてから公開するまでは、`docs/` を触るPRをマージしません。** 別のAIが逆翻訳を原文と照合し、検査と配布ZIPの確認を済ませて翻訳PRをマージします。日本語の変更が先に入った場合は、最新のmainで差分を訳し直します。
3. **Actions → Student materials → Run workflow** を開きます。ブランチに **main** を選び、**publish** にチェックを入れます。**allow_untranslated** はオフのままにします。
4. **student_notes** に学生向けの案内を日本語で入力します。例：`HelloAndroid STEP 4の説明を修正。すでに完成している人はやり直し不要。`
5. **Run workflow** を押します。配布対象の言語に未翻訳があると公開前に失敗し、Summaryに言語・ページ別の件数が出ます。差分翻訳を反映してから新しく実行してください。成功すると、Releasesに教材ZIP・チェックサム・リリースノートが掲載されます。
6. 公開された個別リリースURLを授業で案内します。ここで`docs/`を触るPRのマージを再開します。

授業を進められない不具合などの緊急修正に限り、**publish** と **allow_untranslated** の両方にチェックを入れて公開できます。未翻訳の文は日本語で表示され、公開ゲートを解除したことと未翻訳の合計・言語別・ページ別の件数がリリースノートに残ります。HTMLや対訳カタログの不正、ZIPの破損、mainの更新は解除できません。`student_notes` には学生への影響と、日本語表示が残ることを補足してください。公開後は残った差分を翻訳PRで反映し、次の通常公開に備えます。

手動実行の開始時点のmainをパッケージ化します。以前の自動実行の成果物をそのまま昇格する方式ではないため、自動準備後にmainが変わっている場合は新しい内容になります。公開直前にもmainを確認し、実行中に更新されていた場合は公開を中止します。その場合は最新のmainで新しく実行してください。main以外を選ぶと、パッケージの検証のみ行い、ノート生成・公開は行いません。

版名は `materials-日付-コミットID`（例：`materials-2026.09.15-796cc2d12345`）です。日付はコミット日時の日本時間で、同じコミットは同じ版になります。公開済みの版は再実行しても上書きしません。添付中に失敗した場合は下書きに留まり、mainが変わっていなければ同じ実行の **Re-run failed jobs** で再開できます。mainが更新された場合は新しく実行し、不要になった下書きはGitHubから削除してください。

#### リリースノートとフィードバックの扱い

- GitHubの自動生成ノートに、前回公開した教材からのPR一覧を載せます。初回は過去の変更を含みます。直接mainへコミットした変更も、折りたたみのコミット一覧で確認できます。
- PRタイトルは学生が読んで分かる日本語にします。例：`HelloAndroid：STEP 4のボタン処理の説明を修正`。
- PRに `enhancement` を付けると「教材の追加」、`bug` は「誤記・不具合の修正」、それ以外は「その他の更新」に分類されます。`skip-release-notes` はPR一覧から除外しますが、コミット一覧には残ります。
- 自動生成はPRタイトルなどをまとめる機能です。修正内容をAIが解釈して学生への影響ややり直しの要否を書く機能ではないため、その案内は公開時の `student_notes` に記入します。
- フィードバックは「教材の版・単元/STEP・起きたこと」で集めます。授業を進められない不具合は修正後すぐに手動公開し、誤字や説明の補足はまとめて公開する運用がおすすめです。

#### ローカルで配布ZIPを確認する

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/package-student-materials.py
```

`dist/android1-student-materials-2026-09-19.zip` のように、版の日付（HEADのコミット日時をJSTにした日付。版タグと同じ日付）が入った名前で生成されます。対象はGit管理された `docs` のファイルで、完成版ZIPはソースから再生成します。再生成したZIPの中身は、展開済みの見本として `samples/` にも収録します（`samples/` はリポジトリにはなく、配布ZIPの中だけにできます。`gradlew` の実行権限も引き継ぎます）。新しい教材・画像は `git add` 後に実行してください。ローカルの編集内容も含むため、正式な配布版はGitHub Actionsから公開します。

単元を追加するときは、完成プロジェクトのZIP生成処理と `はじめに.txt` の単元一覧を `scripts/package-student-materials.py` に、リリースノートの単元一覧を `scripts/release-student-materials.py` に追加してください。あわせて `config/teaching-materials.json`（`scan_roots`、指定AVD名の `required_in`、`projects`）とREADMEのリンク・表も更新します。各教科書のサイドバーには全単元を並べているので、既存の全単元の教科書のサイドバーにも新しい単元を足します（`scripts/check-teaching-materials.py` が `projects` の並びと照合するので、直し忘れるとCIが落ちます）。HTML・画像・共通資料は `docs` 配下のGit管理ファイルが自動で含まれます。

参考：[GitHubのリリースノート自動生成](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes)、[ワークフローの手動実行](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)。

### 多言語展開（準備中）

この教材を使う学生の母国語は、日本語・英語・中国語・ミャンマー語・モンゴル語・広東語・フランス語の7つです。日本語で書いた教科書（`docs/`）を、配布前にほかの6言語へ展開する準備を進めています（全体の計画と決まったことは [issue #215](https://github.com/LeoAndo/jec-26cm-android-programming-1/issues/215)）。**現在は全言語の `distribute` が `false` のため、学生用ZIPは日本語のみです。** 配布対象にした言語は、ZIPを作るときに `docs/<言語>/` へ生成されます。

- **日常のPRでは翻訳しません。** 教材は今までどおり日本語だけを直します。翻訳は、学生への配布前にまとめて翻訳PRで行います。
- **コミットするのは、翻訳済みのHTMLではなく対訳カタログです。** `i18n/<言語>/<ページ>.json` に、原文と訳文の対を文単位で置きます。各言語のHTMLは、カタログから作ります（リポジトリにはコミットしません）。コード・画像・リンク・STEPの番号は日本語版からそのまま引き継ぐので、どの言語でも同じ位置に同じものが出ます。
- **日本語の文を直すと、その文は自動で未翻訳に戻ります。** 未翻訳の文は日本語のまま表示されます。古い訳が学生に届くことはありません。
- `<pre>` のコード、`<code>` の中身、Android Studioの画面に出る言葉、学生がアプリに打ち込む日本語は訳しません。授業は日本語で進むので、翻訳は読んで理解するための補助という位置づけです。

| 言語 | コード | 書き方 |
| --- | --- | --- |
| 英語 | `en` | |
| 中国語 | `zh-Hans` | 簡体字 |
| 広東語 | `zh-Hant-HK` | 繁体字の書き言葉に、香港の語彙を使う |
| ミャンマー語 | `my` | Unicode |
| モンゴル語 | `mn` | キリル文字 |
| フランス語 | `fr` | |

配布対象の言語があるZIPには、入口の `index.html` と `はじめに.txt` に各言語の案内を入れます。教科書の冒頭にある言語リンクで同じページ・STEPへ移動できます。翻訳ページには「AIによる翻訳／日本語版が正／疑問は先生へ」の注記と日本語版へのリンクが付きます。コード・画像・CSS・JS・完成版ZIPは日本語版と共有します。未翻訳の文は日本語のまま、`lang="ja"` を付けて表示します。

本文と言語リンクは静的HTMLなので、JavaScriptなしでも読めます。JavaScriptはコピーなどの操作文言をページの言語へ切り替え、共通資料の戻り先・STEP・確認済みの記録を言語の移動先へ引き継ぎます。記録の保存キーは同じ単元で共通です。`file://` ではページごとに保存領域が分かれるブラウザもあるため、言語リンクには記録も一時的に渡します。別々に開いているタブどうしを常時同期するものではありません。

`config/i18n.json` の `languages[].distribute` で配布対象を指定します。各言語の `ui`、`translation_notice`、`japanese_version`、`language_label`、`open_instructions`、`start_here` は、共通操作と配布時の案内文です。翻訳が途中の言語を配布対象にしないでください。対象が0言語なら、言語の入口や翻訳HTMLは追加せず、従来の日本語だけの構成で配布します。

言語の一覧は `config/i18n.json`、翻訳の手順とルールは [skills/translate-teaching-materials/SKILL.md](skills/translate-teaching-materials/SKILL.md)、言語ごとの用語集は `i18n/<言語>/glossary.md` にあります。翻訳そのものはエージェントが行い、スクリプトは入口と出口をそろえます。

```sh
python3 scripts/localize-student-materials.py sync --lang en     # 未翻訳の文を dist/i18n-work/ に書き出す
python3 scripts/localize-student-materials.py merge --lang en    # 訳した結果を検査して、対訳カタログへ入れる
python3 scripts/localize-student-materials.py check              # 対訳カタログを検査する（CIでも実行）
python3 scripts/localize-student-materials.py status             # 言語×ページごとに、訳した数を出す
python3 scripts/localize-student-materials.py build --lang en    # dist/i18n-preview/docs/en/ に確認用のページを作る
```

CIは、対訳カタログが壊れていないことを確かめ、未翻訳の文の数を Summary に出します。通常のPRとmainへのpushは未翻訳があっても失敗にはしません。`publish` のときだけ、配布対象の言語に未翻訳があれば公開を止めます（緊急公開の手順は上の「手動公開」を参照）。教科書のHTMLは、開始タグと終了タグを必ず対応させてください（`<p>` や `<li>` の閉じ忘れがあると、文を取り出せず、`check` が失敗します）。

---

# 開発環境：教員
```
Android Studio Panda 2 | 2025.3.2
Build #AI-253.30387.90.2532.14935130, built on February 25, 2026
Runtime version: 21.0.9+-14787801-b1163.94 aarch64
VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o.
Toolkit: sun.lwawt.macosx.LWCToolkit
macOS 26.6.2
StudioFlags with current overrides:
  LazyStudioFlagSettings(StudioFlagSettings(data.size=3)):
    studiobot.attachments=true
    studiobot.chat.enable.context.attachment=false
  PropertyOverrides(cache.size=477):
    flags.configuration.level=COMPLETE
  MendelOverrides(MendelFlagsProvider count=0):
  ServerFlagOverrides(Name: analytics/surveys/followup
        PercentEnabled: 100
        Value: custom proto
        
        Name: analytics/surveys/sentiment/url
        PercentEnabled: 100
        Value: https://google.qualtrics.com/jfe/form/SV_4ZzP5RfbOtMwbxc
        
        Name: cxx/page_align_16kb
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/ClassCastException
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/ClassNotFoundException
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/PluginException-0073ff27
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/PluginException-722647e2
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/PluginException-8b332315
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/b_372743206
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/b_392056649
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/b_452882570
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/b_458923805
        PercentEnabled: 100
        Value: custom proto
        
        Name: exceptions/b_500401440
        PercentEnabled: 100
        Value: custom proto
        
        Name: studio_flags/benchmark.survey.2026.enable
        PercentEnabled: 100
        Value: true
        
        Name: studio_flags/cloud.enabled
        PercentEnabled: 100
        Value: true
        
        Name: studio_flags/firebasetestlab.direct.access.monthly.quota
        PercentEnabled: 100
        Value: true
        
        Name: studio_flags/rundebug.install.use.pm.terminate
        PercentEnabled: 100
        Value: false
        
        Name: studio_flags/studiobot.askgemini.include.build.files.in.context
        PercentEnabled: 100
        Value: true
        
        Name: studio_flags/studiobot.chat.use.compose.for.ui
        PercentEnabled: 100
        Value: true
        
        Name: studio_flags/studiobot.compiler.error.context.enabled
        PercentEnabled: 100
        Value: true
        
        Name: studio_flags/studiobot.completions.per.hour
        PercentEnabled: 100
        Value: 36000
        
        Name: studio_flags/studiobot.conversations.per.hour
        PercentEnabled: 100
        Value: 500
        
        Name: studio_flags/studiobot.current.file.context
        PercentEnabled: 100
        Value: true
        
        Name: studio_flags/studiobot.dac.skills.limit
        PercentEnabled: 100
        Value: 0
        
        Name: studio_flags/studiobot.generations.per.hour
        PercentEnabled: 100
        Value: 3600
        
        Name: studio_flags/studiobot.inline.code.completion.file.context.enabled
        PercentEnabled: 100
        Value: true
        
        Name: studio_flags/studiobot.npa.icon.image.generation.model.name
        PercentEnabled: 100
        Value: gemini-2.5-flash-image
        
        Name: studio_flags/studiobot.npa.mockup.image.generation.model.name
        PercentEnabled: 100
        Value: gemini-3-pro-image-preview
        
        Name: studio_flags/studiobot.project.facts.context.enabled
        PercentEnabled: 100
        Value: true
        
        Name: studio_flags/studiobot_gias_user_tier
        PercentEnabled: 100
        Value: custom proto
        
        Name: studio_flags/studiobot_push_notifications/create_with_ai_promotion_notification_DAC
        PercentEnabled: 100
        Value: custom proto
        
        Name: studio_flags/studiobot_push_notifications/notification_flag_list
        PercentEnabled: 100
        Value: custom proto
        
        ):
    rundebug.install.use.pm.terminate=false
    studiobot.askgemini.include.build.files.in.context=true
    studiobot.compiler.error.context.enabled=true
    studiobot.completions.per.hour=36000
    studiobot.conversations.per.hour=500
    studiobot.current.file.context=true
    studiobot.generations.per.hour=3600
    studiobot.inline.code.completion.file.context.enabled=true
    studiobot.project.facts.context.enabled=true
  AgpReleaseBranchProvider(releasedWithAgp=true):
    gradle.ide.use.alongside.agp=true
  AgpTestSuitesProvider(journeysWithGeminiEnabled=false):
GC: G1 Young Generation, G1 Concurrent GC, G1 Old Generation
Memory: 2048M
Cores: 14
Metal Rendering is ON
Registry:
  ide.experimental.ui=true
Non-Bundled Plugins:
  org.jetbrains.junie (253.819.54)
  org.jetbrains.completion.full.line (253.30387.199)
  Dart (509.0.0)
  com.anthropic.code.plugin (0.1.14-beta)
  com.intellij.marketplace (253.30387.205)
  com.jetbrains.kmm (0.9-253.30387-AS-94)
  com.github.copilot (1.17.0-251)
  aws.toolkit.core (3.106.253)
  Docker (253.30387.30)
  com.intellij.ml.llm (253.30387.186)
  io.flutter (96.0.0)
  codiumai.codiumai (2.2.8)
```

# 開発環境：学生

2026年9月16日〜18日に実施したアンケートの回答です。**回答数は4件（n=4）のみで、クラス全員を調べた結果ではありません。**傾向を見るための標本として扱ってください。回答は匿名化して記録します。

| | Android Studio | Xcode | MacBook / OS |
| --- | --- | --- | --- |
| 回答1 | Panda 2 2025.3.2 | Xcode 26.3 (17C529) | MacBook Air / macOS Tahoe 26.3.1 |
| 回答2 | Android Studio Quail 4 | version 27 | macOS 27 |
| 回答3 | 2025.3.2 | 26.3 | 26.3.1 |
| 回答4 | 21.0.9+-14787801-b1163.94 aarch64 | 26.3 | 26.3.1 |

- 表の内容は回答をそのまま記録したものです。ビルド番号のない回答や、製品名のない回答があり、表記はそろっていません。教員側で補完・推測はしていません。
- windowsは利用していない（従来どおり、この点は変わりません）。
- Xcodeは本授業では使いませんが、学生の端末の状況を把握するためアンケート項目に含めました。

## 回答の読み取り（教員による推測。表には反映していません）

- **回答3の `2025.3.2` は、Panda 2 2025.3.2のビルド番号と思われます。**製品名が省かれているだけで、教員環境と同じ版である可能性が高いと読めます。
- **回答4の `21.0.9+-14787801-b1163.94 aarch64` は、Android Studioのバージョンではないと思われます。**Help → Aboutの `Runtime version` 行（同梱されているJetBrains Runtimeの版）を写した記入ミスと読めます。この文字列は、上の「開発環境：教員」ブロックの `Runtime version:` 行と完全に一致します。教員のPanda 2 2025.3.2と同じJetBrains Runtimeのビルドを積んでいるため、**回答4もPanda 2 2025.3.2である可能性が高い**と推測できます。ただし前後のバージョンのAndroid Studioが同じJetBrains Runtimeを同梱している可能性は否定できないため、**断定はできません。本人に聞き直す必要があります。**
- 上の2点はいずれも教員の推測であり、確認は取れていません。表の記載は回答のまま据え置きます。

## 教員環境とのバージョン差

- **回答2のAndroid Studio Quail 4は、教員環境のPanda 2 | 2025.3.2より新しい版です。**教材はPanda 2を前提に書かれており、各単元のSTEP 01で**Empty Views Activity**を選ぶ手順とPanda 2のウィザード画面のスクリーンショットを載せています。新しいAndroid Studioでは、New Projectウィザードの見た目やテンプレートが生成するコードが教材の画面と異なる可能性があります。**これは調査が必要なリスクであり、不具合が確認されたわけではありません（Quail 4での動作は未検証です）。**対応方針は教員が判断します。
- n=2からn=4になったことで、基準より新しい版を使っている回答の割合は2件中1件から4件中1件になりました。**割合が下がっただけで、リスクがなくなったわけではありません。**1人でも教材の前提より新しい版を使っている以上、上のリスクはそのまま残ります。また回答4のAndroid Studioの版は未確定なので、実際の内訳はこれと異なる可能性があります。

# 学生の躓く傾向
1. メソッドやフィールドが多くなると、コードを追えなくなる
2. SharedPreferencesの扱いに苦戦
3. ActivityResultのrequestCodeとresultCodeの扱いに苦戦
4. SQLiteOpenHelperの扱いに苦戦
5. Intentの扱いに苦戦 (putExtraでのデータ渡し等)

# 基本方針 - 前年からの変更点
1. クリックイベント処理などを簡略化。修正コード量をできるだけ削減
2. SharedPreferences用の演習アプリを新規追加
3. ActivityResultからActivityResultLauncherを使った実装に完全移行
4. SQLiteOpenHelperからRoomを使った実装に完全移行
5. 割り勘アプリは、出来るだけ公平な分配で割り勘にする仕様に変更
6. IntentのputExtraについての演習アプリを新規追加
7. リストの実装(RecyclerView)は難しいのでAndroid 1では扱わない
8. コード量を減らすため、varキーワードを多用する
9. finalキーワードの利用はワーニングが出る箇所のみ使用
10. @NonNullと@Nullableアノテーションは、学生自身が書く実装では意識させない教科書の構成にする。ただしAndroid Studioが自動で付けたものと、配布する予定で学生が直接書かないコード（A07BillSplitterのBillSplitter.javaなど）は例外とし、実装ミスの特定が楽になるようそのまま使う
11. 基本的にライブラリ追加なしで授業用テキストを作成する。ただし、androidxパッケージに関しては必要に応じて導入する
12. フォルダブルやタブレット端末へのアプリ対応は学生側に意識させない教科書の構成にする
13. ダークテーマ対応は学生側に意識させない教科書の構成にする
14. 各単元では画面回転時のデータ保持と横画面時のレイアウト対応を扱わない。考え方と対処法は[共通資料：開発Tips](docs/common/dev-tips.html)に掲載する


# 授業用教科書の基本方針
1. 各単元で、学生自身が毎回Android StudioのJava / Empty Views Activityからプロジェクトを新規作成し、修正箇所を確認しながらハンズオン形式で進める。公開する完成版は動作確認・コード比較の参考資料とする。Panda2JavaEmptyViewActivityは教員の確認用とし、学生には公開しない。
2. 教科書はGoogle Codelabなどを参考にした構成にしたい。
3. 教科書はhtml形式とする
4. 各単元で利用する教科書で共有部分が発生したらベット共通資料という形で別htmlファイル化する。具体例：apkファイルの作成方法、エミュレータの設定手順など
6. 教科書に掲載するスクリーンショットは教員の開発マシン内にある「jec_26cm_android1_Pixel 9a」エミュレータを利用する
7. **大半の学生は予習も復習もしないという前提で書く。** 学生が教科書を読むのは授業中が最初で、そのとき読むのはその単元を前から順にだけである。過去の単元を読み返していないのと同じように、先の単元もまだ読んでいない。判断基準は「予習も復習もしない学生が、その単元を前から順に読んで躓かないか」で、それを満たす構成であればよい。「家で読んでおいてください」のように、予習してきたことを当てにした導入は採らない。他単元を挙げてよいのは「これは初めてではない」と伝えるときだけで、**手順やコードをその単元に書かずに他単元へ送ってはいけない**。これは過去の単元へ送る場合（「A10と同じ手順です」）だけでなく、先の単元へ送る場合（「A11でも同じ形で書きます」）も同じ扱いとする。先の単元はまだ読んでいないので、学生にとって手がかりにならない。「A10と同じ手順です」と書いたら、その直後に手順とコードをすべて書く。学生に指示すること（チェックを入れない、ここには書かない、など）の理由も、その単元の中に書く。同じ単元の中の参照（別のSTEPを指す）は対象外とする。STEP 00の表の「学んだ単元」列と、サイドバーにある他単元へのリンクも対象外で、読み返したい学生や、別の単元を開きたい学生の導線として残す。サイドバーには全単元を並べるので、まだ読んでいない先の単元へのリンクも並ぶが、単元の一覧は本文ではなく導線である。1つも押さなくても、その単元は前から順に読むだけで進められるので、上の判断基準は崩れない。本文から先の単元へ送ってはいけないことは変わらない

# 単元の範囲の決め方（全単元共通）
演習アプリと教科書を作るとき、範囲が広がりすぎていないかを次の3点で判断する。

1. **1単元で導入する新概念は1つまで。** 「新概念」は、それまでの単元に1度も出ていない考え方やAPIを指す。実在するかは `git grep` で確認する。2つ以上必要に見えるときは、単元を分けるか、片方を後の単元へ回す。
2. **その概念の利点を、学生が画面で体感できる形にする。** 画面上の変化として見えない概念は、その単元では導入しない。「実務ではこう書く」は理由にしない。
3. **網羅を目的にしない。** 型のバリエーション、APIの全メソッド、同じ操作の複数パターンを並べても、理解は増えず読む量だけが増える。代表的な1つに絞り、残りは発展課題か後の単元へ回す。

学生の躓く傾向1「メソッドやフィールドが多くなると、コードを追えなくなる」に直結する判断基準である。

ただし**公式ドキュメントが「こう書け」と指定している形は削らない**。削ってよいのは、公式が推奨する形のうち「その単元では効果が画面に出ない部分」だけで、それは後の単元へ回す。バグになる指定（例：`getApplicationContext()`）は単元に関係なく最初から入れる。

## 適用例

| 単元 | 判断 |
| --- | --- |
| A08SharedPreferencesSample | `OnSharedPreferenceChangeListener` を外した。リスナはライフサイクルと解除の話がセットで必要になり、主題が2つになるため。`commit()` は解説の表で触れるだけにし、コードは書かせない |
| A09MemoApp | メモ一覧を `ArrayList` ではなくTextViewの表示文字列として保存した。A07では重複チェックに `ArrayList` が必要だったが、A09には判定がなく、保存時の `String.join` と復元時の `split` が増えるだけのため |
| A10RoomSample | シングルトン自体はRoom公式の推奨なので残し、排他制御（`synchronized`）だけを外した。A10は読み書きを画面と同じスレッドで行うため、競合する相手がいない。`insert` / `update` / `upsert` のうち `upsert` だけ残した。`LiveData` は単一画面では利点を体感できないため、複数画面で同期をとる単元で導入する。可変長引数と「複数データ」のUIセットも外した |

## 判断に迷ったとき

その概念が**後続の単元で必要になるか**で決める。次の単元で使うなら残す。使わないなら、発展課題か「解説」の読み物にする。

# 完成コードの書き方（全単元共通）
完成プロジェクトのコードは、単元をまたいで同じ書き方にそろえる。教科書に掲載するコードと `teacher/<単元>/code` の照合コードも同じ形にする。

## Viewの取得（findViewById）
1. `findViewById` は `onCreate` の冒頭（インセットのリスナ設定の直後）でまとめて呼び、`var` のローカル変数に入れる。命名は `txtXxx` / `edtXxx` / `btnXxx` / `imgXxx`。
2. `onCreate` 以外のメソッドからも使うViewはフィールドにする（A02CalcGameの `txtMessage`、A04WebViewAppの `webView`）。同じidに対して `findViewById` を2回呼ばない。
3. リスナの中では `findViewById` を呼ばない。押すたびに探し直すことになり、リスナの中身も読みにくくなる。
4. 次の3つは例外として認める。
   - ループでidを動的に引く場合（A02CalcGameの数字ボタン9個）。
   - 配列の初期化子の中でまとめて取得する場合（A03RockPaperScissorsGame、A05BombGame）。`onCreate` の冒頭で取得していれば準拠とみなす。
   - 取得したViewをその場でリスナを付けるためだけに使い、以後参照しない場合（A06ScreenTransitionSampleの `btn1`〜`btn3`）。変数に入れず直接つないでよい。

## レイアウトの余白
5. `android:padding` は、一番外側（`@+id/main` を付けた部品）にも内側の入れ物にも書かない。一番外側に書いても、ひな形の `ViewCompat.setOnApplyWindowInsetsListener` の中の `v.setPadding(...)` が実行時に置き換えるため指定は効かず、Android Studioのプレビューと実機で見た目が食い違う。内側の入れ物に書くと、その単元だけ余白が付いて見た目が揃わなくなる。部品は端から並べ、間隔が必要なときは中の部品の `android:layout_margin` を使う。学生向けの説明は[共通資料：開発Tips](docs/common/dev-tips.html)にある。

## nullに関するアノテーション
6. 学生が教科書を見ながら自分で打ち込むコードには `@NonNull` / `@Nullable` を書かない。`androidx.annotation` のimportも自分では足さない。教科書の本文でも説明しない。
7. **Android Studioが自動で付けたアノテーションはそのまま残す。** オーバーライドの自動生成（A04WebViewAppの `onOptionsItemSelected(@NonNull MenuItem item)`）が該当する。IDEが出力したコードを学生に消させる作業は発生させない。
8. 配布する予定で学生が直接書かないコード（A07BillSplitterの `BillSplitter.java`）は例外とし、`@NonNull` / `@IntRange` / `@CheckResult` とそれを説明するJavadocをそのまま残す。教科書では「Android Studioへのヒント」とだけ触れる。
