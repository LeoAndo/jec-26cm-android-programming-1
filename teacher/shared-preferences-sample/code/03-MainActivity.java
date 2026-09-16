package jp.ac.jec.a08sharedpreferencessample;

import android.content.SharedPreferences;
import android.os.Bundle;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

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

        // ファイル名を指定して、SharedPreferencesを取得する.
        prefs = getSharedPreferences(FILE_NAME, MODE_PRIVATE);
    }
}
