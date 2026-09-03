from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import HeatingType, InsulationQuality, RecommendationPriority


class HomeCreate(BaseModel):
    """Payload for POST /api/homes."""

    size_sqm: float = Field(
        gt=0, le=100_000, description="Living area in square meters", examples=[120]
    )
    year_built: int = Field(ge=1800, description="Year the home was built", examples=[1998])
    heating_type: HeatingType = Field(examples=[HeatingType.GAS])
    insulation_quality: InsulationQuality = Field(examples=[InsulationQuality.AVERAGE])
    occupants: int | None = Field(
        default=None, ge=1, le=50, description="Number of people living in the home"
    )

    @field_validator("year_built")
    @classmethod
    def year_built_not_in_future(cls, value: int) -> int:
        # Checked against the current year at validation time rather than a
        # module-level constant, so the bound doesn't go stale in a long-lived
        # process that keeps running across a year boundary.
        current_year = datetime.now(UTC).year
        if value > current_year:
            raise ValueError(f"year_built cannot be later than the current year ({current_year})")
        return value


class HomeRead(BaseModel):
    """Response body for a home profile."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    size_sqm: float
    year_built: int
    heating_type: HeatingType
    insulation_quality: InsulationQuality
    occupants: int | None
    created_at: datetime


class Recommendation(BaseModel):
    """A single actionable, prioritized energy-saving recommendation."""

    title: str = Field(description="Short, actionable headline, e.g. 'Upgrade loft insulation'")
    description: str = Field(description="1-3 sentences explaining the recommendation and why")
    priority: RecommendationPriority
    category: str = Field(description="e.g. insulation, heating, windows, behavioral")
    estimated_annual_savings_eur: float | None = Field(
        default=None, description="Rough estimated annual savings in EUR, if estimable"
    )


class AdviceResponse(BaseModel):
    """Response body for POST /api/homes/{id}/advice."""

    home_id: str
    summary: str = Field(description="A short overview of the home's energy profile")
    recommendations: list[Recommendation]
    generated_at: datetime
    source: str = Field(description="'llm' for a live model response, 'mock' for the fallback")


class ErrorResponse(BaseModel):
    """Standard error body returned by all failure responses."""

    detail: str
