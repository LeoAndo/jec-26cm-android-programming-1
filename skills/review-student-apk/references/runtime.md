# 動作とクラッシュの確認

## 準備と対象の取り違え防止

リポジトリの `AGENTS.md` §7（指定AVD、オーナーの作業を止めない、準備累計10分・同じ原因の再試行2回まで）を適用する。既に起動している指定AVDを使えるという了承がセッション内にある場合は、聞き直さない。了承がなく利用中の可能性がある場合は、同節の根拠を示して利用可否を確認する。その間は静的解析を進める。

1. `adb devices` と `adb -s <シリアル> emu avd name` で、対象が指定の `jec_26cm_android1_Pixel 9a` であることを確かめる。実機・ほかのAVDを使わず、adbサーバーを再起動しない。自分でAVDを起動する場合のオプションと後片付けも§7に従う。
2. APKのManifestから実際のapplicationIdと起動Activityを確認する。教材既定のpackageをそのまま使わない。以下の `APK_REVIEW_*` は確認した実値に置き換える。`PACKAGE` や `COMPONENT` にはシェル演算子などがない正規のAndroid名であることを確認する。
3. 対象パッケージが既にインストールされているか `adb -s "$APK_REVIEW_SERIAL" shell pm path "$APK_REVIEW_PACKAGE"` で見る。既存アプリがあれば、誰のどの提出物か、データ消去の可否を確認する。無条件の `install -r`、`uninstall`、`pm clear` は使わない。同じパッケージの提出は直列に評価し、今回の評価用に自分が入れたアプリだけを、記録を保存してからアンインストールする。元から入っていたアプリを復元できるとは限らない。

## ログを取りながら確認する

出力先は収集スクリプトが作った今回のディレクトリ。以下は1回分の例であり、再試行は新しいファイル名にする。APKのSHA-256と端末のAPIを記録する。端末上の時刻を使い、Macとの時計の差でログの期間を間違えない。

```sh
adb -s "$APK_REVIEW_SERIAL" shell getprop ro.build.version.sdk
adb -s "$APK_REVIEW_SERIAL" install "$APK_REVIEW_APK"
```

インストールが `Success` になったことを確認する。失敗したら、署名不一致、minSdk、ABI、testOnly、破損やsplit APK不足などの原因を切り分ける。アプリのクラッシュとは記録しない。必要なインストール条件を確認せず、再試行のオプションを増やさない。

起動前からログを連続収集する。クラッシュ後に `pidof` で絞るとプロセスが消えて取り逃すので、収集時点ではPIDで絞らない。既存ログの消去（`logcat -c`）は不要。

```sh
adb -s "$APK_REVIEW_SERIAL" shell "date '+%m-%d %H:%M:%S.000'"
adb -s "$APK_REVIEW_SERIAL" logcat -b main -b system -b crash -v threadtime -T 1 \
  > "$APK_REVIEW_OUTPUT/runtime-01.log" 2> "$APK_REVIEW_OUTPUT/logcat-01.stderr" &
APK_REVIEW_LOG_PID=$!
adb -s "$APK_REVIEW_SERIAL" shell am start -W -n "$APK_REVIEW_COMPONENT"
```

連続収集プロセスが生きていることとstderrを確認してから操作する。起動コマンドの出力も保存する。`-T 1` で直前のログが1件入るので、開始時刻より前の記録を今回の試行に含めない。ツールがバックグラウンドジョブを維持できないときは、起動前に取得した端末時刻を指定して `logcat -b main -b system -b crash -d -v threadtime -T '<端末の開始時刻>'` で取得する。ログが循環して消えた可能性は未確認として残す。

教材の完成チェックと確認したアレンジに応じて、通常操作、入力の境界、画面遷移、保存と再起動などを選ぶ。必要な画面のみ、既存のUI操作ツールか `adb -s ... shell input` で操作する。ランダム操作だけで評価を終えない。ネットワークが必要な単元は接続状態も記録する。実在の個人情報、課金、外部への投稿を使わず、ローカルのテスト用入力にする。

画面の証拠が必要なときだけ `adb -s "$APK_REVIEW_SERIAL" exec-out screencap -p > "$APK_REVIEW_OUTPUT/screen-01.png"` で保存する。試行の終了時刻を記録し、終了時には自分の収集プロセスだけを止める。

```sh
adb -s "$APK_REVIEW_SERIAL" shell "date '+%m-%d %H:%M:%S.000'"
kill "$APK_REVIEW_LOG_PID"
wait "$APK_REVIEW_LOG_PID"
```

例外終了時もログ収集を残しっぱなしにしない。停止による `wait` の非0終了は、APKの失敗ではない。大量の端末ログはローカルに留め、講評には必要な対象アプリの部分だけを使う。

## クラッシュと修正候補

- 今回の実行時間帯と、`Process: <applicationId>, PID: ...`、起動・終了ログを照合する。`:service` のような別プロセスも、対象アプリとの所属が確認できた場合だけ含める。別のアプリの `FATAL EXCEPTION` を混ぜない。
- Java例外は `FATAL EXCEPTION` からスタック全体を読み、入れ子の `Caused by` とアプリ側のフレームを追う。最上段が `RuntimeException` でも、根本の原因がその下にあることがある。
- ANR（応答停止）、native crash、インストール失敗、通信失敗を分ける。Javaの例外がないだけで「クラッシュなし」としない。native crashはログにある信号・backtraceを読み、シンボル不足なら特定の限界を書く。
- 課題名、APK SHA-256、比較版、AVD/API、テストデータと初期状態、操作順、期待結果、実際の結果、再現回数、ログのファイル・行を教員向けレポートに残す。
- 修正場所はログとコードが一致する場合に示す。ログの `MainActivity.java:42` は「ログに出た位置」であり、逆コンパイル結果の42行目や手元の教材の42行目と同一とは限らない。`SourceFile`、`Unknown Source`、難読化名から元の行番号を作らない。
- 例えば `NumberFormatException` なら、再現入力と呼び出し元を確認したうえで、その入力の確認や変換前の条件分岐を候補にする。`NullPointerException` なら、レイアウトのID、`setContentView`、Intentの受け渡しなど、実際の該当式に合わせて調べる。例外名だけで一律の修正コードを出さない。
- 難読化されていれば、そのAPKを作ったビルドの `mapping.txt` とR8 retraceを使う。別ビルドの対応表を流用しない。対応表やソースがないときも、再現操作・例外・確認するクラスやメソッドまでを報告できる。
- 修正を試していなければ「修正候補」とし、直ったと書かない。例外が観測されなかった場合は「実施した操作では観測しなかった」と確認範囲を添える。
