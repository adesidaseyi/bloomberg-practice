# pike - Document Approval Workflow

`ApprovalService` is a document approval workflow. A submitted document is `PENDING`, and from there it can be approved, rejected, or withdrawn by its author. Those decisions are terminal. The service is in-memory and single-process.

## Domain model

- `Document` has `doc_id`, `title`, and `status`.
- Status: `PENDING`, `APPROVED`, `REJECTED`, `WITHDRAWN`.
- `PENDING` is the only non-terminal state.

## Lifecycle

| From | Event | To |
| --- | --- | --- |
| `PENDING` | approve | `APPROVED` |
| `PENDING` | reject | `REJECTED` |
| `PENDING` | withdraw | `WITHDRAWN` |

Nothing leaves `APPROVED`, `REJECTED`, or `WITHDRAWN`.

## Public API

### `submit(title) -> Document`

Creates a `PENDING` document.

### `approve(doc_id) -> Document`

Approves a pending document.

### `reject(doc_id) -> Document`

Rejects a pending document.

### `withdraw(doc_id) -> Document`

Withdraws a pending document.

### `status(doc_id) -> DocStatus`

Returns the document's current status.

### `pending_count() -> int`

Counts documents that are currently `PENDING`.
