import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from app.core.errors import StorageError

JsonObject = dict[str, Any]


class JsonFileRepository:
    """Small JSON file persistence helper used by file-backed repositories."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def ensure_directory(self, directory: Path) -> None:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageError(f"Cannot create storage directory: {directory}") from exc

    def read_json(self, path: Path, default: JsonObject | None = None) -> JsonObject:
        if not path.exists():
            return dict(default or {})

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Cannot read JSON storage file: {path}") from exc

        if not isinstance(data, dict):
            raise StorageError(f"JSON storage file must contain an object: {path}")

        return data

    def write_json(self, path: Path, data: JsonObject) -> None:
        self.ensure_directory(path.parent)

        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=path.parent,
                delete=False,
                prefix=f".{path.name}.",
                suffix=".tmp",
            ) as file:
                json.dump(data, file, ensure_ascii=False, indent=2, sort_keys=True, default=str)
                file.write("\n")
                temp_name = file.name

            os.replace(temp_name, path)
        except OSError as exc:
            raise StorageError(f"Cannot write JSON storage file: {path}") from exc
        finally:
            if "temp_name" in locals() and Path(temp_name).exists():
                Path(temp_name).unlink(missing_ok=True)
