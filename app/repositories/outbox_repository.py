from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.repositories.json_file import JsonFileRepository, JsonObject


class OutboxRepository:
    """Persist queued email messages when SMTP delivery is unavailable."""

    def __init__(self, storage_dir: Path) -> None:
        self._json = JsonFileRepository(storage_dir)
        self._directory = storage_dir / "outbox"

    def enqueue(self, message: JsonObject) -> str:
        message_id = str(uuid4())
        payload = {
            "id": message_id,
            "queued_at": datetime.now(UTC).isoformat(),
            **message,
        }
        self._json.write_json(self._directory / f"{message_id}.json", payload)
        return message_id

    def list_all(self) -> list[JsonObject]:
        if not self._directory.exists():
            return []

        return [self._json.read_json(path) for path in sorted(self._directory.glob("*.json"))]
