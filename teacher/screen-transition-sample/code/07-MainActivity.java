package jp.ac.jec.a06screentransitionsample;

import android.content.Intent;
import android.os.Bundle;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

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

        findViewById(R.id.btn1).setOnClickListener(v -> {
            var intent = new Intent(this, TestActivity.class);
            startActivity(intent);
        });

        findViewById(R.id.btn2).setOnClickListener(v -> {
            TestActivity.start(this, 1, 2L, 3.0f,
                    4.0, true, '5', "6");
        });

        findViewById(R.id.btn3).setOnClickListener(v -> {
            TestActivity.start(this, new int[]{1, 2, 3},
                    new long[]{4, 5, 6}, new float[]{7.0f, 8.0f, 9.0f},
                    new double[]{10.0, 11.0, 12.0}, new boolean[]{true, false, true},
                    new char[]{'a', 'b', 'c'}, new String[]{"7", "8", "9"});
        });
    }
}