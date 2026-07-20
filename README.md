<div align="center">

# Instagram Transcriber

**Turn any Instagram Reel or Post into a clean, timestamped transcript — fully offline, fully free.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18-339933)](https://nodejs.org/)

</div>

---

Paste an Instagram URL (or drop a local video/audio file), and get back a
searchable, timestamped transcript you can copy or export — from a clean web
app or straight from your terminal. No API keys, no subscriptions, no data
leaving your machine. Speech recognition runs locally using
[faster-whisper](https://github.com/SYSTRAN/faster-whisper); downloading is
handled by [yt-dlp](https://github.com/yt-dlp/yt-dlp); audio processing by
[FFmpeg](https://ffmpeg.org/). This project just wires proven tools together
into something pleasant to use.

## Table of contents

- [Features](#features)
- [Quickstart](#quickstart)
- [Using the web app](#using-the-web-app)
- [Using the CLI](#using-the-cli)
- [Configuration](#configuration)
- [Private / login-gated content](#private--login-gated-content)
- [Hardware notes](#hardware-notes)
- [Troubleshooting](#troubleshooting)
- [Project structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

## Features

- **Paste a URL or drag & drop** a local audio/video file — no download step needed for local files
- **Live progress** with a cancel button for in-flight jobs
- **Word-level timestamps**, toggleable in the transcript view
- **Word count, duration, and detected language** shown automatically
- **Copy to clipboard** with one click (and automatically from the CLI)
- **Export** as TXT, SRT (subtitles), or JSON
- **Recent history**, shared between the web app and the CLI
- **Works entirely from the terminal** if you don't want a browser open
- **Dark mode**, responsive layout, no account or sign-in required
- **Runs 100% locally** — nothing is uploaded anywhere except the original
  fetch from Instagram

## Quickstart

### 1. Install prerequisites

You'll need four things. If you already have them, skip ahead.

| Tool | Why | Install |
|---|---|---|
| **Python 3.11+** | Runs the backend | [python.org](https://www.python.org/downloads/) (macOS/Linux usually have it already) |
| **Node.js 18+** | Runs the frontend build tooling | [nodejs.org](https://nodejs.org/) |
| **pnpm** | Package manager for the frontend | `corepack enable pnpm` (ships with modern Node) |
| **uv** | Fast Python package/environment manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **ffmpeg** | Audio extraction/conversion | macOS: `brew install ffmpeg` · Ubuntu/Debian: `sudo apt install ffmpeg` · [more options](https://ffmpeg.org/download.html) |

> **macOS note:** if `brew install ffmpeg` seems to hang or starts
> compiling LLVM/Clang from source, your Command Line Tools are probably
> mismatched with Homebrew's prebuilt bottles. Don't wait it out — see
> [Troubleshooting](#troubleshooting) for a 30-second fix.

### 2. Clone and set up

```bash
git clone https://github.com/yusosadick/instagram-transcriber.git
cd instagram-transcriber
./scripts/setup.sh
```

`setup.sh` checks that everything above is installed, installs all Python
and Node dependencies, creates your local `.env` files, and creates the
`models/`, `output/`, and `temp/` folders. It does **not** download the
speech recognition model yet — that happens automatically the first time you
transcribe something (see [Hardware notes](#hardware-notes) for sizes).

### 3. Run it

```bash
pnpm dev
```

This starts both the backend API (`http://localhost:8000`) and the web app
(`http://localhost:5173`) together. Open the web app in your browser and
paste an Instagram Reel or Post URL.

That's it — first transcription will take a bit longer while the model
downloads (once, ever, after that it's cached and reused).

## Using the web app

1. Paste an Instagram Reel/Post URL into the input box (or click **Upload
   file** to drag & drop a local audio/video file instead)
2. Click **Transcribe**
3. Watch the progress bar — you can cancel at any point
4. Once it's done, read the transcript, toggle timestamps on/off, and:
   - **Copy transcript** — copies the plain text to your clipboard
   - **Download TXT / SRT / JSON** — saves the transcript in that format
5. Past transcriptions show up under **Recent** — from both the web app and
   the CLI

## Using the CLI

No browser needed. From the `instagram-transcriber` directory:

```bash
uv run --project backend transcriber "https://www.instagram.com/reel/XXXXXXX/"

# or transcribe a local file instead of downloading
uv run --project backend transcriber ./some-video.mp4
```

Output:

```
Downloading...
Extracting audio...
Transcribing...
Done.

Language: en (100% confidence)
Duration: 12.4s   Words: 38
Saved to: output/transcript.txt, subtitles.srt, transcript.json
```

The transcript is also copied to your clipboard automatically. Useful flags:

| Flag | Description |
|---|---|
| `--model <name>` | Force a specific whisper model (e.g. `--model small` for a faster, lower-quality run) |
| `--cookies <path>` | Path to a `cookies.txt` for private/login-gated content |
| `--output-dir <path>` | Where to write `transcript.txt` / `subtitles.srt` / `transcript.json` (default: `output/`) |
| `--no-clipboard` | Skip copying the transcript to your clipboard |

Tip: if you'd rather not type `uv run --project backend` every time,
`uv sync` also installs the `transcriber` command into `backend/.venv` — you
can activate that virtualenv (`source backend/.venv/bin/activate`) and just
run `transcriber "<url>"` directly.

## Configuration

Copy `.env.example` to `.env` (setup.sh does this for you) and adjust as
needed:

| Variable | Default | Description |
|---|---|---|
| `COOKIES_FILE` | unset | Path to a `cookies.txt` for private content — see below |
| `MODEL_SIZE` | `auto` | `auto` picks the best model for your hardware, or set a specific [faster-whisper model name](https://github.com/SYSTRAN/faster-whisper#model-conversion) (e.g. `tiny`, `small`, `medium`, `large-v3`) |
| `DEVICE` | `auto` | `auto` / `cpu` / `cuda` |
| `COMPUTE_TYPE` | `auto` | CTranslate2 compute type override (e.g. `int8`, `float16`) |

## Private / login-gated content

Some Instagram content requires a logged-in session to download. If you hit
a "requires login" error:

1. Install a browser extension like [Get cookies.txt
   LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Log into Instagram in that browser, then export cookies for
   `instagram.com` to a file (Netscape format)
3. Set `COOKIES_FILE=/path/to/cookies.txt` in your `.env`, or pass
   `--cookies /path/to/cookies.txt` to the CLI

Public content works with no configuration at all.

## Hardware notes

Speech recognition runs on
[CTranslate2](https://github.com/OpenNMT/CTranslate2), which supports NVIDIA
CUDA and CPU — but **not** Apple Silicon GPU acceleration (there's no
Metal/MPS backend). What this means in practice:

- **NVIDIA GPU machines:** uses `large-v3` with `float16` — fast and highest
  quality.
- **Apple Silicon and other CPU-only machines:** uses `large-v3-turbo` with
  `int8` quantization automatically — a much better speed/quality tradeoff
  on CPU than the full `large-v3` model. Still, transcription can run slower
  than real-time on older or lower-power CPUs.
- **Cancel latency on slow CPUs:** cancellation is checked between whisper
  segments. On a slow CPU, a short clip may decode as a single segment
  before anything is cancellable, so `Cancel` can take a while to actually
  stop a job rather than being instant. If this bothers you, set
  `MODEL_SIZE=small` or `MODEL_SIZE=base` in `.env` for snappier (if less
  accurate) transcription and cancellation.

You can always override the automatic choice — see
[Configuration](#configuration).

## Troubleshooting

**`brew install ffmpeg` hangs / starts compiling LLVM from source**
Some Homebrew setups don't have a prebuilt ("bottled") ffmpeg for your exact
macOS/toolchain combination, so it falls back to compiling everything from
source — including LLVM, which can take an hour or more. Skip it and grab a
prebuilt static binary instead:

```bash
curl -LsSf https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip -o /tmp/ffmpeg.zip
curl -LsSf https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip -o /tmp/ffprobe.zip
cd /tmp && unzip -o ffmpeg.zip && unzip -o ffprobe.zip
mv ffmpeg ffprobe /usr/local/bin/
xattr -d com.apple.quarantine /usr/local/bin/ffmpeg /usr/local/bin/ffprobe 2>/dev/null
ffmpeg -version   # should print a version, not "command not found"
```

**`onnxruntime` fails to install on Intel Mac** (`can't be installed because
it doesn't have a source distribution or wheel for the current platform`)
Newer `onnxruntime` releases dropped macOS x86_64 (Intel) wheels. This repo
already pins `onnxruntime<1.24` in `backend/pyproject.toml` to avoid it — if
you still hit this, make sure you're on the latest `main` and re-run
`uv sync --project backend`.

**Web app shows "Not Found" and nothing happens when you click Transcribe**
This almost always means `apps/web/.env` is missing, so the frontend can't
find the backend. `./scripts/setup.sh` creates it automatically; if you set
things up manually, copy `apps/web/.env.example` to `apps/web/.env` and
restart `pnpm dev`.

**"This content requires a logged-in session"**
See [Private / login-gated content](#private--login-gated-content) above.

**First transcription takes a long time**
The whisper model (600 MB – 3 GB depending on hardware) downloads once on
first use and is cached under `models/` forever after — this is expected
and only happens the first time.

**`GET /api/health` is your friend**
With the backend running, `curl localhost:8000/api/health` reports whether
ffmpeg is detected and which device/compute type will be used — a fast way
to sanity-check your setup.

## Project structure

```
apps/web/                  React + TypeScript + Vite + Tailwind frontend
backend/backend/
  config.py                 Settings (env-driven)
  cli.py                     `transcriber` command
  api/                        FastAPI app, routes, schemas
  core/
    downloader.py             yt-dlp wrapper
    audio.py                   ffmpeg wrapper
    model_manager.py           hardware detection + model caching
    transcriber.py             faster-whisper wrapper
    exporter.py                 txt/srt/json writers
    history.py                  recent-history store
    job_manager.py              in-memory job registry + cancellation
    pipeline.py                  shared orchestration used by API and CLI
models/  output/  temp/       gitignored runtime data (created on first run)
```

## Development

See the [Development guide](docs/DEV_GUIDE.md) for the job status state
machine, running services independently, linting/type-checking, and how to
add a new export format.

For running this in a more permanent/unattended setting, see the
[Production guide](docs/PRODUCTION_GUIDE.md).

## Contributing

Issues and pull requests are welcome. A few guidelines to keep this project
pleasant to maintain:

- **Reuse, don't reinvent.** This project exists to wire together yt-dlp,
  faster-whisper, and ffmpeg cleanly — prefer using what those libraries
  already give you over writing custom logic.
- **Keep the CLI and API in sync.** Both call the same
  `backend/backend/core/pipeline.py` — don't duplicate pipeline logic in
  either entrypoint.
- **No unnecessary dependencies.** This app is meant to stay lightweight and
  easy to audit. If you're adding a dependency, make sure it earns its
  place.
- Run `pnpm --filter web build` and `uv run --project backend ruff check
  backend` before opening a PR.

## Credits

This project is a thin, opinionated integration layer over:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — media download
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — speech
  recognition, including bundled Silero VAD and word-level timestamps
- [FFmpeg](https://ffmpeg.org/) — audio extraction and conversion

All the hard work of speech recognition and media downloading is done by
these projects — this repo just gives them a pleasant UI and a clean CLI.

## License

[MIT](LICENSE)
