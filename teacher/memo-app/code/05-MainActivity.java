package jp.ac.jec.a09memoapp;

import android.os.Bundle;
import android.widget.EditText;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.snackbar.Snackbar;

public class MainActivity extends AppCompatActivity {
    private static final String FILE_NAME = "app";
    private static final String MEMO = "memo";

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


        var txtMemoList = (TextView) findViewById(R.id.txt_memo_list);
        var edtMemo = (EditText) findViewById(R.id.edt_memo);

        var prefs = getSharedPreferences(FILE_NAME, MODE_PRIVATE);

        txtMemoList.setText(prefs.getString(MEMO, ""));

        findViewById(R.id.btn_add).setOnClickListener(v -> {
            var edtMemoStr = edtMemo.getText().toString();
            if (edtMemoStr.isEmpty()) {
                Snackbar.make(v, "メモを入力してください", Snackbar.LENGTH_SHORT).show();
                return;
            }
            txtMemoList.append(edtMemoStr + "\n");
            var edit = prefs.edit();
            edit.putString(MEMO, txtMemoList.getText().toString());
            edit.apply();
            edtMemo.setText("");
        });
    }
}