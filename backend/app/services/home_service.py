import logging

from sqlalchemy.orm import Session

from app.db.models import Home
from app.exceptions import HomeNotFoundError
from app.schemas.home import HomeCreate

logger = logging.getLogger(__name__)


def create_home(db: Session, payload: HomeCreate) -> Home:
    home = Home(**payload.model_dump())
    db.add(home)
    db.commit()
    db.refresh(home)
    logger.info(
        "Created home %s (%sm2, built %s, %s heating)",
        home.id,
        home.size_sqm,
        home.year_built,
        home.heating_type,
    )
    return home


def get_home(db: Session, home_id: str) -> Home:
    home = db.get(Home, home_id)
    if home is None:
        raise HomeNotFoundError(home_id)
    return home
