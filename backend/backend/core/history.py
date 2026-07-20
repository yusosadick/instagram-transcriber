import json
import threading
from dataclasses import asdict, dataclass
from pathlib import Path

from backend.config import settings


@dataclass
class HistoryItem:
    id: str
    source_type: str  # "url" | "file"
    source: str
    title: str
    created_at: str
    duration: float
    word_count: int
    language: str


class HistoryStore:
    def __init__(self, path: Path, max_entries: int):
        self._path = path
        self._max_entries = max_entries
        self._lock = threading.Lock()

    def _read(self) -> list[dict]:
        if not self._path.exists():
            return []
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _write(self, entries: list[dict]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_entry(self, item: HistoryItem) -> None:
        with self._lock:
            entries = self._read()
            entries.insert(0, asdict(item))
            entries = entries[: self._max_entries]
            self._write(entries)

    def list_entries(self) -> list[dict]:
        with self._lock:
            return self._read()

    def delete_entry(self, item_id: str) -> bool:
        with self._lock:
            entries = self._read()
            filtered = [e for e in entries if e["id"] != item_id]
            if len(filtered) == len(entries):
                return False
            self._write(filtered)
            return True


history_store = HistoryStore(settings.history_file, settings.max_history_entries)
