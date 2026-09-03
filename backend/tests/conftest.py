import os
from collections.abc import Generator

# Must be set before `app.main` (and therefore app.core.config / app.db.session) is
# imported below, so the app's own module-level engine never touches a real file on
# disk during tests - the app's default DB/LLM deps are overridden per-request
# anyway, but this keeps the startup-time create_all() call harmless too.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("LLM_MODE", "mock")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_llm_client
from app.db.base import Base
from app.db.session import get_db
from app.llm.mock_client import MockLLMClient
from app.main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """A fresh in-memory SQLite DB per test, sharing one connection via StaticPool
    so the schema created in this fixture is visible to the app's own sessions."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient with the DB and LLM dependencies overridden - in-memory DB and the
    deterministic mock LLM, so tests need neither a real database nor an API key."""

    def _get_db_override() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_llm_client] = lambda: MockLLMClient()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


VALID_HOME_PAYLOAD = {
    "size_sqm": 120,
    "year_built": 1985,
    "heating_type": "gas",
    "insulation_quality": "poor",
    "occupants": 3,
}
