from pydantic import BaseModel

from backend.core.job_manager import JobStatus


class CreateJobFromUrlRequest(BaseModel):
    url: str


class JobResponse(BaseModel):
    id: str
    status: JobStatus


class JobErrorPayload(BaseModel):
    code: str
    message: str


class JobStatusResponse(BaseModel):
    id: str
    status: JobStatus
    stage_message: str
    progress_percent: int
    error: JobErrorPayload | None = None


class TranscriptWordSchema(BaseModel):
    start: float
    end: float
    word: str


class TranscriptSegmentSchema(BaseModel):
    start: float
    end: float
    text: str
    words: list[TranscriptWordSchema]


class TranscriptResultSchema(BaseModel):
    segments: list[TranscriptSegmentSchema]
    language: str
    language_probability: float
    duration: float
    word_count: int
    text: str
    model_size: str
    device: str


class HistoryItemSchema(BaseModel):
    id: str
    source_type: str
    source: str
    title: str
    created_at: str
    duration: float
    word_count: int
    language: str


class HealthResponse(BaseModel):
    status: str
    ffmpeg: bool
    device: str
    compute_type: str
