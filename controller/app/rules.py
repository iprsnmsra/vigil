import yaml
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import os

logger = logging.getLogger(__name__)

@dataclass
class Rule:
    name: str
    alert_match: Dict[str, str]
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    cooldown: str

    def dict(self):
        return asdict(self)

class RuleEngine:
    def __init__(self):
        self.rules: List[Rule] = []

    def load_rules(self, path: str = "rules.yaml"):
        """Loads rules from YAML file."""
        if not os.path.exists(path):
            logger.warning(f"Rules file {path} not found.")
            return

        with open(path, "r") as f:
            try:
                data = yaml.safe_load(f)
                if not data or not isinstance(data, list):
                    return
                self.rules = [Rule(**r) for r in data]
                logger.info(f"Loaded {len(self.rules)} rules.")
            except Exception as e:
                logger.error(f"Error loading rules: {e}")

    def match_alert(self, alert: Dict[str, Any]) -> Optional[Rule]:
        """Finds the first rule that matches the given alert."""
        labels = alert.get("labels", {})
        
        for rule in self.rules:
            matches = True
            for k, v in rule.alert_match.items():
                if labels.get(k) != v:
                    matches = False
                    break
            
            if matches:
                return rule
        return None

rule_engine = RuleEngine()
