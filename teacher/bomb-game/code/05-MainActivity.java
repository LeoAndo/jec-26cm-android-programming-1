package jp.ac.jec.a05bombgame;

import android.os.Bundle;
import android.util.Log;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.Arrays;
import java.util.concurrent.ThreadLocalRandom;

public class MainActivity extends AppCompatActivity {
    private int[] randomIgnitionNumbers; // 導火線スイッチの数字

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

        generateIgnitionNumbers();
    }

    /**
     * 導火線スイッチの数字をランダムに2つ生成する.
     */
    private void generateIgnitionNumbers() {
        do {
            // 1から9まで範囲のランダムな数値を2つ作る.同じ値が含まれていたら作り直す.
            randomIgnitionNumbers = ThreadLocalRandom.current().ints(2, 1, 10).toArray();
        } while (Arrays.stream(randomIgnitionNumbers).distinct().count() != 2);

        // debug
        for (var randomIgnitionNumber : randomIgnitionNumbers) {
            Log.d("MainActivity", "randomIgnitionNumber = " + randomIgnitionNumber);
        }
    }
}
