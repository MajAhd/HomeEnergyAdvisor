from app.db.models import Home
from app.llm.mock_client import MockLLMClient
from app.models.enums import HeatingType, InsulationQuality


def _home(**overrides) -> Home:
    defaults = dict(
        id="test-id",
        size_sqm=100.0,
        year_built=1990,
        heating_type=HeatingType.GAS,
        insulation_quality=InsulationQuality.POOR,
        occupants=4,
    )
    return Home(**{**defaults, **overrides})


def test_old_poorly_insulated_gas_home_gets_high_priority_recommendations() -> None:
    home = _home(
        year_built=1970, heating_type=HeatingType.GAS, insulation_quality=InsulationQuality.POOR
    )

    result = MockLLMClient().generate_advice(home)

    assert any(rec.priority == "high" for rec in result.recommendations)
    categories = {rec.category for rec in result.recommendations}
    assert "insulation" in categories
    assert "heating" in categories


def test_new_efficient_home_gets_no_high_priority_recommendations() -> None:
    home = _home(
        year_built=2022,
        heating_type=HeatingType.HEAT_PUMP,
        insulation_quality=InsulationQuality.EXCELLENT,
    )

    result = MockLLMClient().generate_advice(home)

    assert all(rec.priority != "high" for rec in result.recommendations)


def test_result_always_has_between_three_and_six_recommendations() -> None:
    for insulation in InsulationQuality:
        for heating in HeatingType:
            home = _home(heating_type=heating, insulation_quality=insulation)
            result = MockLLMClient().generate_advice(home)
            assert 3 <= len(result.recommendations) <= 6


def test_summary_mentions_no_api_key_fallback() -> None:
    result = MockLLMClient().generate_advice(_home())

    assert "Mock advice" in result.summary
