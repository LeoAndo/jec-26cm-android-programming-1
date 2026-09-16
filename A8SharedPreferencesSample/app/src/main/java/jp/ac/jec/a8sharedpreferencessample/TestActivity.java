package jp.ac.jec.a8sharedpreferencessample;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.Set;

public class TestActivity extends AppCompatActivity {
    private SharedPreferences prefs;
    private TextView output;

    private final SharedPreferences.OnSharedPreferenceChangeListener listener =
            (sharedPreferences, key) -> output.append("onSharedPreferenceChanged: " + key + "\n");

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_test);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        output = findViewById(R.id.tv_output);

        // MainActivityとは別の画面だが、同じファイル名を指定しているので同じデータを読み書きできる.
        prefs = getSharedPreferences(PrefKeys.FILE_NAME, MODE_PRIVATE);

        findViewById(R.id.btn_apply).setOnClickListener(v -> {
            output.setText("");
            prefs.edit()
                    .putInt(PrefKeys.INT_VALUE, 3)
                    .putString(PrefKeys.STRING_VALUE, "iOS")
                    .putBoolean(PrefKeys.BOOLEAN_VALUE, true)
                    .putFloat(PrefKeys.FLOAT_VALUE, 3.0f)
                    .putLong(PrefKeys.LONG_VALUE, 3L)
                    .putStringSet(PrefKeys.STRING_SET_VALUE, Set.of("Hello", "iOS"))
                    .apply();
            output.append("apply() -> void\n");
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        // MainActivityと同じく、画面が見えている間だけデータの変更を検知する.
        prefs.registerOnSharedPreferenceChangeListener(listener);
    }

    @Override
    protected void onPause() {
        super.onPause();
        // 登録したままにするとリスナーが残り続けてしまうため、必ず解除する.
        prefs.unregisterOnSharedPreferenceChangeListener(listener);
    }
}
