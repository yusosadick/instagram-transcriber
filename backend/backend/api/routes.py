import asyncio
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.api.schemas import (
    CreateJobFromUrlRequest,
    HealthResponse,
    HistoryItemSchema,
    JobResponse,
    JobStatusResponse,
    TranscriptResultSchema,
)
from backend.config import settings
from backend.core.audio import check_ffmpeg_available
from backend.core.errors import TranscriberError, UnsupportedURLError
from backend.core.history import history_store
from backend.core.job_manager import job_manager
from backend.core.model_manager import select_device_and_compute_type
from backend.core.pipeline import FileSource, URLSource, run_pipeline
from backend.core.validators import validate_instagram_url

router = APIRouter(prefix="/api")

_ALLOWED_EXPORT_FORMATS = {
    "txt": "transcript.txt",
    "srt": "subtitles.srt",
    "json": "transcript.json",
}


def _run_job(job_id: str, source) -> None:
    job = job_manager.get_job(job_id)
    if job is None:
        return

    def on_stage(status: str, message: str) -> None:
        job_manager.update_status(job_id, status, message)

    try:
        result = run_pipeline(job_id, source, cancel_event=job.cancel_event, on_stage=on_stage)
        job_manager.set_result(job_id, result)
    except TranscriberError as exc:
        status = "cancelled" if exc.code == "cancelled" else "failed"
        job_manager.set_error(job_id, exc.code, exc.message, status=status)


@router.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job_from_url(payload: CreateJobFromUrlRequest) -> JobResponse:
    try:
        validate_instagram_url(payload.url)
    except UnsupportedURLError as exc:
        raise HTTPException(
            status_code=400, detail={"code": exc.code, "message": exc.message}
        ) from exc

    job = job_manager.create_job()
    asyncio.create_task(asyncio.to_thread(_run_job, job.id, URLSource(url=payload.url)))
    return JobResponse(id=job.id, status=job.status)


@router.post("/jobs/upload", response_model=JobResponse, status_code=201)
async def create_job_from_upload(file: UploadFile) -> JobResponse:
    if not file.content_type or not (
        file.content_type.startswith("audio/") or file.content_type.startswith("video/")
    ):
        raise HTTPException(status_code=400, detail="Only audio or video files are supported")

    job = job_manager.create_job()
    upload_dir = settings.temp_dir / job.id
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest_path = upload_dir / (file.filename or "upload")
    with dest_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    source = FileSource(path=dest_path, original_name=file.filename or "uploaded file")
    asyncio.create_task(asyncio.to_thread(_run_job, job.id, source))
    return JobResponse(id=job.id, status=job.status)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job id")
    return JobStatusResponse(
        id=job.id,
        status=job.status,
        stage_message=job.stage_message,
        progress_percent=job.progress_percent,
        error=job.error,
    )


@router.post("/jobs/{job_id}/cancel", response_model=JobResponse, status_code=202)
async def cancel_job(job_id: str) -> JobResponse:
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job id")
    if job.status in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=409, detail="Job already terminal")
    job_manager.request_cancel(job_id)
    return JobResponse(id=job.id, status=job.status)


@router.get("/jobs/{job_id}/result", response_model=TranscriptResultSchema)
async def get_job_result(job_id: str) -> TranscriptResultSchema:
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job id")
    if job.status != "completed" or job.result is None:
        raise HTTPException(status_code=409, detail="Job not completed yet")
    result = job.result
    return TranscriptResultSchema(
        segments=[
            {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
                "words": [{"start": w.start, "end": w.end, "word": w.word} for w in seg.words],
            }
            for seg in result.segments
        ],
        language=result.language,
        language_probability=result.language_probability,
        duration=result.duration,
        word_count=result.word_count,
        text=result.text,
        model_size=result.model_size,
        device=result.device,
    )


@router.get("/jobs/{job_id}/download/{fmt}")
async def download_export(job_id: str, fmt: str) -> FileResponse:
    filename = _ALLOWED_EXPORT_FORMATS.get(fmt)
    if filename is None:
        raise HTTPException(status_code=404, detail="Unknown export format")
    path = settings.output_dir / job_id / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)


@router.get("/history", response_model=list[HistoryItemSchema])
async def list_history() -> list[dict]:
    return history_store.list_entries()


@router.delete("/history/{item_id}", status_code=204)
async def delete_history_item(item_id: str) -> None:
    history_store.delete_entry(item_id)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    device, compute_type = select_device_and_compute_type(settings.device)
    return HealthResponse(
        status="ok",
        ffmpeg=check_ffmpeg_available(),
        device=device,
        compute_type=compute_type,
    )
