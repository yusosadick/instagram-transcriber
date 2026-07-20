import logging
from functools import lru_cache

import ctranslate2
from faster_whisper import WhisperModel

from backend.config import settings

logger = logging.getLogger(__name__)

CUDA_DEFAULT_MODEL = "large-v3"
CPU_DEFAULT_MODEL = "large-v3-turbo"


def select_device_and_compute_type(preference: str = "auto") -> tuple[str, str]:
    if preference == "cuda":
        return "cuda", "float16"
    if preference == "cpu":
        return "cpu", "int8"

    if ctranslate2.get_cuda_device_count() > 0:
        return "cuda", "float16"
    # CPU covers Apple Silicon too — CTranslate2 has no Metal/MPS backend, so
    # there is no GPU acceleration path on Apple Silicon, only CPU int8.
    return "cpu", "int8"


def resolve_model_size(configured: str, device: str) -> str:
    if configured != "auto":
        return configured
    return CUDA_DEFAULT_MODEL if device == "cuda" else CPU_DEFAULT_MODEL


def resolve_compute_type(configured: str, device: str) -> str:
    if configured != "auto":
        return configured
    return "float16" if device == "cuda" else "int8"


@lru_cache(maxsize=4)
def get_model(model_size: str, device: str, compute_type: str) -> WhisperModel:
    cache_dir = settings.models_dir / model_size
    was_cached = cache_dir.exists() and any(cache_dir.iterdir())
    logger.info(
        "Loading whisper model=%s device=%s compute_type=%s (%s)",
        model_size,
        device,
        compute_type,
        "cache hit" if was_cached else "downloading — first run only",
    )
    return WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type,
        download_root=str(settings.models_dir),
    )


def load_model_for_settings() -> tuple[WhisperModel, str, str, str]:
    device, _ = select_device_and_compute_type(settings.device)
    model_size = resolve_model_size(settings.model_size, device)
    compute_type = resolve_compute_type(settings.compute_type, device)
    model = get_model(model_size, device, compute_type)
    return model, model_size, device, compute_type
