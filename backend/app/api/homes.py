from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import advice_source_label, get_llm_client
from app.db.session import get_db
from app.llm.base import LLMClient
from app.schemas.home import AdviceResponse, HomeCreate, HomeRead
from app.services import advice_service, home_service

router = APIRouter(prefix="/api/homes", tags=["homes"])


@router.post("", response_model=HomeRead, status_code=status.HTTP_201_CREATED)
def create_home(payload: HomeCreate, db: Session = Depends(get_db)) -> HomeRead:
    """Create a home profile."""
    home = home_service.create_home(db, payload)
    return HomeRead.model_validate(home)


@router.get("/{home_id}", response_model=HomeRead)
def read_home(home_id: str, db: Session = Depends(get_db)) -> HomeRead:
    """Retrieve a home profile by id."""
    home = home_service.get_home(db, home_id)
    return HomeRead.model_validate(home)


@router.post("/{home_id}/advice", response_model=AdviceResponse)
def create_advice(
    home_id: str,
    db: Session = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
) -> AdviceResponse:
    """Generate prioritized energy-saving recommendations for a home via the LLM."""
    return advice_service.generate_advice(
        db, home_id, llm_client, source=advice_source_label(llm_client)
    )
