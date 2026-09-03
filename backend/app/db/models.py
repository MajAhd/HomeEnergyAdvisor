import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import HeatingType, InsulationQuality


def _new_id() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Home(Base):
    """A user-submitted home profile used to generate energy-saving advice."""

    __tablename__ = "homes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_new_id)
    size_sqm: Mapped[float] = mapped_column(Float, nullable=False)
    year_built: Mapped[int] = mapped_column(Integer, nullable=False)
    heating_type: Mapped[HeatingType] = mapped_column(Enum(HeatingType), nullable=False)
    insulation_quality: Mapped[InsulationQuality] = mapped_column(
        Enum(InsulationQuality), nullable=False
    )
    occupants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
