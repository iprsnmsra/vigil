import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from fastapi import FastAPI

from .config import settings
from .rules import rule_engine
from .actions import (
    audit_log,
    RestartAction,
    RollbackAction,
    ScaleAction,
    GitHubIssueAction,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

recent_incidents: List[Dict[str, Any]] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.VERSION}")
    rule_engine.load_rules(settings.RULES_PATH if hasattr(settings, 'RULES_PATH') and settings.RULES_PATH else "rules.yaml")
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)


@app.post("/webhooks/alertmanager")
async def handle_alert(payload: Dict[str, Any]):
    """Receives Alertmanager webhook payloads and triggers healing actions."""
    logger.info("Received alert payload")

    alerts = payload.get("alerts", [])
    executed_actions = []

    for alert in alerts:
        match = rule_engine.match_alert(alert)
        if match:
            labels = alert.get("labels", {})
            target = labels.get("pod") or labels.get("deployment") or labels.get("alertname", "workload")
            logger.info(f"Alert matched rule '{match.name}' for target '{target}'")

            for act in match.actions:
                act_type = act.get("type")
                action_obj = None

                if act_type == "restart":
                    action_obj = RestartAction(target=target)
                elif act_type == "rollback":
                    action_obj = RollbackAction(target=target)
                elif act_type == "scale":
                    action_obj = ScaleAction(target=target, replicas=act.get("replicas", 3))
                elif act_type == "github_issue":
                    action_obj = GitHubIssueAction(target=target, alert_data=alert)

                if action_obj:
                    if settings.DRY_RUN:
                        action_obj.dry_run()
                    else:
                        action_obj.execute()

                    if isinstance(action_obj, GitHubIssueAction) and action_obj.analysis_result:
                        recent_incidents.append({
                            "target": target,
                            "rule": match.name,
                            "analysis": action_obj.analysis_result,
                        })

                    executed_actions.append({"rule": match.name, "action": act_type, "target": target})

    return {
        "status": "success",
        "processed_alerts": len(alerts),
        "actions_triggered": executed_actions,
    }


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


@app.get("/api/incidents")
async def get_incidents():
    """Returns recent incident root-cause analyses."""
    return {"incidents": recent_incidents[-10:]}
