package jp.ac.jec.a10roomsample;

import android.content.Context;

import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;

@Database(entities = {Item.class}, version = 1, exportSchema = false)
public abstract class AppDatabase extends RoomDatabase {
    private static AppDatabase instance;

    public abstract ItemDao itemDao();

    /**
     * データベースを取得する.
     * 1つだけ作って使い回す書き方をシングルトンという.
     * allowMainThreadQueries()は、読み書きを画面と同じスレッドで行うための指定.
     * 本来は別スレッドで行うが、この授業では扱わない.
     */
    public static AppDatabase getInstance(Context context) {
        if (instance == null) {
            instance = Room.databaseBuilder(context, AppDatabase.class, "app.db")
                    .allowMainThreadQueries()
                    .build();
        }
        return instance;
    }
}
