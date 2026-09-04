from app.db.models import Home
from app.llm.prompts import RECOMMENDATION_JSON_SCHEMA, SYSTEM_PROMPT, build_user_prompt
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


def test_user_prompt_includes_all_home_attributes() -> None:
    # Arrange
    home = _home()

    # Act
    prompt = build_user_prompt(home)

    # Assert
    assert "100.0" in prompt
    assert "1990" in prompt
    assert "gas" in prompt
    assert "poor" in prompt
    assert "Occupants: 4" in prompt


def test_user_prompt_omits_occupants_line_when_not_provided() -> None:
    # Arrange
    home = _home(occupants=None)

    # Act
    prompt = build_user_prompt(home)

    # Assert
    assert "Occupants" not in prompt


def test_system_prompt_instructs_grounding_in_given_facts() -> None:
    # Assert
    assert "Do not invent" in SYSTEM_PROMPT


def test_system_prompt_instructs_prioritization() -> None:
    # Assert
    assert "prioritiz" in SYSTEM_PROMPT.lower() or "priority" in SYSTEM_PROMPT.lower()


def test_recommendation_schema_requires_summary_and_recommendations() -> None:
    # Assert
    assert set(RECOMMENDATION_JSON_SCHEMA["required"]) == {"summary", "recommendations"}
    assert RECOMMENDATION_JSON_SCHEMA["additionalProperties"] is False


def test_recommendation_schema_item_requires_all_fields() -> None:
    # Arrange
    item_schema = RECOMMENDATION_JSON_SCHEMA["properties"]["recommendations"]["items"]

    # Assert
    assert set(item_schema["required"]) == {
        "title",
        "description",
        "priority",
        "category",
        "estimated_annual_savings_eur",
    }
    assert item_schema["properties"]["priority"]["enum"] == ["high", "medium", "low"]
