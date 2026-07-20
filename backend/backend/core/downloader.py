import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import yt_dlp

from backend.core.errors import DownloadError, JobCancelledError, PrivateContentError

_PRIVATE_SIGNALS = ("login", "private", "rate-limit", "rate limit", "restricted")


@dataclass
class DownloadResult:
    audio_path: Path
    title: str
    uploader: str | None
    source_duration: float | None


class _CancelledSentinel(Exception):
    """Raised inside yt-dlp's progress hook to unwind out of its download loop."""


def download_media(
    url: str,
    dest_dir: Path,
    cookies_file: Path | None,
    cancel_event: threading.Event,
    on_progress: Callable[[str], None] | None = None,
) -> DownloadResult:
    dest_dir.mkdir(parents=True, exist_ok=True)

    def progress_hook(d: dict) -> None:
        if cancel_event.is_set():
            raise _CancelledSentinel()
        if on_progress and d.get("status") == "downloading":
            pct = d.get("_percent_str", "").strip()
            on_progress(f"Downloading... {pct}")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(dest_dir / "%(id)s.%(ext)s"),
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "wav"},
        ],
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    if cookies_file is not None:
        ydl_opts["cookiefile"] = str(cookies_file)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except _CancelledSentinel as exc:
        raise JobCancelledError() from exc
    except yt_dlp.utils.DownloadError as exc:
        message = str(exc)
        lowered = message.lower()
        if any(signal in lowered for signal in _PRIVATE_SIGNALS):
            raise PrivateContentError(
                "This content requires a logged-in session. Export a cookies.txt "
                "from your browser and set COOKIES_FILE, then retry."
            ) from exc
        raise DownloadError(f"Could not download media — {message}") from exc

    audio_path = dest_dir / f"{info['id']}.wav"
    if not audio_path.exists():
        # yt-dlp's postprocessor may have picked a different extension/name.
        candidates = list(dest_dir.glob(f"{info['id']}.*"))
        if not candidates:
            raise DownloadError("Download completed but no audio file was produced")
        audio_path = candidates[0]

    return DownloadResult(
        audio_path=audio_path,
        title=info.get("title") or info.get("id"),
        uploader=info.get("uploader"),
        source_duration=info.get("duration"),
    )
