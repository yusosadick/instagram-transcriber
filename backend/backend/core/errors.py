class TranscriberError(Exception):
    code = "internal_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedURLError(TranscriberError):
    code = "invalid_url"


class PrivateContentError(TranscriberError):
    code = "private_content"


class DownloadError(TranscriberError):
    code = "download_failed"


class AudioExtractionError(TranscriberError):
    code = "audio_extraction_failed"


class TranscriptionError(TranscriberError):
    code = "transcription_failed"


class JobCancelledError(TranscriberError):
    code = "cancelled"

    def __init__(self, message: str = "Job was cancelled"):
        super().__init__(message)
