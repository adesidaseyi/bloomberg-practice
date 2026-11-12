import java.util.function.DoubleSupplier;

public class Breaker {
    public enum State { CLOSED, OPEN, HALF_OPEN }

    private final int threshold;
    private final double cooldown;
    private final DoubleSupplier clock;
    private State state = State.CLOSED;
    private int failures = 0;
    private double openedAt = 0.0;
    private int probes = 0;

    public Breaker() { this(3, 30.0, null); }

    public Breaker(int failureThreshold, double cooldownSeconds) {
        this(failureThreshold, cooldownSeconds, null);
    }

    public Breaker(int failureThreshold, double cooldownSeconds, DoubleSupplier clock) {
        if (failureThreshold <= 0) throw new IllegalArgumentException("failure_threshold must be positive");
        if (cooldownSeconds < 0) throw new IllegalArgumentException("cooldown_seconds must be non-negative");
        this.threshold = failureThreshold;
        this.cooldown = cooldownSeconds;
        this.clock = clock != null ? clock : () -> System.nanoTime() / 1_000_000_000.0;
    }

    public boolean allow() {
        refresh();
        if (state == State.OPEN) return false;
        if (state == State.HALF_OPEN) return true;
        return true;
    }

    public void recordSuccess() {
        if (state == State.HALF_OPEN) {
            state = State.CLOSED;
            openedAt = 0.0;
            failures = 0;
        }
        probes = 0;
    }

    public void recordFailure() {
        if (state == State.HALF_OPEN) {
            state = State.OPEN;
            openedAt = clock.getAsDouble();
            probes = 0;
            return;
        }
        if (state == State.OPEN) return;
        failures++;
        if (failures >= threshold) {
            state = State.OPEN;
            openedAt = clock.getAsDouble();
        }
    }

    public State state() {
        refresh();
        return state;
    }

    public int failureCount() { return failures; }

    public void reset() {
        state = State.CLOSED;
        openedAt = 0.0;
        probes = 0;
    }

    private void refresh() {
        if (state == State.OPEN && clock.getAsDouble() - openedAt >= cooldown) {
            state = State.HALF_OPEN;
            probes = 0;
        }
    }
}
