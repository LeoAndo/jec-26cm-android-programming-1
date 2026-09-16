package jp.ac.jec.a8sharedpreferencessample;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.Set;

public class MainActivity extends AppCompatActivity {
    private SharedPreferences prefs;

    private final SharedPreferences.OnSharedPreferenceChangeListener listener = (sharedPreferences, key) -> {
        Log.d("MainActivity", "key: " + key);
    };

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

        prefs = getSharedPreferences(PrefKeys.FILE_NAME, MODE_PRIVATE);

        findViewById(R.id.btn_commit).setOnClickListener(v -> {
            var editor = prefs.edit();
            editor.putInt(PrefKeys.INT_VALUE, 1);
            editor.putString(PrefKeys.STRING_VALUE, "Hello");
            editor.putBoolean(PrefKeys.BOOLEAN_VALUE, true);
            editor.putFloat(PrefKeys.FLOAT_VALUE, 1.0f);
            editor.putLong(PrefKeys.LONG_VALUE, 1L);
            editor.putStringSet(PrefKeys.STRING_SET_VALUE, Set.of("Hello", "World"));
            var commit = editor.commit();
            if (commit) {
                Log.d("MainActivity", "保存に成功しました");
            } else {
                Log.d("MainActivity", "保存に失敗しました");
            }
        });

        findViewById(R.id.btn_apply).setOnClickListener(v -> {
            prefs.edit()
                    .putInt(PrefKeys.INT_VALUE, 2)
                    .putString(PrefKeys.STRING_VALUE, "Android")
                    .putBoolean(PrefKeys.BOOLEAN_VALUE, false)
                    .putFloat(PrefKeys.FLOAT_VALUE, 2.0f)
                    .putLong(PrefKeys.LONG_VALUE, 2L)
                    .putStringSet(PrefKeys.STRING_SET_VALUE, Set.of("Hello", "Android"))
                    .apply();
        });

        findViewById(R.id.btn_get).setOnClickListener(v -> {
            // getする
            var intValue = prefs.getInt(PrefKeys.INT_VALUE, 0);
            var stringValue = prefs.getString(PrefKeys.STRING_VALUE, "");
            var booleanValue = prefs.getBoolean(PrefKeys.BOOLEAN_VALUE, false);
            var floatValue = prefs.getFloat(PrefKeys.FLOAT_VALUE, 0);
            var longValue = prefs.getLong(PrefKeys.LONG_VALUE, 0);
            var stringSetValue = prefs.getStringSet(PrefKeys.STRING_SET_VALUE, Set.of());
            Log.d("MainActivity", "intValue: " + intValue);
            Log.d("MainActivity", "stringValue: " + stringValue);
            Log.d("MainActivity", "booleanValue: " + booleanValue);
            Log.d("MainActivity", "floatValue: " + floatValue);
            Log.d("MainActivity", "longValue: " + longValue);
            Log.d("MainActivity", "stringSetValue: " + stringSetValue);
        });

        findViewById(R.id.btn_remove).setOnClickListener(v -> {
            // removeする
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
            prefs.edit().clear().apply();
        });

        findViewById(R.id.btn_test).setOnClickListener(v -> {
            var intent = new Intent(this, TestActivity.class);
            startActivity(intent);
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        // データの変更を検知する
        prefs.registerOnSharedPreferenceChangeListener(listener);
    }

    @Override
    protected void onPause() {
        super.onPause();
        prefs.unregisterOnSharedPreferenceChangeListener(listener);
    }
}