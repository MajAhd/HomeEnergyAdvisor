import pytest
from sqlalchemy.orm import Session

from app.exceptions import HomeNotFoundError
from app.models.enums import HeatingType, InsulationQuality
from app.schemas.home import HomeCreate
from app.services import home_service


def test_create_home_persists_and_returns_home(db_session: Session) -> None:
    # Arrange
    payload = HomeCreate(
        size_sqm=85,
        year_built=2010,
        heating_type=HeatingType.HEAT_PUMP,
        insulation_quality=InsulationQuality.GOOD,
        occupants=2,
    )

    # Act
    home = home_service.create_home(db_session, payload)

    # Assert
    assert home.id
    assert home.size_sqm == 85
    assert home.heating_type == HeatingType.HEAT_PUMP


def test_get_home_returns_created_home(db_session: Session) -> None:
    # Arrange
    payload = HomeCreate(
        size_sqm=60,
        year_built=1970,
        heating_type=HeatingType.OIL,
        insulation_quality=InsulationQuality.POOR,
        occupants=None,
    )
    created = home_service.create_home(db_session, payload)

    # Act
    fetched = home_service.get_home(db_session, created.id)

    # Assert
    assert fetched.id == created.id


def test_get_home_raises_not_found_for_missing_id(db_session: Session) -> None:
    # Act & Assert
    with pytest.raises(HomeNotFoundError):
        home_service.get_home(db_session, "missing-id")
