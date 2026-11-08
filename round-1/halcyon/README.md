# halcyon - Order Lifecycle

`OrderService` tracks working orders for a trading desk. An order is placed with a symbol, side, and quantity, then filled in one or more executions or cancelled while it still has open quantity. The service is in-memory and single-process.

## Domain model

- `Order` has `order_id`, `symbol`, `side` (`buy` or `sell`), `qty`, `filled`, and `status`.
- Status: `OPEN`, `PARTIAL`, `FILLED`, `CANCELLED`.
- `OPEN` and `PARTIAL` are working states. `FILLED` and `CANCELLED` are terminal.

## Lifecycle

| From | Event | To |
| --- | --- | --- |
| `OPEN` | fill less than remaining | `PARTIAL` |
| `OPEN` or `PARTIAL` | fill exactly remaining | `FILLED` |
| `OPEN` or `PARTIAL` | cancel | `CANCELLED` |

Nothing leaves `FILLED` or `CANCELLED`.

## Public API

### `place(symbol, side, qty) -> Order`

Validates side and quantity, then creates an `OPEN` order with `filled = 0`.

### `fill(order_id, qty) -> Order`

Applies a positive execution to a working order and updates `PARTIAL`/`FILLED`.

### `cancel(order_id) -> Order`

Cancels a working order.

### `remaining(order_id) -> int`

Returns the unfilled quantity for a working order, or zero once terminal.

### `open_qty_for(symbol) -> int`

Sums the remaining quantity across working orders for a symbol.
