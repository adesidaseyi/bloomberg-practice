# lumen - Job State Machine

`JobQueue` is a job state machine. A job is `QUEUED`, then `RUNNING` once started. From `RUNNING` it either completes (`DONE`) or fails. A failure retries back to `QUEUED` until the attempt budget is spent, then the job is `FAILED`. The service is in-memory and single-process.

## Domain model

- `Job` has `job_id`, `payload`, `status`, and `attempts`.
- Status: `QUEUED`, `RUNNING`, `DONE`, `FAILED`.
- `max_attempts` is the total number of starts allowed.

## Lifecycle

| From | Event | To |
| --- | --- | --- |
| `QUEUED` | start | `RUNNING` |
| `RUNNING` | complete | `DONE` |
| `RUNNING` | fail, attempts < max | `QUEUED` |
| `RUNNING` | fail, attempts >= max | `FAILED` |

Nothing leaves `DONE` or `FAILED`.

## Public API

### `enqueue(payload) -> Job`

Creates a `QUEUED` job with zero attempts.

### `start(job_id) -> Job`

Starts a queued job and increments its attempt count.

### `complete(job_id) -> Job`

Marks a running job `DONE`.

### `fail(job_id) -> Job`

Retries a running job while budget remains, otherwise marks it `FAILED`.

### `status(job_id) -> JobStatus`

Returns the job's status.
