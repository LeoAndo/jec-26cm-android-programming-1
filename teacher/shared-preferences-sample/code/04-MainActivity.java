package jp.ac.jec.a08sharedpreferencessample;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.Set;

public class MainActivity extends AppCompatActivity {
    private static final String FILE_NAME = "app";
    private static final String INT_VALUE = "int_value";
    private static final String BOOLEAN_VALUE = "boolean_value";
    private static final String FLOAT_VALUE = "float_value";
    private static final String LONG_VALUE = "long_value";
    private static final String STRING_VALUE = "string_value";
    private static final String STRING_SET_VALUE = "string_set_value";

    private SharedPreferences prefs;

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

        var txtOutput = (TextView) findViewById(R.id.txt_output);

        // ファイル名を指定して、SharedPreferencesを取得する.
        prefs = getSharedPreferences(FILE_NAME, MODE_PRIVATE);

        // 保存されているデータを表示する.
        // アプリを終了してから開き直しても、データが残っていることを確認できる.
        txtOutput.setText(currentValues());
    }

    /**
     * 保存されているデータをまとめて1つの文字列にする.
     * データがない場合は、getXxx()の第2引数に渡した初期値が返る.
     */
    private String currentValues() {
        return INT_VALUE + " = " + prefs.getInt(INT_VALUE, 0) + "\n"
                + STRING_VALUE + " = " + prefs.getString(STRING_VALUE, "") + "\n"
                + BOOLEAN_VALUE + " = " + prefs.getBoolean(BOOLEAN_VALUE, false) + "\n"
                + FLOAT_VALUE + " = " + prefs.getFloat(FLOAT_VALUE, 0) + "\n"
                + LONG_VALUE + " = " + prefs.getLong(LONG_VALUE, 0) + "\n"
                + STRING_SET_VALUE + " = " + prefs.getStringSet(STRING_SET_VALUE, Set.of());
    }
}
