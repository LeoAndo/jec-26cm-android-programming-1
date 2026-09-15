package jp.ac.jec.a03rockpaperscissorsgame;

import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.concurrent.ThreadLocalRandom;

public class MainActivity extends AppCompatActivity {

    private int selectedHand = -1; // -1:未選択 0:グー 1:チョキ 2:パー
    private int winCount;

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

        var txtMessage = (TextView) findViewById(R.id.txt_message);
        var imgCpu = (ImageView) findViewById(R.id.img_cpu);
        var btnStart = findViewById(R.id.btn_start);
        var btnNext = findViewById(R.id.btn_next);

        var imageViews = new ImageView[]{
                findViewById(R.id.img_rock),
                findViewById(R.id.img_scissors),
                findViewById(R.id.img_paper)
        };
        for (var imageView : imageViews) {
            imageView.setOnClickListener(v -> {
                btnStart.setEnabled(true);
                for (var i = 0; i < imageViews.length; i++) {
                    if (imageViews[i] == v) {
                        v.setBackgroundColor(Color.RED);
                        // 選択状態を保持
                        selectedHand = i;
                    } else {
                        imageViews[i].setBackground(null);
                    }
                }
            });
        }

        btnNext.setOnClickListener(v -> {
            for (var imageView : imageViews) {
                imageView.setBackground(null);
                imageView.setClickable(true);
            }
            btnStart.setEnabled(false);
            btnNext.setEnabled(false);
            imgCpu.setVisibility(View.INVISIBLE);
            txtMessage.setText("じゃんけんの手を選んでください");
        });

        btnStart.setOnClickListener(v -> {
            for (var item : imageViews) {
                item.setClickable(false);
            }
            btnStart.setEnabled(false);
            btnNext.setEnabled(true);

            var cpu = ThreadLocalRandom.current().nextInt(3);// CPUの手 0:グー 1:チョキ 2:パー
            var item = new int[]{R.drawable.rock, R.drawable.scissors, R.drawable.paper};
            imgCpu.setVisibility(View.VISIBLE);
            imgCpu.setImageResource(item[cpu]);
            var result = (selectedHand - cpu + 3) % 3; // 結果は必ず 0, 1, 2 のいずれかになる
            Log.d("MainActivity", "selectedHandIndex: " + selectedHand + ", cpu: " + cpu + ", result: " + result);
            switch (result) {
                case 0: // 引き分け
                    winCount = 0;
                    txtMessage.setText("引き分け");
                    break;
                case 1: // プレイヤーの負け
                    winCount = 0;
                    txtMessage.setText("あなたの負け");
                    break;
                case 2: // プレイヤーの勝ち
                    winCount++;
                    txtMessage.setText("あなたの勝ち " + winCount + "連勝中！");
                    break;
            }
        });
    }
}