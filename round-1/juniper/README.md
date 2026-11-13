# juniper - Trade Settlement

`SettlementService` tracks executed trades until they settle or fail. The service
is in-memory, single-process, and takes an injected clock so settlement dates are
deterministic in tests.

## Domain model

A `Trade` is marked by properties such as its `trade_id`, the `account_id`, `symbol`, `qty`, `status`, etc.

A trade's notional is `qty * price_cents`.

## Lifecycle

| From | Event | To |
| --- | --- | --- |
| `PENDING` | settle | `SETTLED` |
| `PENDING` | fail | `FAILED` |

Out of scope: redesigning the component, changing the public API, or adding
features the specification does not describe.

Time budget: about 35 minutes.
