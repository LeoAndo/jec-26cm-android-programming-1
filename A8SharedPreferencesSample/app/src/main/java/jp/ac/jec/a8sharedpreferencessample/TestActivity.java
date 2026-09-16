package jp.ac.jec.a8sharedpreferencessample;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.Set;

public class TestActivity extends AppCompatActivity {
    private SharedPreferences prefs;

    private final SharedPreferences.OnSharedPreferenceChangeListener listener = (sharedPreferences, key) -> {
        Log.d("TestActivity", "key: " + key);
    };

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

        prefs = getSharedPreferences(PrefKeys.FILE_NAME, MODE_PRIVATE);

        // データの変更を検知する
        prefs.registerOnSharedPreferenceChangeListener(listener);

        // 適当なデータを保存する
        prefs.edit()
                .putInt(PrefKeys.INT_VALUE, 3)
                .putString(PrefKeys.STRING_VALUE, "iOS")
                .putBoolean(PrefKeys.BOOLEAN_VALUE, true)
                .putFloat(PrefKeys.FLOAT_VALUE, 3.0f)
                .putLong(PrefKeys.LONG_VALUE, 3L)
                .putStringSet(PrefKeys.STRING_SET_VALUE, Set.of("Hello", "iOS"))
                .apply();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // リスナーは不要になったタイミングで解除する.
        // リスナーの登録を解除しないと、画面終了したonDestroy()後でもイベントを拾い続ける.
        prefs.unregisterOnSharedPreferenceChangeListener(listener);
    }
}