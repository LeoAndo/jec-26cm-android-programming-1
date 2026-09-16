package jp.ac.jec.a06screentransitionsample;

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
            TestActivity.start(this);
        });

        findViewById(R.id.btn2).setOnClickListener(v -> {
            TestActivity.start(this, 1, "2");
        });

        findViewById(R.id.btn3).setOnClickListener(v -> {
            TestActivity.start(this, new String[]{"3", "4", "5"});
        });
    }
}
