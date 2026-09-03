from app.db.models import Home
from app.llm.base import LLMAdviceResult, LLMClient
from app.models.enums import HeatingType, InsulationQuality, RecommendationPriority
from app.schemas.home import Recommendation

OLD_HOME_YEAR_THRESHOLD = 1995


class MockLLMClient(LLMClient):
    def generate_advice(self, home: Home) -> LLMAdviceResult:
        recommendations = [
            *_insulation_recommendation(home),
            *_heating_recommendation(home),
            *_windows_recommendation(home),
            _behavioral_recommendation(),
        ]
        return LLMAdviceResult(summary=_summary(home), recommendations=recommendations)


def _summary(home: Home) -> str:
    age = "older" if home.year_built < OLD_HOME_YEAR_THRESHOLD else "newer"
    return (
        f"This {home.size_sqm:.0f} m² {age} home, built in {home.year_built}, uses "
        f"{home.heating_type.value.replace('_', ' ')} heating with "
        f"{home.insulation_quality.value} insulation. [Mock advice - no LLM API key "
        "configured; see README for how to enable live recommendations.]"
    )


def _insulation_recommendation(home: Home) -> list[Recommendation]:
    if home.insulation_quality in (InsulationQuality.POOR, InsulationQuality.AVERAGE):
        priority = (
            RecommendationPriority.HIGH
            if home.insulation_quality == InsulationQuality.POOR
            else RecommendationPriority.MEDIUM
        )
        return [
            Recommendation(
                title="Upgrade loft and wall insulation",
                description=(
                    "Your home's insulation is rated "
                    f"'{home.insulation_quality.value}'. Adding or upgrading loft and "
                    "cavity wall insulation typically cuts heat loss significantly in "
                    "homes at this level."
                ),
                priority=priority,
                category="insulation",
                estimated_annual_savings_eur=(
                    350.0 if priority == RecommendationPriority.HIGH else 180.0
                ),
            )
        ]
    return [
        Recommendation(
            title="Maintain current insulation",
            description=(
                "Insulation is already rated "
                f"'{home.insulation_quality.value}' - no upgrade needed, just keep an "
                "eye out for gaps around loft hatches and pipe penetrations."
            ),
            priority=RecommendationPriority.LOW,
            category="insulation",
            estimated_annual_savings_eur=None,
        )
    ]


def _heating_recommendation(home: Home) -> list[Recommendation]:
    if home.heating_type in (HeatingType.OIL, HeatingType.GAS):
        return [
            Recommendation(
                title="Plan a transition to a heat pump",
                description=(
                    f"{home.heating_type.value.title()} heating is one of the largest "
                    "contributors to a home's energy bill and carbon footprint. A heat "
                    "pump is typically 3-4x more efficient, especially once combined "
                    "with the insulation improvements above."
                ),
                priority=RecommendationPriority.HIGH
                if home.year_built < OLD_HOME_YEAR_THRESHOLD
                else RecommendationPriority.MEDIUM,
                category="heating",
                estimated_annual_savings_eur=400.0,
            )
        ]
    if home.heating_type == HeatingType.ELECTRIC:
        return [
            Recommendation(
                title="Consider a heat pump upgrade",
                description=(
                    "Direct electric heating is simple but costly to run. A heat pump "
                    "uses the same electricity supply far more efficiently."
                ),
                priority=RecommendationPriority.MEDIUM,
                category="heating",
                estimated_annual_savings_eur=250.0,
            )
        ]
    return [
        Recommendation(
            title="Service your heating system annually",
            description=(
                "Your heating type is already efficient - regular servicing keeps it "
                "running at peak efficiency."
            ),
            priority=RecommendationPriority.LOW,
            category="heating",
            estimated_annual_savings_eur=None,
        )
    ]


def _windows_recommendation(home: Home) -> list[Recommendation]:
    if home.year_built < OLD_HOME_YEAR_THRESHOLD:
        return [
            Recommendation(
                title="Upgrade to double or triple glazing",
                description=(
                    f"Homes built in {home.year_built} often still have single or "
                    "early double glazing. Modern double/triple glazing reduces heat "
                    "loss through windows substantially."
                ),
                priority=RecommendationPriority.MEDIUM,
                category="windows",
                estimated_annual_savings_eur=150.0,
            )
        ]
    return []


def _behavioral_recommendation() -> Recommendation:
    return Recommendation(
        title="Lower thermostat by 1-2°C and use a programmable schedule",
        description=(
            "A small, low-effort reduction in set temperature combined with "
            "scheduling heating around when the home is occupied is one of the "
            "cheapest ways to cut energy use."
        ),
        priority=RecommendationPriority.LOW,
        category="behavioral",
        estimated_annual_savings_eur=80.0,
    )
