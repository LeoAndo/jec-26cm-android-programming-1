package jp.ac.jec.a11vocabularybook;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.snackbar.Snackbar;

import java.util.ArrayList;
import java.util.List;

public class CardActivity extends AppCompatActivity {
    private final List<Item> cardList = new ArrayList<>();
    private int cardIndex;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_card);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        var btnBack = (Button) findViewById(R.id.btn_back);
        var btnNext = (Button) findViewById(R.id.btn_next);
        var btnAnswer = (Button) findViewById(R.id.btn_answer);

        var itemDao = AppDatabase.getInstance(this).itemDao();

        // LiveDataを見張っておくと、単語が増えたときに自動で呼ばれる.
        itemDao.getAll().observe(this, items -> {
            cardList.clear();
            cardList.addAll(items);
            if (cardList.isEmpty()) {
                Snackbar.make(findViewById(R.id.main), "単語がありません", Snackbar.LENGTH_INDEFINITE)
                        .setAction("単語を追加する", v -> {
                            CardAddActivity.start(this);
                        }).show();
                return;
            }
            if (cardIndex > cardList.size() - 1) {
                cardIndex = cardList.size() - 1;
            }
            updateCardView();
        });

        btnBack.setOnClickListener(v -> {
            cardIndex--;
            updateCardView();
        });

        btnNext.setOnClickListener(v -> {
            cardIndex++;
            updateCardView();
        });

        btnAnswer.setOnClickListener(v -> {
            var txtJapanese = (TextView) findViewById(R.id.txt_japanese);
            var isVisible = (txtJapanese.getVisibility() == View.VISIBLE);
            txtJapanese.setVisibility(isVisible ? View.INVISIBLE : View.VISIBLE);
            btnAnswer.setText(isVisible ? "答えを表示する" : "答えを非表示にする");
        });
    }

    /**
     * この画面を開く.
     */
    static void start(final Context context) {
        var starter = new Intent(context, CardActivity.class);
        context.startActivity(starter);
    }

    /**
     * いま表示するカードの内容にそろえる.
     */
    private void updateCardView() {
        var card = cardList.get(cardIndex);
        var txtQuestionNo = (TextView) findViewById(R.id.txt_question_no);
        var txtEnglish = (TextView) findViewById(R.id.txt_english);
        var txtJapanese = (TextView) findViewById(R.id.txt_japanese);
        var btnAnswer = (Button) findViewById(R.id.btn_answer);

        txtQuestionNo.setText((cardIndex + 1) + "問目/全" + cardList.size() + "問中");
        txtEnglish.setText(card.getEnglish());
        txtJapanese.setText(card.getJapanese());

        // カードを変えたら、答えは隠した状態に戻す.
        txtJapanese.setVisibility(View.INVISIBLE);
        btnAnswer.setText("答えを表示する");

        findViewById(R.id.btn_back).setEnabled(cardIndex > 0);
        findViewById(R.id.btn_next).setEnabled(cardIndex < cardList.size() - 1);
    }
}
