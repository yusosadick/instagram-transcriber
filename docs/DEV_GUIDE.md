# Development Guide

## Repo layout

```
apps/web/                  React + TS + Vite + Tailwind frontend
backend/backend/
  config.py                 Settings (env-driven), single instance
  cli.py                    `transcriber` entry point
  api/                       FastAPI app, routes, Pydantic schemas
  core/
    errors.py                Typed exception hierarchy
    validators.py             Instagram URL validation
    downloader.py             yt-dlp wrapper
    audio.py                  ffmpeg wrapper (normalize, probe, availability)
    model_manager.py          hardware detection + model caching
    transcriber.py            faster-whisper wrapper
    exporter.py                txt/srt/json writers (single source of formatting)
    history.py                 recent-history JSON store
    job_manager.py             in-memory job registry + cancellation
    pipeline.py                 shared orchestration, used by both API and CLI
models/  output/  temp/       gitignored runtime data
```

## Running services independently

Backend only:

```bash
uv run --project backend uvicorn backend.api.app:app --reload --port 8000
```

Frontend only:

```bash
pnpm --filter web dev
```

Both together: `pnpm dev` (uses `concurrently`, see root `package.json`).

## Job status state machine

```
queued → downloading → extracting_audio → transcribing → exporting → completed
                                                                     ↘ failed
   (any state) --cancel--> cancelling → cancelled
```

Cancellation is cooperative: `POST /api/jobs/{id}/cancel` sets a
`threading.Event` on the job record. `downloader.py`, `audio.py`, and
`transcriber.py` all check that event at natural iteration boundaries
(progress hook, subprocess poll loop, per-segment) and raise
`JobCancelledError`, which `pipeline.py` propagates and the job manager
records as `cancelled`.

## Adding a new export format

Add a writer function to `backend/backend/core/exporter.py` (mirroring
`write_txt`/`write_srt`/`write_json`), call it from `pipeline.py`'s export
stage, add the extension to `_ALLOWED_EXPORT_FORMATS` in
`backend/backend/api/routes.py`, and add an entry to the `FORMATS` array in
`apps/web/src/components/ExportMenu.tsx`. Do not duplicate formatting logic
in the frontend — it only downloads what the backend already wrote.

## Lint / typecheck

```bash
# backend
uv run --project backend ruff check backend
uv run --project backend mypy backend

# frontend
pnpm --filter web lint
pnpm --filter web build   # runs tsc --noEmit + vite build
```

## Debugging yt-dlp / ffmpeg issues

- yt-dlp errors surface as `DownloadError` or `PrivateContentError` (see
  `backend/backend/core/downloader.py`) — check the wrapped message for the
  underlying yt-dlp reason.
- ffmpeg failures capture the last 500 chars of stderr in
  `AudioExtractionError` — usually enough to diagnose a codec or corrupt-file
  issue.
- `GET /api/health` reports whether ffmpeg/ffprobe are on `PATH` and which
  device/compute_type will be used.
