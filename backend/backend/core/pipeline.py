import shutil
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from backend.config import settings
from backend.core import audio, downloader, validators
from backend.core.errors import TranscriberError
from backend.core.exporter import write_json, write_srt, write_txt
from backend.core.history import HistoryItem, history_store
from backend.core.transcriber import TranscriptionResult, transcribe_audio

StageCallback = Callable[[str, str], None]  # (status, message) -> None


@dataclass
class URLSource:
    url: str


@dataclass
class FileSource:
    path: Path
    original_name: str


Source = URLSource | FileSource


def _noop_stage(_status: str, _message: str) -> None:
    pass


def run_pipeline(
    job_id: str,
    source: Source,
    *,
    cancel_event: threading.Event | None = None,
    on_stage: StageCallback = _noop_stage,
    output_dir: Path | None = None,
) -> TranscriptionResult:
    cancel_event = cancel_event or threading.Event()
    output_dir = output_dir or (settings.output_dir / job_id)
    job_temp_dir = settings.temp_dir / job_id
    job_temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        if isinstance(source, URLSource):
            validators.validate_instagram_url(source.url)

            on_stage("downloading", "Downloading...")
            download_result = downloader.download_media(
                source.url,
                job_temp_dir,
                settings.cookies_file,
                cancel_event,
                on_progress=lambda msg: on_stage("downloading", msg),
            )
            raw_audio_path = download_result.audio_path
            title = download_result.title
            source_label = source.url
            source_type = "url"
        else:
            raw_audio_path = source.path
            title = source.original_name
            source_label = source.original_name
            source_type = "file"

        on_stage("extracting_audio", "Extracting audio...")
        normalized_path = job_temp_dir / "audio_16k.wav"
        audio.normalize_to_wav16k_mono(raw_audio_path, normalized_path)

        on_stage("transcribing", "Transcribing...")
        result = transcribe_audio(
            normalized_path,
            settings.model_size,
            settings.device,
            settings.compute_type,
            cancel_event,
        )

        on_stage("exporting", "Exporting...")
        created_at = datetime.now(timezone.utc).isoformat()
        write_txt(result, output_dir / "transcript.txt")
        write_srt(result, output_dir / "subtitles.srt")
        write_json(result, output_dir / "transcript.json", source=source_label, title=title, created_at=created_at)

        history_store.add_entry(
            HistoryItem(
                id=job_id,
                source_type=source_type,
                source=source_label,
                title=title,
                created_at=created_at,
                duration=result.duration,
                word_count=result.word_count,
                language=result.language,
            )
        )

        on_stage("completed", "Done.")
        return result
    except TranscriberError:
        raise
    except Exception as exc:  # noqa: BLE001 - single boundary that wraps any unexpected failure
        raise TranscriberError(f"Unexpected error — {exc}") from exc
    finally:
        shutil.rmtree(job_temp_dir, ignore_errors=True)
