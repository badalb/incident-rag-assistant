
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.investigation_routes import router as investigation_router
from app.investigation.investigation_service import InvestigationService


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize shared application resources at startup
    and release them during shutdown.
    """

    logger.info("Starting Incident RCA Assistant...")

    service = InvestigationService()

    app.state.investigation_service = service

    logger.info("Investigation service initialized.")

    yield

    logger.info("Shutting down Incident RCA Assistant...")

    service.close()

    logger.info("Investigation service closed.")


app = FastAPI(
    title="Incident RCA Assistant",
    description=(
        "Enterprise incident investigation using "
        "Hybrid Retrieval, Neo4j GraphRAG and LLM-based RCA."
    ),
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "UP",
        "application": "Incident RCA Assistant"
    }


app.include_router(investigation_router)
