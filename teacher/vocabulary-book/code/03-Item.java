package jp.ac.jec.a11vocabularybook;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity
public class Item {
    @PrimaryKey(autoGenerate = true)
    private int internalId;

    @NonNull
    private String english;

    @NonNull
    private String japanese;

    public Item(@NonNull String english, @NonNull String japanese) {
        this.english = english;
        this.japanese = japanese;
    }

    public int getInternalId() {
        return internalId;
    }

    public void setInternalId(int internalId) {
        this.internalId = internalId;
    }

    @NonNull
    public String getEnglish() {
        return english;
    }

    public void setEnglish(@NonNull String english) {
        this.english = english;
    }

    @NonNull
    public String getJapanese() {
        return japanese;
    }

    public void setJapanese(@NonNull String japanese) {
        this.japanese = japanese;
    }

    @Override
    public String toString() {
        return english + " : " + japanese;
    }
}
