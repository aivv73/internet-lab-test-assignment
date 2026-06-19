from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


def create_client(frontend_dist_dir: Path) -> TestClient:
    settings = Settings(frontend_dist_dir=frontend_dist_dir, log_file=frontend_dist_dir / "app.log")
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


def write_frontend_build(frontend_dist_dir: Path) -> None:
    frontend_dist_dir.mkdir(parents=True)
    (frontend_dist_dir / "index.html").write_text(
        '<!doctype html><app-root></app-root><script src="main.js"></script>',
        encoding="utf-8",
    )
    (frontend_dist_dir / "main.js").write_text("console.log('frontend');", encoding="utf-8")


def test_serves_angular_index_at_root(tmp_path: Path) -> None:
    frontend_dist_dir = tmp_path / "frontend" / "browser"
    write_frontend_build(frontend_dist_dir)
    client = create_client(frontend_dist_dir)

    response = client.get("/")

    assert response.status_code == 200
    assert "<app-root>" in response.text


def test_serves_angular_static_build_files(tmp_path: Path) -> None:
    frontend_dist_dir = tmp_path / "frontend" / "browser"
    write_frontend_build(frontend_dist_dir)
    client = create_client(frontend_dist_dir)

    response = client.get("/main.js")

    assert response.status_code == 200
    assert "console.log('frontend')" in response.text


def test_spa_routes_fall_back_to_angular_index(tmp_path: Path) -> None:
    frontend_dist_dir = tmp_path / "frontend" / "browser"
    write_frontend_build(frontend_dist_dir)
    client = create_client(frontend_dist_dir)

    response = client.get("/review/contact-demo")

    assert response.status_code == 200
    assert "<app-root>" in response.text


def test_frontend_fallback_does_not_intercept_api_routes(tmp_path: Path) -> None:
    frontend_dist_dir = tmp_path / "frontend" / "browser"
    write_frontend_build(frontend_dist_dir)
    client = create_client(frontend_dist_dir)

    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert "<app-root>" not in response.text


def test_missing_frontend_build_returns_404_without_breaking_api(tmp_path: Path) -> None:
    client = create_client(tmp_path / "missing" / "browser")

    root_response = client.get("/")
    health_response = client.get("/api/health")

    assert root_response.status_code == 404
    assert health_response.status_code == 200
