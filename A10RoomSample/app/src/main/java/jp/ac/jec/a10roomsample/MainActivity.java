package jp.ac.jec.a10roomsample;

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

        var edtId = (EditText) findViewById(R.id.edt_id);
        var edtTitle = (EditText) findViewById(R.id.edt_title);
        var txtItemList = (TextView) findViewById(R.id.txt_item_list);

        // データベースを取得する.
        var itemDao = AppDatabase.getInstance(this).itemDao();

        txtItemList.setText(itemList(itemDao));

        findViewById(R.id.btn_upsert).setOnClickListener(v -> {
            var title = edtTitle.getText().toString();
            if (title.isEmpty()) {
                Snackbar.make(v, "タイトルを入力してください", Snackbar.LENGTH_SHORT).show();
                return;
            }
            // idが空なら新規追加、入っていればそのidのデータを書き換える.
            var item = new Item(title);
            var idStr = edtId.getText().toString();
            if (!idStr.isEmpty()) {
                item.setInternalId(Integer.parseInt(idStr));
            }
            itemDao.upsert(item);
            txtItemList.setText(itemList(itemDao));
            edtId.setText("");
            edtTitle.setText("");
        });

        findViewById(R.id.btn_delete).setOnClickListener(v -> {
            var idStr = edtId.getText().toString();
            if (idStr.isEmpty()) {
                Snackbar.make(v, "削除するidを入力してください", Snackbar.LENGTH_SHORT).show();
                return;
            }
            var item = itemDao.findByInternalId(Integer.parseInt(idStr));
            if (item == null) {
                Snackbar.make(v, "そのidのデータはありません", Snackbar.LENGTH_SHORT).show();
                return;
            }
            itemDao.delete(item);
            txtItemList.setText(itemList(itemDao));
            edtId.setText("");
        });
    }

    /**
     * 保存されているデータをまとめて1つの文字列にする.
     */
    private String itemList(ItemDao itemDao) {
        var text = new StringBuilder();
        for (var item : itemDao.getAll()) {
            text.append(item).append("\n");
        }
        return text.toString();
    }
}
