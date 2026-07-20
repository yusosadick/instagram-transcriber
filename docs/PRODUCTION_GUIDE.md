# Production Guide

This app is designed for local, single-user use. "Production" here means
"running unattended on a machine you trust," not a multi-tenant cloud
deployment.

## Building the frontend

```bash
pnpm --filter web build
```

Output goes to `apps/web/dist/`. Serve it with any static file server, or
point the FastAPI app at it with a `StaticFiles` mount if you want a single
process to serve both — not configured by default to keep dev/prod parity
simple (Vite dev server + FastAPI, same as `pnpm dev`).

## Running the backend

```bash
uv run --project backend uvicorn backend.api.app:app --host 127.0.0.1 --port 8000
```

**Do not run with `--workers > 1` or behind a multi-process manager.** The
`JobManager` and model cache in `backend/backend/core/` are in-memory and
process-local — a second worker process would not see jobs created on the
first. This app is intentionally single-process; scale by running it, not by
adding workers.

Do not use `--reload` in production (it re-imports and re-loads the whisper
model on every file change).

## Model prefetch

Whisper model weights are cached under `./models` and never re-downloaded
once present. To warm the cache ahead of first use (e.g. before a demo):

```bash
./scripts/setup.sh --prefetch-model
```

## Disk space

- `models/` — one model snapshot, roughly 600MB (`large-v3-turbo`, int8) to
  ~3GB (`large-v3`, float16 on CUDA).
- `output/` — grows with every completed job (three small text files per
  job). Prune old job folders periodically if disk space matters; nothing
  does this automatically.
- `temp/` — always cleaned up automatically after each job (success, failure,
  or cancellation) via a `try/finally` in `pipeline.py`. Should not
  accumulate; if it does, something crashed the process mid-job.

## Persistence

- `backend/data/history.json` — recent-history list (capped, oldest entries
  pruned). Back it up if you care about history surviving a wipe.
- `output/<job_id>/` — the actual transcript artifacts.

## Security

- Binds to `127.0.0.1` by default — not reachable from the network unless you
  explicitly change `--host`.
- No authentication, by design: this is a local single-user tool. Do not
  expose it on a shared network or the public internet without adding auth
  in front of it (e.g. a reverse proxy with basic auth) — there is none
  built in.
