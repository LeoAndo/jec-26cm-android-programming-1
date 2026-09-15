package jp.ac.jec.a06screentransitionsample;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.IntentCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.ArrayList;
import java.util.Arrays;

public class TestActivity extends AppCompatActivity {
    private static final String EXTRA_KEY_INT_VALUE = "intValue";
    private static final String EXTRA_KEY_LONG_VALUE = "longValue";
    private static final String EXTRA_KEY_FLOAT_VALUE = "floatValue";
    private static final String EXTRA_KEY_DOUBLE_VALUE = "doubleValue";
    private static final String EXTRA_KEY_BOOLEAN_VALUE = "booleanValue";
    private static final String EXTRA_KEY_CHAR_VALUE = "charValue";
    private static final String EXTRA_KEY_STRING_VALUE = "stringValue";

    private static final String EXTRA_KEY_INT_ARRAY_VALUE = "intArrayValue";
    private static final String EXTRA_KEY_LONG_ARRAY_VALUE = "longArrayValue";
    private static final String EXTRA_KEY_FLOAT_ARRAY_VALUE = "floatArrayValue";
    private static final String EXTRA_KEY_DOUBLE_ARRAY_VALUE = "doubleArrayValue";
    private static final String EXTRA_KEY_BOOLEAN_ARRAY_VALUE = "booleanArrayValue";
    private static final String EXTRA_KEY_CHAR_ARRAY_VALUE = "charArrayValue";
    private static final String EXTRA_KEY_STRING_ARRAY_VALUE = "stringArrayValue";

    private static final String EXTRA_KEY_INTEGER_ARRAY_LIST_VALUE = "integerArrayListValue";
    private static final String EXTRA_KEY_STRING_ARRAY_LIST_VALUE = "stringArrayListValue";

