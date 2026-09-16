package jp.ac.jec.a02calcgame;

import android.os.Bundle;
import android.os.SystemClock;
import android.widget.Button;
import android.widget.Chronometer;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.snackbar.Snackbar;

import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;

public class MainActivity extends AppCompatActivity {
    private int nowNo = 1; // 今の問題が何問目かのカウント数
    private int correctNo; // 正解数
    private int answer; // 計算結果の答え
    private long elapsedTimeMillis; // タイマーの経過時間(ms)
    private boolean isPlaying = false; // ゲーム中かどうかのフラグ (Chronometer#mStartedフラグを取得できないため用意)
    private TextView txtMessage; // メッセージの表示欄。onCreate以外のメソッドからも使うためフィールドにする

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

        // Viewのインスタンスを取得する
        var chronometer = (Chronometer) findViewById(R.id.chronometer);
        txtMessage = (TextView) findViewById(R.id.txt_message);
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

        // 数字ボタンを押下した時の処理
        var numberButtonIds = new int[]{
                R.id.btn1, R.id.btn2, R.id.btn3, R.id.btn4,
                R.id.btn5, R.id.btn6, R.id.btn7, R.id.btn8, R.id.btn9
        };
        for (var id : numberButtonIds) {
            var btn = (Button) findViewById(id);
            btn.setOnClickListener(v -> {
                if (!isPlaying) {
                    Snackbar.make(v, "ゲーム中のみボタンを押せます", Snackbar.LENGTH_SHORT).show();
                    return;
                }
                var number = Integer.parseInt(btn.getText().toString());
                if (number == answer) {
                    correctNo++;
                }
                if (nowNo <= 9) {
                    nowNo++;
                    startQuestion();
                } else {
                    chronometer.stop();
                    elapsedTimeMillis = SystemClock.elapsedRealtime() - chronometer.getBase();
                    var timeSec = TimeUnit.MILLISECONDS.toSeconds(elapsedTimeMillis);
                    var message = correctNo + "問正解しました！時間は" + timeSec + "秒です";
                    txtMessage.setText(message);
                    btnReset.setEnabled(true);
                    btnStart.setEnabled(false);
                    btnStop.setEnabled(false);
                    isPlaying = false;
                }
            });
        }
    }

    /**
     * 問題を開始する
     */
    private void startQuestion() {
        var randomNumber = ThreadLocalRandom.current().nextInt(1, 10);
        // var randomNumber = RandomGenerator.getDefault().nextInt(1, 10); // API Level 35から利用可能. OSバージョンの分岐は使わない
        answer = 10 - randomNumber;
        var message = nowNo + "問目: 10 - " + randomNumber + " =";
        txtMessage.setText(message);
    }
}
