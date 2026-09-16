package jp.ac.jec.a8sharedpreferencessample;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.Locale;
import java.util.Set;

public class MainActivity extends AppCompatActivity {
    private SharedPreferences prefs;
    private ScrollView scrollOutput;
    private TextView output;

    // データの変更を検知するリスナー.
    // 1回のedit()で6個のキーを変更すると、6回呼ばれる.
    // clear()で全削除したときは、keyがnullで通知される.
    private final SharedPreferences.OnSharedPreferenceChangeListener listener =
            (sharedPreferences, key) -> appendLine("onSharedPreferenceChanged: " + key);

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        scrollOutput = findViewById(R.id.scroll_output);
        output = findViewById(R.id.tv_output);

        prefs = getSharedPreferences(PrefKeys.FILE_NAME, MODE_PRIVATE);

        findViewById(R.id.btn_commit).setOnClickListener(v -> {
            clearOutput();
            var editor = prefs.edit();
            editor.putInt(PrefKeys.INT_VALUE, 1);
            editor.putString(PrefKeys.STRING_VALUE, "Hello");
            editor.putBoolean(PrefKeys.BOOLEAN_VALUE, true);
            editor.putFloat(PrefKeys.FLOAT_VALUE, 1.0f);
            editor.putLong(PrefKeys.LONG_VALUE, 1L);
            editor.putStringSet(PrefKeys.STRING_SET_VALUE, Set.of("Hello", "World"));
            // commit()は保存が終わるまで待ち、成功したかどうかを返す.
            var result = editor.commit();
            appendLine("commit() -> " + result);
        });

        findViewById(R.id.btn_apply).setOnClickListener(v -> {
            clearOutput();
            prefs.edit()
                    .putInt(PrefKeys.INT_VALUE, 2)
                    .putString(PrefKeys.STRING_VALUE, "Android")
                    .putBoolean(PrefKeys.BOOLEAN_VALUE, false)
                    .putFloat(PrefKeys.FLOAT_VALUE, 2.0f)
                    .putLong(PrefKeys.LONG_VALUE, 2L)
                    .putStringSet(PrefKeys.STRING_SET_VALUE, Set.of("Hello", "Android"))
                    .apply();
            // apply()は戻り値がなく、ファイルへの保存はバックグラウンドで行われる.
            appendLine("apply() -> void");
        });

        findViewById(R.id.btn_get).setOnClickListener(v -> showText(currentValues()));

        findViewById(R.id.btn_remove).setOnClickListener(v -> {
            clearOutput();
            prefs.edit()
                    .remove(PrefKeys.INT_VALUE)
                    .remove(PrefKeys.STRING_VALUE)
                    .remove(PrefKeys.BOOLEAN_VALUE)
                    .remove(PrefKeys.FLOAT_VALUE)
                    .remove(PrefKeys.LONG_VALUE)
                    .remove(PrefKeys.STRING_SET_VALUE)
                    .apply();
        });

        findViewById(R.id.btn_clear).setOnClickListener(v -> {
            clearOutput();
            prefs.edit().clear().apply();
        });

        findViewById(R.id.btn_xml).setOnClickListener(v -> showText(readPrefsXml()));

        findViewById(R.id.btn_test).setOnClickListener(v -> {
            var intent = new Intent(this, TestActivity.class);
            startActivity(intent);
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        // 画面が見えている間だけ、データの変更を検知する.
        prefs.registerOnSharedPreferenceChangeListener(listener);
        // 起動したときと、TestActivityから戻ってきたときに、保存されているデータを表示する.
        showText(currentValues());
    }

    @Override
    protected void onPause() {
        super.onPause();
        // 登録したままにするとリスナーが残り続けてしまうため、必ず解除する.
        prefs.unregisterOnSharedPreferenceChangeListener(listener);
    }

    /**
     * 保存されているデータをまとめて1つの文字列にする.
     * データがない場合は、getXxx()の第2引数に渡した初期値が返る.
     */
    private String currentValues() {
        return format(PrefKeys.INT_VALUE, prefs.getInt(PrefKeys.INT_VALUE, 0))
                + format(PrefKeys.STRING_VALUE, prefs.getString(PrefKeys.STRING_VALUE, ""))
                + format(PrefKeys.BOOLEAN_VALUE, prefs.getBoolean(PrefKeys.BOOLEAN_VALUE, false))
                + format(PrefKeys.FLOAT_VALUE, prefs.getFloat(PrefKeys.FLOAT_VALUE, 0))
                + format(PrefKeys.LONG_VALUE, prefs.getLong(PrefKeys.LONG_VALUE, 0))
                + format(PrefKeys.STRING_SET_VALUE, prefs.getStringSet(PrefKeys.STRING_SET_VALUE, Set.of()));
    }

    /** キーと値を「キー = 値」の形に整える. */
    private String format(String key, Object value) {
        return String.format(Locale.US, "%-17s = %s\n", key, value);
    }

    /**
     * SharedPreferencesの実体であるXMLファイルを読み込んで返す.
     * 自分のアプリのデータなので、特別な権限なしで読める.
     */
    private String readPrefsXml() {
        var file = new File(getApplicationInfo().dataDir, "shared_prefs/" + PrefKeys.FILE_NAME + ".xml");
        if (!file.exists()) {
            return file.getAbsolutePath() + "\n\n(file not found)";
        }
        try {
            return file.getAbsolutePath() + "\n\n"
                    + new String(Files.readAllBytes(file.toPath()), StandardCharsets.UTF_8);
        } catch (IOException e) {
            return "read error: " + e;
        }
    }

    private void showText(String text) {
        output.setText(text);
        scrollOutput.post(() -> scrollOutput.fullScroll(View.FOCUS_UP));
    }

    private void clearOutput() {
        output.setText("");
    }

    private void appendLine(String line) {
        output.append(line + "\n");
    }
}
