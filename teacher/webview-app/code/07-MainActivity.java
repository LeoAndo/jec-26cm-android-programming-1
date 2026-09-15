package jp.ac.jec.a04webviewapp;

import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.CheckBox;

import androidx.activity.EdgeToEdge;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {
    private WebView webView;

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

        webView = findViewById(R.id.webView);
        var checkBox = (CheckBox) findViewById(R.id.checkBox);

        webView.setWebViewClient(new WebViewClient());
        webView.getSettings().setJavaScriptEnabled(checkBox.isChecked());

        checkBox.setOnCheckedChangeListener((buttonView, isChecked) -> {
            webView.getSettings().setJavaScriptEnabled(isChecked);
            webView.reload();
        });

        webView.getSettings().setBuiltInZoomControls(true);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        for (var menuItem : AppMenuItem.values()) {
            menu.add(Menu.NONE, menuItem.ordinal(), Menu.NONE, menuItem.getTitle());
        }
        return true; // trueを指定し、メニューを表示する
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        var appMenuItem = AppMenuItem.values()[item.getItemId()];
        webView.loadUrl(appMenuItem.getUrl());
        return true; // trueを指定し、イベントを消費して処理を終了する
    }
}