    private static final String EXTRA_KEY_PERSON = "person";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_test);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        var intValue = getIntent().getIntExtra(EXTRA_KEY_INT_VALUE, 0);
        var longValue = getIntent().getLongExtra(EXTRA_KEY_LONG_VALUE, 0);
        var floatValue = getIntent().getFloatExtra(EXTRA_KEY_FLOAT_VALUE, 0);
        var doubleValue = getIntent().getDoubleExtra(EXTRA_KEY_DOUBLE_VALUE, 0);
        var booleanValue = getIntent().getBooleanExtra(EXTRA_KEY_BOOLEAN_VALUE, false);
        var charValue = getIntent().getCharExtra(EXTRA_KEY_CHAR_VALUE, ' ');
        var stringValue = getIntent().getStringExtra(EXTRA_KEY_STRING_VALUE);
        Log.d("TestActivity", "intValue: " + intValue);
        Log.d("TestActivity", "longValue: " + longValue);
        Log.d("TestActivity", "floatValue: " + floatValue);
        Log.d("TestActivity", "doubleValue: " + doubleValue);
        Log.d("TestActivity", "booleanValue: " + booleanValue);
        Log.d("TestActivity", "charValue: " + charValue);
        Log.d("TestActivity", "stringValue: " + stringValue);

        var intArrayValue = getIntent().getIntArrayExtra(EXTRA_KEY_INT_ARRAY_VALUE);
        var longArrayValue = getIntent().getLongArrayExtra(EXTRA_KEY_LONG_ARRAY_VALUE);
        var floatArrayValue = getIntent().getFloatArrayExtra(EXTRA_KEY_FLOAT_ARRAY_VALUE);
        var doubleArrayValue = getIntent().getDoubleArrayExtra(EXTRA_KEY_DOUBLE_ARRAY_VALUE);
        var booleanArrayValue = getIntent().getBooleanArrayExtra(EXTRA_KEY_BOOLEAN_ARRAY_VALUE);
        var charArrayValue = getIntent().getCharArrayExtra(EXTRA_KEY_CHAR_ARRAY_VALUE);
        var stringArrayValue = getIntent().getStringArrayExtra(EXTRA_KEY_STRING_ARRAY_VALUE);
        Log.d("TestActivity", "intArrayValue: " + Arrays.toString(intArrayValue));
        Log.d("TestActivity", "longArrayValue: " + Arrays.toString(longArrayValue));
        Log.d("TestActivity", "floatArrayValue: " + Arrays.toString(floatArrayValue));
        Log.d("TestActivity", "doubleArrayValue: " + Arrays.toString(doubleArrayValue));
        Log.d("TestActivity", "booleanArrayValue: " + Arrays.toString(booleanArrayValue));
        Log.d("TestActivity", "charArrayValue: " + Arrays.toString(charArrayValue));
        Log.d("TestActivity", "stringArrayValue: " + Arrays.toString(stringArrayValue));

        var integerArrayListValue = getIntent().getIntegerArrayListExtra(EXTRA_KEY_INTEGER_ARRAY_LIST_VALUE);
        var stringArrayListValue = getIntent().getStringArrayListExtra(EXTRA_KEY_STRING_ARRAY_LIST_VALUE);
        Log.d("TestActivity", "integerArrayListValue: " + integerArrayListValue);
        Log.d("TestActivity", "stringArrayListValue: " + stringArrayListValue);

        var person = IntentCompat.getSerializableExtra(getIntent(), EXTRA_KEY_PERSON, Person.class);
        Log.d("TestActivity", "person: " + person);
    }

    // startメソッドはAndroid Studioのコードテンプレートを利用して作成できる！
    static void start(Context context, int intValue, long longValue, float floatValue,
                      double doubleValue, boolean booleanValue, char charValue, String stringValue) {
        var intent = new Intent(context, TestActivity.class);
        intent.putExtra(EXTRA_KEY_INT_VALUE, intValue);
        intent.putExtra(EXTRA_KEY_LONG_VALUE, longValue);
        intent.putExtra(EXTRA_KEY_FLOAT_VALUE, floatValue);
        intent.putExtra(EXTRA_KEY_DOUBLE_VALUE, doubleValue);
        intent.putExtra(EXTRA_KEY_BOOLEAN_VALUE, booleanValue);
        intent.putExtra(EXTRA_KEY_CHAR_VALUE, charValue);
        intent.putExtra(EXTRA_KEY_STRING_VALUE, stringValue);
        context.startActivity(intent);
    }

    static void start(Context context, int[] intArrayValue, long[] longArrayValue,
                      float[] floatArrayValue, double[] doubleArrayValue,
                      boolean[] booleanArrayValue, char[] charArrayValue, String[] stringArrayValue) {
        var intent = new Intent(context, TestActivity.class);
        intent.putExtra(EXTRA_KEY_INT_ARRAY_VALUE, intArrayValue);
        intent.putExtra(EXTRA_KEY_LONG_ARRAY_VALUE, longArrayValue);
        intent.putExtra(EXTRA_KEY_FLOAT_ARRAY_VALUE, floatArrayValue);
        intent.putExtra(EXTRA_KEY_DOUBLE_ARRAY_VALUE, doubleArrayValue);
        intent.putExtra(EXTRA_KEY_BOOLEAN_ARRAY_VALUE, booleanArrayValue);
        intent.putExtra(EXTRA_KEY_CHAR_ARRAY_VALUE, charArrayValue);
        intent.putExtra(EXTRA_KEY_STRING_ARRAY_VALUE, stringArrayValue);
        context.startActivity(intent);
    }

    static void start(Context context, ArrayList<Integer> integerArrayListValue, ArrayList<String> stringArrayListValue) {
        var intent = new Intent(context, TestActivity.class);
        intent.putIntegerArrayListExtra(EXTRA_KEY_INTEGER_ARRAY_LIST_VALUE, integerArrayListValue);
        intent.putStringArrayListExtra(EXTRA_KEY_STRING_ARRAY_LIST_VALUE, stringArrayListValue);
        context.startActivity(intent);
    }

    static void start(Context context, Person person) {
        var intent = new Intent(context, TestActivity.class);
        intent.putExtra(EXTRA_KEY_PERSON, person);
        context.startActivity(intent);
    }
}