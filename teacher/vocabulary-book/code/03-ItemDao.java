package jp.ac.jec.a11vocabularybook;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Query;
import androidx.room.Upsert;

import java.util.List;

@Dao
public interface ItemDao {
    @Query("SELECT * FROM item")
    LiveData<List<Item>> getAll();

    @Query("SELECT COUNT(*) FROM item WHERE english = :english")
    int countByEnglish(String english);

    @Upsert
    void upsert(Item item);
}
