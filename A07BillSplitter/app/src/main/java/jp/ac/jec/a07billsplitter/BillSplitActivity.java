package jp.ac.jec.a07billsplitter;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.widget.EditText;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.snackbar.Snackbar;

import java.util.Objects;

public class BillSplitActivity extends AppCompatActivity {
    private static final String EXTRA_KEY_PARTICIPANTS = "participants";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_bill_split);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // start()経由でしか起動しないため、nullになるのは呼び出し側のバグのとき
        var participants = Objects.requireNonNull(getIntent().getStringArrayExtra(EXTRA_KEY_PARTICIPANTS));

        var txtNumberOfPeople = (TextView) findViewById(R.id.txt_number_of_people);
        var edtTotalAmount = (EditText) findViewById(R.id.edt_total_amount);
        var txtParticipantList = (TextView) findViewById(R.id.txt_participant_list);
        var btnCalc = findViewById(R.id.btn_calc);

        var numberOfPeople = participants.length; // ex) 4
        txtNumberOfPeople.setText("参加者は" + numberOfPeople + "人");

        btnCalc.setOnClickListener(v -> {
            var edtTotalAmountStr = edtTotalAmount.getText().toString(); // ex) "1234"

            // 入力チェック1: 未入力
            if (edtTotalAmountStr.isEmpty()) {
                Snackbar.make(v, "支払い金額を入力してください", Snackbar.LENGTH_SHORT).show();
                return;
            }

            // 入力チェック2: int型に変換できない（桁数が多すぎる場合など）
            final int totalAmount; // ex) 1234
            try {
                totalAmount = Integer.parseInt(edtTotalAmountStr);
            } catch (NumberFormatException e) {
                Snackbar.make(v, "支払い金額は数字で入力してください", Snackbar.LENGTH_SHORT).show();
                return;
            }

            // 入力チェック3: 金額が人数より少ないと、支払額が0円の人が出てしまう
            // ここを通れば合計金額は必ず1以上になる
            if (totalAmount < numberOfPeople) {
                Snackbar.make(v, numberOfPeople + "人で割るには" + numberOfPeople + "円以上を入力してください", Snackbar.LENGTH_SHORT).show();
                return;
            }

            // 入力チェックが済んでいるので、BillSplitterが例外を投げることはない
            var result = BillSplitter.calculateAndFormat(totalAmount, participants);
            txtParticipantList.setText(result);
        });
    }

    static void start(final Context context, final String[] participants) {
        var starter = new Intent(context, BillSplitActivity.class);
        starter.putExtra(EXTRA_KEY_PARTICIPANTS, participants);
        context.startActivity(starter);
    }
}
