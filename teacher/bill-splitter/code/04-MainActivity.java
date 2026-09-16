package jp.ac.jec.a07billsplitter;

import android.os.Bundle;
import android.widget.EditText;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.snackbar.Snackbar;

import java.util.ArrayList;

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

        var participants = new ArrayList<String>();

        var edtParticipantName = (EditText) findViewById(R.id.edt_participant_name);
        var txtParticipantList = (TextView) findViewById(R.id.txt_participant_list);
        var btnAdd = findViewById(R.id.btn_add);
        var btnBillSplit = findViewById(R.id.btn_bill_split);

        btnAdd.setOnClickListener(v -> {
            var participantName = edtParticipantName.getText().toString();
            if (participantName.isEmpty()) {
                Snackbar.make(v, "参加者名を入力してください", Snackbar.LENGTH_SHORT).show();
                return;
            }
            if (participants.contains(participantName)) {
                Snackbar.make(v, "参加者名が重複しています", Snackbar.LENGTH_SHORT).show();
                return;
            }

            participants.add(participantName);
            txtParticipantList.append(participantName + "\n");
            edtParticipantName.setText("");
        });
    }
}