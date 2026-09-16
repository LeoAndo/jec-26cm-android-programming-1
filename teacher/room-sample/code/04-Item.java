package jp.ac.jec.a10roomsample;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity
public class Item {
    @PrimaryKey(autoGenerate = true)
    private int internalId;

    @NonNull
    private String title;

    public Item(@NonNull String title) {
        this.title = title;
    }

    public int getInternalId() {
        return internalId;
    }

    public void setInternalId(int internalId) {
        this.internalId = internalId;
    }

    @NonNull
    public String getTitle() {
        return title;
    }

    public void setTitle(@NonNull String title) {
        this.title = title;
    }

    @Override
    public String toString() {
        return "Item{" +
                "internalId=" + internalId +
                ", title='" + title + '\'' +
                '}';
    }
}
