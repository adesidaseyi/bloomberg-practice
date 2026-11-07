from __future__ import annotations
import unittest
from dataclasses import dataclass
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Job:
    job_id: str
    payload: str
    status: JobStatus
    attempts: int


class JobQueue:
    """A job state machine. A job is QUEUED, then RUNNING once started. From
    RUNNING it either completes (DONE) or fails. A failure retries (back to
    QUEUED) until the attempt budget is spent, then the job is FAILED."""

    def __init__(self, max_attempts: int = 2) -> None:
        # Initialize the queue state and retry limits for future jobs.
        self._jobs: dict[str, Job] = {}
        self._max = max_attempts
        self._seq = 0

    def enqueue(self, payload: str) -> Job:
        # Add a new job to the queue and assign it a unique job ID.
        self._seq += 1
        jid = f"J{self._seq}"
        job = Job(jid, payload, JobStatus.QUEUED, 0)
        self._jobs[jid] = job
        return job

    #  jobs that retry one time too many
    def start(self, job_id: str) -> Job:
        # Start only queued or failed jobs that still have retry budget remaining.
        job = self._get(job_id)
        if job.status not in (JobStatus.QUEUED, JobStatus.FAILED):
            raise ValueError("only queued or failed jobs can start")
        if job.attempts >= self._max:
            raise ValueError("job has exceeded max attempts")
        job.status = JobStatus.RUNNING
        job.attempts += 1
        return job

     # jobs completed while not running
    def complete(self, job_id: str) -> Job:
        # Mark a running job as finished successfully.
        job = self._get(job_id)
        if job.status != JobStatus.RUNNING:
            raise ValueError("only running jobs can complete")
        job.status = JobStatus.DONE
        return job

    def fail(self, job_id: str) -> Job:
        # Retry a failed run or permanently fail it once the retry budget is exhausted.
        job = self._get(job_id)
        if job.status != JobStatus.RUNNING:
            raise ValueError("only running jobs can fail")
        if job.attempts <= self._max:
            job.status = JobStatus.QUEUED
        else:
            job.status = JobStatus.FAILED
        return job

    def status(self, job_id: str) -> JobStatus:
        # Return the current status for a given job ID.
        return self._get(job_id).status

    def _get(self, job_id: str) -> Job:
        # Look up a job by ID and raise if it does not exist.
        job = self._jobs.get(job_id)
        if job is None:
            raise ValueError("job not found")
        return job


class TestJobQueue(unittest.TestCase):
    def test_start_rejects_jobs_that_exceeded_max_attempts(self) -> None:
        queue = JobQueue(max_attempts=2)
        job = queue.enqueue("payload")
        job.status = JobStatus.FAILED
        job.attempts = 2

        with self.assertRaises(ValueError):
            queue.start(job.job_id)

    def test_start_rejects_jobs_not_in_eligible_states(self) -> None:
        queue = JobQueue(max_attempts=2)
        job = queue.enqueue("payload")
        queue.start(job.job_id)
        queue.complete(job.job_id)

        with self.assertRaises(ValueError):
            queue.start(job.job_id)

    def test_start_rejects_running_job(self) -> None:
        queue = JobQueue()
        job = queue.enqueue("payload")
        queue.start(job.job_id)

        with self.assertRaises(ValueError):
            queue.start(job.job_id)

    def test_start_rejects_done_job(self) -> None:
        queue = JobQueue()
        job = queue.enqueue("payload")
        queue.start(job.job_id)
        queue.complete(job.job_id)

        with self.assertRaises(ValueError):
            queue.start(job.job_id)

    def test_complete_rejects_jobs_not_running(self) -> None:
        for status in (JobStatus.QUEUED, JobStatus.DONE, JobStatus.FAILED):
            with self.subTest(status=status):
                queue = JobQueue()
                job = queue.enqueue("payload")
                job.status = status

                with self.assertRaises(ValueError):
                    queue.complete(job.job_id)


if __name__ == "__main__":
    import unittest

    unittest.main()
