# cobalt - Wallet Authorization Holds

`WalletService` is a wallet with authorization holds. Funds are authorized (reserved), then either captured (settled out of the balance) or voided (released). All amounts are integer cents. The service is in-memory and single-process.

## Domain model

- `Hold` has `hold_id`, `account_id`, `amount`, and `status`.
- Status: `HELD`, `CAPTURED`, `VOIDED`.
- An account has a raw balance and an available amount. Available is the balance minus active holds.

## Lifecycle

| From | Event | To |
| --- | --- | --- |
| `HELD` | capture | `CAPTURED` |
| `HELD` | void | `VOIDED` |

Nothing leaves `CAPTURED` or `VOIDED`.

## Public API

### `open_account(account_id, cents) -> None`

Creates an account with a non-negative integer-cent balance.

### `balance(account_id) -> int`

Returns the raw balance.

### `available(account_id) -> int`

Returns the balance minus the sum of active `HELD` amounts.

### `authorize(account_id, cents) -> Hold`

Reserves funds if the amount is positive and no more than available.

### `capture(hold_id) -> Hold`

Settles a held authorization exactly once, reducing the balance.

### `void(hold_id) -> Hold`

Releases a held authorization without touching the balance.
