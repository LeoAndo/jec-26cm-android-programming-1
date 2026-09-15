package jp.ac.jec.a05bombgame;

import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

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

        var txtMessage = (TextView) findViewById(R.id.txt_message);
        var imgBomb = (ImageView) findViewById(R.id.img_bomb);
        var btnRetry = findViewById(R.id.btn_retry);
        var numberButtons = new Button[]{
                findViewById(R.id.btn1), findViewById(R.id.btn2), findViewById(R.id.btn3),
                findViewById(R.id.btn4), findViewById(R.id.btn5), findViewById(R.id.btn6),
                findViewById(R.id.btn7), findViewById(R.id.btn8), findViewById(R.id.btn9)
        };

        for (var button : numberButtons) {
            button.setOnClickListener(v -> {
                button.setEnabled(false);
            });
        }
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
