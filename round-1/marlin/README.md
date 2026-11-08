# marlin - Inventory Reservations

`InventoryService` reserves stock for a fulfilment system. Units are reserved with a TTL hold, then either committed (shipped) or released back to available stock. Expired holds return their units automatically. The service is in-memory, single-process, and clock-injected.

## Domain model

- `Reservation` has `reservation_id`, `sku`, `qty`, `status`, and `expires_at`.
- Status: `HELD`, `COMMITTED`, `RELEASED`.
- Each SKU has a fixed capacity and an available count. A `HELD` reservation has already reduced available stock.

## Lifecycle

| From | Event | To |
| --- | --- | --- |
| `HELD` | commit | `COMMITTED` |
| `HELD` | release | `RELEASED` |
| `HELD` | TTL reached | `RELEASED` |

Nothing leaves `COMMITTED` or `RELEASED`.

## Public API

### `available(sku) -> int`

Applies due expiry, then returns the units currently available.

### `reserve(sku, qty) -> Reservation`

Applies expiry, validates stock, creates a `HELD` reservation with a TTL, and reduces available.

### `commit(reservation_id) -> Reservation`

Ships a held reservation; it stops being reserved.

### `release(reservation_id) -> Reservation`

Returns a held reservation's units to available stock.

### `reserved_units(sku) -> int`

Reports how many units are currently held for the SKU.
