package jp.ac.jec.a06screentransitionsample;

import android.os.Bundle;
import android.util.Log;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class TestActivity extends AppCompatActivity {
    private static final String EXTRA_KEY_INT_VALUE = "intValue";
    private static final String EXTRA_KEY_STRING_VALUE = "stringValue";

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

        var intValue = getIntent().getIntExtra(EXTRA_KEY_INT_VALUE, 0);
        var stringValue = getIntent().getStringExtra(EXTRA_KEY_STRING_VALUE);
        Log.d("TestActivity", "intValue: " + intValue);
        Log.d("TestActivity", "stringValue: " + stringValue);
    }
}
