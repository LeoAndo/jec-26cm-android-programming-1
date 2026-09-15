# Androidプログラミング1 — 授業用教材

## HelloAndroidの教科書

1コマ90分、全2コマを目安にした、JavaとXMLの入門教材です。予習なしで授業内の操作・確認・ミニ練習まで進められる構成です。

- [HelloAndroid：はじめてのアプリ作り](docs/hello-android/index.html)
- [完成プロジェクト（初回から参照可能）](docs/hello-android/downloads/A01HelloAndroid.zip)
- [共通資料：エミュレータの準備とアプリの実行](docs/common/emulator.html)
- [共通資料：Auto Importの設定](docs/common/auto-import.html)
- [共通資料：Logcatの使い方](docs/common/logcat.html)
- [共通資料：提出用APKの作り方](docs/common/apk.html)
- [教員用：授業の進め方・確認項目](teacher/hello-android/index.html)

### 開き方

教員はこのリポジトリをダウンロードした後、Finderで `docs/hello-android/index.html` をダブルクリックし、ブラウザで開きます。GitHub上のHTMLファイルはソース表示になるため、ローカルで開いてください。教材の本文・画像・操作機能は外部ライブラリを使わず、オフラインで利用できます。Android Studioの初回準備・ビルドと公式資料の閲覧にはインターネット接続が必要です。

ブラウザの印刷（macOS：`⌘ P`）で、教材を紙やPDFに出力できます。チェック欄は自分の進み具合を確認するためのものです。教員への提出・送信は行いません。

### 学生への配布

学生には `docs` フォルダを配布します。教科書から完成プロジェクトのZIPをダウンロードでき、初回から参考資料として使えます。`teacher` フォルダと `Panda2JavaEmptyViewActivity` は配布しません。

各単元で、学生自身が毎回Android Studioからプロジェクトを新規作成します。完成版は動作確認とコード比較の参考資料として使います。作成先は `/Users/ユーザ名/Documents/Android1/プロジェクト名` です。HelloAndroidの保存先は `/Users/ユーザ名/Documents/Android1/A01HelloAndroid` です。

### 教員が確認に使うプロジェクト

| フォルダ | 役割 |
| --- | --- |
| `Panda2JavaEmptyViewActivity` | 教員が出発点を確認するためのJava / Empty Views Activityのひな形（学生には非公開） |
| `A01HelloAndroid` | 完成プロジェクト。配布用ZIPを教科書に同梱し、初回から学生も参照可能 |

教員用ガイドとステップごとの照合用コードは `teacher/hello-android` にまとめています。完成版の見本は `Documents/Android1/samples/A01HelloAndroid`、授業で作るプロジェクトは `Documents/Android1/A01HelloAndroid` に置きます。

### 完成プロジェクトのZIPを更新する（教員用）

ZIPの再生成には、GitとPython 3、および **`git clone` で取得したリポジトリ** が必要です。GitHubの「Download ZIP」で取得したフォルダにはGit管理情報がないため、再生成には使えません。教材の閲覧と、同梱済みの完成プロジェクトZIPの利用は「Download ZIP」でも可能です。

```sh
git clone https://github.com/LeoAndo/jec-26cm-android-programming-1.git
cd jec-26cm-android-programming-1
```

完成コードを変更したときは、このリポジトリ直下で次を実行し、配布用ZIPも更新します。

```sh
python3 scripts/package-hello-android.py
```

ZIPにはGitで管理しているプロジェクトのファイルを収録し、IDE設定・ローカルSDK設定・ビルド出力を除外します。既存ファイルの編集内容も反映します。ファイルを新しく追加した場合は、配布対象であることを確認して、そのファイルを `git add` してから再生成してください。

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
```
Android Studio Panda 2 | 2025.3.2
macOS バージョン不明
windowsは利用していない
```

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
10. @NonNullと@Nullableアノテーションは部分的に使いたい (実装ミスの特定が楽になるため)
11. 基本的にライブラリ追加なしで授業用テキストを作成する。ただし、androidxパッケージに関しては必要に応じて導入する
12. フォルダブルやタブレット端末へのアプリ対応は学生側に意識させない教科書の構成にする
13. ダーツテーマ対応は学生側に意識させない教科書の構成にする


# 授業用教科書の基本方針
1. 各単元で、学生自身が毎回Android StudioのJava / Empty Views Activityからプロジェクトを新規作成し、修正箇所を確認しながらハンズオン形式で進める。公開する完成版は動作確認・コード比較の参考資料とする。Panda2JavaEmptyViewActivityは教員の確認用とし、学生には公開しない。
2. 教科書はGoogle Codelabなどを参考にした構成にしたい。
3. 教科書はhtml形式とする
4. 各単元で利用する教科書で共有部分が発生したらベット共通資料という形で別htmlファイル化する。具体例：apkファイルの作成方法、エミュレータの設定手順など
6. 教科書に掲載するスクリーンショットは教員の開発マシン内にある「jec_26cm_android1_Pixel 9a」エミュレータを利用する
