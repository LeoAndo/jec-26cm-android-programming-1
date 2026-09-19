package jp.ac.jec.a01helloandroid;

import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

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

        var text = (TextView) findViewById(R.id.text);
        var button = (Button) findViewById(R.id.button);
        var btn1 = (Button) findViewById(R.id.btn1);
        var btn2 = (Button) findViewById(R.id.btn2);

        var string = text.getText().toString();
        Log.d("MainActivity", string);

        button.setOnClickListener(v -> {
            text.setText("Hello, Android!");
            var updateString = text.getText().toString();
            Log.d("MainActivity", updateString);
        });

        btn1.setOnClickListener(v -> {
            var btn1Str = btn1.getText().toString();
            Snackbar.make(v, btn1Str, Snackbar.LENGTH_SHORT).show();
        });
        btn2.setOnClickListener(v -> {
            var btn2Str = btn2.getText().toString();
            Toast.makeText(this, btn2Str, Toast.LENGTH_SHORT).show();
        });
    }
}