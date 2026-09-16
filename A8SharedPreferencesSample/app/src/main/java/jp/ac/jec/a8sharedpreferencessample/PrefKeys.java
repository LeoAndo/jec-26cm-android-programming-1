package jp.ac.jec.a8sharedpreferencessample;

/**
 * SharedPreferences のファイル名とキーをまとめたクラス.
 * 画面が増えてもここを参照すればよいので、Activity 同士が依存し合わずに済む.
 */
public final class PrefKeys {
    public static final String FILE_NAME = "app";
    public static final String INT_VALUE = "int_value";
    public static final String BOOLEAN_VALUE = "boolean_value";
    public static final String FLOAT_VALUE = "float_value";
    public static final String LONG_VALUE = "long_value";
    public static final String STRING_VALUE = "string_value";
    public static final String STRING_SET_VALUE = "string_set_value";

    // 定数をまとめるだけのクラスなので、インスタンス化させない.
    private PrefKeys() {
    }
}
