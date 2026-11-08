# vesper - Connection Pool

`ConnectionPool` is a fixed-capacity connection pool. `acquire()` hands out an idle connection or opens a new one up to the capacity; `release()` returns one to the idle set. A closed pool accepts no new work. The service is in-memory and single-process.

## Domain model

- `Connection` has `conn_id` and `status`.
- Status: `IN_USE`, `IDLE`.
- The pool has a fixed capacity and a closed flag.

## Lifecycle

```text
(new) -> IN_USE <-> IDLE
close() -> the pool refuses further acquire/release
```

## Public API

### `acquire() -> Connection`

Returns an idle connection or creates a new one while under capacity.

### `release(conn_id) -> Connection`

Returns an in-use connection to the idle set.

### `close() -> None`

Closes the pool and rejects further acquire/release.

### `in_use_count() / idle_count() / size()`

Report the pool's current counts.
