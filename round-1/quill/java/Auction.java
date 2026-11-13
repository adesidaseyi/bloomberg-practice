import java.util.function.DoubleSupplier;

public class Auction {
    public enum Status { OPEN, CLOSED }

    public static class Bid {
        public final String bidId;
        public final String bidderId;
        public final int amountCents;

        Bid(String bidId, String bidderId, int amountCents) {
            this.bidId = bidId;
            this.bidderId = bidderId;
            this.amountCents = amountCents;
        }
    }

    private final int reserve;
    private final double closesAt;
    private final DoubleSupplier clock;
    private Status status = Status.OPEN;
    private Bid highest = null;
    private int seq = 0;

    public Auction(int reserveCents, double closesAt) {
        this(reserveCents, closesAt, null);
    }

    public Auction(int reserveCents, double closesAt, DoubleSupplier clock) {
        if (reserveCents < 0) throw new IllegalArgumentException("reserve must be non-negative");
        this.reserve = reserveCents;
        this.closesAt = closesAt;
        this.clock = clock != null ? clock : () -> System.nanoTime() / 1_000_000_000.0;
    }

    public Bid bid(String bidderId, int cents) {
        if (cents <= 0) throw new IllegalArgumentException("bid amount must be positive");
        Bid b = new Bid("B" + (++seq), bidderId, cents);
        highest = b;
        return b;
    }

    public Status status() {
        refresh();
        return status;
    }

    public Bid highestBid() { return highest; }

    public Bid winner() {
        refresh();
        return status == Status.CLOSED ? highest : null;
    }

    private void refresh() {
        if (status == Status.OPEN && clock.getAsDouble() >= closesAt) {
            status = Status.CLOSED;
        }
    }
}
