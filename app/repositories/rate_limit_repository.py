from pathlib import Path

from app.repositories.json_file import JsonFileRepository, JsonObject


class RateLimitRepository:
    """Persist rate-limit counters/windows in a JSON file."""

    def __init__(self, storage_dir: Path) -> None:
        self._json = JsonFileRepository(storage_dir)
        self._path = storage_dir / "rate-limit.json"

    def get_state(self) -> JsonObject:
        return self._json.read_json(self._path, default={})

    def save_state(self, state: JsonObject) -> None:
        self._json.write_json(self._path, state)
