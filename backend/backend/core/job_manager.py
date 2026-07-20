import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from backend.core.transcriber import TranscriptionResult

JobStatus = Literal[
    "queued",
    "downloading",
    "extracting_audio",
    "transcribing",
    "exporting",
    "completed",
    "failed",
    "cancelling",
    "cancelled",
]

# Coarse, stage-weighted progress — intentionally approximate rather than
# plumbing true byte/frame-level progress from yt-dlp/ffmpeg/whisper to the UI.
_STAGE_PROGRESS: dict[JobStatus, int] = {
    "queued": 0,
    "downloading": 5,
    "extracting_audio": 35,
    "transcribing": 45,
    "exporting": 95,
    "completed": 100,
    "failed": 100,
    "cancelling": 99,
    "cancelled": 100,
}


@dataclass
class JobRecord:
    id: str
    status: JobStatus = "queued"
    stage_message: str = "Queued"
    result: TranscriptionResult | None = None
    error: dict | None = None
    cancel_event: threading.Event = field(default_factory=threading.Event)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def progress_percent(self) -> int:
        return _STAGE_PROGRESS[self.status]


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def create_job(self) -> JobRecord:
        job = JobRecord(id=f"job_{uuid.uuid4().hex[:10]}")
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update_status(self, job_id: str, status: JobStatus, message: str) -> None:
        job = self.get_job(job_id)
        if job is not None:
            job.status = status
            job.stage_message = message

    def set_result(self, job_id: str, result: TranscriptionResult) -> None:
        job = self.get_job(job_id)
        if job is not None:
            job.result = result
            job.status = "completed"
            job.stage_message = "Done."

    def set_error(self, job_id: str, code: str, message: str, status: JobStatus = "failed") -> None:
        job = self.get_job(job_id)
        if job is not None:
            job.status = status
            job.error = {"code": code, "message": message}
            job.stage_message = message

    def request_cancel(self, job_id: str) -> bool:
        job = self.get_job(job_id)
        if job is None or job.status in ("completed", "failed", "cancelled"):
            return False
        job.cancel_event.set()
        job.status = "cancelling"
        return True


job_manager = JobManager()
