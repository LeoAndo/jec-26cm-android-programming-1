package jp.ac.jec.a07billsplitter;

import android.content.Context;
import android.content.Intent;
import android.icu.text.NumberFormat;
import android.os.Bundle;
import android.widget.EditText;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.snackbar.Snackbar;

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

        var participants = getIntent().getStringArrayExtra(EXTRA_KEY_PARTICIPANTS);
        assert participants != null;

        var numberOfPeople = participants.length; // ex) 4
        ((TextView) findViewById(R.id.txt_number_of_people)).setText("参加者は" + numberOfPeople + "人");

        var currencyInstance = NumberFormat.getCurrencyInstance();
        var currencySymbol = currencyInstance.getCurrency().getSymbol(); // ex) "￥"
        ((TextView) findViewById(R.id.txt_total_amount)).setText("支払額（" + currencySymbol + "）");

        findViewById(R.id.btn_calc).setOnClickListener(v -> {
            var edtTotalAmount = (EditText) findViewById(R.id.edt_total_amount);
            var edtTotalAmountStr = edtTotalAmount.getText().toString(); // ex) "1234"
            if (edtTotalAmountStr.isEmpty()) {
                Snackbar.make(v, "支払い金額を入力してください", Snackbar.LENGTH_SHORT).show();
                return;
            }

            var totalAmount = Integer.parseInt(edtTotalAmountStr); // ex) 1234
            try {
                var result = BillSplitter.calculateAndFormat(totalAmount, participants);
                ((TextView) findViewById(R.id.txt_participant_list)).setText(result);
            } catch (IllegalArgumentException e) {
                var errorMessage = (e.getMessage() != null) ? e.getMessage() : "エラーが発生しました";
                Snackbar.make(v, errorMessage, Snackbar.LENGTH_SHORT).show();
            }
        });
    }

    static void start(@NonNull final Context context, @NonNull final String[] participants) {
        var starter = new Intent(context, BillSplitActivity.class);
        starter.putExtra(EXTRA_KEY_PARTICIPANTS, participants);
        context.startActivity(starter);
    }
}