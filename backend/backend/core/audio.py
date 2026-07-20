import json
import shutil
import subprocess
from pathlib import Path

from backend.core.errors import AudioExtractionError


def check_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AudioExtractionError(f"ffprobe failed — {result.stderr.strip()[-500:]}")
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def normalize_to_wav16k_mono(input_path: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-vn",
            str(output_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not output_path.exists():
        raise AudioExtractionError(f"Audio extraction failed — {result.stderr.strip()[-500:]}")
    return output_path
