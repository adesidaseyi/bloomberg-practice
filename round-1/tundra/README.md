# tundra - LRU Cache with TTL

`LRUCache` is a capacity-bounded cache with per-entry TTL and least-recently-used eviction. A read counts as a use, expired entries are not returned, and expired entries do not count toward size. The service is in-memory, single-process, and clock-injected.

## Domain model

- Each entry has a value and an `expires_at` instant.
- The cache has a fixed capacity and a per-entry TTL.
- The least-recently-used end is evicted first; a successful read makes an entry most-recently-used.

## Lifecycle

```text
put -> live entry (expires at now + ttl)
get -> value if live, and the entry becomes most-recently-used
over capacity -> evict the least-recently-used live entry
```

## Public API

### `put(key, value) -> None`

Inserts or updates an entry, resets its expiry, and marks it most-recently-used.

### `get(key) -> value or None`

Returns a live value; a live read marks the entry most-recently-used. Expired keys return `None`.

### `size() -> int`

Counts live entries only.
