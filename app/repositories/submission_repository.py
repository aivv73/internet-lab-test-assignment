from pathlib import Path

from app.repositories.json_file import JsonFileRepository, JsonObject


class SubmissionRepository:
    """Persist contact submissions as separate JSON files."""

    def __init__(self, storage_dir: Path) -> None:
        self._json = JsonFileRepository(storage_dir)
        self._directory = storage_dir / "submissions"

    def save(self, submission_id: str, submission: JsonObject) -> None:
        self._json.write_json(self._path_for(submission_id), submission)

    def get(self, submission_id: str) -> JsonObject | None:
        path = self._path_for(submission_id)
        if not path.exists():
            return None
        return self._json.read_json(path)

    def list_all(self) -> list[JsonObject]:
        if not self._directory.exists():
            return []

        return [self._json.read_json(path) for path in sorted(self._directory.glob("*.json"))]

    def _path_for(self, submission_id: str) -> Path:
        safe_id = _safe_file_stem(submission_id)
        return self._directory / f"{safe_id}.json"


def _safe_file_stem(value: str) -> str:
    return "".join(character for character in value if character.isalnum() or character in "-_")
