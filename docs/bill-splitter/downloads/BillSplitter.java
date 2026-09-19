package jp.ac.jec.a07billsplitter;

import android.icu.text.NumberFormat;

import androidx.annotation.CheckResult;
import androidx.annotation.IntRange;
import androidx.annotation.NonNull;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

/**
 * できるだけ全員の支払額を均等にする
 *
 * <pre>
 *     {@code
 *     var participants = new String[]{"鈴木一郎", "鈴木二郎", "鈴木三郎"};
 *     var result = BillSplitter.calculateAndFormat(1234, participants);
 *     // result -> "鈴木一郎: ￥411\n鈴木二郎: ￥411\n鈴木三郎: ￥412\n合計: ￥1,234"
 *     }
 * </pre>
 * <p>
 * このクラスは計算だけを担当し、画面に出すメッセージは持たない。
 * ユーザーの入力ミス（未入力・金額が少なすぎる等）は呼び出し側の画面でチェックすること。
 * ここで投げる {@link IllegalArgumentException} は「プログラムの不具合」を知らせるためのもの。
 * <p>
 * メソッドに付いている注釈はAndroid Studioへのヒント。
 * {@code @NonNull} はnullを渡す（返す）とNG、{@code @IntRange} は範囲外の値を渡すとNG、
 * {@code @CheckResult} は戻り値を使わずに捨てるとNG、という意味で、それぞれ警告が表示される。
 */
final class BillSplitter {

    /**
     * 金額の表示に使うロケール。
     * 引数なしの {@code getCurrencyInstance()} は端末の言語設定に従うため、
     * 英語(US)端末では "$411.00" のように小数第2位まで表示されてしまう。
     * この計算は「1円単位」で行っているので、円に固定して表示のズレを防ぐ。
     */
    private static final Locale CURRENCY_LOCALE = Locale.JAPAN;

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
     * <p>
     * 合計金額が人数より少ない場合は支払額が0円の人が出る ex) splitBill(2, 5) -> {1, 1, 0, 0, 0}
     *
     * @param totalAmount    合計金額 ex) 1234
     * @param numberOfPeople 人数 ex) 4
     * @return 各人の支払額リスト（変更可能なリスト） ex) {309, 309, 308, 308}
     * @throws IllegalArgumentException 参加者が2人未満の場合、合計金額が1未満の場合
     */
    @NonNull
    @CheckResult
    private static List<Integer> splitBill(
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
     * @param totalAmount  合計金額 ex) 1234
     * @param participants 参加者リスト ex) {"鈴木一郎", "鈴木二郎", "鈴木三郎"}
     * @return 表示用文字列 ex) "鈴木一郎: ￥411\n鈴木二郎: ￥411\n鈴木三郎: ￥412\n合計: ￥1,234"
     * @throws IllegalArgumentException 参加者が2人未満の場合、合計金額が1未満の場合
     */
    @NonNull
    @CheckResult
    static String calculateAndFormat(@IntRange(from = 1) final int totalAmount, @NonNull final String[] participants) {
        var currencyInstance = NumberFormat.getCurrencyInstance(CURRENCY_LOCALE);

        // splitBillの戻り値をそのまま並び替えると、splitBill側の作り方に依存してしまう
        // （変更できないリストを返すようになった瞬間に落ちる）ので、コピーしてから並び替える
        var payments = new ArrayList<>(splitBill(totalAmount, participants.length));

        // paymentsをシャッフルすることで、先頭から順に1円ずつ追加する順番を変える
        Collections.shuffle(payments);

        var result = new StringBuilder();
        var total = 0; // 支払額の合計（totalAmountと一致するかの検算用）
        for (var i = 0; i < payments.size(); i++) {
            var payment = payments.get(i);
            total += payment;
            result.append(participants[i]).append(": ").append(currencyInstance.format(payment)).append("\n");
        }
        result.append("合計: ").append(currencyInstance.format(total));
        return result.toString();
    }
}
