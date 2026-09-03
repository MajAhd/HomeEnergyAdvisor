"""Enums shared between the ORM layer and the API schemas.

Living in one place keeps the set of valid values ("what is a heating type?") defined
exactly once, instead of drifting between the DB model and the Pydantic schema.
"""

from enum import StrEnum


class HeatingType(StrEnum):
    GAS = "gas"
    OIL = "oil"
    ELECTRIC = "electric"
    HEAT_PUMP = "heat_pump"
    DISTRICT_HEATING = "district_heating"
    OTHER = "other"


class InsulationQuality(StrEnum):
    POOR = "poor"
    AVERAGE = "average"
    GOOD = "good"
    EXCELLENT = "excellent"


class RecommendationPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
