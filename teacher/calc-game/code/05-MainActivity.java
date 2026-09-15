package jp.ac.jec.a02calcgame;

import android.os.Bundle;
import android.os.SystemClock;
import android.widget.Chronometer;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {
    private int nowNo = 1; // 今の問題が何問目かのカウント数
    private int correctNo; // 正解数
    private int answer; // 計算結果の答え
    private long elapsedTimeMillis; // タイマーの経過時間(ms)
    private boolean isPlaying = false; // ゲーム中かどうかのフラグ (Chronometer#mStartedフラグを取得できないため用意)


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

        var chronometer = (Chronometer) findViewById(R.id.chronometer);
        var txtMessage = (TextView) findViewById(R.id.txt_message);
        var btnStart = findViewById(R.id.btn_start);
        var btnStop = findViewById(R.id.btn_stop);
        var btnReset = findViewById(R.id.btn_reset);

        // Startボタンを押下した時の処理
        btnStart.setOnClickListener(v -> {
            chronometer.setBase(SystemClock.elapsedRealtime() - elapsedTimeMillis);
            chronometer.start();
            btnStop.setEnabled(true);
            btnStart.setEnabled(false);
            btnReset.setEnabled(false);
            // 初回開始時だけ問題を作る。STOP後のSTARTでは現在の問題をそのまま再開する
            if (answer == 0) {
                startQuestion();
            }
            isPlaying = true;
        });

        // Stopボタンを押下した時の処理
        btnStop.setOnClickListener(v -> {
            chronometer.stop();
            elapsedTimeMillis = SystemClock.elapsedRealtime() - chronometer.getBase();
            btnStop.setEnabled(false);
            btnStart.setEnabled(true);
            btnReset.setEnabled(true);
            isPlaying = false;
        });

        // Resetボタンを押下した時の処理
        btnReset.setOnClickListener(v -> {
            chronometer.stop();
            chronometer.setBase(SystemClock.elapsedRealtime());
            btnStop.setEnabled(false);
            btnStart.setEnabled(true);
            btnReset.setEnabled(false);
            txtMessage.setText("");
            elapsedTimeMillis = 0;
            nowNo = 1;
            correctNo = 0;
            answer = 0;
            isPlaying = false;
        });
    }
}
