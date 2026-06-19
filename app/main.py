from fastapi import FastAPI

app = FastAPI(
    title="Developer Landing API",
    description="Backend API for a developer landing contact form with AI integration.",
    version="0.1.0",
)


@app.get("/api/health", tags=["health"])
async def health() -> dict[str, str]:
    """Return a minimal health response for scaffold verification."""
    return {"status": "ok", "service": "developer-landing-api", "version": "0.1.0"}
