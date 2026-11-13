import java.util.*;
import java.util.function.DoubleSupplier;

public class Settlement {
    public enum TradeStatus { PENDING, SETTLED, FAILED }

    public static class Trade {
        public final String tradeId;
        public final String accountId;
        public final String symbol;
        public final int qty;
        public final int priceCents;
        public final double settleOn;
        public TradeStatus status;

        Trade(String tradeId, String accountId, String symbol, int qty,
              int priceCents, double settleOn) {
            this.tradeId = tradeId;
            this.accountId = accountId;
            this.symbol = symbol;
            this.qty = qty;
            this.priceCents = priceCents;
            this.settleOn = settleOn;
            this.status = TradeStatus.PENDING;
        }
    }

    private final Map<String, Trade> trades = new LinkedHashMap<>();
    private final DoubleSupplier clock;
    private int seq = 0;

    public Settlement() {
        this(null);
    }

    public Settlement(DoubleSupplier clock) {
        this.clock = clock != null ? clock : () -> System.nanoTime() / 1_000_000_000.0;
    }

    public Trade book(String accountId, String symbol, int qty, int priceCents,
                      double settleOn) {
        if (qty <= 0) throw new IllegalArgumentException("qty must be positive");
        if (priceCents <= 0) throw new IllegalArgumentException("price must be positive");
        Trade t = new Trade("S" + (++seq), accountId, symbol, qty, priceCents, settleOn);
        trades.put(t.tradeId, t);
        return t;
    }

    public Trade settle(String tradeId) {
        Trade t = trade(tradeId);
        if (t.status != TradeStatus.PENDING)
            throw new IllegalArgumentException("only pending trades can settle");
        t.status = TradeStatus.SETTLED;
        return t;
    }

    public Trade fail(String tradeId) {
        Trade t = trade(tradeId);
        t.status = TradeStatus.FAILED;
        return t;
    }

    public int pendingNotional(String accountId) {
        int total = 0;
        for (Trade t : trades.values()) {
            if (t.accountId.equals(accountId)) total += t.qty * t.priceCents;
        }
        return total;
    }

    public Trade trade(String tradeId) {
        Trade t = trades.get(tradeId);
        if (t == null) throw new IllegalArgumentException("trade not found");
        return t;
    }
}
