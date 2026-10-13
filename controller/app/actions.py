import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditLog:
    def __init__(self):
        self.actions: List[Dict[str, Any]] = []

    def log_action(self, action_name: str, target: str, status: str, details: str = ""):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action_name,
            "target": target,
            "status": status,
            "details": details
        }
        self.actions.append(entry)
        logger.info(f"Audit: {action_name} on {target} - {status}")

    def get_recent_actions(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.actions[-limit:]

audit_log = AuditLog()

class Action(ABC):
    def __init__(self, target: str):
        self.target = target

    @abstractmethod
    def execute(self) -> bool:
        pass

    def dry_run(self) -> bool:
        logger.info(f"[DRY RUN] Would execute {self.__class__.__name__} on {self.target}")
        audit_log.log_action(self.__class__.__name__, self.target, "DRY_RUN")
        return True

class RestartAction(Action):
    def execute(self) -> bool:
        logger.info(f"Executing RestartAction on {self.target}")
        audit_log.log_action("RestartAction", self.target, "SUCCESS")
        return True

class RollbackAction(Action):
    def execute(self) -> bool:
        logger.info(f"Executing RollbackAction on {self.target}")
        audit_log.log_action("RollbackAction", self.target, "SUCCESS")
        return True

class ScaleAction(Action):
    def __init__(self, target: str, replicas: int):
        super().__init__(target)
        self.replicas = replicas

    def execute(self) -> bool:
        logger.info(f"Executing ScaleAction on {self.target} to {self.replicas} replicas")
        audit_log.log_action("ScaleAction", self.target, "SUCCESS", f"replicas={self.replicas}")
        return True

class GitHubIssueAction(Action):
    def __init__(
        self,
        target: str,
        alert_data: Optional[Dict[str, Any]] = None,
        pod_logs: str = "",
        events: str = "",
    ):
        super().__init__(target)
        self.alert_data = alert_data or {"labels": {"alertname": "IncidentAlert", "pod": target}}
        self.pod_logs = pod_logs
        self.events = events
        self.analysis_result: Optional[Dict[str, Any]] = None

    def execute(self) -> bool:
        from .ai_analyzer import gemini_analyzer
        self.analysis_result = gemini_analyzer.analyze_incident(
            alert=self.alert_data,
            pod_logs=self.pod_logs,
            events=self.events,
            action_taken="Remediation executed",
        )
        model_used = self.analysis_result.get("model", "unknown")
        logger.info(f"Executing GitHubIssueAction for {self.target} (AI: {model_used})")
        audit_log.log_action("GitHubIssueAction", self.target, "SUCCESS", f"AI_Model={model_used}")
        return True

    def dry_run(self) -> bool:
        from .ai_analyzer import gemini_analyzer
        self.analysis_result = gemini_analyzer.analyze_incident(
            alert=self.alert_data,
            pod_logs=self.pod_logs,
            events=self.events,
            action_taken="Dry-run simulation",
        )
        model_used = self.analysis_result.get("model", "unknown")
        logger.info(f"[DRY RUN] Prepared GitHub issue for {self.target} (AI: {model_used})")
        audit_log.log_action("GitHubIssueAction", self.target, "DRY_RUN", f"AI_Model={model_used}")
        return True
