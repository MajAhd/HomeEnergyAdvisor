import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.homes import router as homes_router
from app.api.middleware import log_requests
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine
from app.exceptions import HomeNotFoundError, LLMError, LLMResponseParsingError

configure_logging()
settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Generates AI-powered energy efficiency recommendations for a home profile.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(log_requests)

app.include_router(homes_router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(HomeNotFoundError)
def home_not_found_handler(request: Request, exc: HomeNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(LLMError)
def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    # error, not warning: this means the LLM provider failed for a live user
    # request and is worth alerting on, not just noting.
    logger.error("LLM provider failure [%s]: %s", request.state.request_id, exc)
    # 502: we're a valid gateway to an upstream (the LLM provider) that failed.
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(LLMResponseParsingError)
def llm_parsing_error_handler(request: Request, exc: LLMResponseParsingError) -> JSONResponse:
    logger.error("LLM response parsing failure [%s]: %s", request.state.request_id, exc)
    return JSONResponse(status_code=502, content={"detail": str(exc)})
