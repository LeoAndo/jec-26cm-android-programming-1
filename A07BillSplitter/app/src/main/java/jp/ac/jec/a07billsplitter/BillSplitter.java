package jp.ac.jec.a07billsplitter;

import android.icu.text.NumberFormat;

import androidx.annotation.CheckResult;
import androidx.annotation.IntRange;
import androidx.annotation.NonNull;
import androidx.annotation.VisibleForTesting;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * できるだけ全員の支払額を均等にする
 * 学生の進捗状況によってはこのファイルを公開しても良いかもしれない。
 */
final class BillSplitter {

    private BillSplitter() {
    }

    /**
     * 割り勘計算を行う
     *
     * <pre>
     *     {@code
     *     var payments = splitBill(1234, 4);
     *     }
     * </pre>
     *
     * @param totalAmount    合計金額 ex) 1234
     * @param numberOfPeople 人数 ex) 4
     * @return 各人の支払額リスト ex) {309, 309, 308, 308}
     * @throws IllegalArgumentException 参加者が2人未満の場合、合計金額が1未満の場合
     */
    @VisibleForTesting
    @NonNull
    @CheckResult
    static List<Integer> splitBill(
            @IntRange(from = 1) final int totalAmount,
            @IntRange(from = 2) final int numberOfPeople) {
        if (totalAmount < 1) {
            throw new IllegalArgumentException("合計金額は1以上を指定してください");
        }
        if (numberOfPeople < 2) {
            throw new IllegalArgumentException("人数は2人以上を指定してください");
        }

        var payments = new ArrayList<Integer>();

        // 基本金額（切り捨て）
        var baseAmount = totalAmount / numberOfPeople;

        // 全員が基本金額を支払った場合の合計
        var baseTotal = baseAmount * numberOfPeople;

        // 端数金額
        var remainder = totalAmount - baseTotal;

        // 各人の支払額を計算
        for (var i = 0; i < numberOfPeople; i++) {
            // 先頭から順に、端数分を1円ずつ追加
            if (i < remainder) {
                payments.add(baseAmount + 1);
            } else {
                payments.add(baseAmount);
            }
        }

        return payments;
    }

    /**
     * 計算結果を表示用にフォーマットした文字列を返す
     *
     * <pre>
     *     {@code
     *     var  participants = new String[]{"鈴木一郎", "鈴木二郎", "鈴木三郎"};
     *     var result = BillSplitter.calculateAndFormat(totalAmount, participants);
     *     }
     * </pre>
     *
     * @param totalAmount  合計金額 ex) 1234
     * @param participants 参加者リスト ex) {"鈴木一郎", "鈴木二郎", "鈴木三郎"}
     * @return 表示用文字列 ex) "鈴木一郎: ￥411\n鈴木二郎: ￥411\n鈴木三郎: ￥412\n合計: ￥1234"
     */
    @NonNull
    @CheckResult
    static String calculateAndFormat(@IntRange(from = 1) final int totalAmount, @NonNull final String[] participants) {
        var currencyInstance = NumberFormat.getCurrencyInstance();
        var payments = splitBill(totalAmount, participants.length);
        // paymentsをシャッフルすることで、先頭から順に1円ずつ追加する順番を変える
        Collections.shuffle(payments);

        var result = new StringBuilder();
        var total = 0; // debug用
        for (var i = 0; i < payments.size(); i++) {
            var payment = payments.get(i);
            total += payment;
            result.append(participants[i]).append(": ").append(currencyInstance.format(payment)).append("\n");
        }
        result.append("合計: ").append(currencyInstance.format(total));
        return result.toString();
    }
}