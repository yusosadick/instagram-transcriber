#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== Instagram Transcriber setup =="

missing=0

if ! command -v uv >/dev/null 2>&1; then
  echo "✗ uv not found. Install it with:"
  echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
  missing=1
else
  echo "✓ uv $(uv --version)"
fi

if ! command -v pnpm >/dev/null 2>&1; then
  echo "✗ pnpm not found. Install it with:"
  echo "    corepack enable pnpm"
  missing=1
else
  echo "✓ pnpm $(pnpm --version)"
fi

if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  echo "✗ ffmpeg/ffprobe not found. Install it with:"
  if [[ "$(uname -s)" == "Darwin" ]]; then
    echo "    brew install ffmpeg"
  else
    echo "    sudo apt-get install ffmpeg"
  fi
  missing=1
else
  echo "✓ ffmpeg $(ffmpeg -version | head -n1 | cut -d' ' -f3)"
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "✗ python3 not found — required for uv to provision a Python 3.11+ interpreter."
  missing=1
fi

if [[ "$missing" -eq 1 ]]; then
  echo ""
  echo "Install the missing tools above, then re-run ./scripts/setup.sh"
  exit 1
fi

echo ""
echo "-- Installing backend dependencies (uv sync) --"
uv sync --project backend

echo ""
echo "-- Installing frontend dependencies (pnpm install) --"
pnpm install

mkdir -p models output temp

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "✓ Created .env from .env.example"
fi
if [[ ! -f apps/web/.env ]]; then
  cp apps/web/.env.example apps/web/.env
  echo "✓ Created apps/web/.env from apps/web/.env.example"
fi

echo ""
echo "Whisper model weights download automatically on first transcription"
echo "(~600MB-3GB depending on model size) and are cached under ./models — never re-downloaded."
if [[ "${1:-}" == "--prefetch-model" ]]; then
  echo "Prefetching model now..."
  uv run --project backend python -c "from backend.core.model_manager import load_model_for_settings; load_model_for_settings()"
fi

echo ""
echo "Setup complete. Run 'pnpm dev' to start the web UI + API, or"
echo "'uv run --project backend transcriber \"<instagram-url>\"' to use the CLI."
