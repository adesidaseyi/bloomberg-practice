import java.util.*;

public class OrderBook {
    public enum Side { BUY, SELL }
    public enum OrderStatus { OPEN, PARTIAL, FILLED, CANCELLED }

    public static class Order {
        public final String orderId;
        public final Side side;
        public final int priceCents;
        public final int qty;
        public int remaining;
        public OrderStatus status;
        public final int seq;

        Order(String orderId, Side side, int priceCents, int qty, int seq) {
            this.orderId = orderId;
            this.side = side;
            this.priceCents = priceCents;
            this.qty = qty;
            this.remaining = qty;
            this.status = OrderStatus.OPEN;
            this.seq = seq;
        }
    }

    public static class Trade {
        public final String tradeId;
        public final int priceCents;
        public final int qty;
        public final String buyOrderId;
        public final String sellOrderId;

        Trade(String tradeId, int priceCents, int qty, String buyOrderId, String sellOrderId) {
            this.tradeId = tradeId;
            this.priceCents = priceCents;
            this.qty = qty;
            this.buyOrderId = buyOrderId;
            this.sellOrderId = sellOrderId;
        }
    }

    private final Map<String, Order> orders = new LinkedHashMap<>();
    private final Map<String, Order> bids = new LinkedHashMap<>();
    private final Map<String, Order> asks = new LinkedHashMap<>();
    private int seq = 0;
    private int tradeSeq = 0;

    public List<Trade> submit(String side, int priceCents, int qty) {
        Side s;
        if ("buy".equals(side)) s = Side.BUY;
        else if ("sell".equals(side)) s = Side.SELL;
        else throw new IllegalArgumentException("side must be buy or sell");
        if (priceCents <= 0) throw new IllegalArgumentException("price must be positive");
        if (qty <= 0) throw new IllegalArgumentException("qty must be positive");

        Order incoming = new Order("O" + (++seq), s, priceCents, qty, seq);
        orders.put(incoming.orderId, incoming);
        List<Trade> trades = new ArrayList<>();

        Order resting = bestOpposite(s);
        if (resting != null && crosses(incoming, resting)) {
            int level = resting.priceCents;
            while (incoming.remaining > 0) {
                resting = bestOpposite(s);
                if (resting == null || resting.priceCents != level) break;
                if (!crosses(incoming, resting)) break;
                execute(incoming, resting, trades);
            }
        }

        if (incoming.remaining == 0) {
            incoming.status = OrderStatus.FILLED;
        } else {
            if (incoming.remaining < incoming.qty) incoming.status = OrderStatus.PARTIAL;
            book(s).put(incoming.orderId, incoming);
        }
        return trades;
    }

    public Order cancel(String orderId) {
        Order o = order(orderId);
        if (o.status != OrderStatus.OPEN && o.status != OrderStatus.PARTIAL)
            throw new IllegalArgumentException("only open or partially filled orders can be cancelled");
        o.status = OrderStatus.CANCELLED;
        bids.remove(orderId);
        asks.remove(orderId);
        return o;
    }

    public Order order(String orderId) {
        Order o = orders.get(orderId);
        if (o == null) throw new IllegalArgumentException("order not found");
        return o;
    }

    public Integer bestBid() {
        Integer best = null;
        for (Order o : bids.values()) if (best == null || o.priceCents > best) best = o.priceCents;
        return best;
    }

    public Integer bestAsk() {
        Integer best = null;
        for (Order o : asks.values()) if (best == null || o.priceCents < best) best = o.priceCents;
        return best;
    }

    private void execute(Order incoming, Order resting, List<Trade> trades) {
        int take = Math.min(incoming.remaining, resting.remaining);
        String buyId = incoming.side == Side.BUY ? incoming.orderId : resting.orderId;
        String sellId = incoming.side == Side.BUY ? resting.orderId : incoming.orderId;
        trades.add(new Trade("T" + (++tradeSeq), incoming.priceCents, take, buyId, sellId));
        incoming.remaining -= take;
        resting.remaining -= take;
        if (incoming.remaining == 0) incoming.status = OrderStatus.FILLED;
        else incoming.status = OrderStatus.PARTIAL;
        if (resting.remaining == 0) {
            resting.status = OrderStatus.FILLED;
            book(resting.side).remove(resting.orderId);
        } else {
            resting.status = OrderStatus.PARTIAL;
        }
    }

    private Order bestOpposite(Side side) {
        Map<String, Order> b = side == Side.BUY ? asks : bids;
        Order best = null;
        for (Order o : b.values()) {
            if (best == null) { best = o; continue; }
            if (side == Side.BUY) {
                if (o.priceCents < best.priceCents ||
                    (o.priceCents == best.priceCents && o.seq > best.seq)) best = o;
            } else {
                if (o.priceCents > best.priceCents ||
                    (o.priceCents == best.priceCents && o.seq > best.seq)) best = o;
            }
        }
        return best;
    }

    private static boolean crosses(Order incoming, Order resting) {
        if (incoming.side == Side.BUY) return resting.priceCents <= incoming.priceCents;
        return resting.priceCents >= incoming.priceCents;
    }

    private Map<String, Order> book(Side side) {
        return side == Side.BUY ? bids : asks;
    }
}
