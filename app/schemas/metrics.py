from pydantic import BaseModel, Field


class MetricsResponse(BaseModel):
    """Aggregate contact API metrics."""

    total_submissions: int = Field(default=0, ge=0)
    by_category: dict[str, int] = Field(default_factory=dict)
    by_sentiment: dict[str, int] = Field(default_factory=dict)
    email_delivery: dict[str, int] = Field(default_factory=dict)
    ai_fallbacks: int = Field(default=0, ge=0)
