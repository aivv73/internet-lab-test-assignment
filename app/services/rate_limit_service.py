from collections.abc import Callable
from math import ceil

from app.core.config import Settings
from app.core.errors import RateLimitExceededError
from app.repositories.json_file import JsonObject
from app.repositories.rate_limit_repository import RateLimitRepository


class RateLimitService:
    """Combined IP + email rate limiter backed by JSON file storage."""

    def __init__(
        self,
        repository: RateLimitRepository,
        settings: Settings,
        *,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._repository = repository
        self._settings = settings
        self._clock = clock or _time_now

    def check_and_increment(self, *, ip_address: str, email: str) -> None:
        """Record a contact attempt or raise when the limit is exceeded."""
        now = self._clock()
        state = self._repository.get_state()

        checks = [
            _RateLimitCheck(
                key=f"ip:{ip_address}",
                max_requests=self._settings.rate_limit_ip_requests,
                window_seconds=self._settings.rate_limit_ip_window_seconds,
            ),
            _RateLimitCheck(
                key=f"email:{email.strip().lower()}",
                max_requests=self._settings.rate_limit_email_requests,
                window_seconds=self._settings.rate_limit_email_window_seconds,
            ),
        ]

        cleaned_state = _drop_expired_entries(state, now)

        for check in checks:
            entry = _current_entry(cleaned_state, check, now)
            if entry.count >= check.max_requests:
                retry_after_seconds = ceil(entry.window_start + check.window_seconds - now)
                raise RateLimitExceededError(max(retry_after_seconds, 1))

        for check in checks:
            entry = _current_entry(cleaned_state, check, now)
            cleaned_state[check.key] = {
                "count": entry.count + 1,
                "window_start": entry.window_start,
                "window_seconds": check.window_seconds,
            }

        self._repository.save_state(cleaned_state)


class _RateLimitCheck:
    def __init__(self, *, key: str, max_requests: int, window_seconds: int) -> None:
        self.key = key
        self.max_requests = max_requests
        self.window_seconds = window_seconds


class _RateLimitEntry:
    def __init__(self, *, count: int, window_start: float) -> None:
        self.count = count
        self.window_start = window_start


def _current_entry(state: JsonObject, check: _RateLimitCheck, now: float) -> _RateLimitEntry:
    raw_entry = state.get(check.key)
    if not isinstance(raw_entry, dict):
        return _RateLimitEntry(count=0, window_start=now)

    count = raw_entry.get("count", 0)
    window_start = raw_entry.get("window_start", now)

    if not isinstance(count, int) or not isinstance(window_start, int | float):
        return _RateLimitEntry(count=0, window_start=now)

    if now - float(window_start) >= check.window_seconds:
        return _RateLimitEntry(count=0, window_start=now)

    return _RateLimitEntry(count=count, window_start=float(window_start))


def _drop_expired_entries(state: JsonObject, now: float) -> JsonObject:
    cleaned: JsonObject = {}
    for key, raw_entry in state.items():
        if not isinstance(raw_entry, dict):
            continue

        window_start = raw_entry.get("window_start")
        window_seconds = raw_entry.get("window_seconds")
        if not isinstance(window_start, int | float) or not isinstance(window_seconds, int):
            continue

        if now - float(window_start) < window_seconds:
            cleaned[key] = raw_entry

    return cleaned


def _time_now() -> float:
    import time

    return time.time()
