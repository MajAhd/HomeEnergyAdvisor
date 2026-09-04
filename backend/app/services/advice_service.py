import logging
import time
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.llm.base import LLMClient
from app.schemas.home import AdviceResponse
from app.services.home_service import get_home

logger = logging.getLogger(__name__)


def generate_advice(
    db: Session, home_id: str, llm_client: LLMClient, source: str
) -> AdviceResponse:
    """Look up the home and produce a fresh set of recommendations for it.

    Advice is generated fresh on every call rather than cached/persisted - the
    simplest correct behavior for this scope. A production version would likely
    store generated advice (keyed by home + a hash of its fields) so repeat requests
    are free and a history of past advice is available; noted as a tradeoff in the
    README.
    """
    home = get_home(db, home_id)

    logger.info("Requesting %s advice for home %s", source, home_id)
    start = time.perf_counter()
    result = llm_client.generate_advice(home)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "Generated %d recommendation(s) for home %s via %s (%.0fms)",
        len(result.recommendations),
        home_id,
        source,
        duration_ms,
    )

    return AdviceResponse(
        home_id=home.id,
        summary=result.summary,
        recommendations=result.recommendations,
        generated_at=datetime.now(UTC),
        source=source,
    )
