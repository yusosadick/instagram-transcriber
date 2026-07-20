import subprocess
import sys
import threading
from pathlib import Path

import typer

from backend.config import settings
from backend.core.errors import TranscriberError
from backend.core.pipeline import FileSource, URLSource, run_pipeline
from backend.core.validators import is_instagram_url

app = typer.Typer(add_completion=False, no_args_is_help=True)

_STAGE_LABELS = {
    "downloading": "Downloading...",
    "extracting_audio": "Extracting audio...",
    "transcribing": "Transcribing...",
    "completed": "Done.",
}


def _make_stage_printer():
    printed: set[str] = set()

    def on_stage(status: str, _message: str) -> None:
        label = _STAGE_LABELS.get(status)
        if label and status not in printed:
            typer.echo(label)
            printed.add(status)

    return on_stage


def _copy_to_clipboard(text: str) -> bool:
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except Exception:
        pass
    if sys.platform == "darwin":
        try:
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            return True
        except Exception:
            return False
    return False


@app.command()
def main(
    source: str = typer.Argument(
        ..., help="Instagram Reel/Post URL, or a path to a local audio/video file"
    ),
    model: str = typer.Option(None, "--model", help="Override the whisper model size"),
    cookies: Path = typer.Option(
        None, "--cookies", help="Path to a cookies.txt for private/login-gated content"
    ),
    output_dir: Path = typer.Option(
        None, "--output-dir", help="Directory to write transcript.txt/subtitles.srt/transcript.json"
    ),
    no_clipboard: bool = typer.Option(
        False, "--no-clipboard", help="Skip copying the transcript to the clipboard"
    ),
) -> None:
    if model:
        settings.model_size = model
    if cookies:
        settings.cookies_file = cookies

    out_dir = output_dir or settings.output_dir

    if is_instagram_url(source):
        job_source = URLSource(url=source)
    elif Path(source).expanduser().exists():
        path = Path(source).expanduser().resolve()
        job_source = FileSource(path=path, original_name=path.name)
    else:
        typer.echo(
            "Error: Not a valid Instagram Reel/Post URL, and no local file found at that path",
            err=True,
        )
        raise typer.Exit(code=1)

    cancel_event = threading.Event()
    on_stage = _make_stage_printer()

    try:
        result = run_pipeline(
            "cli",
            job_source,
            cancel_event=cancel_event,
            on_stage=on_stage,
            output_dir=out_dir,
        )
    except TranscriberError as exc:
        if exc.code == "cancelled":
            typer.echo("Cancelled.")
            raise typer.Exit(code=0) from None
        typer.echo(f"Error: {exc.message}", err=True)
        raise typer.Exit(code=1) from None

    if not no_clipboard:
        _copy_to_clipboard(result.text)

    typer.echo(f"\nLanguage: {result.language} ({result.language_probability:.0%} confidence)")
    typer.echo(f"Duration: {result.duration:.1f}s   Words: {result.word_count}")
    typer.echo(f"Saved to: {out_dir}/transcript.txt, subtitles.srt, transcript.json")


if __name__ == "__main__":
    app()
