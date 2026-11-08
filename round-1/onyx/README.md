# onyx - Access Token Store

`TokenStore` issues short-lived access tokens. A token is valid while it is `ACTIVE` and unexpired. It can be refreshed to extend its life, or revoked. The service is in-memory, single-process, and clock-injected.

## Domain model

- `Token` has `token_id`, `user_id`, `status`, and `expires_at`.
- Status: `ACTIVE`, `REVOKED`.
- An expired token still has `ACTIVE` status in this model, but it is invalid. Expiry is evaluated against the clock.

## Lifecycle

| From | Event | To |
| --- | --- | --- |
| `ACTIVE` | refresh, unexpired | `ACTIVE` with a new expiry |
| `ACTIVE` | revoke, unexpired | `REVOKED` |
| `ACTIVE` | TTL reached | expired (stored `ACTIVE`, invalid) |

Nothing leaves `REVOKED`.

## Public API

### `issue(user_id) -> Token`

Creates an `ACTIVE` token with `expires_at = now + ttl`.

### `validate(token_id) -> bool`

Reports whether the token exists, is `ACTIVE`, and is unexpired.

### `refresh(token_id) -> Token`

Extends an active, unexpired token from the current time.

### `revoke(token_id) -> Token`

Revokes an active, unexpired token.
