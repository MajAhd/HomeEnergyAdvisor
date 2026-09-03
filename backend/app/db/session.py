from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()
is_sqlite = settings.database_url.startswith("sqlite")

if is_sqlite and ":memory:" not in settings.database_url:
    # e.g. "sqlite:///./data/home_energy_advisor.db" -> ./data
    db_path = Path(settings.database_url.split("///")[-1])
    db_path.parent.mkdir(parents=True, exist_ok=True)

# check_same_thread is only relevant to SQLite; harmless to pass unconditionally
# since it's ignored by other dialects when not applicable, but we scope it to
# avoid surprising a future Postgres deployment.
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
