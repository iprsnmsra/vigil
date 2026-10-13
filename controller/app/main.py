import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI

from .config import settings
from .rules import rule_engine
from .actions import audit_log

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.VERSION}")
    rule_engine.load_rules()
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)


@app.post("/webhooks/alertmanager")
async def handle_alert(payload: Dict[str, Any]):
    """Receives Alertmanager webhook payloads."""
    logger.info("Received alert payload")

    alerts = payload.get("alerts", [])
    for alert in alerts:
        match = rule_engine.match_alert(alert)
        if match:
            logger.info(f"Alert matched rule: {match.name}")
            # In a real system, we'd trigger actions asynchronously here

    return {"status": "success", "processed_alerts": len(alerts)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.VERSION}


@app.get("/api/rules")
async def get_rules():
    """Returns loaded healing rules."""
    return {"rules": [rule.dict() for rule in rule_engine.rules]}


@app.get("/api/actions")
async def get_actions():
    """Returns audit log of actions taken."""
    return {"actions": audit_log.get_recent_actions()}
