from __future__ import annotations
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
        self._jobs: dict[str, Job] = {}
        self._max = max_attempts
        self._seq = 0

    def enqueue(self, payload: str) -> Job:
        self._seq += 1
        jid = f"J{self._seq}"
        job = Job(jid, payload, JobStatus.QUEUED, 0)
        self._jobs[jid] = job
        return job

    def start(self, job_id: str) -> Job:
        job = self._get(job_id)
        job.status = JobStatus.RUNNING
        job.attempts += 1
        return job

    def complete(self, job_id: str) -> Job:
        job = self._get(job_id)
        job.status = JobStatus.DONE
        return job

    def fail(self, job_id: str) -> Job:
        job = self._get(job_id)
        if job.attempts <= self._max:
            job.status = JobStatus.QUEUED
        else:
            job.status = JobStatus.FAILED
        return job

    def status(self, job_id: str) -> JobStatus:
        return self._get(job_id).status

    def _get(self, job_id: str) -> Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise ValueError("job not found")
        return job
