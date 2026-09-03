from app.db.models import Home
from app.models.enums import HeatingType, InsulationQuality

SYSTEM_PROMPT = """\
You are an energy efficiency advisor for residential homes. Given a structured \
home profile, you produce a short summary and a prioritized list of concrete, \
actionable energy-saving recommendations.

Rules:
- Base every recommendation strictly on the home profile provided. Do not invent \
facts about the home that weren't given to you.
- Prioritize recommendations that matter most for THIS home: an old, poorly \
insulated home heated by oil or gas should see insulation and heating-system \
recommendations ranked "high"; a new, well-insulated, heat-pump home should see \
mostly "low"-priority, incremental suggestions.
- Each recommendation must be specific enough to act on (e.g. "Add 200-300mm of \
loft insulation" rather than "Improve insulation").
- estimated_annual_savings_eur is a rough order-of-magnitude estimate for a \
typical Western/Central European household. Set it to null when you cannot make \
even a rough estimate - never fabricate a precise-looking number you aren't \
reasonably confident in.
- Return 3 to 6 recommendations, ordered by priority (high first).
- Write the summary and recommendations in plain, non-technical English a \
homeowner can understand.
"""


def build_user_prompt(home: Home) -> str:
    """Render the home profile as the user turn."""
    occupants_line = f"- Occupants: {home.occupants}\n" if home.occupants is not None else ""
    return (
        "Home profile:\n"
        f"- Size: {home.size_sqm} square meters\n"
        f"- Year built: {home.year_built}\n"
        f"- Heating type: {_humanize(home.heating_type)}\n"
        f"- Insulation quality: {_humanize(home.insulation_quality)}\n"
        f"{occupants_line}"
        "\nGenerate the energy efficiency summary and recommendations for this home."
    )


def _humanize(value: HeatingType | InsulationQuality) -> str:
    return value.value.replace("_", " ")


RECOMMENDATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "A 2-3 sentence overview of this home's energy profile",
        },
        "recommendations": {
            "type": "array",
            "minItems": 3,
            "maxItems": 6,
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                    "category": {
                        "type": "string",
                        "description": "e.g. insulation, heating, windows, behavioral",
                    },
                    "estimated_annual_savings_eur": {"type": ["number", "null"]},
                },
                "required": [
                    "title",
                    "description",
                    "priority",
                    "category",
                    "estimated_annual_savings_eur",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary", "recommendations"],
    "additionalProperties": False,
}
