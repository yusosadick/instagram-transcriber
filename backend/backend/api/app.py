import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config import settings
from backend.core.audio import check_ffmpeg_available

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    if not check_ffmpeg_available():
        logger.warning(
            "ffmpeg/ffprobe not found on PATH — downloads and transcription will fail "
            "until ffmpeg is installed (see scripts/setup.sh)."
        )
    yield


app = FastAPI(title="Instagram Transcriber API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
