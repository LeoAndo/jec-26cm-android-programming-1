package jp.ac.jec.a11vocabularybook;

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

public class CardAddActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_card_add);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        var edtEnglish = (EditText) findViewById(R.id.edt_english);
        var edtJapanese = (EditText) findViewById(R.id.edt_japanese);
        var txtCardList = (TextView) findViewById(R.id.txt_card_list);

        var itemDao = AppDatabase.getInstance(this).itemDao();

        // LiveDataを見張っておくと、単語が増えたときに自動で呼ばれる.
        itemDao.getAll().observe(this, items -> {
            var text = new StringBuilder();
            for (var item : items) {
                text.append(item).append("\n");
            }
            txtCardList.setText(text.toString());
        });

        findViewById(R.id.btn_add).setOnClickListener(v -> {
            var english = edtEnglish.getText().toString();
            var japanese = edtJapanese.getText().toString();
            if (english.isEmpty() || japanese.isEmpty()) {
                Snackbar.make(v, "英単語と日本語の両方を入力してください", Snackbar.LENGTH_SHORT).show();
                return;
            }
            if (itemDao.countByEnglish(english) > 0) {
                Snackbar.make(v, "すでに登録されている単語です", Snackbar.LENGTH_SHORT).show();
                return;
            }
            // 一覧を出し直す処理は書かない. LiveDataが自動で知らせてくれる.
            itemDao.upsert(new Item(english, japanese));
            edtEnglish.setText("");
            edtJapanese.setText("");
        });
    }

    /**
     * この画面を開く.
     */
    static void start(final Context context) {
        var starter = new Intent(context, CardAddActivity.class);
        context.startActivity(starter);
    }
}
