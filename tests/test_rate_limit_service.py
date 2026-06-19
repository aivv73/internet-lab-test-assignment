from pathlib import Path

import pytest

from app.core.config import Settings
from app.core.errors import RateLimitExceededError
from app.repositories.rate_limit_repository import RateLimitRepository
from app.services.rate_limit_service import RateLimitService


class FakeClock:
    def __init__(self, now: float = 1_000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def make_service(tmp_path: Path, clock: FakeClock) -> RateLimitService:
    settings = Settings(
        storage_dir=tmp_path,
        log_file=tmp_path / "app.log",
        rate_limit_ip_requests=2,
        rate_limit_ip_window_seconds=60,
        rate_limit_email_requests=1,
        rate_limit_email_window_seconds=120,
    )
    return RateLimitService(RateLimitRepository(tmp_path), settings, clock=clock)


def test_rate_limit_allows_requests_within_limits(tmp_path: Path) -> None:
    clock = FakeClock()
    service = make_service(tmp_path, clock)

    service.check_and_increment(ip_address="127.0.0.1", email="first@example.com")
    service.check_and_increment(ip_address="127.0.0.1", email="second@example.com")

    state = RateLimitRepository(tmp_path).get_state()
    assert state["ip:127.0.0.1"]["count"] == 2
    assert state["email:first@example.com"]["count"] == 1


def test_rate_limit_blocks_when_ip_limit_is_exceeded(tmp_path: Path) -> None:
    clock = FakeClock()
    service = make_service(tmp_path, clock)

    service.check_and_increment(ip_address="127.0.0.1", email="first@example.com")
    service.check_and_increment(ip_address="127.0.0.1", email="second@example.com")

    with pytest.raises(RateLimitExceededError) as exc_info:
        service.check_and_increment(ip_address="127.0.0.1", email="third@example.com")

    assert exc_info.value.code == "rate_limit_exceeded"
    assert exc_info.value.details == {"retry_after_seconds": 60}


def test_rate_limit_blocks_when_email_limit_is_exceeded(tmp_path: Path) -> None:
    clock = FakeClock()
    service = make_service(tmp_path, clock)

    service.check_and_increment(ip_address="127.0.0.1", email="User@Example.com")

    with pytest.raises(RateLimitExceededError) as exc_info:
        service.check_and_increment(ip_address="192.168.1.10", email=" user@example.com ")

    assert exc_info.value.details == {"retry_after_seconds": 120}


def test_rate_limit_resets_windows_after_expiration(tmp_path: Path) -> None:
    clock = FakeClock()
    service = make_service(tmp_path, clock)

    service.check_and_increment(ip_address="127.0.0.1", email="first@example.com")
    service.check_and_increment(ip_address="127.0.0.1", email="second@example.com")

    clock.advance(61)

    service.check_and_increment(ip_address="127.0.0.1", email="third@example.com")

    state = RateLimitRepository(tmp_path).get_state()
    assert state["ip:127.0.0.1"]["count"] == 1


def test_rate_limit_does_not_increment_state_for_blocked_requests(tmp_path: Path) -> None:
    clock = FakeClock()
    service = make_service(tmp_path, clock)

    service.check_and_increment(ip_address="127.0.0.1", email="user@example.com")

    with pytest.raises(RateLimitExceededError):
        service.check_and_increment(ip_address="192.168.1.10", email="user@example.com")

    state = RateLimitRepository(tmp_path).get_state()
    assert "ip:192.168.1.10" not in state
    assert state["email:user@example.com"]["count"] == 1
