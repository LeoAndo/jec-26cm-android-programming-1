package jp.ac.jec.a10roomsample;

import androidx.annotation.Nullable;
import androidx.room.Dao;
import androidx.room.Delete;
import androidx.room.Query;
import androidx.room.Upsert;

import java.util.List;

@Dao
public interface ItemDao {
    @Query("SELECT * FROM item")
    List<Item> getAll();

    @Nullable
    @Query("SELECT * FROM item WHERE internalId = :internalId")
    Item findByInternalId(int internalId);

    @Upsert
    void upsert(Item item);

    @Delete
    void delete(Item item);
}
