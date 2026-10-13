import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
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
    def execute(self) -> bool:
        logger.info(f"Executing GitHubIssueAction for {self.target}")
        audit_log.log_action("GitHubIssueAction", self.target, "SUCCESS")
        return True
