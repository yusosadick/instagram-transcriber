import json
from dataclasses import asdict
from pathlib import Path

from backend.core.transcriber import TranscriptionResult


def _srt_timestamp(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_txt(result: TranscriptionResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.text + "\n", encoding="utf-8")
    return path


def write_srt(result: TranscriptionResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i, seg in enumerate(result.segments, start=1):
        lines.append(str(i))
        lines.append(f"{_srt_timestamp(seg.start)} --> {_srt_timestamp(seg.end)}")
        lines.append(seg.text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_json(result: TranscriptionResult, path: Path, *, source: str, title: str, created_at: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": source,
        "title": title,
        "created_at": created_at,
        "language": result.language,
        "language_probability": result.language_probability,
        "duration": result.duration,
        "word_count": result.word_count,
        "model_size": result.model_size,
        "device": result.device,
        "text": result.text,
        "segments": [asdict(seg) for seg in result.segments],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
