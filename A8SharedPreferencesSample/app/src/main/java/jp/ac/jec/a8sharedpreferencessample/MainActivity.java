package jp.ac.jec.a8sharedpreferencessample;

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

        // ファイル名を指定して、SharedPreferencesを取得する.
        prefs = getSharedPreferences(PrefKeys.FILE_NAME, MODE_PRIVATE);

        // 保存されているデータを表示する.
        // アプリを終了してから開き直しても、データが残っていることを確認できる.
        showText(currentValues());

        findViewById(R.id.btn_commit).setOnClickListener(v -> {
            // データを保存するときは、edit()でEditorを取得する.
            var editor = prefs.edit();
            editor.putInt(PrefKeys.INT_VALUE, 1);
            editor.putString(PrefKeys.STRING_VALUE, "Hello");
            editor.putBoolean(PrefKeys.BOOLEAN_VALUE, true);
            editor.putFloat(PrefKeys.FLOAT_VALUE, 1.0f);
            editor.putLong(PrefKeys.LONG_VALUE, 1L);
            editor.putStringSet(PrefKeys.STRING_SET_VALUE, Set.of("Hello", "World"));
            // commit()を呼ぶまでは保存されない. 戻り値で成功したかどうかが分かる.
            var result = editor.commit();
            showText("commit() -> " + result + "\n\n" + currentValues());
        });

        findViewById(R.id.btn_get).setOnClickListener(v -> showText(currentValues()));

        findViewById(R.id.btn_clear).setOnClickListener(v -> {
            // clear()は、保存されているデータをすべて削除する.
            prefs.edit().clear().commit();
            showText(currentValues());
        });

        findViewById(R.id.btn_xml).setOnClickListener(v -> showText(readPrefsXml()));
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
}
