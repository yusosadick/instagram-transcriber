import threading
from dataclasses import dataclass, field
from pathlib import Path

from backend.core.errors import JobCancelledError, TranscriptionError
from backend.core.model_manager import get_model, resolve_compute_type, resolve_model_size, select_device_and_compute_type


@dataclass
class TranscriptWord:
    start: float
    end: float
    word: str


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str
    words: list[TranscriptWord] = field(default_factory=list)


@dataclass
class TranscriptionResult:
    segments: list[TranscriptSegment]
    language: str
    language_probability: float
    duration: float
    text: str
    model_size: str
    device: str

    @property
    def word_count(self) -> int:
        return len(self.text.split())


def transcribe_audio(
    audio_path: Path,
    model_size_preference: str,
    device_preference: str,
    compute_type_preference: str,
    cancel_event: threading.Event,
) -> TranscriptionResult:
    device, _ = select_device_and_compute_type(device_preference)
    model_size = resolve_model_size(model_size_preference, device)
    compute_type = resolve_compute_type(compute_type_preference, device)

    try:
        model = get_model(model_size, device, compute_type)
    except Exception as exc:  # noqa: BLE001 - surface as a typed transcription error
        raise TranscriptionError(f"Could not load whisper model — {exc}") from exc

    try:
        segment_iter, info = model.transcribe(
            str(audio_path),
            vad_filter=True,
            word_timestamps=True,
        )

        segments: list[TranscriptSegment] = []
        text_parts: list[str] = []
        for seg in segment_iter:
            if cancel_event.is_set():
                raise JobCancelledError()
            words = [
                TranscriptWord(start=w.start, end=w.end, word=w.word.strip())
                for w in (seg.words or [])
            ]
            segment_text = seg.text.strip()
            segments.append(
                TranscriptSegment(start=seg.start, end=seg.end, text=segment_text, words=words)
            )
            text_parts.append(segment_text)
    except JobCancelledError:
        raise
    except Exception as exc:  # noqa: BLE001 - wrap unexpected whisper/ctranslate2 errors
        raise TranscriptionError(f"Transcription failed — {exc}") from exc

    return TranscriptionResult(
        segments=segments,
        language=info.language,
        language_probability=info.language_probability,
        duration=info.duration,
        text=" ".join(text_parts).strip(),
        model_size=model_size,
        device=device,
    )
