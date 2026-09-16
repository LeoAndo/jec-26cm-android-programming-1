package jp.ac.jec.a07billsplitter;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.widget.EditText;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

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
    }

    static void start(@NonNull final Context context, @NonNull final String[] participants) {
        var starter = new Intent(context, BillSplitActivity.class);
        starter.putExtra(EXTRA_KEY_PARTICIPANTS, participants);
        context.startActivity(starter);
    }
}
